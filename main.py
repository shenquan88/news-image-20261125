"""Builds the poster submitted for the make.fun news-image contest.

A lone 1024x1024 canvas that captures the headlines recorded on 25 November
2026, drawn with the interpreter alone: zlib, struct, base64, json and math
from the standard library, nothing else. No network calls, no random seed, no
clock, and no font file to open, so successive runs stay byte-for-byte
identical and the program survives an image that ships neither Pillow nor a
single system font.

The letterforms are DejaVu Sans Bold outlines carried inside this file in font
units, rasterised here by a small scanline filler with supersampled edges. The
same table renders on Windows, Linux or a scratch container, which is why the
bytes do not drift between machines.

The six items are arranged as three AABBCC couplets, one verse per card, and
each poster row holds a single couplet: the card on the left rhymes with its
neighbour on the right. The underlying facts remain untouched; only the wording
is made to rhyme.
"""

import base64
import json
import math
import os
import struct
import tempfile
import zlib


W, H = 1024, 1024
BG = (10, 14, 26)
GOLD = (240, 192, 96)
CARD_BG = (255, 255, 255)
CARD_BORDER = (212, 220, 232)
TITLE_COLOR = (15, 23, 42)
SOURCE_COLOR = (122, 132, 150)
TICKER_BG = (14, 20, 38)

# a distinct accent per couplet keeps the AABBCC grouping easy to spot
PAIR_A = (214, 158, 46)    # golden amber
PAIR_B = (46, 158, 112)    # fresh green
PAIR_C = (54, 118, 198)    # cool blue

# (icon, verse text, outlet, pair label, accent colour)
# A: space rhymes with pace; B: day rhymes with play; C: claimed rhymes with named
NEWS = [
    ("\U0001f680", "Shenzhou-24 flies Pakistan's first astronaut to space,",
     "BBC", "A", PAIR_A),
    ("\U0001f4c8", "Dow tops fifty thousand as bulls set the pace.",
     "MarketWatch", "A", PAIR_A),
    ("\U0001f7e2", "Nvidia climbs thirty-one percent in a day,",
     "MarketWatch", "B", PAIR_B),
    ("\U0001f3ae", "GTA VI launches and rewrites the play.",
     "The Guardian", "B", PAIR_B),
    ("\U0001f6f0\ufe0f", "Eight years to Mercury \u2014 its orbit is claimed,",
     "CBS News", "C", PAIR_C),
    ("\U0001f3c6", "Dancing With the Stars: a champion is named.",
     "Hollywood Reporter", "C", PAIR_C),
]

# ---------------------------------------------------------------------------
# Embedded face: DejaVu Sans Bold contours in font units (y up), stored as
# zlib+base64 JSON: {"upem", "asc", "desc", "glyphs": {codepoint: [advance,
# [[x, y, on_curve, ...], ...]]}}. The advance and the outline axes are the
# font's own, scaled by size / upem at draw time.
# ---------------------------------------------------------------------------
_GLYPH_BLOB = "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"

# unit circle, scaled by 1e6, so no libm trigonometry decides a pixel
_COS = (
    1000000, 998795, 995185, 989177, 980785, 970031, 956940, 941544, 923880, 903989, 881921, 857729,
    831470, 803208, 773010, 740951, 707107, 671559, 634393, 595699, 555570, 514103, 471397, 427555,
    382683, 336890, 290285, 242980, 195090, 146730, 98017, 49068, 0, -49068, -98017, -146730,
    -195090, -242980, -290285, -336890, -382683, -427555, -471397, -514103, -555570, -595699, -634393, -671559,
    -707107, -740951, -773010, -803208, -831470, -857729, -881921, -903989, -923880, -941544, -956940, -970031,
    -980785, -989177, -995185, -998795, -1000000, -998795, -995185, -989177, -980785, -970031, -956940, -941544,
    -923880, -903989, -881921, -857729, -831470, -803208, -773010, -740951, -707107, -671559, -634393, -595699,
    -555570, -514103, -471397, -427555, -382683, -336890, -290285, -242980, -195090, -146730, -98017, -49068,
    0, 49068, 98017, 146730, 195090, 242980, 290285, 336890, 382683, 427555, 471397, 514103,
    555570, 595699, 634393, 671559, 707107, 740951, 773010, 803208, 831470, 857729, 881921, 903989,
    923880, 941544, 956940, 970031, 980785, 989177, 995185, 998795,
)
_SIN = (
    0, 49068, 98017, 146730, 195090, 242980, 290285, 336890, 382683, 427555, 471397, 514103,
    555570, 595699, 634393, 671559, 707107, 740951, 773010, 803208, 831470, 857729, 881921, 903989,
    923880, 941544, 956940, 970031, 980785, 989177, 995185, 998795, 1000000, 998795, 995185, 989177,
    980785, 970031, 956940, 941544, 923880, 903989, 881921, 857729, 831470, 803208, 773010, 740951,
    707107, 671559, 634393, 595699, 555570, 514103, 471397, 427555, 382683, 336890, 290285, 242980,
    195090, 146730, 98017, 49068, 0, -49068, -98017, -146730, -195090, -242980, -290285, -336890,
    -382683, -427555, -471397, -514103, -555570, -595699, -634393, -671559, -707107, -740951, -773010, -803208,
    -831470, -857729, -881921, -903989, -923880, -941544, -956940, -970031, -980785, -989177, -995185, -998795,
    -1000000, -998795, -995185, -989177, -980785, -970031, -956940, -941544, -923880, -903989, -881921, -857729,
    -831470, -803208, -773010, -740951, -707107, -671559, -634393, -595699, -555570, -514103, -471397, -427555,
    -382683, -336890, -290285, -242980, -195090, -146730, -98017, -49068,
)
_STEPS = 128

