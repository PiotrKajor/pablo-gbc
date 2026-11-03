"""Pablo GBC - procedural art library.
Everything the game draws (tiles, sprites, font, title) is defined here.
Pixel values are 2bpp indices 0..3; colours come from palettes.
"""
import random, math, subprocess
from PIL import Image, ImageDraw, ImageFont


def c555(rgb):
    r, g, b = rgb
    return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)


class Cv:
    def __init__(self, w, h, fill=0):
        self.w, self.h = w, h
        self.im = Image.new('P', (w, h), fill)
        self.d = ImageDraw.Draw(self.im)

    def get(self, x, y):
        return self.im.getpixel((x, y)) if 0 <= x < self.w and 0 <= y < self.h else 0

    def set(self, x, y, v):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.im.putpixel((x, y), v)

    @staticmethod
    def art(lines):
        h = len(lines)
        w = max(len(l) for l in lines)
        for l in lines:
            assert len(l) == w, (len(l), w, l)
        c = Cv(w, h)
        for y, l in enumerate(lines):
            for x, ch in enumerate(l):
                c.set(x, y, 0 if ch in '. ' else int(ch))
        return c

    def blit(self, src, x, y, key=True):
        for yy in range(src.h):
            for xx in range(src.w):
                v = src.get(xx, yy)
                if v or not key:
                    self.set(x + xx, y + yy, v)

    def flipx(self):
        c = Cv(self.w, self.h)
        c.im = self.im.transpose(Image.FLIP_LEFT_RIGHT)
        c.d = ImageDraw.Draw(c.im)
        return c

    def sub(self, x, y, w, h):
        c = Cv(w, h)
        for yy in range(h):
            for xx in range(w):
                c.set(xx, yy, self.get(x + xx, y + yy))
        return c

    def rows(self):
        return [[self.get(x, y) for x in range(self.w)] for y in range(self.h)]


def tile_bytes(c, x0=0, y0=0):
    out = []
    for y in range(8):
        lo = hi = 0
        for x in range(8):
            v = c.get(x0 + x, y0 + y)
            lo |= (v & 1) << (7 - x)
            hi |= ((v >> 1) & 1) << (7 - x)
        out += [lo, hi]
    return out


