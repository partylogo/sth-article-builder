#!/usr/bin/env python3
"""通用封面壓字：任何底圖 + 主標 + 副標。

產圖：
  overlay.py --base base.png --title 主標 --subtitle 副標 --out out.png [--box x,y,w,h] [--color #fff]
量版面（setup 用，不產圖）：
  overlay.py --base base.png --measure [--box x,y,w,h]

- 沒給 --box 時，自動找放字區域：從左或右起算，寬度由寬到窄試，取顏色變化夠小的最寬那塊。
- 沒給 --color 時，依放字區域的亮度選白字或深色字。
- 主標、副標各一行，放不下就報錯（回傳碼 2），不縮字、不換行，讓呼叫端照字數上限縮寫。
- 輸出檔已存在就報錯（回傳碼 3），永不覆蓋。
"""
import argparse
import glob
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageStat

FONT_CANDIDATES = [
    # macOS 新版把 PingFang 放在 AssetsV2 底下
    ("/System/Library/AssetsV2/com_apple_MobileAsset_Font7/*/AssetData/PingFang.ttc", "PingFang TC Semibold"),
    ("/System/Library/Fonts/PingFang.ttc", "PingFang TC Semibold"),
    ("/System/Library/Fonts/STHeiti Medium.ttc", None),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "Noto Sans CJK TC Bold"),
    ("/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc", "Noto Sans CJK TC Bold"),
    ("C:/Windows/Fonts/msjhbd.ttc", None),
]


def find_font(size):
    for pattern, want in FONT_CANDIDATES:
        for path in glob.glob(pattern):
            for index in range(40):
                try:
                    font = ImageFont.truetype(path, size, index=index)
                except OSError:
                    break
                if want is None or " ".join(font.getname()) == want:
                    return font, path, index
    sys.exit("找不到可用的中文字型（PingFang、黑體、Noto Sans CJK、微軟正黑體都沒有）")


def parse_box(text, size):
    x, y, w, h = (float(v) for v in text.split(","))
    if max(x, y, w, h) <= 1:  # 比例寫法：0.06,0.2,0.5,0.6
        x, y, w, h = x * size[0], y * size[1], w * size[0], h * size[1]
    return int(x), int(y), int(w), int(h)


def auto_box(img, side=None):
    """找夠空的區域裡最寬的那塊：從左邊或右邊起算，寬度由寬到窄試，顏色變化夠小就用。"""
    W, H = img.size
    pad_x, pad_y = int(W * 0.06), int(H * 0.18)
    gray = img.convert("L")

    def busyness(box):
        # 切成 40px 寬的直條，取最花的那條：照片只占邊上一小塊，整塊平均會被稀釋
        x, y, w, h = box
        strips = [gray.crop((sx, y, min(sx + 40, x + w), y + h)) for sx in range(x, x + w, 40)]
        return max(ImageStat.Stat(st).stddev[0] for st in strips)

    tried = []
    for right_edge in (0.94, 0.86, 0.8, 0.74, 0.68, 0.62, 0.56, 0.5):
        w = int(W * right_edge) - pad_x
        starts = {"left": pad_x, "right": W - pad_x - w, "center": (W - w) // 2}
        for name in ([side] if side else ["left", "right"]):
            box = (starts[name], pad_y, w, H - 2 * pad_y)
            score = busyness(box)
            tried.append((score, name, box))
            if score < 18:
                return f"{name}-{int(right_edge * 100)}%", box
    score, name, box = min(tried, key=lambda t: t[0])
    return f"{name}（沒有夠空的區域，挑最空的）", box


def pick_color(img, box):
    x, y, w, h = box
    lum = ImageStat.Stat(img.convert("L").crop((x, y, x + w, y + h))).mean[0]
    return "#ffffff" if lum < 140 else "#1a1a1a"


def layout(img, box):
    _, _, w, h = box
    title_size = max(28, int(img.size[1] * 0.1))
    sub_size = int(title_size * 0.62)
    title_font, path, index = find_font(title_size)
    sub_font, _, _ = find_font(sub_size)
    per_char = title_font.getlength("測")
    return {
        "title_font": title_font,
        "sub_font": sub_font,
        "font_path": path,
        "font_index": index,
        "title_max_chars": int(w // per_char),
        "subtitle_max_chars": int(w // sub_font.getlength("測")),
    }


def main():
    ap = argparse.ArgumentParser(description="通用封面壓字")
    ap.add_argument("--base", required=True)
    ap.add_argument("--title")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--out")
    ap.add_argument("--box", help="放字區域 x,y,w,h（像素，或 0–1 的比例）")
    ap.add_argument("--side", choices=["left", "right", "center"], help="只在這一側找放字區域")
    ap.add_argument("--color", help="字色，例：#ffffff")
    ap.add_argument("--measure", action="store_true", help="只回報版面與每行字數上限")
    a = ap.parse_args()

    img = Image.open(a.base).convert("RGB")
    if a.box:
        box_name, box = "given", parse_box(a.box, img.size)
    else:
        box_name, box = auto_box(img, a.side)
    color = a.color or pick_color(img, box)
    lay = layout(img, box)

    if a.measure:
        print(json.dumps({
            "base_size": img.size,
            "box": box,
            "box_from": box_name,
            "box_ratio": [round(box[0] / img.size[0], 3), round(box[1] / img.size[1], 3),
                          round(box[2] / img.size[0], 3), round(box[3] / img.size[1], 3)],
            "color": color,
            "font": f"{lay['font_path']}#{lay['font_index']}",
            "title_max_chars": lay["title_max_chars"],
            "subtitle_max_chars": lay["subtitle_max_chars"],
        }, ensure_ascii=False))
        return

    if not a.title or not a.out:
        sys.exit("產圖要給 --title 與 --out")
    if os.path.exists(a.out):
        print(f"輸出檔已存在，不覆蓋：{a.out}", file=sys.stderr)
        sys.exit(3)

    x, y, w, h = box
    tf, sf = lay["title_font"], lay["sub_font"]
    for text, font, label in ((a.title, tf, "主標"), (a.subtitle, sf, "副標")):
        if text and font.getlength(text) > w:
            print(f"{label}放不下：「{text}」寬 {int(font.getlength(text))}px，可放 {w}px", file=sys.stderr)
            sys.exit(2)

    draw = ImageDraw.Draw(img)
    gap = int(tf.size * 0.45)
    th = tf.getbbox("測")[3]
    sh = sf.getbbox("測")[3] if a.subtitle else 0
    total = th + (gap + sh if a.subtitle else 0)
    top = y + (h - total) // 2
    draw.text((x, top), a.title, font=tf, fill=color)
    if a.subtitle:
        draw.text((x, top + th + gap), a.subtitle, font=sf, fill=color)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    img.save(a.out, quality=90)
    print(f"{a.out}（主標 {len(a.title)} 字、副標 {len(a.subtitle)} 字，放在 {box_name} 區域）")


if __name__ == "__main__":
    main()