_FACE = json.loads(zlib.decompress(base64.b64decode(_GLYPH_BLOB)).decode("utf-8"))
_UPEM = float(_FACE["upem"])
_KERN = {(l, r): v for (l, r, v) in _FACE.get("kern", ())}


class Face:
    """One size of the embedded face."""

    def __init__(self, size):
        self.size = size
        self.scale = float(size) / _UPEM
        self.asc = _FACE["asc"] * self.scale
        self.desc = _FACE["desc"] * self.scale

    def advance(self, ch):
        g = _FACE["glyphs"].get(str(ord(ch)))
        return (g[0] if g else _FACE["glyphs"]["32"][0]) * self.scale

    def kern(self, prev, ch):
        return _KERN.get((prev, ord(ch)), 0) * self.scale

    def length(self, text):
        # sums the same advances and kern pairs the wrap points depend on
        total = 0.0
        prev = -1
        for ch in text:
            if prev >= 0:
                total += self.kern(prev, ch)
            total += self.advance(ch)
            prev = ord(ch)
        return total


# The outlines travel in the source, so there is no font path to probe and no
# fallback chain to walk: the same glyphs appear on an image that ships no
# fonts at all, which is the case for the official python3.13-slim runtime.
def load_font(size):
    return Face(size)


def load_emoji_font(size):
    """No colour emoji font exists on a font-less runtime, so the drawn icons
    below always run; the hook stays so the ticker keeps one code path."""
    return None


# ---------------------------------------------------------------------------
# Rasteriser: nonzero winding, analytic horizontal coverage, supersampled
# vertically. Every shape becomes a list of closed contours in device pixels.
# ---------------------------------------------------------------------------
def _quad(p0, c, p1, steps=10):
    out = []
    for i in range(1, steps + 1):
        t = i / float(steps)
        mt = 1.0 - t
        a = mt * mt
        b = 2.0 * mt * t
        d = t * t
        out.append((a * p0[0] + b * c[0] + d * p1[0],
                    a * p0[1] + b * c[1] + d * p1[1]))
    return out


def _trace(run):
    """Turn one TrueType contour (x, y, on_curve triples) into a polygon."""
    pts = []
    for i in range(0, len(run), 3):
        pts.append((run[i], -run[i + 1], run[i + 2]))
    if len(pts) < 3:
        return []
    if pts[0][2]:
        seq = pts + [pts[0]]
    else:
        last = pts[-1]
        start = ((last[0] + pts[0][0]) * 0.5, (last[1] + pts[0][1]) * 0.5, 1)
        seq = [start] + pts
    poly = [(seq[0][0], seq[0][1])]
    cur = seq[0]
    i = 1
    n = len(seq)
    while i < n:
        p = seq[i]
        if p[2]:
            poly.append((p[0], p[1]))
            cur = p
            i += 1
            continue
        nxt = seq[i + 1] if i + 1 < n else seq[0]
        if nxt[2]:
            poly.extend(_quad((cur[0], cur[1]), (p[0], p[1]), (nxt[0], nxt[1])))
            cur = nxt
            i += 2
        else:
            mid = ((p[0] + nxt[0]) * 0.5, (p[1] + nxt[1]) * 0.5)
            poly.extend(_quad((cur[0], cur[1]), (p[0], p[1]), mid))
            cur = (mid[0], mid[1], 1)
            i += 1
    if len(poly) > 2:
        return poly
    return []


