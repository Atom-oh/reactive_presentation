# EKS Hybrid Nodes 1시간 세션 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 개념과 아키텍처 중심의 60분 L200 덱 `eks-hybrid-nodes-1h/`를 만들고, 무음 HyperFrames 데모 영상 4편을 넣고, 기존 덱을 "Deep Dive (2시간)"으로 이름만 바꾼다.

**Architecture:** Remarp markdown(블록 4개)을 `remarp_to_slides.py build`로 HTML로 만든다. 생성기가 잃는 수정(표지 그라데이션, GA 태그, Thank you 스타일)은 post-build 스크립트로 다시 넣는다. 영상은 `videos/<id>/` HyperFrames 프로젝트에서 `media/<id>.mp4`로 렌더해 `<video>`로 넣는다. 슬라이드 내용은 Deep Dive 덱에서 가져와 줄이며 새 사실을 만들지 않는다.

**Tech Stack:** Remarp + reactive-presentation 프레임워크(`common/`), Python 3, 헤드리스 Chromium(`~/.cache/ms-playwright/chromium-1223/chrome-linux/chrome`), HyperFrames CLI(`npx hyperframes`), ffmpeg(`~/.local/bin/ffmpeg`).

**Spec:** `docs/superpowers/specs/2026-10-18-eks-hybrid-nodes-1h-session-design.md`

## Global Constraints

