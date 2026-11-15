"""Every word's picture (docs/art.md 「詞的圖」): 120 x 120, one glossy vinyl toy each, the thing big
and in the middle. The ids are the words in design/bopomofo.py (assets/bopomofo.json); art_test.dart
checks every word has its picture.
"""
import math
import sys

sys.dont_write_bytecode = True

import kit  # noqa: E402
from kit import Shape, arc, circle, ellipse, poly, rect, rrect, smooth, star, heart  # noqa: E402

OUT = kit.ART / "words"
S = 120
P = {}


def pic(fn):
    P[fn.__name__.rstrip("_")] = fn
    return fn


def line(*pts):
    return Shape([("M",) + pts[0]] + [("L",) + p for p in pts[1:]])


def curve(p0, c1, c2, p1):
    return Shape([("M",) + p0, ("C",) + c1 + c2 + p1])


# ================================================================ people
def person(c, *, hair="short", hair_col="#3B2E2A", shirt=kit.BLUE, scale=1.0, glasses=False, old=False, mustache=False,
           open_=True, legs=kit.NAVY, dress=False, arms_up=False, cx=60):
    """A Playmobil-like figure: big round head, small body. scale 1 fills the picture."""
    s = scale
    top = 120 - 112 * s
    hx, hy, hr = cx, top + 34 * s, 26 * s
    by = hy + hr * .9
    # Body.
    if dress:
        body = Shape([("M", cx - 15 * s, by), ("L", cx + 15 * s, by), ("L", cx + 28 * s, by + 46 * s), ("L", cx - 28 * s, by + 46 * s), ("Z",)])
        c.vinyl(rrect(cx - 13 * s, by + 40 * s, 9 * s, 14 * s, 4 * s) + rrect(cx + 4 * s, by + 40 * s, 9 * s, 14 * s, 4 * s), kit.SKIN, rim=1.6, hl=None)
        c.vinyl(body, shirt, rim=2.2, hl=(.3, .15))
    else:
        c.vinyl(rrect(cx - 15 * s, by + 30 * s, 13 * s, 26 * s, 6 * s) + rrect(cx + 2 * s, by + 30 * s, 13 * s, 26 * s, 6 * s), legs, rim=2, hl=None)
        c.vinyl(rrect(cx - 20 * s, by, 40 * s, 36 * s, 12 * s), shirt, rim=2.2, hl=(.25, .2))
    # Arms.
    if arms_up:
        for d in (-1, 1):
            c.vinyl(rrect(cx + d * 24 * s - 5 * s, by - 26 * s, 10 * s, 30 * s, 5 * s).rotate(d * 22, cx + d * 20 * s, by + 4 * s), shirt, rim=1.8, hl=None)
            c.vinyl(circle(cx + d * 33 * s, by - 26 * s, 6 * s), kit.SKIN, rim=1.6, hl=None)
    else:
        for d in (-1, 1):
            c.vinyl(rrect(cx + d * 22 * s - 5 * s, by + 3 * s, 10 * s, 26 * s, 5 * s).rotate(-d * 12, cx + d * 22 * s, by + 3 * s), shirt, rim=1.8, hl=None, shadow=False)
            c.vinyl(circle(cx + d * 26 * s, by + 30 * s, 6 * s), kit.SKIN, rim=1.6, hl=None, shadow=False)
    # Hair behind.
    if hair == "long":
        c.vinyl(rrect(hx - hr * 1.12, hy - hr * .7, hr * 2.24, hr * 2.2, hr), hair_col, rim=2.2, hl=None)
    if hair == "pigtails":
        for d in (-1, 1):
            c.vinyl(ellipse(hx + d * hr * 1.15, hy + hr * .25, hr * .38, hr * .55), hair_col, rim=2, hl=None)
    # Head.
    c.vinyl(circle(hx, hy, hr), kit.SKIN, rim=2.2, hl=(.25, .32), hl_size=.7)
    # Hair on top.
    if hair in ("short", "long", "pigtails", "spiky"):
        cap = Shape([("M", hx - hr * 1.02, hy + hr * .05), ("C", hx - hr * 1.05, hy - hr * 1.25, hx + hr * 1.05, hy - hr * 1.25, hx + hr * 1.02, hy + hr * .05),
                     ("C", hx + hr * .6, hy - hr * .45, hx - hr * .2, hy - hr * .35, hx - hr * 1.02, hy + hr * .05), ("Z",)])
        if hair == "spiky":
            cap = cap + poly([(hx - hr * .6, hy - hr * .7), (hx - hr * .35, hy - hr * 1.35), (hx - hr * .05, hy - hr * .8), (hx + hr * .3, hy - hr * 1.4),
                              (hx + hr * .5, hy - hr * .75)])
        c.vinyl(cap, hair_col, rim=2, hl=(.3, .3), hl_size=.6, shadow=False)
    elif hair == "bun":
        c.vinyl(circle(hx, hy - hr * 1.1, hr * .42), hair_col, rim=2, hl=None, shadow=False)
        cap = Shape([("M", hx - hr * 1.02, hy + hr * .05), ("C", hx - hr * 1.05, hy - hr * 1.25, hx + hr * 1.05, hy - hr * 1.25, hx + hr * 1.02, hy + hr * .05),
                     ("C", hx + hr * .5, hy - hr * .55, hx - hr * .5, hy - hr * .55, hx - hr * 1.02, hy + hr * .05), ("Z",)])
        c.vinyl(cap, hair_col, rim=2, hl=(.3, .3), hl_size=.6, shadow=False)
    elif hair == "bald":
        for d in (-1, 1):
            c.vinyl(ellipse(hx + d * hr * .92, hy - hr * .05, hr * .22, hr * .4), hair_col, rim=1.6, hl=None, shadow=False)
    # Face.
    c.eyes(hx, hy + hr * .12, hr * .72, r=hr * .1)
    c.cheeks(hx, hy + hr * .42, hr * 1.2, hr * .14)
    if mustache:
        c.vinyl(ellipse(hx - hr * .2, hy + hr * .5, hr * .24, hr * .1) + ellipse(hx + hr * .2, hy + hr * .5, hr * .24, hr * .1), hair_col, rim=1, hl=None, shadow=False)
    c.smile(hx, hy + hr * .5 + (hr * .14 if mustache else 0), hr * .42, open_=open_)
    if glasses:
        for d in (-1, 1):
            c.stroke(circle(hx + d * hr * .36, hy + hr * .12, hr * .24), kit.INK, 1.8)
        c.stroke(line((hx - hr * .12, hy + hr * .1), (hx + hr * .12, hy + hr * .1)), kit.INK, 1.6)
    if old:
        c.stroke(arc(hx - hr * .36, hy - hr * .16, hr * .2, 200, 340), kit.dk(kit.SKIN, .3), 1.2)
        c.stroke(arc(hx + hr * .36, hy - hr * .16, hr * .2, 200, 340), kit.dk(kit.SKIN, .3), 1.2)


@pic
def baba(c):
    person(c, hair="short", shirt=kit.BLUE, glasses=True)


@pic
def mama(c):
    person(c, hair="long", hair_col="#5A3A2E", shirt=kit.PINK, dress=True)


@pic
def didi(c):
    person(c, hair="short", hair_col="#2E2440", shirt=kit.GREEN, scale=.82, legs=kit.BLUE)


@pic
def gege(c):
    person(c, hair="spiky", hair_col="#2E2440", shirt=kit.ORANGE, scale=.94, legs=kit.NAVY)


@pic
def jiejie(c):
    person(c, hair="pigtails", hair_col="#3B2E2A", shirt=kit.PURPLE, dress=True, scale=.9)


@pic
def grandma(c):
    person(c, hair="bun", hair_col="#C9C6D2", shirt="#E85D6F", glasses=True, old=True, dress=True)


@pic
def yeye(c):
    person(c, hair="short", hair_col="#D7D3DF", shirt=kit.BROWN, mustache=True, old=True, open_=False)


@pic
def mouth(c):
    c.vinyl(circle(60, 60, 50), kit.SKIN, rim=2.4, hl=(.25, .2), hl_size=.6)
    c.eyes(60, 40, 34, r=4.5)
    c.cheeks(60, 56, 62, 7)
    lips = Shape([("M", 26, 68), ("C", 40, 58, 52, 64, 60, 62), ("C", 68, 64, 80, 58, 94, 68), ("C", 84, 96, 36, 96, 26, 68), ("Z",)])
    c.vinyl(lips, "#E8455E", rim=2.2, hl=(.3, .2), hl_size=.6, shadow=False)
    c.flat(Shape([("M", 34, 70), ("C", 48, 66, 72, 66, 86, 70), ("C", 78, 86, 42, 86, 34, 70), ("Z",)]), "#7A1E33")
    c.flat(rrect(42, 69, 36, 7, 3), kit.WHITE)
    c.flat(ellipse(60, 82, 12, 5), "#FF8FA3")