def _arc(cx, cy, rx, ry, i0, i1):
    pts = []
    for k in range(i0, i1 + 1):
        idx = k % _STEPS
        pts.append((cx + rx * (_COS[idx] * 1e-6), cy + ry * (_SIN[idx] * 1e-6)))
    return pts


def _ellipse_contour(cx, cy, rx, ry):
    return _arc(cx, cy, rx, ry, 0, _STEPS)


def _round_rect_contour(x0, y0, x1, y1, r):
    if x1 <= x0 or y1 <= y0:
        return []
    limit = min((x1 - x0) * 0.5, (y1 - y0) * 0.5)
    if r > limit:
        r = limit
    if r <= 0:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    q = _STEPS // 4
    pts = []
    pts += _arc(x1 - r, y0 + r, r, r, 3 * q, 4 * q)
    pts += _arc(x1 - r, y1 - r, r, r, 0, q)
    pts += _arc(x0 + r, y1 - r, r, r, q, 2 * q)
    pts += _arc(x0 + r, y0 + r, r, r, 2 * q, 3 * q)
    return pts


def _pairs(points):
    """Accept both [(x, y), ...] and the flat [x, y, x, y, ...] the icon
    routines write."""
    if not points:
        return []
    if isinstance(points[0], (int, float)):
        return [(float(points[i]), float(points[i + 1]))
                for i in range(0, len(points) - 1, 2)]
    return [(float(x), float(y)) for (x, y) in points]


def _stroke(pts, width):
    """Quads along a polyline, the way a wide pen lays them down."""
    h = width * 0.5
    quads = []
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        dx = bx - ax
        dy = by - ay
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0.0:
            continue
        nx = -dy / length * h
        ny = dx / length * h
        quads.append([(ax + nx, ay + ny), (bx + nx, by + ny),
                      (bx - nx, by - ny), (ax - nx, ay - ny)])
    return quads


def _coverage(contours, x0, y0, x1, y1, ss):
    """Coverage per pixel over the given integer box, 0.0 .. 1.0."""
    bw = x1 - x0
    bh = y1 - y0
    cov = [0.0] * (bw * bh)
    edges = []
    for contour in contours:
        n = len(contour)
        for i in range(n):
            ax, ay = contour[i]
            bx, by = contour[(i + 1) % n]
            if ay != by:
                edges.append((ax, ay, bx, by))
    if not edges:
        return cov
    inv = 1.0 / ss
    for sub in range(bh * ss):
        sy = y0 + (sub + 0.5) * inv
        hits = []
        for (ax, ay, bx, by) in edges:
            if (ay <= sy < by) or (by <= sy < ay):
                t = (sy - ay) / (by - ay)
                hits.append((ax + t * (bx - ax), 1 if by > ay else -1))
        if not hits:
            continue
        hits.sort()
        wind = 0
        start = 0.0
        row = (sub // ss) * bw
        for (x, direction) in hits:
            if wind == 0:
                start = x
            wind += direction
            if wind == 0 and x > start:
                _span(cov, row, bw, start, x, x0, inv)
    for i, v in enumerate(cov):
        if v > 1.0:
            cov[i] = 1.0
    return cov


def _span(cov, row, bw, xa, xb, x0, inv):
    i0 = int(xa - x0)
    if i0 < 0:
        i0 = 0
    i1 = int(xb - x0)
    if i1 >= bw:
        i1 = bw - 1
    if i0 > i1:
        return
    if i0 == i1:
        lo = xa if xa > x0 + i0 else x0 + i0
        hi = xb if xb < x0 + i0 + 1 else x0 + i0 + 1
        if hi > lo:
            cov[row + i0] += (hi - lo) * inv
        return
    lo = xa if xa > x0 + i0 else x0 + i0
    hi = x0 + i0 + 1
    if hi > lo:
        cov[row + i0] += (hi - lo) * inv
    base = row + i0 + 1
    for i in range(base, row + i1):
        cov[i] += inv
    lo = x0 + i1
    hi = xb if xb < x0 + i1 + 1 else x0 + i1 + 1
    if hi > lo:
        cov[row + i1] += (hi - lo) * inv


class Surface:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))
        self.cover = None          # opt-in 8-bit coverage, used when pasting

    def _blend(self, x0, y0, x1, y1, cov, color, alpha):
        px = self.px
        w = self.w
        cr = color[0]
        cg = color[1]
        cb = color[2]
        k = 0
        span = x1 - x0
        for y in range(y0, y1):
            row = y * w * 3
            for x in range(span):
                a = cov[k] * alpha
                k += 1
                if a <= 0.0:
                    continue
                p = row + (x0 + x) * 3
                if a >= 0.999:
                    px[p] = cr
                    px[p + 1] = cg
                    px[p + 2] = cb
                else:
                    ia = 1.0 - a
                    px[p] = int(px[p] * ia + cr * a + 0.5)
                    px[p + 1] = int(px[p + 1] * ia + cg * a + 0.5)
                    px[p + 2] = int(px[p + 2] * ia + cb * a + 0.5)
        if self.cover is not None:
            k = 0
            for y in range(y0, y1):
                row = y * w
                for x in range(span):
                    v = int(cov[k] * alpha * 255.0 + 0.5)
                    k += 1
                    if v <= 0:
                        continue
                    p = row + x0 + x
                    if v > self.cover[p]:
                        self.cover[p] = v

    def paste(self, src, mask_cover):
        px = self.px
        sp = src.px
        w = self.w
        for i in range(w * self.h):
            a = mask_cover[i]
            if a == 0:
                continue
            p = i * 3
            if a == 255:
                px[p] = sp[p]
                px[p + 1] = sp[p + 1]
                px[p + 2] = sp[p + 2]
                continue
            f = a / 255.0
            ia = 1.0 - f
            px[p] = int(px[p] * ia + sp[p] * f + 0.5)
            px[p + 1] = int(px[p + 1] * ia + sp[p + 1] * f + 0.5)
            px[p + 2] = int(px[p + 2] * ia + sp[p + 2] * f + 0.5)


