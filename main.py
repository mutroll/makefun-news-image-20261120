#!/usr/bin/env python3
"""news-image-20261120: one poster that sums up Friday 20 November 2026.

Pure Python 3.13 standard library, no network, fully deterministic.
Draws a newspaper-style front page (masthead, six story panels, footer)
into an RGB framebuffer and encodes it as a PNG written to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

Stories (all events that happened or were first reported on 20 Nov 2026,
corroborated by 2+ sources; see ../notes-news-20261120.md):
  1. Cyclone Akvan bears down on Odisha, India (landfall due ~noon IST)
  2. Asian tech sell-off: SoftBank -16%, Nikkei -3.7%, Kospi under 5,000
  3. Japan core inflation 2.2% in October, highest of 2026
  4. Taiwan short-selling curbs take effect today
  5. EU to summon Russia's envoy after Kyiv embassy strikes
  6. World Children's Day (UN, 20 November)
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ------------------------------------------------------------------ font
# A hand-drawn 5x7 block font, written for this poster. Each glyph is
# 7 rows of 5 characters; '#' is a lit pixel. Chunky on purpose: scaled
# up it stays legible when the whole poster is shrunk to ~300 px across.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", ".#.#.", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "%": ("##..#", "#.#.#", "...#.", "..#..", ".#...", "#.#.#", "#..##"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
}


def text_width(s, scale, tracking=1):
    """Pixel width of a string in the block font."""
    return len(s) * (5 * scale + tracking) - tracking


def wrap_words(text, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split(" ")
        line = ""
        for w in words:
            if line and len(line) + 1 + len(w) > max_chars:
                lines.append(line)
                line = w
            elif line:
                line = line + " " + w
            else:
                line = w
        if line:
            lines.append(line)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.pxbuf = bytearray(bg * (w * h))

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pxbuf[i:i + 3] = color

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.pxbuf[i:(i + (x1 - x0) * 3)] = color * (x1 - x0)

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, thick, color):
        for dy in range(-r - thick, r + thick + 1):
            for dx in range(-r - thick, r + thick + 1):
                d = (dx * dx + dy * dy) ** 0.5
                if r - thick <= d <= r:
                    self.px(cx + dx, cy + dy, color)

    def line(self, x1, y1, x2, y2, color, thick=2):
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for i in range(steps + 1):
            t = i / steps
            x = int(round(x1 + (x2 - x1) * t))
            y = int(round(y1 + (y2 - y1) * t))
            self.rect(x - thick // 2, y - thick // 2, thick, thick, color)

    def poly(self, pts, color):
        # Simple scanline fill for a convex polygon.
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    t = (y - y1) / (y2 - y1)
                    xs.append(x1 + t * (x2 - x1))
            if len(xs) >= 2:
                xs.sort()
                self.rect(int(xs[0]), y, int(xs[-1]) - int(xs[0]) + 1, 1, color)

    def text(self, s, x, y, scale, color, tracking=1):
        s = s.upper()  # the block font only carries capitals
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for r, row in enumerate(glyph):
                for c, bit in enumerate(row):
                    if bit == "#":
                        self.rect(x + c * scale, y + r * scale, scale, scale, color)
            x += 5 * scale + tracking

    def text_c(self, s, cx, y, scale, color, tracking=1):
        self.text(s, cx - text_width(s, scale, tracking) // 2, y, scale, color, tracking)


# -------------------------------------------------------------------- png
def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def save_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.pxbuf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += _chunk(b"IHDR", ihdr)
    data += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)

# ------------------------------------------------------------------ colors
PAPER = bytes((246, 241, 227))
INK = bytes((27, 27, 22))
CREAM = bytes((250, 246, 232))
WHITE = bytes((255, 253, 246))
RED = bytes((179, 39, 30))
NAVY = bytes((31, 58, 95))
TEAL = bytes((14, 107, 92))
GOLD = bytes((200, 147, 27))
SKY = bytes((127, 168, 201))
GREY = bytes((90, 86, 76))

import math

MX = 24          # page margin
CW = W - 2 * MX  # content width


# ------------------------------------------------------------------ scenes
def _star(c, cx, cy, r, color):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((int(cx + rr * math.cos(ang)), int(cy + rr * math.sin(ang))))
    c.poly(pts, color)


def scene_cyclone(c, x, y, w, h):
    """Spiral storm over a coastline."""
    cx, cy = x + w // 2, y + h // 2 - 8
    for r, col in ((74, NAVY), (58, TEAL), (42, NAVY), (27, TEAL)):
        c.ring(cx, cy, r, 7, col)
    c.disc(cx, cy, 11, WHITE)
    c.ring(cx, cy, 11, 2, NAVY)
    # rain streaks
    for i, rx in enumerate(range(x + 8, x + w - 8, 26)):
        c.line(rx, y + h - 26, rx - 6, y + h - 8, SKY, 3)
    # coastline + houses
    c.poly([(x, y + h - 4), (x + w, y + h - 4), (x + w, y + h - 18),
            (x + w // 2, y + h - 30), (x, y + h - 18)], TEAL)
    for hx in (x + 18, x + w - 52):
        c.rect(hx, y + h - 34, 30, 16, RED)
        c.poly([(hx - 3, y + h - 34), (hx + 15, y + h - 46),
                (hx + 33, y + h - 34)], NAVY)


def scene_fallchart(c, x, y, w, h):
    """Falling bars with a down arrow."""
    base = y + h - 10
    heights = [30, 25, 20, 15, 10]
    bw = 26
    gap = (w - len(heights) * bw) // (len(heights) + 1)
    for i, hh in enumerate(heights):
        bx = x + gap + i * (bw + gap)
        c.rect(bx, base - hh, bw, hh, RED)
    c.line(x + 6, y + 12, x + w - 30, base - 8, INK, 3)
    c.poly([(x + w - 30, base - 8), (x + w - 44, base - 16),
            (x + w - 40, base), (x + w - 30, base - 8)], INK)


def scene_risechart(c, x, y, w, h):
    """Rising bars with an up arrow."""
    base = y + h - 10
    heights = [10, 14, 18, 22, 26]
    bw = 26
    gap = (w - len(heights) * bw) // (len(heights) + 1)
    for i, hh in enumerate(heights):
        bx = x + gap + i * (bw + gap)
        c.rect(bx, base - hh, bw, hh, TEAL)
    c.line(x + 6, base - 6, x + w - 30, y + 6, INK, 3)
    c.poly([(x + w - 30, y + 6), (x + w - 44, y + 4),
            (x + w - 38, y + 20)], INK)


def scene_shield(c, x, y, w, h):
    """A small shield (market protection) sized to its strip."""
    cx, cy = x + w // 2, y + h // 2
    c.poly([(cx - 24, cy - 20), (cx + 24, cy - 20), (cx + 24, cy + 2),
            (cx, cy + 22), (cx - 24, cy + 2)], NAVY)
    c.poly([(cx - 18, cy - 14), (cx + 18, cy - 14), (cx + 18, cy + 1),
            (cx, cy + 16), (cx - 18, cy + 1)], GOLD)
    c.line(cx - 10, cy - 1, cx - 3, cy + 6, NAVY, 4)
    c.line(cx - 3, cy + 6, cx + 12, cy - 12, NAVY, 4)


def scene_eu(c, x, y, w, h):
    """Circle of twelve stars on a navy disc."""
    cx, cy = x + w // 2, y + h // 2
    c.disc(cx, cy, 62, NAVY)
    c.ring(cx, cy, 62, 2, GOLD)
    for i in range(12):
        ang = -math.pi / 2 + i * math.pi / 6
        sx = cx + int(42 * math.cos(ang))
        sy = cy + int(42 * math.sin(ang))
        _star(c, sx, sy, 7, GOLD)


def scene_globe(c, x, y, w, h):
    """A globe with three small figures standing on it."""
    cx, cy = x + w // 2, y + h // 2 + 6
    c.disc(cx, cy, 56, SKY)
    c.ring(cx, cy, 56, 3, NAVY)
    c.ring(cx, cy, 30, 2, NAVY)
    c.line(cx - 56, cy, cx + 56, cy, NAVY, 2)
    c.line(cx, cy - 56, cx, cy + 56, NAVY, 2)
    for i, fx in enumerate((cx - 34, cx, cx + 34)):
        col = (RED, TEAL, GOLD)[i]
        c.disc(fx, cy - 66, 7, col)
        c.rect(fx - 3, cy - 58, 6, 16, col)


# ------------------------------------------------------------------ layout
def card(c, x, y, w, h, accent):
    c.rect(x, y, w, h, WHITE)
    c.rect(x, y, w, 6, accent)
    c.rect(x, y, w, 2, INK)
    c.rect(x, y + h - 2, w, 2, INK)
    c.rect(x, y, 2, h, INK)
    c.rect(x + w - 2, y, 2, h, INK)


def kicker(c, x, y, s):
    c.text(s, x, y, 2, RED)


def heads(c, x, y, lines, scale=3, color=INK):
    for i, ln in enumerate(lines):
        c.text(ln, x, y + i * (7 * scale + 6), scale, color)


def body(c, x, y, lines, scale=2, color=INK):
    for i, ln in enumerate(lines):
        c.text(ln, x, y + i * (7 * scale + 4), scale, color)


def build():
    c = Canvas(W, H, PAPER)

    # ---- masthead
    c.rect(0, 0, W, 150, NAVY)
    c.text_c("THE WORLD IN ONE DAY", W // 2, 16, 4, CREAM)
    c.text_c("FRIDAY 20 NOVEMBER 2026", W // 2, 54, 6, WHITE)
    c.rect(MX, 108, CW, 4, RED)
    c.text_c("NEWS OF FRIDAY 20 NOVEMBER 2026 - AS REPORTED SO FAR TODAY",
             W // 2, 122, 2, CREAM)

    # ---- lead story: cyclone (full width)
    lx, ly, lw, lh = MX, 162, CW, 238
    card(c, lx, ly, lw, lh, RED)
    kicker(c, lx + 20, ly + 18, "INDIA - CYCLONE AKVAN")
    heads(c, lx + 20, ly + 46, ["CYCLONE AKVAN BEARS DOWN",
                                "ON INDIA'S EAST COAST"])
    body(c, lx + 20, ly + 118, ["Landfall due near Gopalpur",
                                "around noon today; 300,000",
                                "evacuated, 423 rescue teams",
                                "Winds 90-100 km/h, gusts 110"])
    scene_cyclone(c, lx + 640, ly + 22, 316, 196)

    # ---- row of three
    pw, ph = 317, 228
    ry = 412
    for i, (kx, heads_l, body_l, scene) in enumerate([
            ("ASIA - MARKETS",
             ["SOFTBANK -16%", "AS TECH SINKS"],
             ["Nikkei -3.7%, Kospi", "below 5,000", "AI sell-off spreads",
              "after Anthropic debut"],
             scene_fallchart),
            ("JAPAN - ECONOMY",
             ["JAPAN PRICES AT", "2026 HIGH"],
             ["Core inflation +2.2%", "in October, a 2026 high",
              "Dec rate rise expected"],
             scene_risechart),
            ("TAIWAN - MARKETS",
             ["TAIWAN CURBS", "SHORT SELLING"],
             ["New limits take", "effect today after", "Taiex lost 5,248 pts",
              "in three days"],
             scene_shield)]):
        px = MX + i * (pw + 12)
        card(c, px, ry, pw, ph, NAVY)
        kicker(c, px + 14, ry + 14, kx)
        heads(c, px + 14, ry + 38, heads_l)
        body(c, px + 14, ry + 104, body_l)
        scene(c, px + 14, ry + 168, pw - 28, 48)

    # ---- row of two
    pw2, ph2 = 476, 228
    ry2 = 652
    # EU envoy
    px = MX
    card(c, px, ry2, pw2, ph2, TEAL)
    kicker(c, px + 14, ry2 + 14, "EUROPE - DIPLOMACY")
    heads(c, px + 14, ry2 + 38, ["EU TO SUMMON", "RUSSIAN ENVOY"])
    body(c, px + 14, ry2 + 104, ["After Thursday's strikes",
                                 "damaged the Austrian and",
                                 "Dutch embassies in Kyiv"])
    scene_eu(c, px + 330, ry2 + 96, 132, 120)
    # Children's Day
    px = MX + pw2 + 24
    card(c, px, ry2, pw2, ph2, GOLD)
    kicker(c, px + 14, ry2 + 14, "WORLD - CHILDREN")
    heads(c, px + 14, ry2 + 38, ["TODAY IS WORLD", "CHILDREN'S DAY"])
    body(c, px + 14, ry2 + 104, ["UN marks the rights of",
                                 "the child; the treaty",
                                 "was adopted 20 Nov 1989"])
    scene_globe(c, px + 330, ry2 + 96, 132, 120)

    # ---- footer: also today
    fy = 892
    c.rect(0, fy, W, H - fy, NAVY)
    c.text("ALSO TODAY", MX + 20, fy + 14, 2, GOLD)
    body(c, MX + 20, fy + 40, ["Fiona the hippo dies at Cincinnati Zoo",
                               "Day 2 of India v New Zealand Test in Wellington",
                               "Trump to brief reporters on his China trip"],
         scale=2, color=CREAM)

    return c


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    canvas = build()
    path = os.path.join(outdir, "entry.png")
    size = save_png(canvas, path)
    print("wrote %s (%d bytes, %dx%d)" % (path, size, W, H))


if __name__ == "__main__":
    main()
