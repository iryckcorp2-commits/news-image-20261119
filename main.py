#!/usr/bin/env python3
"""make.fun bounty entry: Sum up 19 November's world news in one image.

The program draws a 1024x1024 newspaper front page for Thursday
19 November 2026, entirely with code (Python 3.13 standard library
only: no network, no fonts, no image files).  It writes the result to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png when set).

Stories (all first reported on 19 Nov 2026, verified from news search):
  1. GTA VI launches worldwide on PS5 and Xbox Series X|S at midnight
     local time; first reviews 99/100; presales top $1.6B (SensorTower).
  2. Trump, Xi and Putin hold their first three-way summit in
     Shenzhen, on the APEC sidelines.
  3. Ukraine strikes the Crimean Bridge for a third time in a week;
     road traffic halted, rail still running.
  4. The International Court of Justice rules on the Rohingya
     genocide case (Gambia v. Myanmar).
  5. Anthropic's record $81B IPO debut at a $1.5T valuation.

Determinism: fixed palette, fixed layout, fixed zlib level, no clock,
no randomness, no I/O besides the single output file, so two runs
write byte-identical files.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (245, 240, 225)   # cream newsprint
INK = (20, 20, 20)        # near-black ink
RED = (192, 57, 43)       # masthead red
NAVY = (27, 35, 64)       # night skyline
SKY1 = (245, 158, 66)     # sunset orange
SKY2 = (232, 106, 122)    # sunset pink
SKY3 = (123, 75, 148)     # sunset purple
SKY4 = (46, 42, 90)       # dusk purple
SUN = (255, 233, 168)     # sun disc
LIT = (255, 214, 120)     # lit windows
TINT = (232, 224, 204)    # icon box tint
WHITE = (255, 255, 255)
WATER = (20, 27, 51)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph: 7 rows of 5 bits, "#" = pixel on.  All text is uppercased
# by the renderer, so only one case is stored.
_FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}


class Canvas:
    """A plain RGB canvas with a few drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, color):
        r, g, b = color
        self.px[:] = bytes((r, g, b)) * (self.w * self.h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0 = max(x, 0)
        y0 = max(y, 0)
        x1 = min(x + w, self.w)
        y1 = min(y + h, self.h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            span = (x1 - x0) * 3
            self.px[base:base + span] = bytes(color) * (x1 - x0)

    def frame(self, x, y, w, h, color, t=1):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def hline(self, x, y, length, color, t=1):
        self.rect(x, y, length, t, color)

    def vline(self, x, y, length, color, t=1):
        self.rect(x, y, t, length, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        """Bresenham line with a square brush of side t."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    # ------------------------------------------------------------ text
    def text_width(self, s, scale):
        s = s.upper()
        return max(0, len(s) * 6 * scale - scale)

    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = _FONT.get(ch, _FONT["?"])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, color):
        return self.text(cx - self.text_width(s, scale) // 2, y, s, scale, color)

    def text_right(self, rx, y, s, scale, color):
        return self.text(rx - self.text_width(s, scale), y, s, scale, color)

    def wrap(self, s, scale, max_w):
        """Greedy word wrap; returns a list of lines."""
        words = s.upper().split(" ")
        lines = []
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if self.text_width(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def encode_png(canvas):
    """Encode the canvas as a deterministic PNG (RGB, filter 0)."""
    raw = bytearray()
    row_bytes = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * row_bytes:(y + 1) * row_bytes]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)

    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data +
                struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))

    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            chunk(b"IEND", b""))


# ---------------------------------------------------------------- layout
def draw_masthead(cv):
    cv.frame(8, 8, W - 16, H - 16, INK, 3)
    cv.frame(16, 16, W - 32, H - 32, INK, 1)
    cv.text_center(W // 2, 34, "THE WORLD TODAY", 7, INK)
    cv.rect(32, 132, W - 64, 6, RED)
    cv.text(32, 152, "THURSDAY, 19 NOVEMBER 2026", 3, INK)
    cv.text_right(W - 32, 152, "FIVE STORIES - ONE DAY", 3, RED)
    cv.hline(32, 182, W - 64, INK, 2)


def draw_hero(cv):
    """Vice City at sunset: gradient sky, sun, skyline, water."""
    x0, y0, x1, y1 = 32, 196, W - 32, 446
    # Sky bands.
    cv.rect(x0, y0, x1 - x0, 62, SKY1)
    cv.rect(x0, y0 + 62, x1 - x0, 62, SKY2)
    cv.rect(x0, y0 + 124, x1 - x0, 63, SKY3)
    cv.rect(x0, y0 + 187, x1 - x0, 63, SKY4)
    # Sun with a soft ring.
    cv.disc(700, 322, 62, (255, 205, 130))
    cv.disc(700, 322, 52, SUN)
    # Skyline: fixed building silhouettes with lit windows.
    buildings = [
        (32, 150, 92), (124, 120, 70), (194, 170, 108), (302, 132, 74),
        (376, 178, 96), (472, 140, 82), (554, 168, 104), (658, 128, 72),
        (730, 172, 100), (830, 138, 78), (908, 164, 84),
    ]
    for bx, bw, bh in buildings:
        top = y1 - 44 - bh
        cv.rect(bx, top, bw, bh + 44, NAVY)
        # Antenna on two of the towers.
        if bx in (194, 658):
            cv.vline(bx + bw // 2, top - 22, 22, NAVY, 3)
            cv.disc(bx + bw // 2, top - 24, 3, RED)
        # Lit windows: fixed deterministic pattern.
        for wy in range(top + 10, y1 - 50, 16):
            for wx in range(bx + 8, bx + bw - 8, 16):
                if (wx * 7 + wy * 13) % 5 == 0:
                    cv.rect(wx, wy, 7, 9, LIT)
    # Three small birds in the sunset sky.
    for bx, by in ((300, 240), (340, 262), (880, 246)):
        cv.line(bx - 10, by, bx, by + 6, NAVY, 3)
        cv.line(bx, by + 6, bx + 10, by, NAVY, 3)
    # Water strip with sunset reflections.
    cv.rect(x0, y1 - 44, x1 - x0, 44, WATER)
    for i, (rx, rw, col) in enumerate(
            [(90, 70, SKY1), (210, 46, SKY2), (330, 88, SKY1),
             (470, 54, SKY2), (600, 76, SKY1), (730, 48, SKY2),
             (840, 92, SKY1)]):
        cv.rect(rx, y1 - 34 + (i % 3) * 10, rw, 4, col)
    cv.frame(x0, y0, x1 - x0, y1 - y0, INK, 2)
    # Headline band.
    cv.rect(x0, y1, x1 - x0, 108, INK)
    cv.text_center(W // 2, y1 + 14, "GTA VI IS OUT", 6, WHITE)
    cv.text_center(W // 2, y1 + 62,
                   "ROCKSTAR'S GRAND THEFT AUTO VI LAUNCHES ON PS5 AND XBOX",
                   2, WHITE)
    cv.text_center(W // 2, y1 + 84,
                   "FIRST REVIEWS 99/100 - PRESALES TOP $1.6B",
                   2, LIT)


# ------------------------------------------------------------ story icons
def icon_summit(cv, x, y, s):
    """Three flags over a table: three leaders, one summit."""
    for i, col in enumerate((RED, (46, 95, 163), (46, 125, 50))):
        px = x + 14 + i * 30
        cv.vline(px, y + 18, 52, INK, 3)
        for r in range(14):
            cv.rect(px + 3, y + 18 + r, 20 - r // 2, 2, col)
    cv.rect(x + 8, y + 74, 94, 6, INK)
    cv.rect(x + 14, y + 80, 6, 18, INK)
    cv.rect(x + 90, y + 80, 6, 18, INK)


def icon_bridge(cv, x, y, s):
    """A bridge deck split by a gap, blast star above the gap."""
    cv.rect(x + 8, y + 62, 40, 8, INK)
    cv.rect(x + 62, y + 62, 40, 8, INK)
    cv.rect(x + 14, y + 62, 8, 36, INK)
    cv.rect(x + 88, y + 62, 8, 36, INK)
    cv.line(x + 18, y + 62, x + 48, y + 36, INK, 3)
    cv.line(x + 92, y + 62, x + 62, y + 36, INK, 3)
    cx, cy = x + 55, y + 22
    for dx, dy in ((-12, 0), (12, 0), (0, -12), (0, 12),
                   (-9, -9), (9, -9), (-9, 9), (9, 9)):
        cv.line(cx, cy, cx + dx, cy + dy, (255, 176, 32), 4)
    cv.disc(cx, cy, 5, (255, 176, 32))


def icon_court(cv, x, y, s):
    """A courthouse: pediment, columns, steps."""
    cv.line(x + 55, y + 12, x + 12, y + 36, INK, 3)
    cv.line(x + 55, y + 12, x + 98, y + 36, INK, 3)
    cv.rect(x + 10, y + 36, 90, 5, INK)
    for px in (18, 42, 66, 88):
        cv.rect(x + px, y + 44, 7, 34, INK)
    cv.rect(x + 10, y + 80, 90, 5, INK)
    cv.rect(x + 6, y + 88, 98, 5, INK)


def icon_chart(cv, x, y, s):
    """Rising bars with an upward arrow: a record debut."""
    for i, bh in enumerate((26, 42, 58)):
        cv.rect(x + 16 + i * 26, y + 88 - bh, 18, bh, (46, 95, 163))
    cv.line(x + 16, y + 88 - 62, x + 94, y + 14, RED, 4)
    cv.line(x + 94, y + 14, x + 78, y + 16, RED, 4)
    cv.line(x + 94, y + 14, x + 92, y + 30, RED, 4)


def draw_story(cv, x, y, w, h, kicker, headline, sub, icon):
    cv.rect(x, y, w, 3, RED)
    cv.rect(x, y + 10, 110, 110, TINT)
    cv.frame(x, y + 10, 110, 110, INK, 1)
    icon(cv, x, y + 10, 110)
    tx = x + 124
    tw = w - 124
    cv.text(tx, y + 12, kicker, 2, RED)
    lines = cv.wrap(headline, 3, tw)
    ly = y + 36
    for line in lines[:3]:
        cv.text(tx, ly, line, 3, INK)
        ly += 22
    for line in cv.wrap(sub, 2, tw)[:2]:
        cv.text(tx, ly + 2, line, 2, INK)
        ly += 15


def draw_grid(cv):
    cv.text(32, 566, "THE REST OF THE DAY", 3, INK)
    cv.hline(32, 594, W - 64, INK, 2)
    stories = [
        ("SHENZHEN", "TRUMP, XI, PUTIN IN FIRST THREE-WAY SUMMIT",
         "APEC SIDELINES; ARMS CONTROL AND UKRAINE ON THE TABLE",
         icon_summit),
        ("UKRAINE", "KYIV HITS CRIMEAN BRIDGE A THIRD TIME",
         "ROAD TRAFFIC HALTED; RAIL STILL RUNNING",
         icon_bridge),
        ("THE HAGUE", "WORLD COURT RULES ON ROHINGYA CASE",
         "GAMBIA'S CASE OVER THE 2017 CRACKDOWN",
         icon_court),
        ("MARKETS", "ANTHROPIC'S $81B IPO SETS RECORD",
         "AI LAB LISTS AT A $1.5T VALUATION",
         icon_chart),
    ]
    positions = [(32, 606), (528, 606), (32, 796), (528, 796)]
    for (sx, sy), (kicker, headline, sub, icon) in zip(positions, stories):
        draw_story(cv, sx, sy, 464, 178, kicker, headline, sub, icon)


def draw_footer(cv):
    cv.hline(32, 978, W - 64, INK, 2)
    cv.text_center(W // 2, 988,
                   "SOURCES: USA TODAY, LE MONDE, NYT, BBC - 19 NOV 2026",
                   2, INK)


def build():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_hero(cv)
    draw_grid(cv)
    draw_footer(cv)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
