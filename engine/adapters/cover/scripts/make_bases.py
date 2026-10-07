#!/usr/bin/env python3
"""產內建底圖（3 種 × 2 種比例），不含任何品牌元素。

  make_bases.py [輸出資料夾]   預設：../bases

改了這支要重跑一次，把 bases/ 裡的圖一起更新。
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

SIZES = {"16x9": (1200, 675), "191x100": (1200, 630)}


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def dark(size):
    """深色漸層：左上偏亮的深藍灰，字放左邊或中間都行。"""
    W, H = size
    img = Image.new("RGB", size)
    px = img.load()
    for yy in range(H):
        for xx in range(W):
            t = min(1, (xx / W) * 0.6 + (yy / H) * 0.4)
            px[xx, yy] = lerp((40, 48, 66), (14, 17, 26), t)
    return img


def light(size):
    """淺色素面：米白底，右下角一塊淡色圓形，字放左邊。"""
    W, H = size
    img = Image.new("RGB", size, (247, 244, 238))
    glow = Image.new("RGB", size, (247, 244, 238))
    ImageDraw.Draw(glow).ellipse((int(W * 0.62), int(H * 0.35), int(W * 1.15), int(H * 1.3)), fill=(226, 232, 240))
    return Image.blend(img, glow.filter(ImageFilter.GaussianBlur(40)), 1.0)


def accent(size):
    """左右分色：左邊深色放字，右邊一塊斜切的色塊。"""
    W, H = size
    img = Image.new("RGB", size, (24, 28, 36))
    d = ImageDraw.Draw(img)
    d.polygon([(int(W * 0.76), 0), (W, 0), (W, H), (int(W * 0.66), H)], fill=(46, 92, 160))
    d.polygon([(int(W * 0.84), 0), (W, 0), (W, H), (int(W * 0.74), H)], fill=(66, 122, 196))
    return img


STYLES = {"dark": dark, "light": light, "accent": accent}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "bases")
    os.makedirs(out, exist_ok=True)
    for name, fn in STYLES.items():
        for ratio, size in SIZES.items():
            path = os.path.join(out, f"{name}-{ratio}.png")
            fn(size).save(path, optimize=True)
            print(path)


if __name__ == "__main__":
    main()
