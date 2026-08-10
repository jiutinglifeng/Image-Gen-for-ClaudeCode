# imagegen — Claude Code 多模型生图 Skill

在用 Claude Code 构建 web 项目时，直接生成图片素材(hero 图、图标、插画、配图等)并保存到项目目录，供代码直接引用。通过一个 AI 中转站调用 gpt-image-2 / 豆包 Seedream / Gemini 三个生图模型，不用分别注册每一家官方账号。

## 功能

- 三选一生图模型：`gpt-image`(gpt-image-2-c)、`doubao`(豆包 Seedream)、`gemini`(Gemini)，默认用 `gpt-image`，对话里直接说"用豆包/Gemini 生成"就能切换，不用记参数。
- 生成前会把完整 prompt 和使用的模型展示出来，等你确认后才真正调用 API，避免误触发浪费额度。
- Prompt 统一用中文结构化模板组织(用途/主体/风格/构图/色彩/氛围/文字/约束)，会尽量贴合项目已有的视觉风格，而不是生成一张风格突兀的图。
- 内置常见资产类型(首页 hero 图、图标、文章配图、空状态插画)的 prompt 模板，见 `references/sample-prompts.md`。

## 依赖

- Python 3
- `pip install requests python-dotenv`
- 一个可用的中转站账号(默认配置的是 openlux.ai，换别的中转站见下方"更换中转站")

## 安装

1. 把整个 `imagegen/` 文件夹放到 `~/.claude/skills/imagegen/`(全局生效，任何项目都能用)，或者放到某个项目的 `.claude/skills/imagegen/`(只在该项目生效)。
2. 复制 `.env.example` 为 `.env`，填入你的 API Key：
   ```bash
   cp .env.example .env
   ```
   然后编辑 `.env`，把 `OPENLUX_API_KEY` 换成真实的 key。三个模型共用同一个 key，不用分开配。
3. 还没有 openlux.ai 账号的话，可以用这个邀请链接注册：https://api.openlux.ai/register?aff=Ur4Y

`.env` 不会被 git 追踪(见 `.gitignore`)，放心填真实 key，但也别手动把它加进版本控制。

每次生成图片都会消耗中转站账户余额，具体费用取决于中转站定价和你选的模型/质量档位。

## 使用

在 Claude Code 对话里正常描述需求即可，比如"帮首页做一张 hero 图"，符合场景时会自动触发这个 skill。也可以手动调用：

```bash
python3 scripts/generate_image.py \
  --provider gpt-image \
  --prompt "完整的中文 prompt" \
  --size 1024x1024 \
  --out ./public/images/hero.jpg
```

`--provider` 可选 `gpt-image` / `doubao` / `gemini`；`--size`、`--quality`、`--format` 是否生效取决于所选 provider，详见 `references/provider-params.md`。

## 更换中转站

默认对接的是 openlux.ai。如果想换成别的中转站，或者直连各家官方 API，需要改这几处：

| 文件 | 要改的常量 | 说明 |
|---|---|---|
| `scripts/providers/gpt_image.py` | `API_URL`、`DEFAULT_MODEL` | 换成新中转站的生图 endpoint，以及它支持的 model 名(不一定还叫 `gpt-image-2-c`) |
| `scripts/providers/doubao.py` | `API_URL`、`DEFAULT_MODEL` | 同上 |
| `scripts/providers/gemini.py` | `API_URL` | **model 名是写在 URL 路径里的**(`.../models/gemini-3-pro-image-preview:generateContent`)，不是单独的常量，换 model 版本也要改这个 URL |

改完之后，强烈建议先跑一次最小化的测试请求，确认真实返回的 JSON 结构，而不要想当然地认为解析逻辑还能直接用——不同中转站/不同厂商在响应结构上的差异比想象中大，这个 skill 里三个 provider 的解析代码，都是先各写一个小测试脚本、拿到真实返回样本以后才定下来的。

大概率不用改的地方：
- 鉴权方式(`Authorization: Bearer <key>`)是业界通用约定，大部分中转站都遵循。
- `gpt_image.py` / `doubao.py` 的响应解析逻辑(`data[0].b64_json` 或 `data[0].url`)是 OpenAI 生图 API 的标准形状，多数"OpenAI 兼容"中转站都会保持这个结构，但仍建议实测确认一次。
- `gemini.py` 的解析逻辑同时兼容 base64(`inlineData`)和 URL(`fileData.fileUri`)两种返回形式，即使新中转站的行为跟 openlux.ai 不完全一样，大概率也能覆盖到。

环境变量名 `OPENLUX_API_KEY` 是历史命名，换了中转站也可以继续沿用(不影响功能)；如果想改成更通用的名字，需要同步修改三个 provider 文件里读取环境变量的那一行。

## 已知限制

- 只支持文生图，不支持图片编辑/以图生图。
- 不支持 Midjourney(官方没有公开 API，中转站是异步任务+多轮选图放大，交互链路太复杂，暂不支持)。
- 一次只生成一张，不做批量编排。
- 不会自动判断"这类图用哪个模型效果最好"，需要用户显式指定，或者默认用 `gpt-image`。

## 第三方代码

`scripts/remove_chroma_key.py` 移植自 [OpenAI Codex](https://github.com/openai/codex) 项目自带的 imagegen sample skill，遵循 Apache License 2.0，完整许可证见 `scripts/LICENSE-remove_chroma_key.txt`。当前版本未接入主流程，仅作为透明背景处理(chroma-key 抠图转 alpha 通道)的备用工具。
