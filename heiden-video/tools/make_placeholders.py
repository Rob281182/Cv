#!/usr/bin/env python3
"""Generate labelled placeholder plates for shots with no footage, and a
placeholder HEIDEN wordmark. Replace the wordmark with the real logo.

usage: make_placeholders.py <shotlist> <out_dir> <W> <H>
       make_placeholders.py --wordmark <out_png>
"""
import sys, os, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_DIR = "/usr/share/fonts/opentype/inter"
def font(name, size):
    for cand in (os.path.join(FONT_DIR, name), "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(cand):
            return ImageFont.truetype(cand, size)
    return ImageFont.load_default()

def read_shotlist(path):
    shots = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 5:
            continue
        shots.append(dict(id=parts[0], stem=parts[1], start=float(parts[2]),
                          dur=float(parts[3]), desc=parts[4]))
    return shots

def plate(W, H, idx, total, desc, out):
    # near-black base with a faint warm/cool drift per shot, plus a soft "rim light" blob
    img = Image.new("RGB", (W, H), (8, 8, 10))
    grad = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / max(H - 1, 1)
        v = int(40 - 22 * t)
        grad.putpixel((0, y), (v + 2, v, v + 3))
    img.paste(grad.resize((W, H)))
    light = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(light)
    cx = int(W * (0.25 + 0.5 * ((idx * 7) % 10) / 10))
    cy = int(H * (0.3 + 0.4 * ((idx * 3) % 10) / 10))
    r = int(min(W, H) * 0.55)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=110)
    light = light.filter(ImageFilter.GaussianBlur(min(W, H) * 0.22))
    warm = (54, 44, 36) if idx % 2 else (36, 44, 54)
    img = Image.composite(Image.new("RGB", (W, H), warm), img, light)

    d = ImageDraw.Draw(img)
    big = font("InterDisplay-Black.otf", int(H * 0.42))
    num = f"{idx:02d}"
    bb = d.textbbox((0, 0), num, font=big)
    d.text((W * 0.5 - (bb[2] - bb[0]) / 2, H * 0.5 - (bb[3] - bb[1]) / 2 - bb[1]),
           num, font=big, fill=(52, 52, 58))

    small = font("Inter-SemiBold.otf", int(H * 0.026) if W > H else int(W * 0.030))
    body = font("Inter-Regular.otf", int(H * 0.030) if W > H else int(W * 0.040))
    pad = int(W * 0.06)
    d.text((pad, pad), "PLACEHOLDER  —  no footage yet for this shot", font=small, fill=(140, 140, 150))
    d.text((pad, pad + (int(H * 0.04) if W > H else int(W * 0.045))), f"Shot {idx:02d} of {total:02d}", font=small, fill=(200, 200, 210))
    wrap = 36 if W < H else 70
    lines = textwrap.wrap(desc, wrap)
    lh = int(H * 0.042) if W > H else int(W * 0.056)
    y = H - pad - len(lines) * lh
    for ln in lines:
        d.text((pad, y), ln, font=body, fill=(225, 222, 215))
        y += lh
    img.save(out, quality=92)

def wordmark(out):
    W, H = 2400, 760
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f1 = font("InterDisplay-Black.otf", 440)
    f2 = font("Inter-SemiBold.otf", 96)
    t1, t2 = "HEIDEN", "C Y C L E   W O R K S"
    # letter-spaced HEIDEN
    sp = 22
    widths = [d.textlength(c, font=f1) for c in t1]
    total = sum(widths) + sp * (len(t1) - 1)
    x = (W - total) / 2
    bb = d.textbbox((0, 0), "H", font=f1)
    y1 = 40 - bb[1]
    for c, w in zip(t1, widths):
        d.text((x, y1), c, font=f1, fill=(255, 255, 255, 255))
        x += w + sp
    bb2 = d.textbbox((0, 0), t2, font=f2)
    d.text(((W - (bb2[2] - bb2[0])) / 2, 40 + (bb[3] - bb[1]) + 70), t2, font=f2, fill=(255, 255, 255, 255))
    img.save(out)

if __name__ == "__main__":
    if sys.argv[1] == "--wordmark":
        wordmark(sys.argv[2]); sys.exit()
    shotlist, out_dir, W, H = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    os.makedirs(out_dir, exist_ok=True)
    shots = read_shotlist(shotlist)
    for i, s in enumerate(shots, 1):
        plate(W, H, i, len(shots), s["desc"], os.path.join(out_dir, f"{s['stem']}.png"))
    print(f"{len(shots)} placeholder plates -> {out_dir}")
