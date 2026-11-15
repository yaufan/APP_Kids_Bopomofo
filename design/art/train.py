"""The toy train (docs/art.md 「火車」): the locomotive, a carriage per station colour, the grey
carriage still to come, a wheel and a puff of smoke (the app turns the wheels and puffs the smoke),
the four drivers, a piece of track, a flag, a station sign and the station building.

The app writes the symbol on a carriage's white panel and puts the driver in the cab window; the
numbers it uses for that are in docs/art.md (keep them in step with the ones here).
"""
import sys

sys.dont_write_bytecode = True

import kit  # noqa: E402
from kit import circle, ellipse, rrect, poly, smooth, arc, rect, Shape  # noqa: E402

OUT = kit.ART / "train"


# ---------------------------------------------------------------- carriages and locomotive
def carriage(col, ghost=False):
    """120 x 100: a box carriage, its white panel at x 22..98, y 18..70 (the symbol goes there).
    The wheels (wheel.svg) go at x 32 and 88, y 86, 26 across, drawn by the app."""
    c = kit.Ctx(120, 100)
    if ghost:
        g = "#C9C3D3"
        c.flat(rrect(6, 10, 108, 70, 16), g, op=.35)
        c.stroke(rrect(6, 10, 108, 70, 16), "#A9A2B8", 2.6)
        c.flat(rrect(22, 18, 76, 52, 12), WHITE_GHOST, op=.55)
        c.flat(rrect(14, 78, 92, 8, 4), "#A9A2B8", op=.6)
        return c.svg()
    draw_carriage(c, col)
    return c.svg()


def draw_carriage(c, col):
    """The carriage's body in 120 x 100 units (also used by icon.py)."""
    c.flat(rrect(14, 76, 92, 10, 5), kit.dk(kit.STEEL, .3))
    c.vinyl(rrect(-1, 58, 10, 9, 4), kit.STEEL, rim=1.6, hl=None, shadow=False)
    c.vinyl(rrect(111, 58, 10, 9, 4), kit.STEEL, rim=1.6, hl=None, shadow=False)
    c.vinyl(rrect(6, 8, 108, 72, 16), col, rim=2.6, hl=(.12, .14), hl_size=.9)
    c.vinyl(rrect(10, 4, 100, 10, 5), kit.lt(col, .35), rim=1.8, hl=None, shadow=False)
    # The panel: a cream window the symbol is written on.
    c.flat(rrect(22, 18, 76, 52, 12), kit.rim_of(col), op=.55)
    c.fill(rrect(23, 19, 74, 50, 11), c.linear(0, 19, 0, 69, [(0, "#FFFFFF", 1), (1, "#FFF1DD", 1)]))
    c.highlight(32, 25, 5, op=.6)


def draw_wheel(c, x, y, r):
    """A wheel of radius r at x, y (as wheel.svg)."""
    k = r / 17
    c.vinyl(circle(x, y, 17 * k), "#43405A", rim=1.8 * k, shadow=False, hl=None)
    c.vinyl(circle(x, y, 12 * k), kit.lt(kit.STEEL, .25), rim=1.4 * k, shadow=False, hl=None, round_=False)
    for a in (0, 60, 120):
        c.flat(rrect(x - 1.4 * k, y - 11 * k, 2.8 * k, 22 * k, 1.4 * k).rotate(a, x, y), kit.dk(kit.STEEL, .25))
    c.vinyl(circle(x, y, 4.5 * k), kit.RED, rim=1.2 * k, shadow=False, hl=None)


WHITE_GHOST = "#FFFFFF"


