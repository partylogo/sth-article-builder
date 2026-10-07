#!/usr/bin/env python3
"""從網站首頁找品牌 logo 的候選，下載並轉成 PNG（只讀網站，不登入）。

  find_logo.py https://example.com 輸出資料夾 [--brand 品牌名]

找的地方（照這個順序）：
1. 首頁 <img>：alt 等於品牌名，或 src／class 裡有 logo
2. <link rel="apple-touch-icon">、<link rel="icon">（PNG 或 SVG）

SVG 用 rsvg-convert（沒有就用 ImageMagick）轉成 PNG；兩個都沒有就跳過 SVG 並說明。
每個候選印一行 JSON：檔案路徑、來源、尺寸、有沒有透明背景。
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh) Chrome/128"}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20).read()


def attrs(tag):
    return {k.lower(): html.unescape(v) for k, v in re.findall(r'([\w:-]+)="([^"]*)"', tag)}


def svg_to_png(src, dst):
    if shutil.which("rsvg-convert"):
        cmd = ["rsvg-convert", "-h", "400", "-o", dst, src]
    elif shutil.which("magick"):
        cmd = ["magick", "-background", "none", "-density", "300", src, "-resize", "x400", dst]
    else:
        return "這台電腦沒有 rsvg-convert 或 ImageMagick，SVG 轉不了 PNG"
    r = subprocess.run(cmd, capture_output=True, text=True)
    return None if r.returncode == 0 else (r.stderr.strip() or "SVG 轉檔失敗")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("out")
    ap.add_argument("--brand", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    page = get(a.url).decode("utf-8", "ignore")

    found = []
    for tag in re.findall(r"<img\b[^>]*>", page, re.I):
        at = attrs(tag)
        src, alt, cls = at.get("src", ""), at.get("alt", ""), at.get("class", "")
        if (a.brand and alt.strip().lower() == a.brand.lower()) or re.search(r"logo", src + " " + cls, re.I):
            found.append((src, f"首頁圖片 alt「{alt}」"))
    for tag in re.findall(r"<link\b[^>]*>", page, re.I):
        at = attrs(tag)
        rel = at.get("rel", "").lower()
        if "apple-touch-icon" in rel or rel.strip() == "icon":
            href = at.get("href", "")
            if href.endswith(".ico"):
                continue
            found.append((href, f"網站圖示（{rel}）"))

    seen = set()
    for i, (src, where) in enumerate(found):
        url = urllib.parse.urljoin(a.url, src)
        if url in seen:
            continue
        seen.add(url)
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower() or ".png"
        raw = os.path.join(a.out, f"logo-{len(seen)}{ext}")
        try:
            open(raw, "wb").write(get(url))
        except Exception as e:  # 下載失敗就略過這個候選
            print(json.dumps({"source": url, "where": where, "error": str(e)}, ensure_ascii=False))
            continue
        png = raw
        if ext == ".svg":
            png = raw[:-4] + ".png"
            err = svg_to_png(raw, png)
            if err:
                print(json.dumps({"source": url, "where": where, "error": err}, ensure_ascii=False))
                continue
        try:
            from PIL import Image
            im = Image.open(png)
            alpha = im.mode in ("RGBA", "LA") and im.getchannel("A").getextrema()[0] < 255
            info = {"file": png, "size": im.size, "transparent": alpha}
        except Exception as e:
            info = {"file": png, "error": f"讀不了圖：{e}"}
        print(json.dumps({"source": url, "where": where, **info}, ensure_ascii=False))

    if not seen:
        print("首頁找不到 logo 候選", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
