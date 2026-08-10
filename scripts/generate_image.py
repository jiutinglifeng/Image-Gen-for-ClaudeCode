#!/usr/bin/env python3
"""统一生图入口：按 --provider 分发到对应适配器，把结果保存到 --out 指定路径。

用法示例：
    python3 generate_image.py \\
        --provider gpt-image \\
        --prompt "一只黑白奶牛花纹的猫咪，漫画风格插画，..." \\
        --size 1024x1024 \\
        --out /path/to/project/public/images/cow-cat.jpg
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from providers import doubao, gemini, gpt_image  # noqa: E402

PROVIDERS = {
    "gpt-image": gpt_image,
    "doubao": doubao,
    "gemini": gemini,
}
DEFAULT_PROVIDER = "gpt-image"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="调用 openlux.ai 生图并保存到指定路径")
    parser.add_argument("--prompt", required=True, help="完整的中文 prompt(已经过结构化整理)")
    parser.add_argument(
        "--provider", choices=list(PROVIDERS), default=DEFAULT_PROVIDER,
        help=f"使用哪个生图模型，默认 {DEFAULT_PROVIDER}",
    )
    parser.add_argument("--size", default=None, help="尺寸，不同 provider 取值范围不同，不传则用该 provider 的默认值")
    parser.add_argument("--quality", default=None, help="质量档位，仅 gpt-image 支持，其余 provider 会忽略")
    parser.add_argument("--format", dest="output_format", default=None, help="输出格式，如 jpeg/png")
    parser.add_argument("--out", required=True, help="图片保存路径(含文件名)")
    return parser.parse_args()


def main() -> int:
    load_dotenv(SCRIPT_DIR.parent / ".env")

    args = parse_args()

    if "OPENLUX_API_KEY" not in os.environ:
        print(
            "未找到 OPENLUX_API_KEY。请在 "
            f"{SCRIPT_DIR.parent / '.env'} 里配置 OPENLUX_API_KEY=你的key"
            "(可以参考同目录下的 .env.example)。",
            file=sys.stderr,
        )
        return 1

    module = PROVIDERS[args.provider]
    kwargs = {}
    if args.size is not None:
        kwargs["size"] = args.size
    if args.quality is not None:
        kwargs["quality"] = args.quality
    if args.output_format is not None:
        kwargs["output_format"] = args.output_format

    try:
        image_bytes = module.generate(args.prompt, **kwargs)
    except Exception as exc:  # noqa: BLE001 - 顶层 CLI，打印错误后直接退出即可
        print(f"生成失败 (provider={args.provider}): {exc}", file=sys.stderr)
        return 1

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(image_bytes)

    print(f"已保存 -> {out_path}")
    print(f"provider: {args.provider}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