class Draw:
    """The slice of the drawing API the poster uses, over a Surface."""

    SS = 4

    def __init__(self, surface):
        self.s = surface

    # -- internals ---------------------------------------------------------
    def _fill(self, contours, color, alpha=1.0, ss=None):
        contours = [c for c in contours if len(c) > 2]
        if not contours or color is None:
            return
        if len(color) == 4:
            alpha = alpha * (color[3] / 255.0)
        if alpha <= 0.0:
            return
        if ss is None:
            ss = self.SS
        xs = []
        ys = []
        for contour in contours:
            for (x, y) in contour:
                xs.append(x)
                ys.append(y)
        x0 = int(math.floor(min(xs))) - 1
        x1 = int(math.ceil(max(xs))) + 1
        y0 = int(math.floor(min(ys))) - 1
        y1 = int(math.ceil(max(ys))) + 1
        if x0 < 0:
            x0 = 0
        if y0 < 0:
            y0 = 0
        if x1 > self.s.w:
            x1 = self.s.w
        if y1 > self.s.h:
            y1 = self.s.h
        if x1 <= x0 or y1 <= y0:
            return
        cov = _coverage(contours, x0, y0, x1, y1, ss)
        self.s._blend(x0, y0, x1, y1, cov, color, alpha)

    # -- primitives --------------------------------------------------------
    def rectangle(self, box, fill=None, outline=None, width=1):
        x0, y0, x1, y1 = box
        if fill is not None:
            self._fill([[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]], fill)
        if outline is not None and width:
            w = float(width)
            outer = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            inner = [(x0 + w, y0 + w), (x1 - w, y0 + w),
                     (x1 - w, y1 - w), (x0 + w, y1 - w)]
            self._fill([outer, inner[::-1]], outline)

    def rounded_rectangle(self, box, radius=0, fill=None, outline=None, width=1):
        x0, y0, x1, y1 = box
        outer = _round_rect_contour(x0, y0, x1, y1, radius)
        if fill is not None:
            self._fill([outer], fill)
        if outline is not None and width:
            w = float(width)
            inner = _round_rect_contour(x0 + w, y0 + w, x1 - w, y1 - w,
                                        radius - w if radius > w else 0)
            self._fill([outer, inner[::-1]], outline)

    def ellipse(self, box, fill=None, outline=None, width=1):
        x0, y0, x1, y1 = box
        cx = (x0 + x1) * 0.5
        cy = (y0 + y1) * 0.5
        rx = (x1 - x0) * 0.5
        ry = (y1 - y0) * 0.5
        if rx <= 0 or ry <= 0:
            return
        outer = _ellipse_contour(cx, cy, rx, ry)
        if fill is not None:
            self._fill([outer], fill)
        if outline is not None and width:
            w = float(width)
            irx = rx - w
            iry = ry - w
            if irx <= 0 or iry <= 0:
                self._fill([outer], outline)
            else:
                inner = _ellipse_contour(cx, cy, irx, iry)
                self._fill([outer, inner[::-1]], outline)

    def polygon(self, points, fill=None):
        pts = _pairs(points)
        if fill is not None and len(pts) > 2:
            self._fill([pts], fill)

    def line(self, points, fill=None, width=1):
        pts = _pairs(points)
        if fill is None or len(pts) < 2:
            return
        if len(pts) == 2 and width <= 1:
            self._fill([[(pts[0][0], pts[0][1]), (pts[1][0], pts[1][1]),
                         (pts[1][0] + 0.8, pts[1][1] + 0.8),
                         (pts[0][0] + 0.8, pts[0][1] + 0.8)]], fill)
            return
        self._fill(_stroke(pts, float(width)), fill)

    def arc(self, box, start, end, fill=None, width=1):
        if fill is None:
            return
        x0, y0, x1, y1 = box
        cx = (x0 + x1) * 0.5
        cy = (y0 + y1) * 0.5
        rx = (x1 - x0) * 0.5
        ry = (y1 - y0) * 0.5
        steps = max(8, int((abs(end - start) / 360.0) * _STEPS))
        pts = []
        for i in range(steps + 1):
            deg = start + (end - start) * i / float(steps)
            idx = int(round(deg / 360.0 * _STEPS)) % _STEPS
            pts.append((cx + rx * (_COS[idx] * 1e-6), cy + ry * (_SIN[idx] * 1e-6)))
        self._fill(_stroke(pts, float(width)), fill)

    # -- text --------------------------------------------------------------
    def textlength(self, text, font=None):
        return font.length(text)

    def text(self, xy, text, font=None, fill=None, anchor=None):
        if fill is None or font is None or not text:
            return
        x = float(xy[0])
        y = float(xy[1])
        if anchor and anchor[0] == "m":
            x -= font.length(text) * 0.5
        if anchor and anchor[1] == "m":
            baseline = y + (font.asc + font.desc) * 0.5
        else:
            baseline = y + font.asc
        scale = font.scale
        pen = x
        prev = -1
        for ch in text:
            if prev >= 0:
                pen += font.kern(prev, ch)
            prev = ord(ch)
            g = _FACE["glyphs"].get(str(ord(ch)))
            if g is None:
                pen += font.advance(ch)
                continue
            if g[1] and ch != " ":
                contours = []
                for run in g[1]:
                    poly = _trace(run)
                    if poly:
                        contours.append([(px * scale + pen, py * scale + baseline)
                                         for (px, py) in poly])
                if contours:
                    self._fill(contours, fill, ss=4)
            pen += g[0] * scale


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
    elif base == "\U0001f6f0":
        # planet circled by a small probe
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
        # championship cup
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
        draw.text(xy, char, font=font, fill=(0, 0, 0))
    else:
        draw_emoji_fallback(draw, xy[0], xy[1], float(size), char)


