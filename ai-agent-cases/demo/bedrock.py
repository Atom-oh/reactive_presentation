"""Amazon Bedrock Converse API 호출 헬퍼 (temperature 0, 1회 호출)."""
import os
import time

import boto3

REGION = os.environ.get("AWS_REGION", "ap-northeast-2")
_client = boto3.client("bedrock-runtime", region_name=REGION)


def ask(model_id, system, user, max_tokens=400):
    t0 = time.time()
    resp = _client.converse(
        modelId=model_id,
        system=[{"text": system}],
        messages=[{"role": "user", "content": [{"text": user}]}],
        inferenceConfig={"temperature": 0, "maxTokens": max_tokens},
    )
    text = resp["output"]["message"]["content"][0]["text"].strip()
    usage = resp["usage"]
    return text, time.time() - t0, usage["inputTokens"], usage["outputTokens"]