@pic
def ear(c):
    e = smooth([(48, 12), (78, 16), (94, 40), (88, 70), (70, 92), (52, 108), (36, 100), (40, 80), (30, 60), (30, 34)], .9)
    c.vinyl(e, kit.SKIN, rim=2.6, hl=(.4, .18), hl_size=.7)
    inner = curve((50, 30), (72, 24), (84, 50), (66, 70)) + curve((66, 70), (56, 80), (52, 88), (46, 92))
    c.stroke(curve((48, 32), (74, 22), (86, 52), (66, 70)), kit.dk(kit.SKIN, .35), 5)
    c.stroke(curve((66, 70), (56, 80), (54, 90), (46, 94)), kit.dk(kit.SKIN, .35), 5)
    c.stroke(curve((54, 48), (64, 42), (70, 54), (60, 62)), kit.dk(kit.SKIN, .25), 4)
    del inner


@pic
def hand(c):
    palm = rrect(34, 52, 52, 54, 22)
    fingers = Shape()
    for x, top, a in ((38, 22, -10), (51, 12, -3), (64, 12, 3), (77, 22, 10)):
        fingers = fingers + rrect(x - 6, top, 12, 50, 6).rotate(a, x, 60)
    thumb = rrect(14, 58, 34, 13, 6.5).rotate(-35, 40, 70)
    c.vinyl(palm + fingers + thumb, kit.SKIN, rim=2.4, hl=(.25, .3), hl_size=.6)
    c.stroke(arc(60, 82, 12, 30, 150), kit.dk(kit.SKIN, .3), 1.8)


# ================================================================ animals
def animal_head(c, x, y, r, col, *, ears=None, ear_col=None, inner=kit.PINK, muzzle=None, nose=kit.INK, whiskers=False, open_=True):
    if ears == "round":
        for d in (-1, 1):
            c.vinyl(circle(x + d * r * .72, y - r * .72, r * .38), col, rim=2, hl=None)
            c.flat(circle(x + d * r * .72, y - r * .72, r * .2), inner)
    elif ears == "long":
        for d in (-1, 1):
            e = ellipse(x + d * r * .42, y - r * 1.3, r * .26, r * .7).rotate(d * 10, x + d * r * .42, y - r * .7)
            c.vinyl(e, col, rim=2, hl=None)
            c.flat(ellipse(x + d * r * .42, y - r * 1.25, r * .12, r * .5).rotate(d * 10, x + d * r * .42, y - r * .7), inner)
    elif ears == "pointy":
        for d in (-1, 1):
            c.vinyl(poly([(x + d * r * .9, y - r * .25), (x + d * r * .62, y - r * 1.15), (x + d * r * .1, y - r * .75)]), col, rim=2, hl=None)
            c.flat(poly([(x + d * r * .72, y - r * .38), (x + d * r * .6, y - r * .9), (x + d * r * .3, y - r * .68)]), inner)
    elif ears == "floppy":
        for d in (-1, 1):
            c.vinyl(ellipse(x + d * r * .92, y + r * .05, r * .3, r * .62).rotate(-d * 15, x + d * r * .92, y), ear_col or kit.dk(col, .25), rim=2, hl=None)
    c.vinyl(circle(x, y, r), col, rim=2.2, hl=(.25, .25), hl_size=.7)
    if muzzle:
        c.vinyl(ellipse(x, y + r * .38, r * .42, r * .3), muzzle, rim=1.2, hl=None, shadow=False, round_=False)
    c.eyes(x, y - r * .05, r * .74, r=r * .11)
    c.cheeks(x, y + r * .3, r * 1.3, r * .14)
    c.flat(ellipse(x, y + r * .26, r * .12, r * .09), nose)
    c.smile(x, y + r * .44, r * .3)
    if whiskers:
        for d in (-1, 1):
            for k in (-1, 1):
                c.stroke(line((x + d * r * .5, y + r * .32 + k * r * .06), (x + d * r * .95, y + r * .28 + k * r * .16)), kit.dk(col, .5), 1.3)


def body(c, x, y, rx, ry, col, **kw):
    c.vinyl(ellipse(x, y, rx, ry), col, rim=2.2, **kw)


@pic
def rabbit(c):
    body(c, 60, 92, 26, 20, "#FFF6F2", hl=(.3, .2))
    for d in (-1, 1):
        c.vinyl(ellipse(60 + d * 14, 110, 9, 5), "#FFF6F2", rim=1.6, hl=None, shadow=False)
    animal_head(c, 60, 56, 25, "#FFF6F2", ears="long", nose=kit.ROSE)


@pic
def mouse(c):
    c.stroke(curve((84, 96), (108, 92), (110, 70), (98, 62)), kit.PINK, 4)
    body(c, 60, 92, 28, 20, kit.GREY, hl=(.3, .2))
    animal_head(c, 58, 58, 24, kit.GREY, ears="round", inner=kit.PINK, nose=kit.ROSE, whiskers=True)


@pic
def pigeon(c):
    b = smooth([(24, 76), (40, 56), (70, 52), (98, 62), (110, 76), (92, 94), (58, 100), (34, 94)], .9)
    c.vinyl(b, "#9FA9C9", rim=2.2, hl=(.3, .2))
    c.vinyl(smooth([(48, 68), (74, 64), (96, 74), (78, 88), (54, 84)], .9), "#7E88AD", rim=1.8, hl=None, shadow=False)
    c.vinyl(circle(38, 50, 18), "#9FA9C9", rim=2.2, hl=(.3, .25), hl_size=.6)
    c.flat(ellipse(40, 66, 12, 6), "#7FC8A8", op=.8)
    c.vinyl(poly([(20, 48), (8, 53), (21, 56)]), kit.ORANGE, rim=1.4, hl=None, shadow=False)
    c.eyes(34, 46, 1, r=3.2)
    for x in (56, 70):
        c.stroke(line((x, 98), (x, 110), (x - 5, 113)), kit.ORANGE, 3)


@pic
def dino(c):
    b = smooth([(20, 96), (30, 72), (52, 62), (66, 40), (78, 22), (100, 20), (108, 34), (94, 44), (86, 60), (90, 84), (104, 102), (80, 104), (50, 104)], .7)
    plates = Shape()
    for x, y, a in ((40, 64, -40), (54, 56, -30), (66, 42, -20)):
        plates = plates + poly([(x - 6, y + 4), (x, y - 10), (x + 6, y + 4)]).rotate(a, x, y)
    c.vinyl(plates, kit.ORANGE, rim=1.8, hl=None)
    c.vinyl(b, kit.GREEN, rim=2.4, hl=(.6, .12), hl_size=.6)
    c.flat(smooth([(56, 74), (78, 66), (84, 86), (66, 98)], .9), "#C8F0B0", op=.8)
    c.eyes(96, 30, 1, r=3.6)
    c.smile(103, 37, 6)
    for x in (44, 76):
        c.vinyl(rrect(x - 7, 96, 14, 14, 6), kit.GREEN, rim=1.8, hl=None, shadow=False)


@pic
def chicken(c):
    body(c, 62, 80, 34, 28, kit.WHITE, hl=(.3, .2), rim_col="#B8B0C6")
    c.vinyl(smooth([(66, 76), (92, 70), (98, 86), (76, 92)], .9), "#F1ECF6", rim=1.6, hl=None, shadow=False, rim_col="#B8B0C6")
    c.vinyl(circle(42, 46, 20), kit.WHITE, rim=2.2, hl=(.3, .25), hl_size=.6, rim_col="#B8B0C6")
    c.vinyl(circle(38, 24, 6) + circle(46, 22, 6) + circle(53, 27, 5), kit.RED, rim=1.6, hl=None, shadow=False)
    c.vinyl(poly([(24, 46), (12, 51), (25, 55)]), kit.ORANGE, rim=1.4, hl=None, shadow=False)
    c.vinyl(ellipse(27, 60, 4, 6), kit.RED, rim=1.2, hl=None, shadow=False)
    c.eyes(38, 42, 1, r=3.2)
    for x in (54, 70):
        c.stroke(line((x, 106), (x, 114), (x - 5, 116)), kit.ORANGE, 3)