def draw_globe(base, cx, cy, r):
    globe = Surface(W, H, (0, 0, 0))
    globe.cover = bytearray(W * H)
    g = Draw(globe)

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

    mask = Surface(W, H, (0, 0, 0))
    mask.cover = bytearray(W * H)
    Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))
    base.paste(globe, mask.cover)


def draw_verse_card(draw, x, y, w, h, emoji, verse, source, pair_id, pair_color,
                    verse_font, source_font, badge_font, bar_on_right):
    """A single verse per card; the pair label sits in the corner so the two
    rhyming cards are instantly recognisable."""
    draw.rounded_rectangle(
        [x, y, x + w, y + h], radius=18, fill=CARD_BG, outline=CARD_BORDER, width=2
    )
    # coloured edge strip on the outside, matched per couplet so the halves echo
    if bar_on_right:
        bar = [x + w - 20, y + 14, x + w - 12, y + h - 14]
    else:
        bar = [x + 12, y + 14, x + 20, y + h - 14]
    draw.rounded_rectangle(bar, radius=4, fill=pair_color)

    draw_emoji(draw, (x + 28, y + 16), 40, emoji)

    # couplet badge
    bx, by, br = x + w - 34, y + 38, 17
    if bar_on_right:
        bx = x + w - 48
    draw.ellipse([bx - br, by - br, bx + br, by + br], outline=pair_color, width=2)
    draw.text((bx, by), pair_id, font=badge_font, fill=pair_color, anchor="mm")

    # the measure stops short of the accent strip, so a full line still clears it
    lines = wrap_text(draw, verse, verse_font, w - 48)
    ty = y + 68
    for line in lines[:3]:
        draw.text((x + 28, ty), line, font=verse_font, fill=TITLE_COLOR)
        ty += 29

    draw.text((x + 28, y + h - 30), source, font=source_font, fill=SOURCE_COLOR)