def wheel():
    """40 x 40, round: it turns."""
    c = kit.Ctx(40, 40)
    c.vinyl(circle(20, 20, 17), "#43405A", rim=1.8, shadow=False, hl=None)
    c.vinyl(circle(20, 20, 12), kit.lt(kit.STEEL, .25), rim=1.4, shadow=False, hl=None, round_=False)
    for a in (0, 60, 120):
        c.flat(rrect(18.6, 9, 2.8, 22, 1.4).rotate(a, 20, 20), kit.dk(kit.STEEL, .25))
    c.vinyl(circle(20, 20, 4.5), kit.RED, rim=1.2, shadow=False, hl=None)
    c.flat(circle(14, 13, 2.2), kit.WHITE, op=.8)
    return c.svg()


def locomotive():
    """200 x 140, facing right. Cab window x 20..66, y 30..70 (the driver sits there, drawn by the
    app); chimney top at x 151, y 22 (the smoke starts there); wheels at x 42 (r 21), 108 and 152
    (r 17), y 116, drawn by the app."""
    c = kit.Ctx(200, 140)
    red = kit.RED
    c.flat(rrect(14, 104, 172, 12, 6), kit.dk(kit.STEEL, .35))
    # The cowcatcher.
    c.vinyl(poly([(170, 92), (196, 112), (196, 118), (166, 118)]), kit.GOLD, rim=2, hl=None)
    # The boiler.
    c.vinyl(rrect(70, 50, 112, 56, 26), red, rim=2.6, hl=(.18, .2))
    for x in (100, 132):
        c.flat(rrect(x, 51, 7, 54, 3), kit.dk(red, .25), op=.55)
    # The chimney and the dome.
    c.vinyl(rrect(141, 30, 20, 26, 5), kit.dk(kit.STEEL, .2), rim=2, hl=(.25, .2))
    c.vinyl(rrect(136, 20, 30, 12, 6), kit.dk(kit.STEEL, .35), rim=2, hl=(.2, .25))
    c.vinyl(ellipse(110, 48, 13, 11), kit.GOLD, rim=2, hl=(.3, .25))
    # The lamp at the front.
    c.vinyl(circle(184, 70, 9), kit.YELLOW, rim=2, hl=(.3, .25))
    c.flat(circle(184, 70, 4.5), kit.WHITE, op=.85)
    # The cab: a wall with a big window and a roof.
    c.vinyl(rrect(8, 22, 72, 86, 14), red, rim=2.6, hl=None)
    c.flat(rrect(18, 28, 50, 46, 10), kit.rim_of(red), op=.6)
    c.fill(rrect(20, 30, 46, 42, 9), c.linear(0, 30, 0, 72, [(0, "#CFEFFF", 1), (1, "#FFF6E6", 1)]))
    c.vinyl(rrect(0, 10, 88, 16, 8), kit.dk(red, .2), rim=2.4, hl=(.12, .3))
    c.vinyl(rrect(22, 82, 42, 14, 7), kit.GOLD, rim=1.8, hl=None, shadow=False)
    return c.svg()


def smoke():
    c = kit.Ctx(44, 32)
    s = circle(14, 18, 11) + circle(26, 13, 12) + circle(33, 21, 9)
    c.vinyl(s, "#F4F1FA", rim=1.6, shadow=False, hl=(.28, .22), rim_col="#B9B3C9")
    return c.svg()


def track():
    """A piece of track 120 x 22 (rails along y 6 and 14); pieces join end to end."""
    c = kit.Ctx(120, 22)
    for x in range(4, 120, 20):
        c.vinyl(rrect(x, 2, 12, 18, 3), kit.BROWN, rim=1.4, shadow=False, hl=None, round_=False)
    for y in (5, 13):
        c.flat(rect(0, y + 1.2, 120, 3), "#4C4860")
        c.flat(rect(0, y, 120, 2), "#A7A3BA")
    return c.svg()


def flag(col=kit.RED):
    c = kit.Ctx(40, 50)
    c.vinyl(rrect(6, 4, 5, 44, 2.5), kit.TAN, rim=1.4, hl=None, shadow=False)
    c.vinyl(poly([(11, 6), (36, 14), (11, 24)]), col, rim=1.8, hl=(.25, .3), shadow=False)
    c.vinyl(circle(8.5, 5, 4), kit.GOLD, rim=1.2, hl=None, shadow=False)
    return c.svg()