@pic
def rooster(c):
    tail = Shape()
    for a, col in ((-40, "#2E8B6E"), (-10, "#3F5FB8"), (20, "#2E8B6E")):
        tail = ellipse(82, 56, 9, 23).rotate(a + 12, 78, 78)
        c.vinyl(tail, col, rim=1.8, hl=None)
    body(c, 62, 82, 32, 26, "#E8613D", hl=(.3, .2))
    c.vinyl(circle(40, 48, 19), "#F5A23B", rim=2.2, hl=(.3, .25), hl_size=.6)
    c.vinyl(circle(34, 26, 6) + circle(42, 23, 7) + circle(50, 27, 6), kit.RED, rim=1.6, hl=None, shadow=False)
    # Beak open: 喔喔喔!
    c.vinyl(poly([(23, 44), (8, 42), (22, 49)]), kit.YELLOW, rim=1.4, hl=None, shadow=False)
    c.vinyl(poly([(23, 51), (10, 56), (24, 55)]), kit.YELLOW, rim=1.4, hl=None, shadow=False)
    c.vinyl(ellipse(26, 62, 4, 6), kit.RED, rim=1.2, hl=None, shadow=False)
    c.eyes(37, 44, 1, r=3.2)
    for x in (54, 70):
        c.stroke(line((x, 106), (x, 114), (x - 5, 116)), kit.ORANGE, 3)


@pic
def pig(c):
    body(c, 62, 84, 38, 26, "#FFB3C7", hl=(.3, .2))
    for x in (40, 56, 72, 86):
        c.vinyl(rrect(x - 6, 100, 12, 14, 5), "#FFB3C7", rim=1.6, hl=None, shadow=False)
    c.stroke(curve((98, 76), (110, 70), (104, 62), (100, 68)), "#E8849F", 3)
    animal_head(c, 46, 56, 26, "#FFB3C7", ears="pointy", inner="#F27C9E", nose="#FFB3C7")
    c.vinyl(ellipse(46, 66, 10, 7), "#FF9AB6", rim=1.6, hl=None, shadow=False, round_=False)
    c.flat(ellipse(42, 66, 2, 3), "#B8476A")
    c.flat(ellipse(50, 66, 2, 3), "#B8476A")


@pic
def lion(c):
    mane = Shape()
    for i in range(12):
        a = math.radians(i * 30)
        mane = mane + circle(60 + 34 * math.cos(a), 54 + 34 * math.sin(a), 13)
    c.vinyl(mane + circle(60, 54, 34), "#E2802E", rim=2.4, hl=(.25, .2), hl_size=.6)
    animal_head(c, 60, 56, 27, kit.GOLD, ears="round", inner="#E2802E", muzzle="#FFF0C8", whiskers=False)
    c.vinyl(rrect(44, 92, 32, 22, 10), kit.GOLD, rim=2, hl=None, shadow=False)


@pic
def squirrel(c):
    tail = smooth([(70, 104), (96, 98), (110, 70), (104, 36), (86, 24), (76, 40), (90, 60), (84, 84)], .9)
    c.vinyl(tail, "#C9773F", rim=2.4, hl=(.5, .15), hl_size=.6)
    c.flat(smooth([(86, 40), (96, 50), (98, 72), (90, 86), (88, 64)], .9), "#E9A06A", op=.7)
    body(c, 54, 88, 22, 22, "#D88A4E", hl=(.3, .2))
    c.vinyl(ellipse(54, 92, 11, 14), "#FFE2C2", rim=1.4, hl=None, shadow=False, round_=False)
    c.vinyl(ellipse(54, 96, 9, 7), "#8A5A33", rim=1.4, hl=(.3, .3), shadow=False)
    animal_head(c, 50, 52, 21, "#D88A4E", ears="pointy", inner="#FFC7A0", nose=kit.INK)


@pic
def goose(c):
    b = smooth([(22, 80), (40, 66), (80, 66), (104, 70), (100, 96), (64, 106), (32, 98)], .9)
    neck = rrect(30, 26, 18, 56, 9)
    c.vinyl(b + neck + circle(40, 26, 15), kit.WHITE, rim=2.4, hl=(.25, .1), hl_size=.6, rim_col="#B8B0C6")
    c.vinyl(smooth([(56, 76), (84, 72), (96, 84), (72, 92)], .9), "#F2EEF7", rim=1.6, hl=None, shadow=False, rim_col="#B8B0C6")
    c.vinyl(poly([(26, 24), (6, 30), (26, 34)]), kit.ORANGE, rim=1.6, hl=None, shadow=False)
    c.vinyl(circle(28, 20, 4), kit.ORANGE, rim=1.2, hl=None, shadow=False)
    c.eyes(42, 22, 1, r=3.2)
    for x in (52, 72):
        c.stroke(line((x, 104), (x, 112)), kit.ORANGE, 3.5)
        c.vinyl(poly([(x - 7, 116), (x, 110), (x + 7, 116)]), kit.ORANGE, rim=1.2, hl=None, shadow=False)


@pic
def cat(c):
    c.stroke(curve((84, 100), (110, 98), (108, 66), (96, 66)), "#E98A3B", 7)
    body(c, 60, 92, 28, 20, kit.ORANGE, hl=(.3, .2))
    c.vinyl(ellipse(60, 96, 13, 11), "#FFE8CF", rim=1.4, hl=None, shadow=False, round_=False)
    animal_head(c, 60, 54, 27, kit.ORANGE, ears="pointy", inner=kit.PINK, muzzle="#FFE8CF", nose=kit.ROSE, whiskers=True)
    for x in (48, 56):
        c.stroke(line((x + 14, 32), (x + 16, 38)), kit.dk(kit.ORANGE, .4), 2)


@pic
def dog(c):
    c.stroke(curve((84, 96), (100, 92), (104, 80), (106, 70)), kit.TAN, 7)
    body(c, 60, 92, 28, 20, kit.TAN, hl=(.3, .2))
    animal_head(c, 60, 54, 27, kit.TAN, ears="floppy", ear_col=kit.BROWN, muzzle="#FFF0DC", nose=kit.INK)
    c.vinyl(ellipse(60, 80, 16, 4), kit.RED, rim=1.4, hl=None, shadow=False)
    c.vinyl(circle(60, 86, 4), kit.GOLD, rim=1.2, hl=None, shadow=False)


@pic
def turtle(c):
    c.vinyl(circle(98, 74, 12) + ellipse(30, 96, 9, 7) + ellipse(88, 98, 9, 7) + poly([(14, 80), (4, 84), (16, 88)]), "#8FD67E", rim=2, hl=None)
    shell = Shape([("M", 18, 86), ("C", 18, 40, 92, 36, 94, 86), ("Z",)])
    c.vinyl(shell, "#3FA36A", rim=2.6, hl=(.3, .2))
    for x, y in ((40, 66), (56, 58), (72, 66), (56, 76)):
        c.flat(poly([(x - 8, y), (x - 4, y - 7), (x + 4, y - 7), (x + 8, y), (x + 4, y + 7), (x - 4, y + 7)]), "#7FD08A", op=.8)
    c.flat(rrect(16, 82, 80, 8, 4), "#2E7F52")
    c.eyes(101, 71, 1, r=2.8)
    c.smile(104, 78, 5)


@pic
def fish(c):
    tail = poly([(20, 60), (4, 40), (8, 60), (4, 80)])
    c.vinyl(tail, kit.ORANGE, rim=2, hl=None)
    b = smooth([(18, 60), (44, 34), (84, 36), (110, 58), (86, 84), (44, 86)], .8)
    c.vinyl(b, "#4AA8F0", rim=2.4, hl=(.35, .18))
    c.flat(smooth([(40, 70), (70, 66), (96, 66), (80, 80), (50, 80)], .9), "#BFE6FF", op=.8)
    c.vinyl(poly([(56, 36), (66, 22), (76, 38)]), kit.ORANGE, rim=1.6, hl=None, shadow=False)
    c.eyes(90, 52, 1, r=4)
    c.smile(100, 64, 6)
    for k, (x, y, r) in enumerate(((112, 30, 4), (104, 18, 3))):
        c.vinyl(circle(x, y, r), "#D8F2FF", rim=1.2, hl=None, shadow=False)


# ================================================================ food
@pic
def apple(c):
    a = Shape([("M", 60, 36), ("C", 76, 22, 108, 30, 106, 62), ("C", 104, 92, 80, 110, 60, 102), ("C", 40, 110, 16, 92, 14, 62),
               ("C", 12, 30, 44, 22, 60, 36), ("Z",)])
    c.vinyl(a, "#EE3B47", rim=2.6, hl=(.25, .22))
    c.stroke(curve((60, 36), (60, 26), (62, 18), (66, 12)), "#7A4A2A", 4.5)
    c.vinyl(ellipse(78, 22, 13, 6).rotate(-25, 78, 22), kit.LEAF, rim=1.6, hl=None, shadow=False)


