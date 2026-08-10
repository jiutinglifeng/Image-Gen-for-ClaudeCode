"""gpt-image-2-c provider 适配器(openlux.ai 上的 OpenAI 兼容生图接口)。

请求/响应格式已通过真实调用验证：
- POST /v1/images/generations，flat JSON body
- 响应在 data[0].b64_json(base64) 或 data[0].url(需二次下载)
"""

from __future__ import annotations

import base64
import os

import requests

API_URL = "https://api.openlux.ai/v1/images/generations"
DEFAULT_MODEL = "gpt-image-2-c"
DEFAULT_SIZE = "1024x1024"
DEFAULT_QUALITY = "low"


def generate(
    prompt: str,
    size: str = DEFAULT_SIZE,
    quality: str = DEFAULT_QUALITY,
    output_format: str = "jpeg",
) -> bytes:
    api_key = os.environ["OPENLUX_API_KEY"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": quality,
        "format": output_format,
    }

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    item = data["data"][0]

    if "b64_json" in item:
        return base64.b64decode(item["b64_json"])

    img_resp = requests.get(item["url"], timeout=60)
    img_resp.raise_for_status()
    return img_resp.content
