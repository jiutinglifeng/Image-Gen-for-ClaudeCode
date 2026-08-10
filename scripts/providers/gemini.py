"""Gemini provider 适配器(openlux.ai 上的 Google generateContent 生图接口)。

跟另外两个 provider 的关键差异(已通过真实调用验证)：
- model 写在 URL 路径里，不是 body 字段
- 请求体是嵌套的 contents/parts/role 结构，不是 flat JSON
- 不支持显式 size/quality 控制，这两个参数在这里被忽略
- 响应图片信息在 candidates[].content.parts[].fileData.fileUri
  (同时兼容 file_data/file_uri 命名，以及万一走 base64 的 inlineData/inline_data)
- 支持通过 inline_data 传参考图做图生图，但当前版本没有实现这个能力
"""

from __future__ import annotations

import base64
import os

import requests

API_URL = "https://api.openlux.ai/v1beta/models/gemini-3-pro-image-preview:generateContent"


def generate(
    prompt: str,
    size: str | None = None,  # Gemini 原生接口不支持尺寸控制，忽略
    quality: str | None = None,  # 同上，忽略
    output_format: str | None = None,  # 同上，忽略
) -> bytes:
    api_key = os.environ["OPENLUX_API_KEY"]
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "contents": [{"parts": [{"text": prompt}], "role": "user"}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        "response_format": "url",
    }

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                return base64.b64decode(inline["data"])

            file_data = part.get("fileData") or part.get("file_data") or {}
            file_uri = file_data.get("fileUri") or file_data.get("file_uri")
            if file_uri:
                img_resp = requests.get(file_uri, timeout=60)
                img_resp.raise_for_status()
                return img_resp.content

    raise RuntimeError(f"Gemini 返回中未找到图片数据，完整响应: {data}")