@pic
def melon(c):
    slice_ = Shape([("M", 8, 50), ("L", 112, 50), ("C", 108, 96, 12, 96, 8, 50), ("Z",)])
    c.vinyl(slice_, "#2E9E55", rim=2.6, hl=None)
    c.fill(Shape([("M", 16, 50), ("L", 104, 50), ("C", 100, 86, 20, 86, 16, 50), ("Z",)]), "#F2F7C9")
    red = Shape([("M", 20, 50), ("L", 100, 50), ("C", 96, 80, 24, 80, 20, 50), ("Z",)])
    c.vinyl(red, "#F2475A", rim=0, hl=(.3, .2), shadow=False)
    for x, y in ((40, 58), (58, 64), (76, 58), (50, 70), (68, 70)):
        c.flat(ellipse(x, y, 2.4, 3.6), kit.INK)


@pic
def strawberry(c):
    b = Shape([("M", 60, 110), ("C", 30, 96, 14, 64, 22, 46), ("C", 30, 30, 90, 30, 98, 46), ("C", 106, 64, 90, 96, 60, 110), ("Z",)])
    c.vinyl(b, "#F23B53", rim=2.6, hl=(.25, .2))
    for x, y in ((40, 56), (60, 52), (80, 56), (48, 72), (70, 72), (60, 88), (36, 72), (84, 70), (52, 96), (68, 96)):
        c.flat(ellipse(x, y, 2, 3), "#FFE88A")
    leaves = Shape()
    for a in (-60, -20, 20, 60):
        leaves = leaves + ellipse(60, 30, 7, 16).rotate(a, 60, 40)
    c.vinyl(leaves, kit.LEAF, rim=1.8, hl=None, shadow=False)
    c.stroke(line((60, 30), (60, 14)), "#2E8B4E", 4)


@pic
def peach(c):
    p = Shape([("M", 60, 30), ("C", 90, 26, 108, 52, 102, 76), ("C", 96, 100, 72, 108, 60, 108), ("C", 48, 108, 24, 100, 18, 76),
               ("C", 12, 52, 30, 26, 60, 30), ("Z",)])
    c.vinyl(p, "#FFA9A0", rim=2.6, hl=(.25, .22))
    c.flat(ellipse(76, 70, 22, 26), "#FF7F8A", op=.4)
    c.stroke(curve((60, 32), (52, 52), (52, 84), (60, 106)), "#E8786F", 2.6)
    c.vinyl(ellipse(48, 24, 14, 7).rotate(-20, 48, 24) + ellipse(72, 24, 14, 7).rotate(20, 72, 24), kit.LEAF, rim=1.6, hl=None, shadow=False)


@pic
def pear(c):
    p = Shape([("M", 60, 26), ("C", 74, 26, 76, 46, 82, 56), ("C", 104, 74, 98, 108, 60, 108), ("C", 22, 108, 16, 74, 38, 56),
               ("C", 44, 46, 46, 26, 60, 26), ("Z",)])
    c.vinyl(p, "#D9E86A", rim=2.6, hl=(.3, .3))
    c.stroke(curve((60, 28), (60, 20), (62, 14), (66, 10)), "#7A4A2A", 4)
    c.vinyl(ellipse(76, 18, 11, 5).rotate(-25, 76, 18), kit.LEAF, rim=1.4, hl=None, shadow=False)
    for x, y in ((48, 80), (70, 92), (74, 70), (56, 96)):
        c.flat(circle(x, y, 1.4), "#9AAE3A")


@pic
def lemon(c):
    l = Shape([("M", 8, 62), ("C", 16, 54, 22, 34, 60, 32), ("C", 98, 34, 104, 54, 112, 62), ("C", 104, 70, 98, 92, 60, 92),
               ("C", 22, 92, 16, 70, 8, 62), ("Z",)])
    c.vinyl(l, "#FFE14A", rim=2.6, hl=(.3, .22))
    c.vinyl(ellipse(66, 28, 12, 5).rotate(-15, 66, 28), kit.LEAF, rim=1.4, hl=None, shadow=False)


@pic
def pineapple(c):
    leaves = Shape()
    for a in (-40, -20, 0, 20, 40):
        leaves = leaves + ellipse(60, 22, 6, 20).rotate(a, 60, 40)
    c.vinyl(leaves, kit.LEAF, rim=1.8, hl=None)
    b = ellipse(60, 76, 32, 38)
    c.vinyl(b, "#FFC23A", rim=2.6, hl=(.25, .2))
    def inside(p, q):
        """The part of the line p..q inside the pineapple (an ellipse, a little smaller)."""
        pts = []
        for i in range(41):
            t = i / 40
            x, y = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
            if ((x - 60) / 29) ** 2 + ((y - 76) / 35) ** 2 <= 1:
                pts.append((x, y))
        return pts
    for k in range(-4, 5):
        for a, b in (((60 + k * 14 - 30, 36), (60 + k * 14 + 30, 116)), ((60 + k * 14 + 30, 36), (60 + k * 14 - 30, 116))):
            pts = inside(a, b)
            if len(pts) > 1:
                c.stroke(line(pts[0], pts[-1]), "#D9921E", 2, op=.75)
    c.highlight(46, 54, 8)


@pic
def banana(c):
    b = Shape([("M", 18, 42), ("C", 26, 92, 80, 104, 108, 70), ("C", 110, 62, 104, 58, 98, 64), ("C", 76, 84, 44, 76, 30, 40), ("Z",)])
    c.vinyl(b, "#FFDB4A", rim=2.6, hl=(.3, .5), hl_size=.7)
    c.vinyl(rrect(14, 30, 12, 14, 4).rotate(-20, 20, 37), "#8A6A3A", rim=1.4, hl=None, shadow=False)
    c.flat(circle(106, 66, 3), "#5A4A2A")


@pic
def coconut(c):
    c.vinyl(circle(60, 66, 42), "#8A5A33", rim=2.6, hl=(.25, .2))
    c.vinyl(ellipse(60, 42, 24, 14), "#F4EFE2", rim=2, hl=None, shadow=False)
    c.stroke(line((66, 40), (76, 10)), "#F2475A", 4.5)
    c.stroke(line((76, 10), (84, 8)), "#F2475A", 4.5)
    c.vinyl(ellipse(34, 40, 14, 7).rotate(-30, 34, 40), kit.LEAF, rim=1.4, hl=None, shadow=False)