def spr_tiles(c):
    """8x16-mode order: column major, top tile then bottom tile per 16px chunk."""
    out = []
    for cx in range(c.w // 8):
        for cy in range(c.h // 16):
            out += tile_bytes(c, cx * 8, cy * 16)
            out += tile_bytes(c, cx * 8, cy * 16 + 8)
    return out


# ------------------------------------------------------------------ palettes
def themes():
    """Returns dict theme -> 8 BG palettes (list of 4 RGB tuples)."""
    T = {}
    spec = {
        0: dict(bg=(6, 16, 20),
                rock=[(22, 52, 58), (50, 100, 104), (128, 190, 180)],
                moss=[(20, 60, 40), (60, 130, 70), (170, 230, 110)],
                glow=[(90, 70, 20), (210, 170, 50), (255, 245, 160)],
                back=[(12, 30, 36), (18, 44, 50), (28, 62, 68)]),
        1: dict(bg=(6, 18, 12),
                rock=[(30, 52, 40), (60, 96, 70), (140, 180, 120)],
                moss=[(24, 70, 32), (70, 150, 56), (190, 240, 110)],
                glow=[(90, 70, 20), (210, 170, 50), (255, 245, 160)],
                back=[(12, 34, 26), (18, 48, 36), (26, 62, 46)]),
        2: dict(bg=(14, 10, 24),
                rock=[(44, 36, 70), (86, 72, 128), (170, 150, 210)],
                moss=[(40, 60, 80), (80, 120, 140), (170, 210, 220)],
                glow=[(70, 50, 110), (150, 110, 210), (230, 210, 255)],
                back=[(24, 18, 42), (34, 26, 58), (46, 36, 78)]),
        3: dict(bg=(8, 14, 8),
                rock=[(36, 46, 30), (76, 100, 54), (170, 200, 110)],
                moss=[(30, 70, 30), (80, 150, 50), (200, 245, 100)],
                glow=[(100, 44, 20), (214, 104, 40), (255, 206, 120)],
                back=[(18, 30, 18), (26, 44, 24), (36, 60, 32)]),
    }
    for t, s in spec.items():
        bg = s['bg']
        T[t] = [
            [bg] + s['rock'],
            [bg] + s['moss'],
            [bg] + s['glow'],
            [bg, (60, 76, 84), (150, 176, 184), (244, 251, 244)],      # 3 text/UI
            [bg, (90, 26, 36), (184, 58, 74), (240, 192, 160)],        # 4 hazard
            [bg, (58, 42, 26), (138, 106, 58), (224, 200, 144)],       # 5 brass/wood
            [bg] + s['back'],                                          # 6 back wall
            [bg, (40, 74, 122), (122, 176, 240), (232, 248, 255)],     # 7 soul/crystal
        ]
    return T


OBJ_PALS = [
    [(0, 0, 0), (244, 251, 244), (14, 16, 22), (122, 193, 67)],      # 0 Pablo
    [(0, 0, 0), (58, 74, 82), (157, 180, 184), (244, 251, 244)],     # 1 FX nail
    [(0, 0, 0), (42, 20, 8), (176, 96, 42), (240, 176, 112)],        # 2 crawlid
    [(0, 0, 0), (16, 24, 40), (74, 106, 154), (192, 216, 240)],      # 3 vengefly
    [(0, 0, 0), (12, 40, 20), (63, 143, 58), (214, 245, 110)],       # 4 boss
    [(0, 0, 0), (32, 24, 40), (138, 106, 154), (240, 224, 240)],     # 5 NPC
    [(0, 0, 0), (26, 42, 80), (74, 122, 224), (240, 248, 255)],      # 6 items
    [(0, 0, 0), (255, 255, 255), (255, 255, 255), (255, 255, 255)],  # 7 hit flash
]

# ------------------------------------------------------------------ font
GLYPHS = {}


def _g(ch, *rows):
    GLYPHS[ch] = rows


_g('A', ".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#")
_g('B', "####.", "#...#", "#...#", "####.", "#...#", "#...#", "####.")
_g('C', ".###.", "#...#", "#....", "#....", "#....", "#...#", ".###.")
_g('D', "####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####.")
_g('E', "#####", "#....", "#....", "####.", "#....", "#....", "#####")
_g('F', "#####", "#....", "#....", "####.", "#....", "#....", "#....")
_g('G', ".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###.")
_g('H', "#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#")
_g('I', ".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###.")
_g('J', "..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##..")
_g('K', "#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#")
_g('L', "#....", "#....", "#....", "#....", "#....", "#....", "#####")
_g('M', "#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#")
_g('N', "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#")
_g('O', ".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###.")
_g('P', "####.", "#...#", "#...#", "####.", "#....", "#....", "#....")
_g('Q', ".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#")
_g('R', "####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#")
_g('S', ".####", "#....", "#....", ".###.", "....#", "....#", "####.")
_g('T', "#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..")
_g('U', "#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###.")
_g('V', "#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#..")
_g('W', "#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#")
_g('X', "#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#")
_g('Y', "#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..")
_g('Z', "#####", "....#", "...#.", "..#..", ".#...", "#....", "#####")
_g('0', ".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###.")
_g('1', "..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###.")
_g('2', ".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####")
_g('3', "####.", "....#", "....#", ".###.", "....#", "....#", "####.")
_g('4', "...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#.")
_g('5', "#####", "#....", "####.", "....#", "....#", "#...#", ".###.")
_g('6', ".###.", "#....", "#....", "####.", "#...#", "#...#", ".###.")
_g('7', "#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#...")
_g('8', ".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###.")
_g('9', ".###.", "#...#", "#...#", ".####", "....#", "....#", ".###.")
_g(' ', *["....."] * 7)
_g('.', ".....", ".....", ".....", ".....", ".....", ".....", "..#..")
_g(',', ".....", ".....", ".....", ".....", "..#..", "..#..", ".#...")
_g('!', "..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#..")
_g('?', ".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#..")
_g('-', ".....", ".....", ".....", ".###.", ".....", ".....", ".....")
_g(':', ".....", "..#..", ".....", ".....", ".....", "..#..", ".....")
_g("'", "..#..", "..#..", ".#...", ".....", ".....", ".....", ".....")
_g('"', ".#.#.", ".#.#.", ".....", ".....", ".....", ".....", ".....")
_g('>', "#....", "##...", "###..", "####.", "###..", "##...", "#....")
_g('/', "....#", "....#", "...#.", "..#..", ".#...", "#....", "#....")
_g('*', ".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", ".....")
_g('+', ".....", "..#..", "..#..", "#####", "..#..", "..#..", ".....")
_g('(', "...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#.")
_g(')', ".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#...")
_g('_', ".....", ".....", ".....", ".....", ".....", ".....", "#####")
_g('=', ".....", "#####", ".....", "#####", ".....", ".....", ".....")


def glyph_canvas(ch, color=3):
    ch = ch if ch in GLYPHS else ' '
    c = Cv(8, 8)
    for y, row in enumerate(GLYPHS[ch]):
        for x, p in enumerate(row):
            if p == '#':
                c.set(x + 1, y, color)
    return c


def draw_text(cv, x, y, text, color=3, spacing=6):
    for i, ch in enumerate(text):
        g = glyph_canvas(ch.upper(), color)
        cv.blit(g, x + i * spacing - 1, y)


FONT_FIRST = 32
FONT_COUNT = 64  # ASCII 32..95

# ------------------------------------------------------------------ BG tiles
class TileSet:
    def __init__(self):
        self.tiles = []      # canvases
        self.names = {}
        self.pal = []
        self.flags = []

    def add(self, name, cv, pal, flags=0):
        idx = len(self.tiles)
        self.tiles.append(cv)
        self.pal.append(pal)
        self.flags.append(flags)
        if name:
            self.names[name] = idx
        return idx

    def __getitem__(self, n):
        return self.names[n]


F_SOLID, F_ONEWAY, F_HAZARD = 1, 2, 4

U, D, L, R = 1, 2, 4, 8


def rock_tile(mask, var, rng):
    c = Cv(8, 8, 1)
    # speckle
    for _ in range(9):
        c.set(rng.randrange(8), rng.randrange(8), rng.choice([0, 0, 2]))
    # strata lines
    ry = rng.randrange(2, 6)
    for x in range(8):
        if rng.random() < 0.55:
            c.set(x, ry, 0)
    if mask & U:
        for x in range(8):
            c.set(x, 0, 3)
            c.set(x, 1, 2 if rng.random() < 0.8 else 1)
        for x in range(8):
            if rng.random() < 0.25:
                c.set(x, 0, 2)
    if mask & D:
        for x in range(8):
            c.set(x, 7, 0)
            if rng.random() < 0.6:
                c.set(x, 6, 0)
    if mask & L:
        for y in range(8):
            c.set(0, y, 2 if not (mask & U and y < 2) else 3)
    if mask & R:
        for y in range(8):
            c.set(7, y, 0)
    return c


def moss_tile(mask, rng):
    """tile whose top is exposed: green top w/ drips. palette 1."""
    c = Cv(8, 8, 1)
    for _ in range(9):
        c.set(rng.randrange(8), rng.randrange(8), rng.choice([0, 0, 2]))
    for x in range(8):
        c.set(x, 0, 3)
        c.set(x, 1, 2 if rng.random() < 0.3 else 3)
        c.set(x, 2, 2 if rng.random() < 0.7 else 1)
        if rng.random() < 0.35:
            c.set(x, 3, 2)
    for x in range(0, 8, 3):
        c.set((x + rng.randrange(2)) % 8, 4, 2)
    if mask & D:
        for x in range(8):
            c.set(x, 7, 0)
    if mask & L:
        for y in range(8):
            c.set(0, y, 2)
    if mask & R:
        for y in range(8):
            c.set(7, y, 0)
    return c


def build_tileset():
    ts = TileSet()
    rng = random.Random(1337)
    # 0..2 empty (back wall variants), pal 6
    ts.add('empty', Cv(8, 8, 0), 6)
    e1 = Cv(8, 8, 0)
    for (x, y) in [(2, 2), (5, 6), (6, 1)]:
        e1.set(x, y, 1)
    ts.add('empty1', e1, 6)
    e2 = Cv.art(["........", "..1.....", "..11....", "...1.1..", ".....11.", "......1.", "........", "........"])
    ts.add('empty2', e2, 6)
    # faint ruin bricks (b)
    bb = Cv.art(["22222222", "1.......", "1.......", "22222222", "....1...", "....1...", "22222222", "1......."])
    # make faint: indices 1/2 only (no 3)
    ts.add('backbrick', bb, 6)
    # rock autotile
    for mask in range(16):
        ts.add('rock%d' % mask, rock_tile(mask, 0, rng), 0, F_SOLID)
    for v in range(1, 3):
        ts.add('rockin%d' % v, rock_tile(0, v, rng), 0, F_SOLID)
    for mask in range(16):
        if mask & U:
            ts.add('moss%d' % mask, moss_tile(mask, rng), 1, F_SOLID)
    # one-way platform (plank/ledge)
    ow = Cv.art(["33333333", "22222222", "11.11.11", "........", "........", "........", "........", "........"])
    ts.add('oneway', ow, 5, F_ONEWAY)
    # spikes
    sp = Cv.art(["...3....", "..323...", "..323.3.", ".3223.2.", ".32232.2", "322322.2", "3222222.", "22222222"])
    sp = Cv.art(["...3..3.", "...23.23", "..223.23", "..2223.2", ".2.2223.", ".2.22222", "22222222", "11111111"])
    ts.add('spike', sp, 4, F_HAZARD)
    # bench halves
    bl = Cv.art(["........", "........", "........", "........", "33333333", "22222222", ".2....2.", ".1....1."])
    br = bl.flipx()
    ts.add('benchL', Cv.art(["........", "........", "........", "..333333", "33222222", "22111111", ".2....2.", ".1....1."]), 5)
    ts.add('benchR', Cv.art(["........", "........", "........", "333333..", "222222 3".replace(' ', '3'), "11111122", ".2....2.", ".1....1."]), 5)
    # tablet
    tb = Cv.art(["..2222..", ".233332.", ".23..32.", ".23332..", ".23..32.", ".233332.", ".211112.", ".111111."])
    ts.add('tablet', Cv.art(["..2222..", ".233332.", ".232232.", ".233332.", ".232332.", ".233332.", ".222222.", ".111111."]), 3)
    # deco
    ts.add('stal', Cv.art(["22222222", "12333221", ".123321.", ".122321.", "..1221..", "..1221..", "...12...", "...1...."]), 0)
    ts.add('stag', Cv.art(["....1...", "...12...", "..1221..", "..1221..", ".123321.", ".123321.", "12333221", "22222222"]), 0)
    ts.add('vine', Cv.art(["..2.....", "..23....", "...2....", "..22....", "..2.3...", "...2....", "..22....", "..2....."]), 1)
    ts.add('vine2', Cv.art(["...2....", "..22....", "..2.....", "...23...", "...2....", "..22....", "..3.....", "..2....."]), 1)
    ts.add('chain', Cv.art(["...22...", "...2.2..", "...22...", "...2.2..", "...22...", "...2.2..", "...22...", "...2.2.."]), 5)
    ts.add('lamp', Cv.art(["..2222..", ".233332.", "23333332", "23333332", "23333332", ".233332.", "..2222..", "...22..."]), 2)
    ts.add('crystal', Cv.art(["........", "...3....", "..323.3.", "..323.3.", ".32232.2", ".32232.2", "3222222.", "22222222"]), 7)
    ts.add('mush', Cv.art(["........", "........", "..2222..", ".233332.", "23333332", "..1221..", "...22...", "..1221.."]), 2)
    ts.add('pillar', Cv.art(["11222211", "11222211", "11222211", "11222211", "11222211", "11222211", "11222211", "11222211"]), 6)
    ts.add('pillarT', Cv.art(["22222222", "21111112", "11222211", "11222211", "11222211", "11222211", "11222211", "11222211"]), 6)
    # soul/HUD
    ts.add('hudbg', Cv(8, 8, 0), 3)
    mk = Cv.art(["........", "..3333..", ".333333.", ".30330.3".replace('.3', '33')[:8], ".333333.", ".333333.", "..3333..", "...33..."])
    mk = Cv.art(["........", ".333333.", "33333333", "33033033", "33333333", "33333333", ".333333.", "..3333.."])
    # slanted eyes (angry)
    mk = Cv.art(["........", "..3333..", ".333333.", ".330033.", ".303303.", ".333333.", "..3333..", "...33..."])
    ts.add('mask_full', mk, 3)
    me = Cv.art(["........", "..2222..", ".211112.", ".221122.", ".212212.", ".211112.", "..2222..", "...22..."])
    ts.add('mask_empty', me, 3)
    for part in range(3):          # 0 left cap, 1 mid, 2 right cap
        for fill in range(9):
            c = Cv(8, 8, 0)
            for x in range(8):
                c.set(x, 0, 2)
                c.set(x, 7, 2)
                for y in range(1, 7):
                    c.set(x, y, 3 if x < fill else 1)
            if part == 0:
                for y in range(8):
                    c.set(0, y, 2)
            if part == 2:
                for y in range(8):
                    c.set(7, y, 2)
            ts.add('soul%d_%d' % (part, fill), c, 7)
    # window box
    def box(name, lines):
        ts.add(name, Cv.art(lines), 3)
    box('b_tl', ["........", "........", "..333333", ".3222222", ".3211111", ".3210000", ".3210000", ".3210000"])
    box('b_t', ["........", "........", "33333333", "22222222", "11111111", "00000000", "00000000", "00000000"])
    box('b_tr', ["........", "........", "333333..", "2222223.", "1111123.", "0000123.", "0000123.", "0000123."])
    box('b_l', [".3210000"] * 8)
    box('b_r', ["0000123."] * 8)
    box('b_bl', [".3210000", ".3210000", ".3210000", ".3211111", ".3222222", "..333333", "........", "........"])
    box('b_b', ["00000000", "00000000", "00000000", "11111111", "22222222", "33333333", "........", "........"])
    box('b_br', ["0000123.", "0000123.", "0000123.", "1111123.", "2222223.", "333333..", "........", "........"])
    box('b_fill', ["00000000"] * 8)
    # arrows / misc
    ts.add('arrow_up', Cv.art(["........", "...33...", "..3333..", ".333333.", "...33...", "...33...", "........", "........"]), 3)
    # font
    ts.names['font'] = len(ts.tiles)
    for i in range(FONT_COUNT):
        ts.add(None, glyph_canvas(chr(FONT_FIRST + i)), 3)
    assert len(ts.tiles) <= 256, len(ts.tiles)
    return ts


# ------------------------------------------------------------------ sprites
HEAD = [
    "....11111111....",
    "..111111111111..",
    ".11111111111111.",
    ".11221111112211.",
    ".11122111122111.",
    ".11111111111111.",
    "..111111111111..",
    "...1111111111...",
]


def pablo_frame(head_dy, body, nail=True, lean=0, extra=None, eyes='angry'):
    c = Cv(16, 16)
    hc = Cv.art(HEAD)
    if eyes == 'closed':
        for x in range(16):
            for y in (3, 4):
                if hc.get(x, y) == 2:
                    hc.set(x, y, 1)
        for x in (3, 4, 5, 10, 11, 12):
            hc.set(x, 4, 2)
    if eyes == 'hurt':
        for x in range(16):
            for y in (3, 4):
                if hc.get(x, y) == 2:
                    hc.set(x, y, 1)
        for (x, y) in [(3, 3), (5, 3), (4, 4), (3, 5), (5, 5), (10, 3), (12, 3), (11, 4), (10, 5), (12, 5)]:
            hc.set(x, y, 2)
    bc = Cv.art(body)
    if nail:
        # nail strapped to the back (left side)
        for y in range(2 + head_dy, 13 + head_dy):
            c.set(0, y, 2)
        c.set(0, 1 + head_dy, 1)
        c.set(1, 2 + head_dy, 2)
        c.set(1, 12 + head_dy, 2)
    c.blit(bc, lean, 8 + max(0, head_dy - 0) if False else 8)
    c.blit(hc, lean, head_dy)
    if extra:
        extra(c)
    return c


def build_pablo():
    F = []
    idleA = ["...3333333333...", "..33333333333...", "..33322333333...", "...333223333....",
             "....3322333.....", ".....222222.....", ".....22..22.....", "....222..222...."]
    idleB = ["...3333333333...", "..33333333333...", "..3332233333....", "...33322333.....",
             "....33223.......", ".....222222.....", ".....22..22.....", "....222..222...."]
    runs = [
        ["...3333333333...", "..33333333333...", "..33322333333...", "...333223333....",
         "....3322333.....", ".....22222......", "....222..22.....", "...222....222..."],
        ["...3333333333...", "..33333333333...", "..33322333333...", "...333223333....",
         "....3322333.....", ".....22222......", ".....222.22.....", ".....22...22...."],
        ["...3333333333...", "..33333333333...", "..33322333333...", "...333223333....",
         "....3322333.....", ".....22222......", "....22..222.....", "...222...222...."],
        ["...3333333333...", "..33333333333...", "..33322333333...", "...333223333....",
         "....3322333.....", ".....22222......", ".....22.222.....", "....222...22...."],
    ]
    jump = ["..333333333333..", ".33333333333333.", "..33322333333...", "...333223333....",
            "....3322333.....", ".....22222......", "....222.222.....", "....22...22....."]
    fall = ["...3333333333...", "..33333333333333", "..33322333333...", "..3333223333....",
            "...333223333....", ".....22222......", "....22...22.....", "...222...222...."]
    attack = ["...3333333333...", "..3333333333332.", "..333223333322..", "...3332233322...",
              "....33223332....", ".....22222......", ".....22.222.....", "....222..222...."]
    dash = ["....33333333....", "..333333333333..", "3333322333333...", ".33333223333....",
            "..333322333.....", ".....222222.....", "....222.222.....", "...22.....22...."]
    hurt = ["...3333333333...", "..33333333333...", "..33322333333...", "...333223333....",
            "....3322333.....", ".....222222.....", "....222..22.....", "...222....22...."]
    focus = ["...3333333333...", "..33333333333...", "..33322333333...", "...333223333....",
             "....3322333.....", "....2222222.....", "....2222222.....", "...222222222...."]
    F.append(pablo_frame(0, idleA))
    F.append(pablo_frame(1, idleB))
    for r in runs:
        F.append(pablo_frame(0, r, lean=0))
    F.append(pablo_frame(0, jump))
    F.append(pablo_frame(0, fall))
    F.append(pablo_frame(0, attack))
    F.append(pablo_frame(0, dash, lean=1))
    F.append(pablo_frame(1, hurt, eyes='hurt'))
    F.append(pablo_frame(3, focus, eyes='closed'))
    return F


def build_slash():
    F = []
    for i in range(3):
        c = Cv(16, 16)
        rx = 6 + i * 2
        ry = 7 + i
        cx = 3 - i
        c.d.ellipse([cx - rx, 8 - ry, cx + rx, 8 + ry], fill=3)
        c.d.ellipse([cx - rx + 2, 8 - ry + 2, cx + rx - 1 - 1, 8 + ry - 2], fill=0)
        # cut left part (behind player)
        for y in range(16):
            for x in range(0, 4 - i):
                c.set(x, y, 0)
        # tail shading
        for y in range(16):
            for x in range(16):
                if c.get(x, y) == 3 and (x + y) % 3 == 0 and i > 0:
                    c.set(x, y, 2)
        F.append(c)
    return F


def build_crawlid():
    F = []
    for f in range(2):
        a = ["................", "................", "................", "................",
             "................", "................", "................", ".....11111111...",
             "...1122222222211", "..1233222222222.", ".123332222222221", ".12333222222221.",
             ".1233322222221..", "..11111111111...", "...1.1..1.1.1...", "..1..1..1..1.1.."]
        if f == 1:
            a[14] = "....1.1..1.1.1.."
            a[15] = "...1..1..1..1.1."
        c = Cv.art(a)
        # face (front = right side): eyes
        c.set(13, 9, 3)
        c.set(12, 10, 1)
        F.append(c)
    return F


def build_fly():
    F = []
    for f in range(2):
        c = Cv(16, 16)
        # body
        c.d.ellipse([4, 6, 11, 14], fill=2)
        c.d.ellipse([4, 6, 11, 14], outline=1)
        c.set(6, 9, 3)
        c.set(9, 9, 3)
        c.set(6, 10, 1)
        c.set(9, 10, 1)
        c.set(7, 12, 1)
        c.set(8, 12, 1)
        # wings
        if f == 0:
            c.d.polygon([(4, 7), (0, 1), (6, 3), (7, 6)], fill=3, outline=1)
            c.d.polygon([(11, 7), (15, 1), (9, 3), (8, 6)], fill=3, outline=1)
        else:
            c.d.polygon([(4, 8), (0, 8), (1, 13), (5, 10)], fill=3, outline=1)
            c.d.polygon([(11, 8), (15, 8), (14, 13), (10, 10)], fill=3, outline=1)
        F.append(c)
    return F


def build_npc():
    """4 NPC kinds x 2 frames: elder, wanderer, archivist, gatekeeper."""
    def base(kind, f):
        c = Cv(16, 16)
        # robe
        c.d.polygon([(4, 15), (6, 6), (9, 6), (11, 15)], fill=2, outline=1)
        c.d.rectangle([5, 14, 10, 15], fill=1)
        # head
        c.d.ellipse([4, 1, 11, 8], fill=3, outline=1)
        c.set(6, 4, 1)
        c.set(9, 4, 1)
        if kind == 0:   # elder: antennae + cane
            c.set(5, 0, 1); c.set(4, 0, 1); c.set(10, 0, 1); c.set(11, 0, 1)
            for y in range(6, 16):
                c.set(13, y, 1)
            c.set(12, 6, 1); c.set(14, 6, 1)
            c.set(6, 6, 3); c.set(7, 6, 3)
        elif kind == 1:  # wanderer: hat
            c.d.polygon([(2, 3), (8, -2), (13, 3)], fill=1)
            c.set(8, 1, 2)
            c.d.line([(7, 9), (8, 9)], fill=1)
        elif kind == 2:  # archivist: glasses + book
            c.d.ellipse([4, 3, 7, 6], outline=1)
            c.d.ellipse([8, 3, 11, 6], outline=1)
            c.d.rectangle([2, 9, 6, 13], fill=3, outline=1)
            c.d.line([(4, 9), (4, 13)], fill=1)
        else:            # gatekeeper: tall helm + spear
            c.d.rectangle([4, 0, 11, 2], fill=1)
            c.set(5, 1, 3); c.set(10, 1, 3)
            for y in range(0, 16):
                c.set(14, y, 3)
            c.set(13, 1, 3); c.set(15, 1, 3)
        if f == 1:  # idle bob
            c2 = Cv(16, 16)
            c2.blit(c, 0, 1)
            return c2
        return c
    return [base(k, f) for k in range(4) for f in range(2)]


def build_boss():
    """Moss Warden 32x32, faces LEFT. frames: idleA idleB windup charge air."""
    F = []

    def frame(dy, squash, lean, eyes_bright, legs):
        c = Cv(32, 32)
        top = 6 + dy + squash
        # legs
        for lx in (7, 12, 18, 23):
            c.d.rectangle([lx, 24 + legs[0] if lx < 15 else 24 + legs[1], lx + 3, 31], fill=1)
        # shell dome
        c.d.ellipse([3 + lean, top, 30 + lean, 29], fill=2, outline=1)
        # moss tufts on shell
        rng = random.Random(7)
        for _ in range(40):
            x = rng.randrange(6, 28)
            y = rng.randrange(top + 2, 22)
            if c.get(x + lean, y) == 2:
                c.set(x + lean, y, 3 if rng.random() < 0.5 else 1)
        for tx in (7, 12, 17, 22, 26):
            ty = top + 3 + (tx * 7) % 5
            c.d.polygon([(tx + lean, ty), (tx + 2 + lean, ty - 4), (tx + 4 + lean, ty)], fill=3, outline=1)
        # face plate (left)
        c.d.ellipse([2 + lean, top + 6, 17 + lean, 28], fill=1)
        ec = 3 if eyes_bright else 2
        c.d.polygon([(5 + lean, top + 12), (9 + lean, top + 14), (8 + lean, top + 17), (5 + lean, top + 16)], fill=ec)
        c.d.polygon([(14 + lean, top + 12), (10 + lean, top + 14), (11 + lean, top + 17), (14 + lean, top + 16)], fill=ec)
        # horns
        c.d.polygon([(4 + lean, top + 3), (0 + lean, top - 3), (7 + lean, top + 1)], fill=3, outline=1)
        c.d.polygon([(14 + lean, top + 1), (15 + lean, top - 5), (18 + lean, top + 1)], fill=3, outline=1)
        # mouth teeth
        for x in range(5, 15, 3):
            c.set(x + lean, top + 20, 2)
        return c
    F.append(frame(0, 0, 0, True, (0, 0)))
    F.append(frame(1, 0, 0, True, (0, 0)))
    F.append(frame(0, 3, 0, True, (0, 0)))      # windup (crouch)
    F.append(frame(0, 1, -1, True, (0, 0)))     # charge
    F.append(frame(-2, 0, 0, True, (-4, -4)))   # air
    return F


def build_misc():
    shock = [Cv.art(["...33...", "..3223..", "..3223..", ".322223.", ".322223.", ".322223.", "32222223", "32222223",
                     "32222223", "32222223", "32222223", ".322223.", ".322223.", "..3223..", "..3223..", "...33..."]),
             Cv.art(["....3...", "...323..", "..3223..", "..3223..", ".322223.", ".322223.", ".322223.", "32222223",
                     "32222223", "322 2223".replace(' ', '2'), "32222223", ".322223.", ".322223.", "..3223..", "...323..", "....3..."])]
    cloak = Cv.art(["................", "..3..........3..", ".333........333.", "3.3333....3333.3",
                    "3.333333333333.3", ".333322332233 3.".replace(' ', '3'), "..33322222233...", "..3322222233....",
                    "...32222223.....", "...3222222......", "....322223......", "....322223......",
                    ".....3223.......", ".....3223.......", "......33........", "................"])
    heart = []
    for f in range(2):
        c = Cv(16, 16)
        r = 4 + f
        c.d.ellipse([8 - r, 8 - r, 8 + r, 8 + r], fill=2)
        c.d.ellipse([8 - r + 2, 8 - r + 2, 8 + r - 2, 8 + r - 2], fill=3)
        for (dx, dy) in [(0, -7), (0, 7), (-7, 0), (7, 0), (5, 5), (-5, -5), (5, -5), (-5, 5)]:
            c.set(8 + dx, 8 + dy, 3 if f == 0 else 2)
        heart.append(c)
    spark = []
    for f in range(3):
        c = Cv(8, 16)
        s = f + 1
        for d in range(-s, s + 1):
            c.set(4 + d, 12, 3)
            c.set(4, 12 + d, 3)
        c.set(4, 12, 3)
        spark.append(c)
    spore = []
    for f in range(2):
        c = Cv(8, 16)
        c.set(3, 2 + f, 3)
        c.set(4, 2 + f, 3)
        c.set(3, 3 + f, 2)
        c.set(4, 3 + f, 2)
        spore.append(c)
    # arrow bubble "UP" marker above NPCs
    up = Cv.art(["...33...", "..3333..", ".333333.", "...33...", "...33...", "...33...", "........", "........"])
    upc = Cv(8, 16)
    upc.blit(up, 0, 8)
    return shock, cloak, heart, spark, spore, upc


# ------------------------------------------------------------------ sprite sheet
class SprSheet:
    def __init__(self):
        self.data = []   # list of tile byte-lists (each tile 16 bytes)
        self.names = {}
        self.frames = []  # (name, cv, pal)

    def add(self, name, cv, pal=0):
        base = len(self.data)
        t = spr_tiles(cv)
        for i in range(0, len(t), 16):
            self.data.append(t[i:i + 16])
        self.names[name] = base
        self.frames.append((name, cv, pal))
        return base


def build_sprites():
    ss = SprSheet()
    for i, f in enumerate(build_pablo()):
        ss.add('PABLO%d' % i, f, 0)
    for i, f in enumerate(build_slash()):
        ss.add('SLASH%d' % i, f, 1)
    for i, f in enumerate(build_crawlid()):
        ss.add('CRAWL%d' % i, f, 2)
    for i, f in enumerate(build_fly()):
        ss.add('FLY%d' % i, f, 3)
    for i, f in enumerate(build_npc()):
        ss.add('NPC%d' % i, f, 5)
    for i, f in enumerate(build_boss()):
        ss.add('BOSS%d' % i, f, 4)
    shock, cloak, heart, spark, spore, upc = build_misc()
    for i, f in enumerate(shock):
        ss.add('SHOCK%d' % i, f, 4)
    ss.add('CLOAK', cloak, 6)
    for i, f in enumerate(heart):
        ss.add('HEART%d' % i, f, 4)
    for i, f in enumerate(spark):
        ss.add('SPARK%d' % i, f, 1)
    for i, f in enumerate(spore):
        ss.add('SPORE%d' % i, f, 4)
    ss.add('UPMARK', upc, 1)
    ar = Cv(8, 16)
    ar.blit(Cv.art(["3.......", "33......", "333.....", "3333....", "333.....", "33......", "3......."]), 0, 5)
    ss.add('ARROWR', ar, 1)
    assert len(ss.data) <= 256, len(ss.data)
    return ss


# ------------------------------------------------------------------ title
def title_image():
    W, H = 160, 144
    cv = Cv(W, H)
    # tile-row palettes: choose per 8px band (index into title palettes)
    # background gradient by dithering
    bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

    def level(x, y):
        # glow centred around (80, 96)
        dx = (x - 80) / 80.0
        dy = (y - 100) / 70.0
        g = max(0.0, 1.0 - math.sqrt(dx * dx + dy * dy))
        base = 0.25 + 1.5 * g
        return min(2.2, base)

    for y in range(H):
        for x in range(W):
            lv = level(x, y)
            b = (bayer[y & 3][x & 3] + 0.5) / 16.0
            v = int(lv + b)
            cv.set(x, y, min(v, 2))
    # spores
    rng = random.Random(5)
    for _ in range(30):
        x, y = rng.randrange(4, 156), rng.randrange(40, 120)
        cv.set(x, y, 3)
        if rng.random() < 0.4:
            cv.set(x + 1, y, 2 if cv.get(x + 1, y) < 3 else 3)
    # cliff at bottom
    cl = [(0, 144), (0, 126), (14, 122), (26, 128), (40, 118), (52, 124), (70, 114), (92, 114), (108, 122),
          (124, 116), (140, 124), (160, 120), (160, 144)]
    cv.d.polygon(cl, fill=0)
    cv.d.line(cl[1:-1], fill=1)
    for _ in range(0):   # bez kropek na klifie: oszczędza kafle tytułu (limit 256)
        x = rng.randrange(0, 160)
        ytop = 120
        y = rng.randrange(ytop, 144)
        if cv.get(x, y) == 0:
            cv.set(x, y, 1)
    kn = Cv(W, H, 9)
    # a ledge for the knight to stand on
    kn.d.polygon([(54, 112), (106, 112), (112, 144), (48, 144)], fill=0)
    kn.d.line([(54, 112), (106, 112)], fill=2)
    kn.d.line([(55, 113), (105, 113)], fill=1)
    # --- topór: długie drzewce ukośnie za plecami, duża płaska głowica z ząbkiem (jak na okładce)
    def ax(u, v, c=(48, 74), d=(0.885, 0.467)):   # u wzdłuż drzewca, v w poprzek
        return (round(c[0] + u * d[0] - v * d[1]), round(c[1] + u * d[1] + v * d[0]))
    kn.d.line([ax(-4, 0), (113, 104)], fill=0, width=4)          # drzewce (obrys)
    kn.d.line([ax(-4, 0), (112, 104)], fill=2, width=2)
    kn.d.polygon([(112, 101), (119, 106), (111, 106)], fill=3, outline=0)   # grot na końcu drzewca
    kn.d.polygon([ax(-10, -26), ax(9, -26), ax(9, 20), ax(-10, 20), ax(-10, 8), ax(-1, 2), ax(-10, -4)], fill=2, outline=0)
    kn.d.line([ax(-6, -22), ax(-6, -6)], fill=3)                  # odblask na ostrzu
    kn.d.line([ax(6, -22), ax(6, 16)], fill=1)                    # cień grzbietu
    # cape
    kn.d.polygon([(62, 84), (98, 84), (106, 106), (92, 102), (86, 112), (74, 104), (66, 112), (60, 100)], fill=2, outline=0)
    for (x, y) in [(74, 90), (84, 92), (90, 98), (70, 98), (80, 102)]:
        kn.d.line([(x, y), (x + 3, y + 3)], fill=1)
    # body
    kn.d.rectangle([74, 98, 88, 112], fill=0)
    # head
    kn.d.ellipse([54, 53, 111, 86], fill=3, outline=0)   # szeroka, plaska elipsa jak na artach
    # eyes (slanted)
    kn.d.polygon([(64, 64), (79, 69), (77, 74), (63, 69)], fill=0)
    kn.d.polygon([(100, 64), (85, 69), (87, 74), (101, 69)], fill=0)
    # shading under head
    kn.d.arc([54, 53, 111, 86], 25, 155, fill=2)
    for yy in range(H):
        for xx in range(W):
            v = kn.get(xx, yy)
            if v != 9:
                cv.set(xx, yy + 18, v)
    # title text (rendered with serif font)
    try:
        path = subprocess.check_output(['fc-match', 'serif:bold', '-f', '%{file}']).decode()
        font = ImageFont.truetype(path, 30)
        tim = Image.new('L', (W, 40), 0)
        td = ImageDraw.Draw(tim)
        bb = td.textbbox((0, 0), "PABLO", font=font)
        tw = bb[2] - bb[0]
        td.text(((W - tw) // 2 - bb[0], 2), "PABLO", font=font, fill=255)
        for y in range(40):
            for x in range(W):
                if tim.getpixel((x, y)) > 110:
                    # outline first
                    for ox in (-1, 0, 1):
                        for oy in (-1, 0, 1):
                            if 0 <= y + oy + 2 < H and cv.get(x + ox, y + oy + 2) != 3:
                                cv.set(x + ox, y + oy + 2, 0)
        for y in range(40):
            for x in range(W):
                if tim.getpixel((x, y)) > 110:
                    cv.set(x, y + 2, 3)
    except Exception as e:
        print('title font failed', e)
    # ornaments
    for y0 in (6, 40):
        pass
    cv.d.line([(20, 2), (140, 2)], fill=3)
    cv.d.line([(30, 4), (130, 4)], fill=2)
    cv.d.polygon([(80, 40), (84, 44), (80, 48), (76, 44)], fill=3)
    cv.d.line([(24, 44), (72, 44)], fill=3)
    cv.d.line([(88, 44), (136, 44)], fill=3)
    # subtitle
    draw_text(cv, 34, 51, "A  HOLLOW  TALE", 3)
    draw_text(cv, 62, 129, "NEW GAME", 3)
    draw_text(cv, 62, 137, "CONTINUE", 3)
    return cv


TITLE_ROW_PAL = [0, 0, 1, 1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6, 6, 6, 7]


def title_palettes():
    P = [
        [(4, 8, 8), (10, 28, 28), (24, 70, 60), (244, 251, 244)],      # 0 night + title
        [(4, 8, 8), (12, 40, 36), (30, 98, 80), (244, 251, 244)],      # 1
        [(4, 10, 8), (16, 56, 44), (50, 140, 90), (230, 255, 220)],    # 2
        [(4, 10, 8), (20, 70, 50), (70, 170, 90), (248, 253, 248)],    # 3 head/glow
        [(6, 12, 8), (24, 80, 52), (96, 190, 80), (244, 252, 240)],    # 4 knight body/cape
        [(6, 12, 8), (22, 64, 40), (80, 160, 60), (226, 244, 210)],    # 5
        [(6, 10, 8), (28, 40, 32), (90, 110, 70), (200, 220, 140)],    # 6 cliff
        [(6, 10, 8), (60, 70, 70), (150, 170, 150), (244, 251, 244)],  # 7 press start
    ]
    return P


def tiles_from_canvas(cv):
    tiles, mapping, uniq = [], [], {}
    for ty in range(cv.h // 8):
        for tx in range(cv.w // 8):
            b = tuple(tile_bytes(cv, tx * 8, ty * 8))
            if b not in uniq:
                uniq[b] = len(tiles)
                tiles.append(list(b))
            mapping.append(uniq[b])
    return tiles, mapping
