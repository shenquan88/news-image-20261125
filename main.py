import os
from PIL import Image, ImageDraw, ImageFont


W, H = 1024, 1024
BG = (10, 14, 26)
GOLD = (240, 192, 96)
CARD_BG = (255, 255, 255)
CARD_BORDER = (212, 220, 232)
TITLE_COLOR = (15, 23, 42)
SOURCE_COLOR = (122, 132, 150)
TICKER_BG = (14, 20, 38)

FONT_DIR = r"C:\Windows\Fonts"
ENGLISH_PATHS = [
    os.path.join(FONT_DIR, "segoeuib.ttf"),
    os.path.join(FONT_DIR, "arialbd.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
EMOJI_PATH = os.path.join(FONT_DIR, "seguiemj.ttf")

NEWS = [
    ("\U0001f680", "Shenzhou-24 launches with Pakistan's first astronaut", "BBC"),
    ("\U0001f4c8", "Dow closes above 50,000 for the first time", "MarketWatch"),
    ("\U0001f7e2", "Nvidia surges 31% in a single day", "MarketWatch"),
    ("\U0001f3ae", "GTA VI launch sets sales records", "The Guardian"),
    ("\U0001f6f0\ufe0f", "Spacecraft reaches Mercury orbit after 8-year journey", "CBS News"),
    ("\U0001f3c6", "Dancing With the Stars Season 35 winner crowned", "Hollywood Reporter"),
]


def load_font(paths, size):
    for path in paths:
        if path and os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except Exception:
        pass
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def load_emoji_font(size):
    if os.path.isfile(EMOJI_PATH):
        try:
            return ImageFont.truetype(EMOJI_PATH, size)
        except Exception:
            return None
    return None


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if not current or draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_emoji_fallback(draw, x, y, s, char):
    base = char.replace("\ufe0f", "")
    if base == "\U0001f680":
        draw.polygon(
            [(x + 0.5 * s, y), (x + 0.95 * s, y + 0.42 * s),
             (x + 0.5 * s, y + 0.52 * s), (x + 0.05 * s, y + 0.42 * s)],
            fill=(185, 195, 215),
        )
        draw.rectangle(
            [x + 0.28 * s, y + 0.5 * s, x + 0.72 * s, y + 0.78 * s],
            fill=(235, 235, 235),
        )
        draw.polygon(
            [(x + 0.36 * s, y + 0.78 * s), (x + 0.64 * s, y + 0.78 * s),
             (x + 0.5 * s, y + 0.98 * s)],
            fill=(240, 150, 70),
        )
    elif base == "\U0001f4c8":
        draw.line([x + 0.05 * s, y + 0.85 * s, x + 0.95 * s, y + 0.85 * s], fill=(70, 72, 80), width=3)
        draw.line([x + 0.05 * s, y + 0.85 * s, x + 0.05 * s, y + 0.05 * s], fill=(70, 72, 80), width=3)
        draw.line(
            [x + 0.05 * s, y + 0.72 * s, x + 0.35 * s, y + 0.48 * s,
             x + 0.62 * s, y + 0.58 * s, x + 0.95 * s, y + 0.14 * s],
            fill=(40, 165, 75),
            width=4,
        )
    elif base == "\U0001f7e2":
        draw.ellipse([x, y, x + s, y + s], fill=(60, 190, 80))
    elif base == "\U0001f3ae":
        draw.rounded_rectangle(
            [x, y + 0.15 * s, x + 0.9 * s, y + 0.8 * s],
            radius=int(0.15 * s), fill=(40, 45, 60),
        )
        draw.line([x + 0.3 * s, y + 0.15 * s, x + 0.3 * s, y + 0.5 * s], fill=(230, 230, 230), width=3)
        draw.line([x + 0.6 * s, y + 0.15 * s, x + 0.6 * s, y + 0.5 * s], fill=(230, 230, 230), width=3)
    elif base == "\U0001f4a5":
        for i, (dx, dy) in enumerate([(0.5, 0.02), (0.82, 0.25), (0.9, 0.55), (0.7, 0.8),
                                      (0.4, 0.85), (0.2, 0.62), (0.14, 0.3), (0.3, 0.1)]):
            draw.line([x + 0.5 * s, y + 0.5 * s, x + dx * s, y + dy * s],
                      fill=[(240, 160, 60), (250, 210, 90)][i % 2], width=3)
    elif base == "\u26a0\ufe0f":
        draw.polygon(
            [(x + 0.5 * s, y), (x + s, y + 0.9 * s), (x, y + 0.9 * s)],
            fill=(240, 180, 60),
        )
        draw.rectangle(
            [x + 0.44 * s, y + 0.36 * s, x + 0.56 * s, y + 0.62 * s],
            fill=(30, 30, 30),
        )
        draw.ellipse([x + 0.44 * s, y + 0.7 * s, x + 0.56 * s, y + 0.82 * s], fill=(30, 30, 30))
    elif base == "\U0001f6f0":
        # planet with an orbiting probe
        cx, cy = x + 0.5 * s, y + 0.54 * s
        draw.ellipse([cx - 0.27 * s, cy - 0.27 * s, cx + 0.27 * s, cy + 0.27 * s],
                     fill=(86, 140, 210))
        draw.ellipse([cx - 0.14 * s, cy - 0.12 * s, cx + 0.11 * s, cy + 0.13 * s],
                     fill=(120, 190, 130))
        draw.ellipse([cx - 0.5 * s, cy - 0.17 * s, cx + 0.5 * s, cy + 0.17 * s],
                     outline=(240, 192, 96), width=3)
        draw.ellipse([cx + 0.28 * s, cy - 0.31 * s, cx + 0.42 * s, cy - 0.17 * s],
                     fill=(240, 192, 96))
    elif base == "\U0001f3c6":
        # trophy
        draw.polygon(
            [(x + 0.22 * s, y + 0.16 * s), (x + 0.78 * s, y + 0.16 * s),
             (x + 0.68 * s, y + 0.56 * s), (x + 0.32 * s, y + 0.56 * s)],
            fill=(240, 192, 96),
        )
        draw.arc([x + 0.02 * s, y + 0.14 * s, x + 0.34 * s, y + 0.48 * s],
                 90, 270, fill=(240, 192, 96), width=3)
        draw.arc([x + 0.66 * s, y + 0.14 * s, x + 0.98 * s, y + 0.48 * s],
                 270, 90, fill=(240, 192, 96), width=3)
        draw.rectangle([x + 0.44 * s, y + 0.54 * s, x + 0.56 * s, y + 0.74 * s],
                       fill=(240, 192, 96))
        draw.rectangle([x + 0.28 * s, y + 0.74 * s, x + 0.72 * s, y + 0.86 * s],
                       fill=(240, 192, 96))


def draw_emoji(draw, xy, size, char):
    font = load_emoji_font(size)
    if font is not None:
        draw.text(xy, char, font=font, embedded_color=True)
    else:
        draw_emoji_fallback(draw, xy[0], xy[1], float(size), char)


def draw_globe(base, cx, cy, r):
    globe = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(globe)

    g.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(20, 46, 92, 255))
    g.ellipse(
        [cx - int(r * 0.56), cy - int(r * 0.66), cx + int(r * 0.02), cy - int(r * 0.30)],
        fill=(108, 160, 218, 90),
    )

    grid = (72, 122, 176, 200)
    for w in (0, 62, 118, 160):
        g.ellipse([cx - w, cy - r, cx + w, cy + r], outline=grid, width=2)
    for dy in (-80, 0, 80):
        hw = int((r * r - dy * dy) ** 0.5)
        g.line([cx - hw, cy + dy, cx + hw, cy + dy], fill=grid, width=2)

    land = (112, 190, 122, 255)
    g.polygon(
        [(cx - 0.62 * r, cy - 0.28 * r), (cx - 0.55 * r, cy - 0.45 * r),
         (cx - 0.38 * r, cy - 0.50 * r), (cx - 0.28 * r, cy - 0.32 * r),
         (cx - 0.40 * r, cy - 0.12 * r), (cx - 0.58 * r, cy - 0.08 * r)],
        fill=land,
    )
    g.polygon(
        [(cx - 0.45 * r, cy + 0.02 * r), (cx - 0.33 * r, cy + 0.04 * r),
         (cx - 0.28 * r, cy + 0.28 * r), (cx - 0.30 * r, cy + 0.45 * r),
         (cx - 0.42 * r, cy + 0.30 * r), (cx - 0.47 * r, cy + 0.10 * r)],
        fill=land,
    )
    g.ellipse(
        [cx - 0.52 * r, cy - 0.64 * r, cx - 0.30 * r, cy - 0.46 * r],
        fill=land,
    )
    g.polygon(
        [(cx + 0.18 * r, cy - 0.42 * r), (cx + 0.42 * r, cy - 0.38 * r),
         (cx + 0.55 * r, cy - 0.22 * r), (cx + 0.48 * r, cy + 0.02 * r),
         (cx + 0.40 * r, cy + 0.30 * r), (cx + 0.28 * r, cy + 0.42 * r),
         (cx + 0.22 * r, cy + 0.28 * r), (cx + 0.26 * r, cy + 0.02 * r),
         (cx + 0.18 * r, cy - 0.15 * r)],
        fill=land,
    )
    g.ellipse(
        [cx + 0.28 * r, cy + 0.52 * r, cx + 0.55 * r, cy + 0.72 * r],
        fill=land,
    )

    g.ellipse([cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3], outline=(240, 192, 96, 150), width=3)

    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    base.paste(globe, (0, 0), mask)


def draw_card(draw, x, y, w, h, emoji, title, source, emoji_font, title_font, source_font):
    draw.rounded_rectangle(
        [x, y, x + w, y + h], radius=18, fill=CARD_BG, outline=CARD_BORDER, width=2
    )

    emoji_size = 40
    draw_emoji(draw, (x + 16, y + 12), emoji_size, emoji)

    lines = wrap_text(draw, title, title_font, w - 32)
    ty = y + 66
    for line in lines[:3]:
        draw.text((x + 16, ty), line, font=title_font, fill=TITLE_COLOR)
        ty += 27

    draw.text((x + 16, y + h - 32), source, font=source_font, fill=SOURCE_COLOR)


def build():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    title_font = load_font(ENGLISH_PATHS, 54)
    draw.text((W / 2, 60), "NOVEMBER 25, 2026", font=title_font, fill=GOLD, anchor="mm")
    draw.text((W / 2, 132), "\u00b7 THE DAY IN ONE IMAGE", font=title_font, fill=GOLD, anchor="mm")

    draw_globe(img, 512, 600, 170)

    card_w, card_h = 272, 184
    left_x, right_x = 18, W - 18 - card_w
    ys = [176, 384, 592]

    emoji_font = load_emoji_font(40)
    title_font = load_font(ENGLISH_PATHS, 22)
    source_font = load_font(ENGLISH_PATHS, 16)

    for i, (emoji, title, source) in enumerate(NEWS):
        col = i // 3
        x = left_x if col == 0 else right_x
        y = ys[i % 3]
        draw_card(draw, x, y, card_w, card_h, emoji, title, source, emoji_font, title_font, source_font)

    ticker_y0, ticker_y1 = 936, 992
    draw.rectangle([0, ticker_y0, W, ticker_y1], fill=TICKER_BG)
    tick_font = load_font(ENGLISH_PATHS, 26)
    tick_emoji_font = load_emoji_font(26)
    mid_y = (ticker_y0 + ticker_y1) / 2
    left_text = "DOW 50,000 \u25b2 | NVIDIA +31% | GTA VI RECORD | SHENZHOU-24 "
    rocket = "\U0001f680"

    w1 = draw.textlength(left_text, font=tick_font)
    w2 = draw.textlength(rocket, font=tick_emoji_font) if tick_emoji_font is not None else 30
    total = w1 + w2 + 4
    start_x = (W - total) / 2
    draw.text((start_x, mid_y), left_text, font=tick_font, fill=GOLD, anchor="lm")
    if tick_emoji_font is not None:
        draw.text((start_x + w1 + 4, mid_y), rocket, font=tick_emoji_font, embedded_color=True, anchor="lm")
    else:
        draw_emoji_fallback(draw, start_x + w1 + 4, mid_y - 13, 26, rocket)

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or (
        "/output" if os.path.isdir("/output") else os.path.dirname(os.path.abspath(__file__))
    )
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    build().save(out_path, format="PNG", optimize=True)
    print(out_path)


if __name__ == "__main__":
    main()
