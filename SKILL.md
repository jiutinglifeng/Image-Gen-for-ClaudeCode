---
name: imagegen
description: 调用 openlux.ai 中转站的生图模型(gpt-image-2-c / 豆包 Seedream / Gemini)为当前项目生成图片素材并保存到项目目录里供代码引用。只要是在构建网页/前端项目时提到缺配图、需要生成图片、需要 hero 图/图标/插画/占位图/背景图，或者明确要求用 AI 生图，就应该主动用这个技能——即使用户没有点名"imagegen"或具体模型名也要触发。不支持 Midjourney，也不支持图片编辑/以图生图(当前只支持从文字描述生成新图)。
---

# Image Generation Skill

在构建 web 项目时生成图片素材(hero 图、图标、插画、配图、占位图等)，通过 openlux.ai 调用 gpt-image-2-c / 豆包 Seedream / Gemini 三个模型之一，把结果保存到项目目录，供后续代码直接引用。

## 使用前提

调用脚本前确认：

1. `~/.claude/skills/imagegen/.env` 是否存在且包含 `OPENLUX_API_KEY`。不存在就复制 `.env.example` 为 `.env` 并提示用户填入 key(三个 provider 共用同一个 key，不用分开配)。**不要替用户瞎编一个 key，也不要在对话里要求用户直接粘贴 key 明文**——如果需要引导，让用户自己编辑 `.env` 文件。
2. Python 依赖 `requests`、`python-dotenv` 是否可用，不可用就 `pip install requests python-dotenv`。

## 核心工作流程

生成一张图片，按这个顺序来，**不要跳过第 4 步**：

1. **搞清楚这张图在项目里的角色**：用途(hero/图标/配图/占位图……)、项目已有的视觉语言(去看一眼项目里的 CSS 变量/主题色/已有素材风格，不要凭空猜)、大致尺寸比例。细节见 `references/prompting.md`。
2. **按结构化骨架组织完整中文 prompt**：不要把用户一句话的描述直接透传给生图 API，要按 `references/prompting.md` 里的骨架(用途/主体/风格/构图/色彩/氛围/文字/约束)补全成详细描述。**全部用中文**，这是用户明确要求的，方便直接审阅，不要写成英文。资产类型的参考模板见 `references/sample-prompts.md`。
3. **决定用哪个 provider**：默认 `gpt-image`(即 gpt-image-2-c，用户实测验证过、最推荐的默认选项)。如果用户在对话里点名了具体模型("用豆包生成""换 Gemini 试试")，直接切换，不需要为"切换 provider 本身"单独确认一轮。三个 provider 的能力/参数差异见 `references/provider-params.md`。
4. **生成前，把完整信息展示给用户，等待确认**：包括 (a) 准备使用的 provider，(b) 完整的中文 prompt 原文，(c) 尺寸等关键参数。等用户明确同意或提出修改后才能继续。这是用户明确要求的强制步骤——生成是要花钱的，改一次 prompt 比生成后返工便宜得多，**不能因为"看起来没问题"就自行跳过这一步**。
5. **调用 `scripts/generate_image.py`**，见下面"调用方式"。
6. **检查结果并落地引用**：确认文件已保存到预期路径后，把这张图实际用到项目代码里(比如 `<img>` 标签、CSS `background-image`)。如果生成结果明显有问题(主体不对、文字乱码、意外水印)，跟用户确认是否要调整 prompt 重新生成，而不是将就着用或者自己反复重试硬扛。

## 调用方式

```bash
python3 ~/.claude/skills/imagegen/scripts/generate_image.py \
  --provider gpt-image \
  --prompt "<第 2 步组织好的完整中文 prompt>" \
  --size 1024x1024 \
  --out "<项目里的目标路径，比如 ./public/images/hero.jpg>"
```

- `--provider` 取值：`gpt-image`(默认) / `doubao` / `gemini`。
- `--size` 不传则用各 provider 的默认值；`gemini` 不支持这个参数，传了会被忽略。
- `--quality` 只有 `gpt-image` 支持(`low`/`medium`/`high`)，其他 provider 会忽略。
- `--out` 用绝对路径或相对当前工作目录的相对路径都可以，父目录不存在会自动创建。
- 脚本会打印实际保存路径和使用的 provider，方便确认。

## 输出路径与命名规范

- 优先存进项目里已有的图片资源目录(比如已有 `public/images/`、`src/assets/` 之类的目录就近放)；项目还没有类似目录的话，创建一个合理的(如 `public/images/generated/`)。
- 文件名要语义化，反映图片内容(比如 `hero-cow-cat.jpg`)，不要用 `output.png`、`image1.jpg` 这种无意义命名。
- 不要覆盖已有的同名文件，除非用户明确要求替换——需要保留旧版本时用带版本号的文件名(如 `hero-v2.jpg`)。

## v1 版本范围

当前版本明确不做这些事，遇到对应需求先跟用户确认要不要临时手动处理，不要自己硬造功能：

- 不支持图片编辑/以图生图(只支持从文字描述生成全新图片)。
- 不支持 Midjourney(异步任务+多轮选图放大，交互链路太复杂，已放弃)。
- 不做批量生成编排(一次只生成一张)。
- 不做"根据任务类型自动选择最优 provider"的智能路由——默认值 + 用户显式指定就够，不要自己猜哪个模型效果更好然后擅自切换。

## 参考文档

- `references/prompting.md`：怎么把模糊需求组织成详细 prompt，为什么要这么做。
- `references/sample-prompts.md`：常见资产类型(hero 图、图标、文章配图、空状态插画)的 prompt 模板。
- `references/provider-params.md`：三个 provider 的接口细节、参数取值范围、已知限制，遇到参数不确定的情况先查这个文件。
- `scripts/remove_chroma_key.py`：本地抠图工具(chroma-key 转透明背景)，移植自 OpenAI Codex 项目(Apache 2.0)，当前 v1 未接入主流程，只有明确需要透明背景素材时才考虑用它，用法见脚本 `--help`。