- 60분, L200, 청중은 아키텍트와 의사결정자. 내용은 한국어, 기술 용어는 영어
- 상세 설정 제외: 슬라이드 본문에 YAML, CLI 명령, `.code-block` 금지. 필요하면 "Deep Dive N부" 안내
- 슬라이드 텍스트에 em dash(—)와 가운데 점(·) 금지. 구분자는 ":" 또는 ","
- 퀴즈 없음(`quiz: false`)
- 수치는 Deep Dive 5부와 `~/eks-hybrid-demo/results/`, `RUNBOOK.md`의 실측값만 사용
- 영상: 1920×1080 mp4, 무음, 화면에 "실측 결과 재구성 (2026-10 시뮬레이션 환경)" 표기, 영상당 25MB 이하. 넘으면 CloudFront → 비공개 S3(OAC). 이때 대상 계정과 변경을 보여 주고 승인받은 뒤 진행
- 기존 `eks-hybrid-nodes/` URL 유지
- 보안: S3 public 금지, CloudFront만 공개 진입점
- 생성된 HTML을 손으로 고치지 않는다. md를 고치고 build와 post-build를 다시 돌린다
- 커밋은 브랜치 `feat/eks-hybrid-nodes-1h-2026-10-18`, 메시지 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`

## Review Focus

- 발표 노트북이 오프라인이거나 영상 로드가 느릴 때: 슬라이드에 포스터 이미지가 보이고 Play로 재생되어야 함(Task 1 검사에 포스터 존재 확인)
- 영상 슬라이드에서 키보드 화살표: 다음 슬라이드로 넘어가야 하며 영상 컨트롤이 키를 가로채지 않아야 함(Task 9 Step 4)
- 영상 속 수치가 출처와 다를 위험: 영상마다 수치 대조표를 만든다(Task 5~8 Step 1)
- 1280×720보다 작은 화면(프로젝터): 슬라이드 넘침이 없어야 함(Task 1 검사가 1280×720에서 측정)
- 통합본 `index.html`에서 영상 경로가 깨질 위험: 블록 HTML과 통합본 모두 `media/` 상대 경로로 재생되어야 함(Task 10 Step 3)

---

## File Structure

| 경로 | 역할 |
|---|---|
| `eks-hybrid-nodes-1h/_presentation.md` | 메타데이터와 블록 목록(4개) |
| `eks-hybrid-nodes-1h/01-why-architecture.md` | 1부, 2부(표지~자격 증명), 약 9장 |
| `eks-hybrid-nodes-1h/02-networking.md` | 3부, 약 7장 |
| `eks-hybrid-nodes-1h/03-operations.md` | 4부, 약 4장 |
| `eks-hybrid-nodes-1h/04-demo-close.md` | 5부(영상 4편 + 결과), 6부, 약 12장 |
| `eks-hybrid-nodes-1h/*.html`, `index.html`, `toc.html` | 생성물 |
| `eks-hybrid-nodes-1h/common/` | `eks-hybrid-nodes/common/` 복사 |
| `eks-hybrid-nodes-1h/images/`, `diagrams/` | Deep Dive에서 쓰는 그림만 복사 |
| `eks-hybrid-nodes-1h/videos/v1-gateway-failover/` 외 3개 | HyperFrames 프로젝트 |
| `eks-hybrid-nodes-1h/media/v1-gateway-failover.mp4`, `.jpg` 외 | 렌더 결과와 포스터 |
| `~/eks-hybrid-demo/.work/check_1h.py` | 검사 스크립트(저장소 밖) |
| `~/eks-hybrid-demo/.work/postbuild_1h.py` | 생성기 누락 수정 재적용 |
| `eks-hybrid-nodes/_presentation.md`, `01-overview.md` | Deep Dive 이름 변경 |
| `index.html`(루트 허브) | 카드 이름 변경과 새 카드 |

---

### Task 1: 뼈대와 검사 스크립트

**Files:**
- Create: `eks-hybrid-nodes-1h/_presentation.md`, `eks-hybrid-nodes-1h/common/`(복사), `~/eks-hybrid-demo/.work/check_1h.py`, `~/eks-hybrid-demo/.work/postbuild_1h.py`

**Interfaces:**
- Produces: `python3 ~/eks-hybrid-demo/.work/check_1h.py [--md-only]` 종료 코드 0이면 통과. 검사 항목: md 금지 문자, 본문 YAML/명령, 블록 HTML 존재, 영상 src와 poster 파일 존재, 헤드리스 1280×720 슬라이드별 넘침, 총 슬라이드 수 28~34
- Produces: `python3 ~/eks-hybrid-demo/.work/postbuild_1h.py` 생성된 HTML에 표지, GA, Thank you 수정 적용(멱등)

- [ ] **Step 1: 폴더와 common 복사**

```bash
cd ~/reactive_presentation
mkdir -p eks-hybrid-nodes-1h/{media,videos,images}
cp -r eks-hybrid-nodes/common eks-hybrid-nodes-1h/common
```

- [ ] **Step 2: `_presentation.md` 작성**

```markdown
---
remarp: true
version: 1
title: "EKS Hybrid Nodes, 온프레미스를 EKS로 확장하기 (1시간)"
ratio: "16:9"
date: 2026-10-18
lang: ko
level: 200
audience: "아키텍트, 플랫폼 리드, 의사결정자"
quiz: false
duration: 60

speaker:
  name: ""
  title: "Solutions Architect"
  company: "Amazon Web Services"

theme:
  mode: dark
  source: "./common/pptx-theme"
  footer: "© 2026, Amazon Web Services, Inc. or its affiliates. All rights reserved."
  logo: "./common/pptx-theme/images/logo_1.png"

blocks:
  - name: 01-why-architecture
    title: "왜 하이브리드인가, 개념과 아키텍처"
    duration: 16
  - name: 02-networking
    title: "네트워킹"
    duration: 13
  - name: 03-operations
    title: "운영"
    duration: 8
  - name: 04-demo-close
    title: "데모 영상과 마무리"
    duration: 23
---
```

- [ ] **Step 3: 검사 스크립트 작성** (`~/eks-hybrid-demo/.work/check_1h.py`)

```python
#!/usr/bin/env python3
"""Checks for eks-hybrid-nodes-1h. Exit 0 = pass."""
import re, sys, subprocess, pathlib, json, http.server, threading, functools, socketserver
D = pathlib.Path.home() / "reactive_presentation/eks-hybrid-nodes-1h"
CH = pathlib.Path.home() / ".cache/ms-playwright/chromium-1223/chrome-linux/chrome"
BLOCKS = ["01-why-architecture", "02-networking", "03-operations", "04-demo-close"]
errs = []
def body_without_notes(md):
    return re.sub(r":::notes.*?:::", "", md, flags=re.S)
for b in BLOCKS:
    p = D / f"{b}.md"
    if not p.exists(): errs.append(f"missing {p.name}"); continue
    md = p.read_text(encoding="utf-8"); body = body_without_notes(md)
    for ch, name in (("—", "em dash"), ("·", "middle dot")):
        if ch in md: errs.append(f"{p.name}: {name}")
    if re.search(r"```|code-block|apiVersion:|kubectl |helm |aws [a-z0-9-]+ ", body): errs.append(f"{p.name}: config/command in slide body")
    for m in re.finditer(r'(?:src|poster)="(media/[^"]+)"', md):
        if not (D / m.group(1)).exists(): errs.append(f"{p.name}: missing {m.group(1)}")
if "--md-only" not in sys.argv:
    for b in BLOCKS:
        if not (D / f"{b}.html").exists(): errs.append(f"missing {b}.html")
    if not errs:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(D))
        srv = socketserver.TCPServer(("127.0.0.1", 0), handler); port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        harness = D / "_check.html"
        harness.write_text("""<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0"><pre id="o"></pre>
<iframe id="f" style="width:1280px;height:720px;border:0" src="index.html"></iframe><script>
document.getElementById('f').onload=()=>setTimeout(()=>{const d=document.getElementById('f').contentDocument;
const sl=[...d.querySelectorAll('.slide')];const bad=[];
sl.forEach((s,i)=>{sl.forEach(x=>x.classList.remove('active'));s.classList.add('active');
s.querySelectorAll('.fragment').forEach(e=>e.classList.add('visible'));
[...s.querySelectorAll('.slide-body,.card-grid,.callout,.flow-h,.data-table,table')].forEach(e=>{
if(e.scrollHeight>e.clientHeight+2||e.scrollWidth>e.clientWidth+2)bad.push(i+1+':'+e.className.split(' ')[0]);});
const r=s.getBoundingClientRect();[...s.querySelectorAll('.callout,.card,table,video')].forEach(e=>{
if(e.getBoundingClientRect().bottom>r.bottom-40)bad.push(i+1+':below');});});
document.getElementById('o').textContent=JSON.stringify({n:sl.length,bad});},2500);</script></body></html>""", encoding="utf-8")
        out = subprocess.run([str(CH), "--headless", "--no-sandbox", "--disable-gpu", "--window-size=1300,760",
                              "--virtual-time-budget=8000", "--dump-dom", f"http://127.0.0.1:{port}/_check.html"],
                             capture_output=True, text=True, timeout=120).stdout
        harness.unlink(); srv.shutdown()
        m = re.search(r'<pre id="o">([^<]*)</pre>', out)
        res = json.loads(m.group(1)) if m and m.group(1) else {"n": 0, "bad": ["no result"]}
        if not 28 <= res["n"] <= 34: errs.append(f"slide count {res['n']} not in 28..34")
        if res["bad"]: errs.append(f"overflow: {res['bad']}")
        print(f"slides={res['n']}")
print("\n".join(errs) or "PASS"); sys.exit(1 if errs else 0)
```

- [ ] **Step 4: post-build 스크립트 작성** (`~/eks-hybrid-demo/.work/postbuild_1h.py`)

```python
#!/usr/bin/env python3
"""Re-apply fixes the Remarp generator drops (same as the Deep Dive deck). Idempotent."""
import pathlib
D = pathlib.Path.home() / "reactive_presentation/eks-hybrid-nodes-1h"
REP = [
  ('top:-20%; right:-10%; width:60%; height:80%; background:radial-gradient(ellipse, rgba(255,153,0,0.10)',
   'top:0; right:0; width:50%; height:60%; background:radial-gradient(ellipse, rgba(255,153,0,0.10)'),
  ('font-size:3rem; color:var(--text-primary);">Thank You</h1>', 'font-size:calc(var(--fs-title) * 1.5); color:var(--text-primary);">Thank You</h1>'),
  ('font-size:1rem; margin-top:0.5rem;">수고하셨습니다!</p>', 'font-size:var(--fs-card); margin-top:0.5rem;">수고하셨습니다!</p>'),
  ('class="btn btn-primary btn-sm" style="text-decoration:none;">← 목차로 돌아가기</a>', 'class="btn btn-primary" style="text-decoration:none;">← 목차로 돌아가기</a>'),
]
GA = ('  <script async src="https://www.googletagmanager.com/gtag/js?id=G-GWVLEW5JLL"></script>\n'
      "  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','G-GWVLEW5JLL');</script>\n")
for p in D.glob("*.html"):
    s = p.read_text(encoding="utf-8"); o = s
    for a, b in REP: s = s.replace(a, b)
    if p.name == "index.html" and "googletagmanager" not in s:
        i = s.index("<script>window.__remarpTheme"); j = s.index("\n", i) + 1; s = s[:j] + GA + s[j:]
    if s != o: p.write_text(s, encoding="utf-8"); print("fixed", p.name)
```

- [ ] **Step 5: 검사가 실패하는지 확인**

Run: `python3 ~/eks-hybrid-demo/.work/check_1h.py --md-only`
Expected: FAIL, `missing 01-why-architecture.md` 등 4줄

- [ ] **Step 6: 커밋**

```bash
git add eks-hybrid-nodes-1h/_presentation.md eks-hybrid-nodes-1h/common
git commit -m "feat(eks-hybrid-nodes-1h): scaffold 1-hour session deck"
```

### Task 2: 1부와 2부 (왜 하이브리드인가, 개념과 아키텍처)

**Files:**
- Create: `eks-hybrid-nodes-1h/01-why-architecture.md`
- Copy as needed: Deep Dive `images/`, `diagrams/`에서 참조하는 파일만 `eks-hybrid-nodes-1h/` 같은 경로로

**Interfaces:**
- Consumes: Task 1 검사 스크립트
- 출처: `eks-hybrid-nodes/01-overview.md`(표지, 문제 정의, 아키텍처, 책임 분담, 요금, OS, 자격 증명 결정 슬라이드와 `.hn-tip/.hn-pop` CSS)

슬라이드(9장): 1 표지(`@type: cover`, 제목 "EKS Hybrid Nodes", 부제 "온프레미스를 EKS로 확장하기", 셋째 줄 "개념, 아키텍처, 데모 영상") / 2 아젠다(`@type: agenda`, 6부, 시간 표기 없음) / 3 고객 시나리오 4개 카드 / 4 Hybrid Nodes 한 줄 정의와 무엇이 달라지나 / 5 전체 아키텍처(Deep Dive 그림 재사용) / 6 책임 분담 / 7 요금 모델(Deep Dive 숫자 그대로, 4부 가정 문단 포함) / 8 지원 OS와 노드 준비(nodeadm, Bottlerocket 한 줄) / 9 자격 증명 선택(Deep Dive hover 카드 그대로).

- [ ] **Step 1: Deep Dive 원본 확인**

```bash
grep -n "^<!-- Slide\|^## \|src=\"" eks-hybrid-nodes/01-overview.md
```

- [ ] **Step 2: md 작성.** 각 슬라이드는 `---` + `<!-- Slide N: ... -->` + `@type` + `## 제목` + `:::html`(필요 시) + `:::notes`(`{timing: Xmin}`, `[요약]` 3줄, 멘트, `{cue: transition}`). 원본에서 가져올 때 YAML, 명령, 버전 세부 목록은 빼고 결론만 남긴다. 상세 슬라이드 대신 노트에 "자세한 설정은 Deep Dive N부"라고 쓴다.

- [ ] **Step 3: 참조 그림 복사**

```bash
cd ~/reactive_presentation
grep -oE '(images|diagrams)/[^")]+' eks-hybrid-nodes-1h/01-why-architecture.md | sort -u | while read f; do mkdir -p "eks-hybrid-nodes-1h/$(dirname "$f")"; cp "eks-hybrid-nodes/$f" "eks-hybrid-nodes-1h/$f"; done
```

- [ ] **Step 4: md 검사**

Run: `python3 ~/eks-hybrid-demo/.work/check_1h.py --md-only`
Expected: `01-why-architecture.md` 관련 오류 없음(남은 블록 missing만)

- [ ] **Step 5: 커밋**

```bash
git add eks-hybrid-nodes-1h/01-why-architecture.md eks-hybrid-nodes-1h/images eks-hybrid-nodes-1h/diagrams
git commit -m "feat(eks-hybrid-nodes-1h): parts 1-2, why hybrid and architecture"
```

### Task 3: 3부 네트워킹

**Files:**
- Create: `eks-hybrid-nodes-1h/02-networking.md`
- 출처: `eks-hybrid-nodes/02-networking-gateway.md`(라우팅 비교표, CNI 선택, Gateway 구조), `05-live-demo.md`(역방향 경로 슬라이드)

슬라이드(7장): 1 3부 구분 / 2 필수 연결과 CIDR(그림, 겹치지 않는 4종 CIDR, 포트는 종류만) / 3 Pod 라우팅 3가지(Deep Dive 비교표에서 "Pod CIDR 도달 방법", "라우터 변경", "HA/처리량", "cross-AZ 비용" 4행 + 선택 카드 3개) / 4 Gateway 동작(리더와 스탠바이, VPC 라우트, VXLAN, 장애 시 3~5초) / 5 CNI 선택(Cilium 단독과 VPC CNI 혼합, Gateway는 VPC CNI 필요) / 6 트래픽 방향(VPC에서 hybrid로는 Gateway 또는 라우팅, 온프렘에서 리전으로는 internal LB, hairpin 주의) / 7 비용과 대용량(리더 AZ 집중, cross-AZ 요금, 대용량은 BGP).

- [ ] **Step 1: md 작성** (Task 2 Step 2와 같은 슬라이드 형식)
- [ ] **Step 2: 그림 복사** (Task 2 Step 3 명령에서 파일명을 `02-networking.md`로)
- [ ] **Step 3: 검사** `python3 ~/eks-hybrid-demo/.work/check_1h.py --md-only`, `02-networking.md` 오류 없음
- [ ] **Step 4: 커밋** `git add eks-hybrid-nodes-1h/02-networking.md eks-hybrid-nodes-1h/images eks-hybrid-nodes-1h/diagrams && git commit -m "feat(eks-hybrid-nodes-1h): part 3, networking"`

### Task 4: 4부 운영

**Files:**
- Create: `eks-hybrid-nodes-1h/03-operations.md`
- 출처: `eks-hybrid-nodes/03-node-lifecycle.md`, `04-operations-strategy.md`

슬라이드(4장): 1 4부 구분 / 2 노드 라이프사이클과 업그레이드(조인, 업그레이드 순서, 컨트롤 플레인 버전 skew를 흐름도로) / 3 네트워크 단절 시 동작(Deep Dive 4부 내용: 실행 중 Pod 유지, unreachable taint 300초, 자격 증명 1시간과 복구, 대비 3가지) / 4 버스팅 전략 개념(온프렘 우선, 넘치면 클라우드, 줄일 때 온프렘 보호: pod-deletion-cost 개념만, 데모 V2로 연결).

- [ ] **Step 1: md 작성** (Task 2 Step 2 형식)
- [ ] **Step 2: 그림 복사** (Task 2 Step 3, 파일명 `03-operations.md`)
- [ ] **Step 3: 검사** `--md-only`, `03-operations.md` 오류 없음
- [ ] **Step 4: 커밋** `git commit -m "feat(eks-hybrid-nodes-1h): part 4, operations"`

### Task 5: 영상 V1 Gateway 리더 전환

**Files:**
- Create: `eks-hybrid-nodes-1h/videos/v1-gateway-failover/`(HyperFrames 프로젝트), `eks-hybrid-nodes-1h/media/v1-gateway-failover.mp4`, `media/v1-gateway-failover.jpg`(포스터)

**Interfaces:**
- Produces: `media/v1-gateway-failover.mp4`(1920×1080, 무음, 약 150초, 25MB 이하), `.jpg` 포스터(1920×1080)

- [ ] **Step 1: 수치 대조표 작성** (`videos/v1-gateway-failover/FACTS.md`). 영상에 쓸 값만, 출처 줄과 함께

```markdown
| 값 | 출처 |
|---|---|
| Lease 전환 3초, 5초, 5초 (3회) | ~/eks-hybrid-demo/RUNBOOK.md 1절 |
| 1초 간격 요청 실패 60개 중 1, 60개 중 1, 45개 중 2 | 같은 곳 |
| 라우트 172.17.0.0/16 → 리더 ENI, 전환 후 새 리더 ENI | 같은 곳, demo1-gateway/failover.sh |
| Lease HOLDER 형식 노드이름_uuid | KNOWN-ISSUES.md |
```

- [ ] **Step 2: HyperFrames 진입.** `/hyperframes` 스킬을 읽고 route는 `/general-video`. BRIEF: 메시지 "Gateway 리더가 죽어도 3~5초 안에 스탠바이가 경로를 넘겨받는다", 무음, 16:9, 장면 5개(환경 구성도, 평상시 경로, 리더 Pod 삭제, Lease와 라우트 교체, 결과 카드 3회 측정). 하단 고정 표기 "실측 결과 재구성 (2026-10 시뮬레이션 환경)". 색은 덱 테마(`--bg` #161D26, accent #41B3FF, warning #FBD332, success #00E500).
- [ ] **Step 3: 렌더 전 검사.** `npx hyperframes check`가 통과해야 함
- [ ] **Step 4: 렌더와 크기 확인**

```bash
cd ~/reactive_presentation/eks-hybrid-nodes-1h/videos/v1-gateway-failover
npx hyperframes render --output ../../media/v1-gateway-failover.mp4
~/.local/bin/ffmpeg -v error -ss 5 -i ../../media/v1-gateway-failover.mp4 -frames:v 1 -y ../../media/v1-gateway-failover.jpg
ls -la ../../media/v1-gateway-failover.*
~/.local/bin/ffmpeg -v error -i ../../media/v1-gateway-failover.mp4 -f null - && echo decode-ok
```

Expected: mp4 25MB 이하, `decode-ok`. 넘으면 `-crf`를 올려 재인코딩(`ffmpeg -i in.mp4 -c:v libx264 -crf 28 -preset slow -an out.mp4`). 그래도 넘거나 화질이 무너지면 Task 11의 S3 경로로.

- [ ] **Step 5: 프레임 샘플 확인.** 0초, 30초, 60초, 90초, 끝에서 프레임을 뽑아 Read로 보고 FACTS.md 값과 대조

```bash
for t in 1 30 60 90 140; do ~/.local/bin/ffmpeg -v error -ss $t -i ../../media/v1-gateway-failover.mp4 -frames:v 1 -y ~/eks-hybrid-demo/.work/v1-$t.jpg; done
```

- [ ] **Step 6: 커밋** `git add eks-hybrid-nodes-1h/videos/v1-gateway-failover eks-hybrid-nodes-1h/media/v1-gateway-failover.* && git commit -m "feat(eks-hybrid-nodes-1h): demo video V1 gateway failover"` (렌더 캐시와 node_modules는 `.gitignore`로 제외)

### Task 6: 영상 V2 bursting과 pod-deletion-cost

Task 5와 같은 단계. 차이만 적는다.

- 파일: `videos/v2-bursting/`, `media/v2-bursting.mp4/.jpg`, 약 210초
- FACTS.md 값(출처 `~/eks-hybrid-demo/results/compare-20261015-1239.md`, RUNBOOK 2절): hybrid 호스트 2대 4 vCPU, Pod 요청 930m, hybrid에 8개, burst NodePool m7i/m6i large, xlarge, 한도 32 vCPU / A: 10개일 때 hybrid 6, cloud 4, EC2 3, 최종 hybrid 2, cloud 1, 정리 123초 / B: hybrid 8, cloud 2, EC2 4, 최종 hybrid 3, 정리 118초 / C: hybrid 8, cloud 2, EC2 3, 최종 hybrid 3, 정리 87초 / NodeClaim 1~2초, 15개 Ready 37~38초 / 1회 실행, 반복 측정 필요
- 장면: 문제(스케일 인 때 온프렘 Pod가 먼저 지워짐), 스케일 아웃 애니메이션(노드 박스에 Pod 점이 채워지고 burst 노드가 생김), A/B/C 스케일 인 비교(같은 시작에서 남는 Pod 위치), 비교표, 주의(best-effort, 1회 측정)
- 메시지: "Kyverno만으로 온프렘 Pod를 지키고, Karpenter 게이트는 EC2 정리를 조금 더 빠르게 한다"

### Task 7: 영상 V3 ALB ip 타깃과 역방향

Task 5와 같은 단계. 차이만 적는다.

- 파일: `videos/v3-alb-reverse/`, `media/v3-alb-reverse.mp4/.jpg`, 약 180초
- FACTS.md 값(출처 `~/eks-hybrid-demo/results/lb-20261018-0211.json`, RUNBOOK 5절): 타깃 172.17.0.202, .48 healthy, AZ all / 20/20 / rollout restart 새 IP .230, .76, 54초 수렴, 276건 중 실패 0 / 리더 삭제 인계 4초, 191건 중 실패 1 / 온프렘 → ALB(10.0.46.5, 10.0.51.70) → cloud Pod 20/20 / hairpin 20/20 / NodePort 실패, 원인 SG 443만 허용
- 장면: 질문("Pod IP가 바뀌면 누가 타깃을 바꾸나"), 경로도(ALB → VPC 라우트 → Gateway → VXLAN → hybrid Pod), 타깃 교체 타임라인(initial → healthy, draining), 리더 전환 중 요청 막대, 역방향 3경로(성공, hairpin, 실패와 원인)
- 메시지: "타깃은 Load Balancer Controller가 따라가고, 온프렘에서 들어올 때는 internal LB가 기본 경로다"

### Task 8: 영상 V4 hybrid GPU 추론

Task 5와 같은 단계. 차이만 적는다.

- 파일: `videos/v4-gpu/`, `media/v4-gpu.mp4/.jpg`, 약 120초
- FACTS.md 값(출처 RUNBOOK 3절, KNOWN-ISSUES 데모 3): g6.xlarge, NVIDIA L4 23 GB(시뮬레이션 온프렘 VPC) / device plugin v0.17.1, allocatable GPU 1 / vLLM v0.19.1, 모델 Qwen/Qwen2.5-0.5B-Instruct / Pod 컨테이너 1개(sidecar 없음), hostNetwork 꺼짐 / 클라우드 Pod가 `inference.gpu-demo.svc` 호출, elapsed 약 1초 / 이미지 다운로드 4분 28초 / 드라이버와 container toolkit은 호스트에 직접 설치
- 장면: 왜 온프렘 GPU(데이터 위치, 기존 GPU), 구성(taint와 label, device plugin), 추론 호출 흐름, 결과 카드, 준비할 것(드라이버, 이미지 사전 다운로드)
- 메시지: "온프렘 GPU 노드도 같은 클러스터의 Service로 클라우드에서 호출된다"

### Task 9: 5부와 6부 (데모 영상과 마무리)

**Files:**
- Create: `eks-hybrid-nodes-1h/04-demo-close.md`

**Interfaces:**
- Consumes: `media/v1-gateway-failover.mp4/.jpg`, `v2-bursting`, `v3-alb-reverse`, `v4-gpu`(Task 5~8)

슬라이드(13장): 1 5부 구분 / 2 시뮬레이션 환경(Deep Dive 5부 슬라이드 2 축약, 프로덕션 미지원 고지) / 3 V1 영상 / 4 V1 결과 요약 / 5 V2 영상 / 6 V2 결과(A/B/C 표 축약) / 7 V3 영상 / 8 V3 결과(정방향과 역방향 요약) / 9 V4 영상과 결과(한 장) / 10 Istio 공존 결과(sidecar 동작, Cilium L7은 꺼짐, 1,800건 성공) / 11 도입 판단 체크리스트(연결, CIDR, 라우팅 방식, 자격 증명, CNI, 운영) / 12 다음 단계와 참고 자료(Deep Dive 링크 `../eks-hybrid-nodes/index.html`, 데모 저장소, AWS 문서 6개 내외) / 13 Thank you(`@type: thanks` 또는 Deep Dive와 같은 형식).

- [ ] **Step 1: 영상 슬라이드 HTML 패턴** (모든 영상 슬라이드에 동일하게)

```html
:::html
<style>
.hn-video { width: 100%; max-height: 100%; aspect-ratio: 16 / 9; background: var(--bg-card); border-radius: var(--space-2); }
.hn-video-cap { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); }
</style>
<video class="hn-video" src="media/v1-gateway-failover.mp4" poster="media/v1-gateway-failover.jpg" controls preload="metadata" muted playsinline tabindex="-1"></video>
<div class="hn-video-cap">실측 결과 재구성 (2026-10 시뮬레이션 환경), 무음</div>
:::
```

- [ ] **Step 2: md 작성.** 노트에 영상 구간별 멘트(장면마다 1~2문장)를 쓴다
- [ ] **Step 3: md 검사** `python3 ~/eks-hybrid-demo/.work/check_1h.py --md-only`, 오류 0, PASS
- [ ] **Step 4: 키보드 동작 확인.** Task 10 빌드 뒤 헤드리스에서 영상 슬라이드로 이동하고 `ArrowRight`를 보내 다음 슬라이드로 넘어가는지 확인. `tabindex="-1"` 때문에 영상이 포커스를 잡지 않아야 함. 넘어가지 않으면 영상 클릭 후 `blur()`하는 작은 스크립트를 블록 끝 `<script>`에 추가
- [ ] **Step 5: 커밋** `git commit -m "feat(eks-hybrid-nodes-1h): parts 5-6, demo videos and close"`

### Task 10: 빌드, Deep Dive 이름 변경, 허브 카드

**Files:**
- Generate: `eks-hybrid-nodes-1h/*.html`, `index.html`, `toc.html`
- Modify: `eks-hybrid-nodes/_presentation.md`(title), `eks-hybrid-nodes/01-overview.md`(표지 부제), 루트 `index.html`(카드)

- [ ] **Step 1: 빌드와 post-build**

```bash
cd ~/reactive_presentation
python3 ~/.claude/plugins/marketplaces/oh-my-cloud-skills/plugins/aws-content-plugin/skills/reactive-presentation/scripts/remarp_to_slides.py build eks-hybrid-nodes-1h -o eks-hybrid-nodes-1h > ~/eks-hybrid-demo/.work/build-1h.log 2>&1; echo rc=$?
python3 ~/eks-hybrid-demo/.work/postbuild_1h.py
python3 ~/eks-hybrid-demo/.work/check_1h.py
```

Expected: rc=0, `slides=` 28~34, PASS. 실패한 슬라이드는 md를 고치고 다시 빌드

- [ ] **Step 2: Deep Dive 이름 변경.** `eks-hybrid-nodes/_presentation.md`의 title을 `"EKS Hybrid Nodes Deep Dive (2시간), 온프레미스를 EKS로 확장하는 가이드"`로, `01-overview.md` 표지 셋째 줄을 `Deep Dive (2시간): 개요, 네트워킹, 노드 운영, 라이브 데모`로. 그다음 `~/eks-hybrid-demo/.work/rebuild_all.py`로 미리보기, removed 줄이 표지와 제목뿐인지 확인한 뒤 `--install`
- [ ] **Step 3: 영상 경로 확인.** 블록 HTML과 통합본 `index.html` 모두에서 `media/` 상대 경로가 같은지 확인

```bash
grep -o 'src="media/[^"]*"' eks-hybrid-nodes-1h/04-demo-close.html eks-hybrid-nodes-1h/index.html | sort | uniq -c
```

Expected: 영상 4개가 두 파일에 각각 나타남

- [ ] **Step 4: 허브 카드.** 루트 `index.html`에서 기존 `eks-hybrid-nodes` 카드 제목에 "Deep Dive (2시간)"를 붙이고, 그 앞에 같은 마크업으로 `eks-hybrid-nodes-1h/index.html` 카드("EKS Hybrid Nodes (1시간)", 설명 "개념, 아키텍처, 데모 영상 4편", 태그 L200)를 추가. 내보내기 버튼의 slug도 `eks-hybrid-nodes-1h`로
- [ ] **Step 5: 표지와 Thank you 스크린샷** 2장을 헤드리스로 찍어 Deep Dive와 같은 모양인지 확인
- [ ] **Step 6: 커밋** `git commit -m "feat(eks-hybrid-nodes-1h): build deck, rename Deep Dive, add hub card"`

### Task 11: 큰 영상의 호스팅 (조건부)

Task 5~8에서 25MB를 넘긴 영상이 있을 때만 진행한다.

- [ ] **Step 1: 대상 계정 확인과 승인 요청.** 계정(기본 `<기본 계정>` 또는 `samples-atomoh` 프로필의 `<samples 계정>`), 버킷 이름 `reactive-presentation-media-<account>`, 비공개 버킷(Block Public Access 4개 모두 켬), CloudFront 배포와 OAC, 버킷 정책은 그 배포의 OAC만 허용. 이 변경 목록을 사용자에게 보여 주고 승인받는다
- [ ] **Step 2: 승인 후 생성, 업로드, 확인.** `curl -I https://<dist>.cloudfront.net/eks-hybrid-nodes-1h/<id>.mp4`가 200이고, 버킷 직접 URL은 403이어야 함
- [ ] **Step 3: md의 src를 CloudFront URL로 바꾸고 Task 10 Step 1 재실행.** 검사 스크립트의 파일 존재 확인은 `https://` src를 건너뛴다(필요하면 정규식을 `media/`로 한정한 현재 형태 유지)
- [ ] **Step 4: 정리 방법 기록.** 배포 비활성화 후 삭제, 객체와 버킷 삭제 명령을 PR 본문에 남긴다

### Task 12: 품질 검토와 PR

- [ ] **Step 1: content-review-agent 실행.** 대상 `eks-hybrid-nodes-1h/` 전체, 기준 85점 이상. 지적 사항을 md에서 고치고 Task 10 Step 1 재실행
- [ ] **Step 2: 최종 검사** `python3 ~/eks-hybrid-demo/.work/check_1h.py` PASS
- [ ] **Step 3: 푸시와 PR.** base는 `docs/eks-hybrid-nodes-live-demo-2026-10-17`(PR #5)가 머지되기 전이면 그 브랜치, 머지됐으면 `main`

```bash
git push -u origin feat/eks-hybrid-nodes-1h-2026-10-18
gh pr create --base <위 규칙의 base> --title "feat(eks-hybrid-nodes-1h): 1-hour session with demo videos; rename Deep Dive" --body-file <본문 파일>
```

본문 끝에 `🤖 Generated with [Claude Code](https://claude.com/claude-code)`