# Assembles the poster from top to bottom: header first, then the globe,
# then the three couplet rows, and finally the ticker band.
def build():
    img = Surface(W, H, BG)
    draw = Draw(img)

    title_font = load_font(54)
    draw.text((W / 2, 54), "NOVEMBER 25, 2026", font=title_font, fill=GOLD, anchor="mm")
    sub_font = load_font(40)
    draw.text((W / 2, 112), "\u00b7 THE DAY IN RHYME", font=sub_font, fill=GOLD, anchor="mm")
    # labels the pattern so the A/A, B/B, C/C tags read as rhyming pairs
    hint_font = load_font(17)
    draw.text((W / 2, 148), "SIX STORIES \u00b7 THREE COUPLETS \u00b7 AABBCC",
              font=hint_font, fill=(168, 150, 110), anchor="mm")

    draw_globe(img, 512, 524, 145)

    card_w, card_h = 340, 184
    left_x, right_x = 16, W - 16 - card_w
    ys = [168, 442, 716]

    verse_font = load_font(21)
    source_font = load_font(16)
    badge_font = load_font(20)

    for i, (emoji, verse, source, pair_id, pair_color) in enumerate(NEWS):
        row = i // 2                      # each row holds one couplet
        on_right = i % 2 == 1
        x = right_x if on_right else left_x
        draw_verse_card(draw, x, ys[row], card_w, card_h, emoji, verse, source,
                        pair_id, pair_color, verse_font, source_font, badge_font,
                        on_right)

    ticker_y0, ticker_y1 = 936, 992
    draw.rectangle([0, ticker_y0, W, ticker_y1], fill=TICKER_BG)
    tick_font = load_font(26)
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
        draw.text((start_x + w1 + 4, mid_y), rocket, font=tick_emoji_font, fill=GOLD, anchor="lm")
    else:
        draw_emoji_fallback(draw, start_x + w1 + 4, mid_y - 13, 26, rocket)

    return img


def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def save_png(img, path):
    stride = img.w * 3
    raw = bytearray()
    for y in range(img.h):
        raw.append(0)
        raw += img.px[y * stride:(y + 1) * stride]
    body = zlib.compress(bytes(raw), 9)
    png = (b"\x89PNG\r\n\x1a\n" +
           _chunk(b"IHDR", struct.pack(">IIBBBBB", img.w, img.h, 8, 2, 0, 0, 0)) +
           _chunk(b"IDAT", body) +
           _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


def _usable(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass                       # exists already, or not ours to create
    return os.path.isdir(path) and os.access(path, os.W_OK)


def output_dir():
    """Where the grader collects the artifact: $MAKEFUN_OUTPUT_DIR, else the
    empty /output it mounts, else an output/ folder beside this file, else a
    scratch directory. The first three are tried in that order and the first
    one that actually accepts a write wins, so a read-only tree cannot turn a
    finished poster into a failed run."""
    forced = os.environ.get("MAKEFUN_OUTPUT_DIR")
    candidates = []
    if forced:
        candidates.append(forced)
    candidates.append("/output")
    candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "output"))
    for path in candidates:
        if _usable(path):
            return path
    return tempfile.mkdtemp(prefix="makefun-")


def main():
    out_path = os.path.join(output_dir(), "entry.png")
    try:
        save_png(build(), out_path)
    except OSError:
        # the tree refused the write after all: keep going in scratch space
        out_path = os.path.join(tempfile.mkdtemp(prefix="makefun-"), "entry.png")
        save_png(build(), out_path)
    print(out_path)


if __name__ == "__main__":
    main()
