#!/usr/bin/env python3
"""Minimal LLM Gateway for the Claude Code FSI demo.

Claude Code (CLAUDE_CODE_USE_BEDROCK=1, CLAUDE_CODE_SKIP_BEDROCK_AUTH=1) sends Bedrock
InvokeModel requests here. The gateway authenticates the developer token, enforces the
model allowlist and a DLP check, re-signs the request with its own AWS role (SigV4) and
streams the Bedrock response back unchanged. Every decision is written to an audit log.
"""
import base64, json, os, re, sys, time, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import boto3, requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.eventstream import EventStreamBuffer

REGION = os.environ.get("GW_REGION", "ap-northeast-2")
LISTEN = int(os.environ.get("GW_PORT", "8787"))
BIND = os.environ.get("GW_BIND", "127.0.0.1")
AUDIT = os.environ.get("GW_AUDIT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "audit.jsonl"))
POLICY = json.load(open(os.environ.get("GW_POLICY", os.path.join(os.path.dirname(__file__), "policy.json"))))
TOKENS = POLICY["tokens"]              # bearer token -> {"user": ..., "group": ...}
ALLOWED = set(POLICY["allowed_models"])
DLP = [(r["name"], re.compile(r["pattern"])) for r in POLICY["dlp_rules"]]
SESSION = boto3.Session(region_name=REGION)


def audit(**rec):
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **rec}
    with open(AUDIT, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tag = "\033[32mALLOW\033[0m" if rec.get("decision") == "ALLOW" else "\033[31mBLOCK\033[0m"
    print(f"[{rec['ts'][11:19]}] {tag} user={rec.get('user')} model={rec.get('model')} "
          f"{rec.get('reason', '')} in={rec.get('input_tokens', '-')} out={rec.get('output_tokens', '-')}",
          flush=True)


def user_texts(body):
    """Text the developer typed (user-role text blocks), excluding tool results."""
    for m in body.get("messages", []):
        if m.get("role") != "user":
            continue
        content = m.get("content")
        if isinstance(content, str):
            yield content
            continue
        for block in content or []:
            if block.get("type") == "text":
                yield block.get("text", "")


def signed(method, url, body, headers, service):
    req = AWSRequest(method=method, url=url, data=body, headers=headers)
    SigV4Auth(SESSION.get_credentials().get_frozen_credentials(), service, REGION).add_auth(req)
    return dict(req.headers)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def reply(self, code, obj, err="ValidationException"):
        # Policy denials use 400 ValidationException: Bedrock clients do not retry it,
        # so the developer sees the reason immediately.
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("x-amzn-ErrorType", err)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def ident(self):
        tok = self.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        return TOKENS.get(tok)

    def do_GET(self):  # startup probe: GET /inference-profiles
        who = self.ident()
        if not who:
            return self.reply(401, {"message": "LLM Gateway: 인증 토큰이 없거나 유효하지 않습니다"})
        url = f"https://bedrock.{REGION}.amazonaws.com{self.path}"
        r = requests.get(url, headers=signed("GET", url, None, {}, "bedrock"), timeout=30)
        self.send_response(r.status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(r.content)))
        self.end_headers()
        self.wfile.write(r.content)

    def do_POST(self):
        t0 = time.time()
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        m = re.match(r"^/model/([^/]+)/(invoke|invoke-with-response-stream|count-tokens)$", self.path)
        if not m:
            return self.reply(404, {"message": f"LLM Gateway: unsupported path {self.path}"})
        model, op = urllib.parse.unquote(m.group(1)), m.group(2)
        who = self.ident()
        if not who:
            audit(user="(unknown)", model=model, op=op, decision="BLOCK", reason="auth")
            return self.reply(400, {"message": "LLM Gateway: 인증 토큰이 없거나 유효하지 않습니다"})
        base = dict(user=who["user"], group=who["group"], model=model, op=op)
        if model not in ALLOWED:
            audit(**base, decision="BLOCK", reason="model_not_allowed")
            return self.reply(400, {"message": f"LLM Gateway: 승인되지 않은 모델입니다 ({model}). 허용 모델: {', '.join(sorted(ALLOWED))}"})
        body = json.loads(raw or b"{}")
        if op != "count-tokens":
            for name, rx in DLP:
                for text in user_texts(body):
                    hit = rx.search(text)
                    if hit:
                        masked = hit.group(0)[:4] + "*" * (len(hit.group(0)) - 4)
                        audit(**base, decision="BLOCK", reason=f"dlp:{name}", sample=masked)
                        return self.reply(400, {"message": f"LLM Gateway DLP: 프롬프트에 {name} 패턴이 있어 전송을 차단했습니다 ({masked})"})
        url = f"https://bedrock-runtime.{REGION}.amazonaws.com/model/{urllib.parse.quote(model, safe='')}/{op}"
        hdrs = {"Content-Type": "application/json", "Accept": self.headers.get("Accept", "application/json")}
        r = requests.post(url, data=raw, headers=signed("POST", url, raw, hdrs, "bedrock"), stream=True, timeout=600)
        self.send_response(r.status_code)
        for k in ("Content-Type", "x-amzn-RequestId"):
            if k in r.headers:
                self.send_header(k, r.headers[k])
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        usage, buf = {}, EventStreamBuffer()
        for chunk in r.iter_content(chunk_size=None):
            self.wfile.write(f"{len(chunk):x}\r\n".encode() + chunk + b"\r\n")
            self.wfile.flush()
            if op == "invoke-with-response-stream":
                buf.add_data(chunk)
                for ev in buf:
                    try:
                        inner = json.loads(base64.b64decode(json.loads(ev.payload)["bytes"]))
                    except Exception:
                        continue
                    if inner.get("type") == "message_start":
                        u = inner["message"]["usage"]
                        usage["input_tokens"] = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                    elif inner.get("type") == "message_delta":
                        usage["output_tokens"] = inner.get("usage", {}).get("output_tokens")
        self.wfile.write(b"0\r\n\r\n")
        if op == "invoke" and r.ok:
            try:
                u = json.loads(r.content).get("usage", {})
                usage = {"input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens")}
            except Exception:
                pass
        if op != "count-tokens":
            audit(**base, decision="ALLOW" if r.ok else "ERROR", reason=f"bedrock:{r.status_code}",
                  latency_ms=int((time.time() - t0) * 1000), **usage)


if __name__ == "__main__":
    os.makedirs(os.path.dirname(AUDIT), exist_ok=True)
    print(f"LLM Gateway listening on {BIND}:{LISTEN} -> bedrock-runtime.{REGION}", flush=True)
    ThreadingHTTPServer((BIND, LISTEN), Handler).serve_forever()
