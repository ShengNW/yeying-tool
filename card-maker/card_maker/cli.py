import argparse
import json
from pathlib import Path
from .api import generate_card

def build_parser():
    p = argparse.ArgumentParser(description="Generate 16:9 e-commerce hero card.")
    p.add_argument("--preset", default="none", choices=["none", "month", "new", "season", "seat"])
    # 不再强制 required=True，允许从 --params-json 里读
    p.add_argument("--title")
    p.add_argument("--brand", default="")
    p.add_argument("--bullets", nargs="*", default=None)  # None 表示未在 CLI 指定，避免覆盖 JSON
    p.add_argument("--bg", default="")
    p.add_argument("--accent", default="")
    p.add_argument("--title-align", dest="title_align", default="center", choices=["center", "left"])
    p.add_argument("--width", type=int)
    p.add_argument("--height", type=int)
    p.add_argument("--format", default="png", choices=["png", "jpg", "jpeg"])
    p.add_argument("--out", required=True)
    p.add_argument("--max-mb", dest="max_file_mb", type=float, default=5.0)
    p.add_argument("--texture", default="none", choices=["none", "noise"])
    p.add_argument("--watermark", default="")
    p.add_argument("--params-json", help="Path to a JSON file of params (optional)")

    # === 新增 CLI 参数 ===
    # 默认字体家族；始终写入 params（与上游 validate 的默认一致）
    p.add_argument(
        "--font-family",
        dest="font_family",
        default="NotoSansSC",
        help="Font family to use (default: NotoSansSC)",
    )
    # 只用中文字体策略：on/off，解析为布尔
    p.add_argument(
        "--cjk-only",
        dest="cjk_only",
        choices=["on", "off"],
        default="on",
        help="Enable CJK-only font strategy: on/off (default: on)",
    )
    return p

def main():
    parser = build_parser()
    args = parser.parse_args()

    params = {}
    # 先读 JSON（如果有）
    if args.params_json:
        with open(args.params_json, "r", encoding="utf-8") as f:
            params.update(json.load(f))

    # 再用 CLI 覆盖（只有显式给了才覆盖；但 font_family / cjk_only 根据需求总是写入）
    cli_map = vars(args)

    for k, v in cli_map.items():
        if k == "params_json":
            continue
        if k == "bullets":
            # 只有显式传了 bullets（非 None）才覆盖 JSON
            if v is not None:
                params[k] = v
            continue
        # 其它参数：非 None 且非空字符串则写入
        if v is not None and v != "":
            params[k] = v

    # 将 --cjk-only 的 on/off 解析为布尔；若 JSON 已是布尔则尊重覆盖后的值
    cjk_v = params.get("cjk_only", "on")
    if isinstance(cjk_v, str):
        params["cjk_only"] = True if cjk_v.lower() == "on" else False
    else:
        # 非字符串（可能是 bool），确保是布尔类型
        params["cjk_only"] = bool(cjk_v)

    # 校验必须字段
    title = str(params.get("title", "")).strip()
    if not title:
        parser.error("title 不能为空。请在 JSON 里提供 'title' 或通过 --title 指定。")

    # 确保输出目录存在
    Path(params["out"]).parent.mkdir(parents=True, exist_ok=True)

    out_path = generate_card(params)
    print(out_path)

if __name__ == "__main__":
    main()