@pic
def corn(c):
    for d, a in ((-1, -20), (1, 20)):
        c.vinyl(ellipse(60 + d * 16, 74, 13, 38).rotate(a, 60, 104), kit.LEAF, rim=2, hl=None)
    cob = rrect(42, 16, 36, 86, 18)
    c.vinyl(cob, "#FFD23F", rim=2.6, hl=(.25, .15))
    for y in range(24, 98, 10):
        for x in (50, 60, 70):
            c.flat(ellipse(x + (5 if (y // 10) % 2 else 0) - 2.5, y, 3.6, 3.6), "#F5B21E", op=.7)
    c.vinyl(ellipse(46, 84, 12, 30).rotate(-12, 46, 104), kit.LEAF, rim=1.8, hl=None, shadow=False)
    c.vinyl(ellipse(74, 84, 12, 30).rotate(12, 74, 104), "#5CC46F", rim=1.8, hl=None, shadow=False)


@pic
def cabbage(c):
    outer = smooth([(14, 74), (20, 44), (44, 26), (78, 26), (102, 44), (106, 74), (86, 100), (34, 100)], .9)
    c.vinyl(outer, "#A6E07A", rim=2.6, hl=(.25, .2))
    c.vinyl(ellipse(60, 62, 30, 28), "#E8F7C8", rim=1.8, hl=(.3, .25), shadow=False)
    for a in (-40, 0, 40):
        c.stroke(curve((60, 92), (60 + a * .3, 74), (60 + a * .6, 56), (60 + a * .7, 40)), "#8CCB5E", 2.2)


@pic
def onion(c):
    for x, a in ((52, -8), (62, 0), (72, 8)):
        c.vinyl(rrect(x - 5, 8, 10, 70, 5).rotate(a, x, 80), "#3DBB5C", rim=1.8, hl=None)
    c.vinyl(rrect(42, 60, 36, 48, 14), "#F4F8EE", rim=2.4, hl=(.25, .2), rim_col="#9CB896")
    for x in (50, 60, 70):
        c.stroke(line((x, 104), (x - 2, 114)), "#C8B89A", 2)


@pic
def garlic(c):
    g = Shape([("M", 60, 20), ("C", 64, 34, 104, 46, 104, 78), ("C", 104, 104, 16, 104, 16, 78), ("C", 16, 46, 56, 34, 60, 20), ("Z",)])
    c.vinyl(g, "#F7F2EC", rim=2.6, hl=(.25, .35), rim_col="#B9A99A")
    for x in (40, 60, 80):
        c.stroke(curve((60, 30), (x, 50), (x, 80), (60 if x == 60 else x * .5 + 30, 100)), "#D8CFC4", 2)
    c.vinyl(rrect(56, 12, 8, 12, 3), "#C8B89A", rim=1.2, hl=None, shadow=False)


@pic
def egg(c):
    e = Shape([("M", 60, 14), ("C", 88, 14, 100, 62, 98, 78), ("C", 96, 102, 78, 110, 60, 110), ("C", 42, 110, 24, 102, 22, 78),
               ("C", 20, 62, 32, 14, 60, 14), ("Z",)])
    c.vinyl(e, "#FFF3DE", rim=2.6, hl=(.3, .2), rim_col="#C9A87A")


@pic
def meat(c):
    bone = circle(92, 24, 8) + circle(104, 30, 8) + rrect(80, 26, 16, 34, 6).rotate(40, 88, 44)
    c.vinyl(bone, "#FFF8EE", rim=2, hl=None, rim_col="#B9A99A")
    m = smooth([(20, 86), (24, 56), (46, 40), (72, 46), (82, 66), (70, 92), (40, 104)], .9)
    c.vinyl(m, "#C86A3A", rim=2.6, hl=(.3, .2))


@pic
def hotdog(c):
    bun = rrect(10, 52, 100, 40, 20)
    c.vinyl(bun, "#F2B868", rim=2.6, hl=(.25, .2))
    c.vinyl(rrect(4, 46, 112, 22, 11), "#E0533E", rim=2.2, hl=(.2, .3), shadow=False)
    c.stroke(Shape([("M", 18, 56), ("C", 26, 50, 32, 62, 40, 56), ("C", 48, 50, 54, 62, 62, 56), ("C", 70, 50, 76, 62, 84, 56),
                    ("C", 92, 50, 98, 62, 104, 56)]), kit.YELLOW, 4)
    c.vinyl(rrect(10, 66, 100, 26, 13), "#F2B868", rim=2.2, hl=None, shadow=False)


@pic
def zongzi(c):
    z = Shape([("M", 60, 14), ("C", 66, 14, 104, 92, 100, 98), ("C", 96, 106, 24, 106, 20, 98), ("C", 16, 92, 54, 14, 60, 14), ("Z",)])
    c.vinyl(z, "#5DAA4E", rim=2.6, hl=(.4, .3))
    c.stroke(line((40, 60), (80, 60)), "#C9A46A", 5)
    c.stroke(line((30, 84), (90, 84)), "#C9A46A", 5)
    c.stroke(curve((60, 14), (56, 40), (66, 70), (60, 102)), "#3F8A3A", 2)


@pic
def candy(c):
    for d in (-1, 1):
        c.vinyl(poly([(60 + d * 26, 60), (60 + d * 54, 40), (60 + d * 48, 60), (60 + d * 54, 80)]), kit.PINK, rim=2, hl=None)
    c.vinyl(circle(60, 60, 28), "#FF6FA0", rim=2.6, hl=(.25, .22))
    c.stroke(arc(60, 60, 16, 200, 470), kit.WHITE, 5, op=.8)


@pic
def milk(c):
    box = Shape([("M", 30, 40), ("L", 90, 40), ("L", 90, 108), ("L", 30, 108), ("Z",)])
    roof = Shape([("M", 30, 40), ("L", 44, 18), ("L", 76, 18), ("L", 90, 40), ("Z",)])
    c.vinyl(box + roof, kit.WHITE, rim=2.6, hl=(.3, .2), rim_col="#9CB0D6")
    c.flat(rrect(36, 60, 48, 34, 10), "#6FB6F2")
    c.vinyl(circle(60, 76, 10), kit.WHITE, rim=1.4, hl=None, shadow=False, rim_col="#6F8BC6")
    c.flat(rect(44, 12, 32, 8), "#9CB0D6")


@pic
def juice(c):
    c.vinyl(rrect(32, 34, 56, 76, 10), kit.ORANGE, rim=2.6, hl=(.25, .15))
    c.vinyl(circle(60, 76, 18), "#FFC23A", rim=1.8, hl=None, shadow=False)
    for a in range(0, 360, 60):
        c.stroke(line((60, 76), (60 + 14 * math.cos(math.radians(a)), 76 + 14 * math.sin(math.radians(a)))), "#FFE58A", 2)
    c.stroke(line((72, 34), (78, 8), (90, 6)), kit.dk(kit.SKY, .2), 5)


# ================================================================ things
@pic
def plane(c):
    wing = Shape([("M", 50, 58), ("L", 76, 18), ("L", 88, 20), ("L", 78, 62), ("Z",)])
    c.vinyl(wing, kit.BLUE, rim=2.2, hl=None)
    c.vinyl(Shape([("M", 14, 52), ("L", 22, 30), ("L", 32, 32), ("L", 34, 56), ("Z",)]), kit.RED, rim=2, hl=None)
    b = rrect(10, 50, 104, 26, 13)
    c.vinyl(b, kit.WHITE, rim=2.6, hl=(.15, .2), rim_col="#8A9BC9")
    for x in (40, 54, 68, 82):
        c.vinyl(circle(x, 60, 4.5), kit.SKY, rim=1.4, hl=None, shadow=False)
    c.vinyl(Shape([("M", 50, 70), ("L", 70, 104), ("L", 82, 104), ("L", 76, 70), ("Z",)]), kit.BLUE, rim=2.2, hl=None, shadow=False)
    c.vinyl(ellipse(104, 60, 8, 9), kit.SKY, rim=1.6, hl=None, shadow=False)


@pic
def balloon(c):
    c.stroke(curve((60, 80), (54, 92), (66, 102), (58, 116)), kit.INK, 2)
    b = Shape([("M", 60, 10), ("C", 92, 10, 98, 50, 82, 68), ("C", 74, 78, 66, 82, 60, 82), ("C", 54, 82, 46, 78, 38, 68),
               ("C", 22, 50, 28, 10, 60, 10), ("Z",)])
    c.vinyl(b, kit.RED, rim=2.6, hl=(.28, .2))
    c.vinyl(poly([(55, 86), (60, 80), (65, 86)]), kit.RED, rim=1.4, hl=None, shadow=False)


@pic
def car(c):
    body_ = rrect(10, 52, 100, 36, 14) + rrect(30, 26, 56, 36, 14)
    c.vinyl(body_, kit.YELLOW, rim=2.6, hl=(.25, .15))
    c.vinyl(rrect(36, 32, 20, 20, 5), kit.SKY, rim=1.6, hl=(.3, .3), shadow=False)
    c.vinyl(rrect(60, 32, 20, 20, 5), kit.SKY, rim=1.6, hl=(.3, .3), shadow=False)
    c.vinyl(circle(104, 66, 5), kit.WHITE, rim=1.2, hl=None, shadow=False)
    for x in (32, 88):
        c.vinyl(circle(x, 90, 13), "#43405A", rim=2, hl=None)
        c.vinyl(circle(x, 90, 5.5), kit.GREY, rim=1.2, hl=None, shadow=False)


@pic
def train(c):
    c.vinyl(rrect(8, 40, 50, 52, 10), kit.RED, rim=2.4, hl=(.2, .15))
    c.vinyl(rrect(4, 30, 58, 14, 7), kit.dk(kit.RED, .2), rim=2, hl=None, shadow=False)
    c.vinyl(rrect(16, 48, 32, 24, 6), kit.SKY, rim=1.6, hl=(.3, .3), shadow=False)
    c.vinyl(rrect(54, 56, 58, 36, 16), kit.RED, rim=2.4, hl=(.2, .2))
    c.vinyl(rrect(84, 30, 16, 28, 4), kit.STEEL, rim=1.8, hl=None)
    c.vinyl(circle(110, 72, 6), kit.YELLOW, rim=1.4, hl=None, shadow=False)
    for x, r in ((28, 13), (70, 11), (96, 11)):
        c.vinyl(circle(x, 96, r), "#43405A", rim=2, hl=None)
        c.vinyl(circle(x, 96, r * .4), kit.GOLD, rim=1, hl=None, shadow=False)
    c.vinyl(circle(92, 18, 8) + circle(102, 12, 7), "#F4F1FA", rim=1.4, hl=None, shadow=False, rim_col="#B9B3C9")


@pic
def heart(c):
    c.vinyl(kit.heart(60, 62, 92), "#F2475A", rim=2.8, hl=(.25, .25))


@pic
def cup(c):
    c.stroke(Shape([("M", 86, 44), ("C", 108, 42, 108, 82, 84, 82)]), kit.rim_of(kit.TEAL), 15)
    c.stroke(Shape([("M", 86, 44), ("C", 108, 42, 108, 82, 84, 82)]), kit.TEAL, 9.5)
    cup_ = Shape([("M", 22, 30), ("L", 92, 30), ("L", 86, 102), ("C", 84, 108, 30, 108, 28, 102), ("Z",)])
    c.vinyl(cup_, kit.TEAL, rim=2.6, hl=(.2, .2))
    c.flat(ellipse(57, 32, 34, 6), kit.dk(kit.TEAL, .35))
    c.flat(ellipse(57, 70, 10, 10), kit.WHITE, op=.8)


@pic
def helmet(c):
    h = Shape([("M", 10, 82), ("C", 10, 20, 110, 20, 110, 82), ("Z",)])
    c.vinyl(h, kit.YELLOW, rim=2.6, hl=(.3, .2))
    c.vinyl(rrect(4, 78, 112, 14, 7), kit.dk(kit.YELLOW, .15), rim=2.2, hl=None, shadow=False)
    c.vinyl(rrect(52, 22, 16, 58, 8), "#FFE680", rim=1.6, hl=None, shadow=False)
    c.vinyl(rrect(28, 92, 8, 16, 4) + rrect(84, 92, 8, 16, 4), kit.dk(kit.STEEL, .2), rim=1.4, hl=None, shadow=False)


@pic
def door(c):
    c.vinyl(rrect(24, 8, 72, 108, 10), "#C9773F", rim=2.6, hl=(.2, .1))
    c.flat(rrect(34, 18, 52, 38, 6), kit.dk("#C9773F", .2), op=.5)
    c.flat(rrect(34, 64, 52, 42, 6), kit.dk("#C9773F", .2), op=.5)
    c.vinyl(circle(82, 64, 6), kit.GOLD, rim=1.6, hl=(.3, .3), shadow=False)


@pic
def lamp(c):
    c.vinyl(rrect(54, 50, 12, 52, 6), kit.STEEL, rim=1.8, hl=None)
    c.vinyl(ellipse(60, 106, 30, 8), kit.dk(kit.STEEL, .2), rim=2, hl=None)
    shade = Shape([("M", 38, 14), ("L", 82, 14), ("L", 104, 58), ("L", 16, 58), ("Z",)])
    c.vinyl(shade, kit.YELLOW, rim=2.6, hl=(.3, .2))
    c.flat(ellipse(60, 58, 44, 6), "#FFF6C2", op=.9)


@pic
def clothes(c):
    shirt = Shape([("M", 40, 14), ("C", 50, 22, 70, 22, 80, 14), ("L", 112, 32), ("L", 100, 56), ("L", 88, 50), ("L", 88, 108),
                   ("L", 32, 108), ("L", 32, 50), ("L", 20, 56), ("L", 8, 32), ("Z",)])
    c.vinyl(shirt, kit.BLUE, rim=2.6, hl=(.25, .2))
    c.vinyl(star(60, 70, 14), kit.YELLOW, rim=1.6, hl=None, shadow=False)


@pic
def raincoat(c):
    coat = Shape([("M", 60, 8), ("C", 82, 8, 90, 28, 88, 40), ("L", 108, 102), ("C", 90, 110, 30, 110, 12, 102), ("L", 32, 40),
                  ("C", 30, 28, 38, 8, 60, 8), ("Z",)])
    c.vinyl(coat, kit.YELLOW, rim=2.6, hl=(.3, .15))
    c.flat(ellipse(60, 36, 18, 16), kit.dk(kit.YELLOW, .3), op=.6)
    c.stroke(line((60, 54), (60, 104)), kit.dk(kit.YELLOW, .3), 2)
    for y in (64, 80, 96):
        c.vinyl(circle(66, y, 3.5), kit.RED, rim=1, hl=None, shadow=False)


@pic
def pants(c):
    p = Shape([("M", 26, 14), ("L", 94, 14), ("L", 102, 108), ("L", 68, 108), ("L", 60, 48), ("L", 52, 108), ("L", 18, 108), ("Z",)])
    c.vinyl(p, kit.NAVY, rim=2.6, hl=(.2, .15))
    c.vinyl(rrect(24, 12, 72, 12, 4), kit.dk(kit.NAVY, .2), rim=1.6, hl=None, shadow=False)


@pic
def skirt(c):
    s = Shape([("M", 36, 22), ("L", 84, 22), ("L", 108, 100), ("C", 80, 110, 40, 110, 12, 100), ("Z",)])
    c.vinyl(s, kit.PINK, rim=2.6, hl=(.25, .15))
    for x in (40, 60, 80):
        c.stroke(line((x + (x - 60) * .1, 30), (x + (x - 60) * .5, 102)), kit.dk(kit.PINK, .2), 2)
    c.vinyl(rrect(34, 14, 52, 12, 5), kit.ROSE, rim=1.6, hl=None, shadow=False)


@pic
def shoes(c):
    for x0, col in ((6, kit.RED), (60, kit.RED)):
        sh = Shape([("M", x0 + 6, 60), ("C", x0 + 6, 46, x0 + 22, 44, x0 + 26, 58), ("C", x0 + 40, 66, x0 + 54, 70, x0 + 54, 86),
                    ("L", x0 + 6, 86), ("Z",)])
        c.vinyl(sh, col, rim=2.4, hl=(.3, .25))
        c.vinyl(rrect(x0 + 4, 84, 52, 8, 4), kit.WHITE, rim=1.6, hl=None, shadow=False, rim_col="#B8B0C6")
        c.stroke(line((x0 + 22, 64), (x0 + 32, 62)), kit.WHITE, 2.4)
        c.stroke(line((x0 + 24, 70), (x0 + 34, 68)), kit.WHITE, 2.4)


@pic
def hat(c):
    c.vinyl(ellipse(60, 82, 54, 16), kit.dk(kit.TAN, .05), rim=2.4, hl=None)
    c.vinyl(Shape([("M", 28, 82), ("C", 28, 30, 92, 30, 92, 82), ("Z",)]), kit.TAN, rim=2.6, hl=(.3, .2))
    c.vinyl(rrect(28, 68, 64, 12, 4), kit.RED, rim=1.6, hl=None, shadow=False)


@pic
def bag(c):
    c.stroke(Shape([("M", 38, 46), ("C", 38, 6, 82, 6, 82, 46)]), kit.rim_of(kit.ROSE), 11)
    c.stroke(Shape([("M", 38, 46), ("C", 38, 6, 82, 6, 82, 46)]), kit.ROSE, 6)
    c.vinyl(rrect(16, 40, 88, 68, 18), kit.ROSE, rim=2.6, hl=(.2, .15))
    c.vinyl(rrect(16, 40, 88, 28, 14), kit.dk(kit.ROSE, .15), rim=2, hl=None, shadow=False)
    c.vinyl(circle(60, 66, 6), kit.GOLD, rim=1.4, hl=None, shadow=False)


@pic
def ball(c):
    c.vinyl(circle(60, 60, 46), "#FF7A5C", rim=2.6, hl=(.25, .2))
    c.stroke(Shape([("M", 16, 54), ("C", 40, 70, 80, 70, 104, 54)]), kit.WHITE, 6, op=.9)
    c.stroke(Shape([("M", 54, 14), ("C", 42, 40, 42, 80, 54, 106)]), kit.YELLOW, 6, op=.9)


@pic
def soccer(c):
    c.vinyl(circle(60, 60, 46), kit.WHITE, rim=2.6, hl=(.25, .2), rim_col="#8A86A0")
    c.flat(poly([(60 + 13 * math.cos(math.radians(a)), 62 + 13 * math.sin(math.radians(a))) for a in range(-90, 270, 72)]), kit.INK)
    for a in range(-90, 270, 72):
        x, y = 60 + 36 * math.cos(math.radians(a)), 62 + 36 * math.sin(math.radians(a))
        c.flat(poly([(x + 9 * math.cos(math.radians(b)), y + 9 * math.sin(math.radians(b))) for b in range(a + 90, a + 450, 72)]), kit.INK)
    c.highlight(42, 36, 9)


@pic
def book(c):
    c.vinyl(rrect(14, 22, 92, 80, 8), kit.GREEN, rim=2.6, hl=(.15, .1))
    c.vinyl(rrect(20, 26, 82, 70, 6), "#FFF8E8", rim=1.4, hl=None, shadow=False)
    c.flat(rect(58, 26, 4, 70), kit.dk(kit.GREEN, .2))
    for y in (40, 52, 64, 76):
        c.stroke(line((28, y), (50, y)), "#C9C0D6", 2.4)
        c.stroke(line((70, y), (92, y)), "#C9C0D6", 2.4)


@pic
def bowl(c):
    b = Shape([("M", 10, 50), ("L", 110, 50), ("C", 108, 96, 12, 96, 10, 50), ("Z",)])
    c.vinyl(b, kit.WHITE, rim=2.6, hl=(.2, .3), rim_col="#8EA6D6")
    c.flat(ellipse(60, 50, 50, 8), "#D8E4F6")
    c.flat(Shape([("M", 30, 50), ("C", 36, 34, 84, 34, 90, 50), ("Z",)]), "#FFFDF6")
    c.stroke(Shape([("M", 22, 68), ("C", 40, 74, 80, 74, 98, 68)]), kit.BLUE, 3)
    c.vinyl(rrect(44, 90, 32, 8, 4), "#DDE6F6", rim=1.4, hl=None, shadow=False, rim_col="#8EA6D6")


@pic
def plate(c):
    c.vinyl(ellipse(60, 66, 54, 30), kit.WHITE, rim=2.6, hl=(.2, .2), rim_col="#8EA6D6")
    c.flat(ellipse(60, 64, 36, 18), "#E6EEF9")
    c.stroke(ellipse(60, 66, 46, 24), kit.SKY, 2.6)


@pic
def umbrella(c):
    c.stroke(Shape([("M", 60, 50), ("L", 60, 98), ("C", 60, 110, 44, 110, 44, 100)]), kit.INK, 4.5)
    top = Shape([("M", 8, 58), ("C", 10, 14, 110, 14, 112, 58), ("C", 100, 50, 88, 50, 78, 58), ("C", 68, 50, 52, 50, 42, 58),
                 ("C", 32, 50, 20, 50, 8, 58), ("Z",)])
    c.vinyl(top, kit.PURPLE, rim=2.6, hl=(.3, .25))
    c.stroke(curve((60, 20), (52, 30), (44, 44), (42, 56)), kit.dk(kit.PURPLE, .2), 2)
    c.stroke(curve((60, 20), (68, 30), (76, 44), (78, 56)), kit.dk(kit.PURPLE, .2), 2)
    c.vinyl(circle(60, 18, 4), kit.GOLD, rim=1.2, hl=None, shadow=False)


@pic
def bed(c):
    c.vinyl(rrect(8, 30, 18, 80, 6) + rrect(94, 52, 18, 58, 6), "#C9773F", rim=2.4, hl=None)
    c.vinyl(rrect(14, 62, 92, 30, 8), "#FFF8EE", rim=2.2, hl=None, rim_col="#B9A99A")
    c.vinyl(rrect(22, 48, 30, 18, 9), kit.WHITE, rim=2, hl=(.3, .3), rim_col="#B9A99A")
    c.vinyl(rrect(46, 54, 62, 38, 10), kit.SKY, rim=2.4, hl=(.25, .2))


@pic
def pillow(c):
    p = smooth([(14, 42), (60, 30), (106, 42), (100, 64), (106, 86), (60, 96), (14, 86), (20, 64)], .7)
    c.vinyl(p, "#BFE3FF", rim=2.6, hl=(.25, .25))
    c.flat(circle(60, 63, 5), kit.WHITE, op=.7)


@pic
def cloud(c):
    s = circle(38, 66, 22) + circle(60, 52, 28) + circle(86, 64, 22) + rrect(18, 62, 86, 28, 14)
    c.vinyl(s, kit.WHITE, rim=2.6, hl=(.3, .25), rim_col="#9CB0D6")
    c.face(60, 70, 18)


@pic
def rain(c):
    s = circle(38, 46, 18) + circle(60, 36, 22) + circle(84, 46, 18) + rrect(20, 42, 82, 22, 11)
    c.vinyl(s, "#C8D4EE", rim=2.6, hl=(.3, .25), rim_col="#7F92BE")
    for x, y in ((34, 84), (60, 96), (86, 84), (48, 106), (74, 108)):
        drop = Shape([("M", x, y - 10), ("C", x + 6, y - 2, x + 6, y + 5, x, y + 5), ("C", x - 6, y + 5, x - 6, y - 2, x, y - 10), ("Z",)])
        c.vinyl(drop, kit.BLUE, rim=1.4, hl=None, shadow=False)


@pic
def bottle(c):
    b = Shape([("M", 48, 14), ("L", 72, 14), ("L", 72, 30), ("C", 90, 38, 90, 48, 90, 56), ("L", 90, 104), ("C", 90, 110, 30, 110, 30, 104),
               ("L", 30, 56), ("C", 30, 48, 30, 38, 48, 30), ("Z",)])
    c.vinyl(b, "#9FE0F2", rim=2.6, hl=(.25, .3))
    c.vinyl(rrect(44, 8, 32, 12, 4), kit.BLUE, rim=1.8, hl=None, shadow=False)
    c.flat(rrect(32, 64, 56, 26, 4), kit.WHITE, op=.75)


@pic
def soap(c):
    for x, y, r in ((30, 26, 9), (48, 14, 6), (92, 22, 7)):
        c.vinyl(circle(x, y, r), "#E6F7FF", rim=1.4, hl=(.3, .3), shadow=False, rim_col="#8EC6E6")
    c.vinyl(rrect(14, 44, 92, 56, 24), kit.PINK, rim=2.6, hl=(.2, .2))
    c.flat(rrect(30, 60, 60, 24, 12), kit.lt(kit.PINK, .4), op=.7)


@pic
def fan(c):
    c.vinyl(rrect(56, 64, 8, 36, 4), kit.STEEL, rim=1.6, hl=None)
    c.vinyl(ellipse(60, 106, 30, 8), kit.dk(kit.STEEL, .1), rim=2, hl=None)
    c.vinyl(circle(60, 44, 36), "#E6F2FF", rim=2.6, hl=None, rim_col="#7F92BE")
    for a in (0, 120, 240):
        c.vinyl(ellipse(60, 26, 10, 17).rotate(a, 60, 44), kit.SKY, rim=1.6, hl=None, shadow=False)
    c.vinyl(circle(60, 44, 7), kit.BLUE, rim=1.4, hl=None, shadow=False)
    for k in range(6):
        a = math.radians(k * 30)
        c.stroke(line((60 - 34 * math.cos(a), 44 - 34 * math.sin(a)), (60 + 34 * math.cos(a), 44 + 34 * math.sin(a))), "#9CB0D6", 1, op=.6)


@pic
def spoon(c):
    c.vinyl(rrect(54, 50, 12, 64, 6).rotate(20, 60, 60), kit.GREY, rim=2, hl=None)
    c.vinyl(ellipse(60, 34, 22, 28).rotate(20, 60, 60), "#D6D9E6", rim=2.6, hl=(.3, .3), rim_col="#7E7A96")


@pic
def chopsticks(c):
    for x, a in ((48, -10), (72, 10)):
        c.vinyl(rrect(x - 4, 8, 8, 104, 4).rotate(a, x, 60), "#C9773F", rim=2, hl=None)
        c.vinyl(rrect(x - 4, 8, 8, 26, 4).rotate(a, x, 60), kit.RED, rim=1.6, hl=None, shadow=False)


@pic
def clock(c):
    for d in (-1, 1):
        c.vinyl(circle(60 + d * 30, 24, 13), kit.GOLD, rim=2, hl=(.3, .3))
        c.stroke(line((60 + d * 26, 98), (60 + d * 34, 112)), kit.INK, 4)
    c.vinyl(circle(60, 64, 42), kit.RED, rim=2.6, hl=(.2, .15))
    c.vinyl(circle(60, 64, 32), kit.WHITE, rim=1.6, hl=None, shadow=False)
    for k in range(12):
        a = math.radians(k * 30)
        c.flat(circle(60 + 26 * math.cos(a), 64 + 26 * math.sin(a), 1.8), kit.INK)
    c.stroke(line((60, 64), (60, 44)), kit.INK, 3.5)
    c.stroke(line((60, 64), (74, 70)), kit.INK, 3.5)


@pic
def basket(c):
    c.stroke(Shape([("M", 22, 54), ("C", 22, 4, 98, 4, 98, 54)]), kit.rim_of("#D9A35C"), 10)
    c.stroke(Shape([("M", 22, 54), ("C", 22, 4, 98, 4, 98, 54)]), "#D9A35C", 5)
    b = Shape([("M", 12, 50), ("L", 108, 50), ("L", 96, 104), ("C", 94, 110, 26, 110, 24, 104), ("Z",)])
    c.vinyl(b, "#D9A35C", rim=2.6, hl=(.2, .2))
    for y in (64, 80, 94):
        c.stroke(line((18 + (y - 50) * .2, y), (102 - (y - 50) * .2, y)), kit.dk("#D9A35C", .25), 2.4)
    for x in (36, 60, 84):
        c.stroke(line((x, 52), (x + (60 - x) * .1, 104)), kit.dk("#D9A35C", .25), 2.4)


@pic
def stairs(c):
    s = poly([(10, 110), (10, 86), (34, 86), (34, 62), (58, 62), (58, 38), (82, 38), (82, 14), (110, 14), (110, 110)])
    c.vinyl(s, "#E6B47A", rim=2.6, hl=(.8, .1), hl_size=.4)
    for x, y in ((10, 86), (34, 62), (58, 38), (82, 14)):
        c.flat(rect(x + 1, y + 1, 24 if x < 82 else 27, 5), kit.lt("#E6B47A", .4))


@pic
def pot(c):
    for d in (-1, 1):
        c.vinyl(rrect(60 + d * 50 - 8, 52, 16, 10, 5), "#43405A", rim=1.6, hl=None)
    c.vinyl(rrect(16, 46, 88, 56, 14), kit.STEEL, rim=2.6, hl=(.2, .2))
    c.vinyl(rrect(12, 38, 96, 12, 6), kit.dk(kit.STEEL, .2), rim=2, hl=None, shadow=False)
    c.vinyl(rrect(50, 28, 20, 12, 5), "#43405A", rim=1.6, hl=None, shadow=False)


@pic
def box(c):
    c.vinyl(rrect(16, 50, 88, 58, 6), kit.PURPLE, rim=2.6, hl=(.2, .2))
    c.vinyl(rrect(10, 36, 100, 20, 6), kit.dk(kit.PURPLE, .12), rim=2.4, hl=(.15, .3), shadow=False)
    c.flat(rect(54, 36, 12, 72), kit.YELLOW)
    for d in (-1, 1):
        c.vinyl(ellipse(60 + d * 14, 28, 14, 9).rotate(d * 20, 60, 34), kit.YELLOW, rim=1.8, hl=None, shadow=False)


@pic
def blocks(c):
    c.vinyl(rrect(12, 64, 44, 44, 8), kit.RED, rim=2.4, hl=(.2, .2))
    c.vinyl(rrect(62, 64, 44, 44, 8), kit.BLUE, rim=2.4, hl=(.2, .2))
    c.vinyl(rrect(37, 18, 44, 44, 8), kit.YELLOW, rim=2.4, hl=(.2, .2))
    c.vinyl(star(34, 86, 11), kit.WHITE, rim=0, hl=None, shadow=False, op=.8)
    c.vinyl(circle(84, 86, 10), kit.WHITE, rim=0, hl=None, shadow=False, op=.8)
    c.vinyl(poly([(59, 28), (70, 50), (48, 50)]), kit.WHITE, rim=0, hl=None, shadow=False, op=.8)


@pic
def scissors(c):
    for a in (-18, 18):
        c.vinyl(rrect(56, 10, 10, 62, 5).rotate(a, 60, 66), "#D6D9E6", rim=2, hl=None, rim_col="#7E7A96")
    for x in (42, 78):
        c.vinyl(circle(x, 92, 16), kit.RED, rim=2.4, hl=(.3, .3))
        c.flat(circle(x, 92, 8), kit.CREAM)
    c.vinyl(circle(60, 64, 4), kit.GOLD, rim=1.2, hl=None, shadow=False)


@pic
def table(c):
    for x in (22, 88):
        c.vinyl(rrect(x, 50, 12, 58, 5), "#B9784A", rim=2, hl=None)
    c.vinyl(rrect(8, 36, 104, 18, 8), "#D9955E", rim=2.6, hl=(.15, .25))


@pic
def paper(c):
    c.vinyl(rrect(24, 12, 72, 96, 6), kit.WHITE, rim=2.4, hl=(.2, .1), rim_col="#9CB0D6")
    for y in (34, 50, 66, 82):
        c.stroke(line((36, y), (84, y)), "#BFD2EE", 2.4)
    c.flat(Shape([("M", 96, 84), ("L", 96, 108), ("L", 72, 108), ("Z",)]), "#E6EEF9")


@pic
def ruler(c):
    r = rrect(4, 44, 112, 32, 6).rotate(-20, 60, 60)
    c.vinyl(r, kit.YELLOW, rim=2.6, hl=(.2, .25))
    for k in range(1, 14):
        x = 4 + k * 8
        ln = line((x, 44), (x, 52 if k % 2 else 58))
        c.stroke(ln.rotate(-20, 60, 60), kit.INK, 1.8)


@pic
def comb(c):
    c.vinyl(rrect(10, 34, 100, 22, 10), kit.PINK, rim=2.4, hl=(.15, .25))
    teeth = Shape()
    for x in range(16, 106, 9):
        teeth = teeth + rrect(x, 50, 5, 40, 2.5)
    c.vinyl(teeth, kit.PINK, rim=1.6, hl=None, shadow=False)
    c.vinyl(rrect(10, 34, 100, 22, 10), kit.PINK, rim=0, hl=(.15, .25), shadow=False)


@pic
def calendar(c):
    c.vinyl(rrect(14, 20, 92, 88, 10), kit.WHITE, rim=2.6, hl=None, rim_col="#9CB0D6")
    c.vinyl(rrect(14, 20, 92, 26, 10), kit.RED, rim=2, hl=(.15, .3), shadow=False)
    for x in (36, 84):
        c.vinyl(rrect(x - 4, 10, 8, 18, 4), kit.STEEL, rim=1.4, hl=None, shadow=False)
    for r_ in range(3):
        for k in range(4):
            c.flat(rrect(24 + k * 19, 56 + r_ * 16, 12, 10, 3), "#D8E2F2")
    c.flat(rrect(43, 72, 12, 10, 3), kit.ORANGE)


@pic
def magnet(c):
    m = Shape([("M", 18, 20), ("L", 46, 20), ("L", 46, 62), ("C", 46, 80, 74, 80, 74, 62), ("L", 74, 20), ("L", 102, 20), ("L", 102, 62),
               ("C", 102, 116, 18, 116, 18, 62), ("Z",)])
    c.vinyl(m, kit.RED, rim=2.6, hl=(.2, .5))
    c.vinyl(rrect(18, 20, 28, 18, 3) + rrect(74, 20, 28, 18, 3), "#D6D9E6", rim=1.8, hl=None, shadow=False, rim_col="#7E7A96")


@pic
def broom(c):
    c.vinyl(rrect(55, 6, 10, 70, 5), "#C9773F", rim=2, hl=None)
    b = Shape([("M", 40, 70), ("L", 80, 70), ("L", 104, 112), ("L", 16, 112), ("Z",)])
    c.vinyl(b, kit.GOLD, rim=2.6, hl=(.3, .2))
    c.vinyl(rrect(38, 64, 44, 12, 5), kit.RED, rim=1.8, hl=None, shadow=False)
    for x in (34, 48, 62, 76, 90):
        c.stroke(line((60 + (x - 60) * .4, 80), (x, 108)), kit.dk(kit.GOLD, .3), 1.8)


@pic
def headphones(c):
    c.stroke(Shape([("M", 24, 70), ("C", 20, 10, 100, 10, 96, 70)]), kit.rim_of(kit.BLUE), 14)
    c.stroke(Shape([("M", 24, 70), ("C", 20, 10, 100, 10, 96, 70)]), kit.BLUE, 9)
    for x in (24, 96):
        c.vinyl(rrect(x - 14, 58, 28, 44, 12), kit.BLUE, rim=2.4, hl=(.25, .2))
        c.flat(rrect(x - 8, 66, 16, 28, 8), kit.dk(kit.BLUE, .3), op=.6)


@pic
def earring(c):
    for x in (36, 84):
        c.vinyl(circle(x, 24, 6), kit.GOLD, rim=1.4, hl=None)
        c.stroke(line((x, 30), (x, 46)), kit.GOLD, 3)
        c.vinyl(Shape([("M", x, 46), ("C", x + 20, 66, x + 16, 92, x, 100), ("C", x - 16, 92, x - 20, 66, x, 46), ("Z",)]), "#4FD1C5", rim=2.4, hl=(.3, .3))


@pic
def flower(c):
    c.stroke(curve((60, 64), (60, 84), (56, 100), (60, 116)), kit.LEAF, 5)
    c.vinyl(ellipse(74, 96, 12, 6).rotate(-30, 74, 96), kit.LEAF, rim=1.6, hl=None)
    petals = Shape()
    for k in range(5):
        a = math.radians(k * 72 - 90)
        petals = petals + circle(60 + 22 * math.cos(a), 46 + 22 * math.sin(a), 16)
    c.vinyl(petals, kit.PINK, rim=2.6, hl=(.3, .2))
    c.vinyl(circle(60, 46, 14), kit.YELLOW, rim=2, hl=(.3, .3), shadow=False)
    c.face(60, 46, 9, blush=False)


def build():
    import json
    words = json.loads((kit.ROOT / "app" / "assets" / "bopomofo.json").read_text())["words"]
    missing = [w["id"] for w in words if w["id"] not in P]
    if missing:
        raise SystemExit(f"words without a picture: {missing}")
    for w in words:
        c = kit.Ctx(S, S)
        P[w["id"]](c)
        kit.write_svg(OUT / f"{w['id']}.svg", c.svg())
    extra = sorted(set(P) - {w["id"] for w in words})
    print(f"words: {len(words)} pictures" + (f" (not words: {extra})" if extra else ""))


if __name__ == "__main__":
    build()
