# card-maker

用 Python 生成 16:9 电商主图（中文友好排版，可配置主题/预设）。  
满足：宽高均≥480px、默认 1920×1080、成品 ≤ 5MB（PNG/JPG，自动压缩或缩放）。

## 直接运行模块

```powershell
$env:CARD_MAKER_DEBUG="1"
python -m card_maker.cli --params-json .\examples\month.json --out .\output\month.png --format png --font-family NotoSansSC --cjk-only on
python -m card_maker.cli --params-json .\examples\new.json --out .\output\new.png --format png --font-family NotoSansSC --cjk-only on
python -m card_maker.cli --params-json .\examples\season.json --out .\output\season.png --format png --font-family NotoSansSC --cjk-only on
python -m card_maker.cli --params-json .\examples\seat.json --out .\output\seat.png --format png --font-family NotoSansSC --cjk-only on
```

## 定制化更高一点的

```python
python -m card_maker.cli --params-json .\examples\new_SNW.json --out .\output\new_SNW.png --format png --font-family NotoSansSC --cjk-only on
```

主要就是改`\card-maker\examples\`里面的json，然后命令指定一下输入和输出

# 常用颜色清单（Hex）

- 亮蓝：`#2F6DF6`　| 深蓝：`#1D4ED8`　| 天空蓝：`#1E90FF`
- 青蓝/Teal：`#0EA5A4`　| 祖母绿：`#22C55E`　| 深绿：`#15803D`
- 品红：`#E11D48`　| 正红：`#EF4444`　| 橙：`#F59E0B`
- 金黄：`#FBBF24`　| 紫：`#7C3AED`　| 靛青：`#4F46E5`
- 深灰：`#374151`　| 中灰：`#6B7280`　| 浅灰：`#D1D5DB`
- 纯黑：`#000000`　| 纯白：`#FFFFFF`

# 改哪里（键 → 影响的元素）

（JSON 和 YAML 都能写；JSON 写了会覆盖预设）

- **全局主色**：`accent`
   影响：标题下划线、默认装饰色、（在部分版本）要点小圆点等的默认颜色。
   想“一键全变蓝”，先改这里。
- **整张背景色**：`bg`
- **标题/副标题文字色**：
   `title.color`（主标题），`title.subtitle.color`（副标题）
   说明：若没单独设，下划线通常**跟随 `accent`**；有的版本也支持 `title.underline_color`。
- **要点文本与小圆点**：
   文本：`bullet.color`；小圆点：`bullet.marker_color`
   说明：若不设 `marker_color`，小圆点可能跟随 `accent`。
- **装饰小方块**：`decorations[].color`（颜色）、`decorations[].size`（大小，0–1 的相对数）、`decorations[].x/y`（位置，0–1）
   说明：你说的小方块“变小”，是因为预设里写了 `size: 0.018/0.022`（相对画布宽度）；想更大就把 `size` 调到 **0.024–0.030** 试试。
- **角标/品牌字样**：`brand.color`
- **白色信息卡片（那块白底区域）**：常见是 `panel.bg`（或你项目里叫 `box.bg/card.bg`）；阴影看是否有 `panel.shadow_color/panel.shadow_opacity`。

## 安装（下面的不弄也可以）
```bash
pip install -e .
```

## 命令行

```bash
card-maker --preset month \
  --title "月卡" \
  --brand "& Fangyuan Yili 方圆一鲤" \
  --bullets "验券后三十天内有效" "按天扣除，需连续使用" "适用小黑屋，靠窗区，开放区" \
  --bg "#F3EEE6" \
  --accent "#E7A028" \
  --width 1920 \
  --format png \
  --out output/month_card.png
```

### 参数

- `--preset {month,new,season,seat,none}`：风格预设
- `--title`：主标题（必填）
- `--brand`：顶部品牌（可选）
- `--bullets ...`：多条要点
- `--bg` / `--accent`：背景/强调色
- `--title-align {center,left}`
- `--width` 或 `--height`：至少给一个；比例强制 16:9
- `--format {png,jpg}`（默认 png）
- `--out`：输出路径（必填）
- `--max-mb 5`：文件体积上限
- `--texture {none,noise}`：背景纹理（可选）
- `--watermark`：水印文字（可选）

## Python API

```python
from card_maker.api import generate_card

path = generate_card({
    "preset": "month",
    "title": "月卡",
    "brand": "& Fangyuan Yili 方圆一鲤",
    "bullets": ["验券后三十天内有效","按天扣除，需连续使用","适用小黑屋，靠窗区，开放区"],
    "bg": "#F3EEE6",
    "accent": "#E7A028",
    "width": 1920,
    "format": "png",
    "out": "output/month_card.png"
})
print("saved:", path)
```

## 字体

`card_maker/assets/fonts` 下放置真实的 `NotoSansSC-Regular.ttf`, `NotoSansSC-Bold.ttf`, `Inter-Regular.ttf`。
 如果找不到或字体文件不可用，会自动回退到 Pillow 内置字体以确保可运行。