def sign():
    """A station sign 160 x 64 (the app writes the name on its board, x 10..150, y 6..44)."""
    c = kit.Ctx(160, 64)
    for x in (34, 120):
        c.vinyl(rrect(x, 36, 7, 26, 3), kit.STEEL, rim=1.4, hl=None)
    c.vinyl(rrect(6, 4, 148, 40, 14), kit.CREAM, rim=2.4, hl=(.08, .2), rim_col="#B68A5C")
    return c.svg()


def station():
    """The station building (the rest screen), 220 x 150."""
    c = kit.Ctx(220, 150)
    c.vinyl(rrect(20, 52, 180, 92, 12), "#F7E2B6", rim=2.4, hl=None)
    c.vinyl(Shape([("M", 6, 58), ("L", 110, 10), ("L", 214, 58), ("Z",)]) + rrect(4, 50, 212, 14, 7), kit.RED, rim=2.6, hl=(.2, .5))
    c.vinyl(circle(110, 40, 12), kit.CREAM, rim=2, hl=(.3, .25), shadow=False)
    c.stroke(Shape([("M", 110, 40), ("L", 110, 32)]), kit.INK, 2.4)
    c.stroke(Shape([("M", 110, 40), ("L", 116, 43)]), kit.INK, 2.4)
    for x in (36, 150):
        c.vinyl(rrect(x, 74, 34, 30, 7), "#FFE6A0", rim=2, hl=(.25, .25), shadow=False)
    c.vinyl(rrect(92, 82, 36, 62, 10), kit.dk(kit.SKY, .3), rim=2.2, hl=(.25, .15), shadow=False)
    c.vinyl(rrect(54, 118, 112, 8, 4), kit.BROWN, rim=1.6, hl=None, shadow=False)
    return c.svg()


# ---------------------------------------------------------------- the drivers
def driver(kind):
    """100 x 100, head and shoulders in a driver's cap; the face's middle at (50, 52)."""
    c = kit.Ctx(100, 100)
    draw_driver(c, kind)
    return c.svg()


