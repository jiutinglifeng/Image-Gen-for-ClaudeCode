"""豆包 Seedream provider 适配器(openlux.ai 上的火山引擎兼容生图接口)。

请求/响应格式已通过真实调用验证：
- POST /api/v3/images/generations，flat JSON body(注意路径跟 gpt-image 不同)
- size 用 "2K" 这类标签而不是 WIDTHxHEIGHT
- 响应在 data[0].url(实测走的是这个分支)，同时兼容 b64_json 以防万一
"""

from __future__ import annotations

import base64
import os

import requests

API_URL = "https://api.openlux.ai/api/v3/images/generations"
DEFAULT_MODEL = "doubao-seedream-5-0-pro-260628"
DEFAULT_SIZE = "2K"


def generate(
    prompt: str,
    size: str = DEFAULT_SIZE,
    quality: str | None = None,  # 该接口不支持 quality 参数，忽略
    output_format: str | None = None,  # 该接口用 response_format 而非 output_format，见下方固定写法
) -> bytes:
    api_key = os.environ["OPENLUX_API_KEY"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "size": size,
        "response_format": "url",
        "watermark": False,
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
