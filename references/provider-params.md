# 三个 provider 的参数与约束对照

以下信息均已通过真实调用验证(不是官方文档照抄，是实测确认的 openlux.ai 中转站行为)。写代码/传参数之前遇到不确定的地方，优先看这份文档而不是凭记忆猜。

## 公共信息

- 鉴权统一：`Authorization: Bearer $OPENLUX_API_KEY`，三个 provider 共用同一个 key。
- 三个适配器模块都在 `scripts/providers/`，对外接口统一是 `generate(prompt, size=None, quality=None, output_format=None) -> bytes`，不支持的参数会被对应模块直接忽略。

## gpt-image (`scripts/providers/gpt_image.py`)

- Endpoint: `POST https://api.openlux.ai/v1/images/generations`
- 实际使用的 model 字符串是 `gpt-image-2-c`(带 `-c` 后缀，是用户实测验证过的版本，不要改成不带后缀的 `gpt-image-2`，那个没验证过)。
- 请求体是 flat JSON：
  ```json
  {
    "model": "gpt-image-2-c",
    "prompt": "...",
    "n": 1,
    "size": "1024x1024",
    "quality": "low",
    "format": "jpeg"
  }
  ```
- `size` 用 `WIDTHxHEIGHT` 格式(如 `1024x1024`)。
- `quality` 支持 `low` / `medium` / `high`，生成草稿/低成本预览用 `low`，正式落地素材用 `medium` 或 `high`。
- `format` 支持 `jpeg` / `png`。
- 响应：`data[0].b64_json`(base64，直接解码) 或 `data[0].url`(需要再发一次 GET 下载)，两种都要处理，适配器代码已经兼容。

## doubao / 豆包 Seedream (`scripts/providers/doubao.py`)

- Endpoint: `POST https://api.openlux.ai/api/v3/images/generations`(注意路径跟 gpt-image 不是同一套，是 `/api/v3/...` 不是 `/v1/...`)。
- 实际使用的 model 字符串是 `doubao-seedream-5-0-pro-260628`。
- 请求体：
  ```json
  {
    "model": "doubao-seedream-5-0-pro-260628",
    "prompt": "...",
    "size": "2K",
    "response_format": "url",
    "watermark": false
  }
  ```
- `size` 是标签式的(比如 `"2K"`)，不是 `WIDTHxHEIGHT`，跟 gpt-image 不通用，不要把 gpt-image 的尺寸值传给豆包。
- 没有 `quality` 参数，适配器会直接忽略这个参数。
- `watermark` 固定传 `false`，避免生成的图带水印。
- 响应：实测走的是 `data[0].url`，适配器同时也兼容 `b64_json` 以防以后行为变化。

## Gemini (`scripts/providers/gemini.py`)

- Endpoint: `POST https://api.openlux.ai/v1beta/models/gemini-3-pro-image-preview:generateContent`
- **model 写在 URL 路径里，不是 body 字段**，这是跟另外两个 provider 最大的结构性差异。
- 请求体是嵌套结构，不是 flat JSON：
  ```json
  {
    "contents": [
      {"parts": [{"text": "..."}], "role": "user"}
    ],
    "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    "response_format": "url"
  }
  ```
- 不支持显式的 `size`/`quality` 控制，适配器会忽略这两个参数(传了也不会报错，只是没用)。
- `response_format: "url"` 是 openlux.ai 加的扩展字段(Google 官方 API 本身没有这个参数)，实测确认生效。
- 响应：图片信息在 `candidates[0].content.parts[].fileData.fileUri`(适配器同时兼容 `file_data`/`file_uri` 命名和万一走 base64 的 `inlineData`/`inline_data`)。
- 支持通过在 `parts` 里加一个 `inline_data`(base64 + mime_type)传参考图做图生图/编辑，但当前 imagegen skill 的 v1 版本没有实现这个能力，只是适配器层留了口子。