def draw_driver(c, kind):
    fur, ear_in, muzzle = {
        "bear": (kit.BROWN, kit.TAN, kit.TAN),
        "rabbit": ("#FFF4F0", kit.PINK, "#FFFFFF"),
        "cat": (kit.ORANGE, kit.PINK, "#FFE8CF"),
        "penguin": ("#3E4A78", None, "#FFFFFF"),
    }[kind]
    # Shoulders in the blue uniform, a red scarf.
    c.vinyl(rrect(18, 78, 64, 30, 18), kit.NAVY, rim=2.2, hl=(.2, .2))
    c.vinyl(poly([(38, 78), (62, 78), (50, 90)]), kit.RED, rim=1.6, hl=None, shadow=False)
    # Ears behind the head.
    if kind == "bear":
        for x in (24, 76):
            c.vinyl(circle(x, 30, 11), fur, rim=2.2, hl=None)
            c.flat(circle(x, 30, 5.5), ear_in)
    elif kind == "rabbit":
        for x, a in ((36, -12), (64, 12)):
            e = ellipse(x, 18, 8, 19).rotate(a, x, 34)
            c.vinyl(e, fur, rim=2.2, hl=None)
            c.flat(ellipse(x, 19, 3.6, 13).rotate(a, x, 34), ear_in)
    elif kind == "cat":
        for x, s in ((26, 1), (74, -1)):
            c.vinyl(poly([(x - 9 * s, 40), (x - 4 * s, 16), (x + 13 * s, 32)]), fur, rim=2.2, hl=None)
            c.flat(poly([(x - 5 * s, 35), (x - 3 * s, 23), (x + 6 * s, 32)]), ear_in)
    # The head.
    head = ellipse(50, 54, 31, 28)
    c.vinyl(head, fur, rim=2.4, hl=(.22, .3), hl_size=.8)
    if kind == "penguin":
        c.flat(smooth([(30, 58), (38, 44), (50, 50), (62, 44), (70, 58), (64, 74), (50, 79), (36, 74)]), "#FFFFFF")
    # The cap (a conductor's cap: crown, badge, brim).
    c.vinyl(rrect(26, 20, 48, 18, 8), kit.NAVY, rim=2.2, hl=(.2, .25), shadow=False)
    c.vinyl(rrect(22, 33, 56, 8, 4), kit.dk(kit.NAVY, .3), rim=1.8, hl=None, shadow=False)
    c.vinyl(circle(50, 27, 4.2), kit.GOLD, rim=1.2, hl=None, shadow=False)
    # The face.
    if kind == "bear":
        c.vinyl(ellipse(50, 66, 12, 9), muzzle, rim=1.4, hl=None, shadow=False, round_=False)
        c.flat(ellipse(50, 62, 4.6, 3.4), kit.INK)
        c.stroke(arc(46, 66, 4, 20, 120), kit.INK, 1.6)
        c.stroke(arc(54, 66, 4, 60, 160), kit.INK, 1.6)
        c.eyes(50, 53, 24, r=3.6)
        c.cheeks(50, 64, 40, 4.5)
    elif kind == "rabbit":
        c.eyes(50, 54, 24, r=3.6)
        c.cheeks(50, 64, 40, 5)
        c.flat(ellipse(50, 62, 3.6, 2.8), kit.ROSE)
        c.stroke(arc(46.5, 64, 3.5, 20, 130), kit.INK, 1.5)
        c.stroke(arc(53.5, 64, 3.5, 50, 160), kit.INK, 1.5)
    elif kind == "cat":
        c.flat(ellipse(50, 66, 13, 9), muzzle, op=.9)
        c.eyes(50, 53, 24, r=3.6)
        c.flat(poly([(46.5, 61), (53.5, 61), (50, 64.5)]), kit.ROSE)
        c.stroke(arc(46.5, 65, 3.5, 20, 130), kit.INK, 1.5)
        c.stroke(arc(53.5, 65, 3.5, 50, 160), kit.INK, 1.5)
        for y, d in ((62, -2), (67, 2)):
            c.stroke(Shape([("M", 32, y + d), ("L", 22, y + d * 2)]), kit.dk(kit.ORANGE, .5), 1.3)
            c.stroke(Shape([("M", 68, y + d), ("L", 78, y + d * 2)]), kit.dk(kit.ORANGE, .5), 1.3)
        c.cheeks(50, 63, 42, 4.5)
    else:
        c.eyes(50, 56, 22, r=3.6)
        c.vinyl(ellipse(50, 65, 7, 4.5), kit.ORANGE, rim=1.4, hl=None, shadow=False, round_=False)
        c.cheeks(50, 64, 34, 4.5)


def build():
    for i, col in enumerate(kit.STATIONS):
        kit.write_svg(OUT / f"carriage_{i}.svg", carriage(col))
    kit.write_svg(OUT / "carriage_ghost.svg", carriage(None, ghost=True))
    kit.write_svg(OUT / "locomotive.svg", locomotive())
    kit.write_svg(OUT / "wheel.svg", wheel())
    kit.write_svg(OUT / "smoke.svg", smoke())
    kit.write_svg(OUT / "track.svg", track())
    kit.write_svg(OUT / "flag.svg", flag())
    kit.write_svg(OUT / "sign.svg", sign())
    kit.write_svg(OUT / "station.svg", station())
    for d in ("bear", "rabbit", "cat", "penguin"):
        kit.write_svg(OUT / f"driver_{d}.svg", driver(d))
    print("train: done")


if __name__ == "__main__":
    build()
