"""The buttons' pictures and the bits of scenery (docs/art.md 「按鈕和風景」): one icon per thing to
do at a station, a lock, a check, a big speaker, a sticker star; the sun, clouds, the moon, stars,
hills and a tunnel for the screens' backgrounds.
"""
import math
import sys

sys.dont_write_bytecode = True

import kit  # noqa: E402
from kit import Shape, arc, circle, ellipse, poly, rect, rrect, star  # noqa: E402

ICONS = kit.ART / "icons"
HOME = kit.ART / "home"


def mini_carriage(c, x, y, w, col):
    """A small carriage (w wide) with its two wheels."""
    h = w * .66
    c.vinyl(rrect(x, y, w, h, w * .16), col, rim=2.2, hl=(.15, .15), hl_size=.8)
    c.fill(rrect(x + w * .17, y + h * .16, w * .66, h * .56, w * .1), c.linear(0, y, 0, y + h, [(0, "#FFFFFF", 1), (1, "#FFF1DD", 1)]))
    for k in (.27, .73):
        c.vinyl(circle(x + w * k, y + h + w * .06, w * .12), "#43405A", rim=1.4, hl=None, shadow=False)
        c.flat(circle(x + w * k, y + h + w * .06, w * .045), kit.GOLD)


def icon_see():
    c = kit.Ctx(96, 96)
    mini_carriage(c, 14, 22, 68, kit.PINK)
    c.vinyl(circle(48, 44, 11), kit.SKY, rim=1.6, hl=(.3, .3), shadow=False)
    c.flat(circle(48, 44, 5), kit.INK)
    c.sparkle(80, 16, 9, kit.YELLOW)
    c.sparkle(16, 18, 6, kit.YELLOW)
    return c.svg()


def speaker(c, x, y, s, col=kit.ORANGE):
    """A round speaker button with sound waves (s: its radius)."""
    c.vinyl(circle(x, y, s), col, rim=2.4, hl=(.25, .2))
    body = Shape([("M", x - s * .45, y - s * .2), ("L", x - s * .2, y - s * .2), ("L", x + s * .12, y - s * .5), ("L", x + s * .12, y + s * .5),
                  ("L", x - s * .2, y + s * .2), ("L", x - s * .45, y + s * .2), ("Z",)])
    c.flat(body, kit.WHITE)
    for k, r in enumerate((.32, .55)):
        c.stroke(arc(x + s * .12, y, s * r, -50, 50), kit.WHITE, s * .1)


def icon_listen():
    c = kit.Ctx(96, 96)
    speaker(c, 42, 50, 30)
    for k, r in enumerate((10, 18)):
        c.stroke(arc(70, 50, r, -45, 45), kit.ORANGE, 4, op=.9)
    return c.svg()


def icon_spell():
    c = kit.Ctx(96, 96)
    mini_carriage(c, 4, 30, 42, kit.PINK)
    mini_carriage(c, 50, 30, 42, kit.SKY)
    c.vinyl(rrect(42, 44, 12, 6, 3), kit.STEEL, rim=1.2, hl=None, shadow=False)
    return c.svg()


def icon_write():
    c = kit.Ctx(96, 96)
    c.vinyl(rrect(8, 18, 60, 66, 12), kit.GREEN, rim=2.2, hl=(.15, .12))
    c.flat(rrect(16, 26, 44, 50, 9), "#FFFFFF")
    c.stroke(Shape([("M", 26, 38), ("L", 50, 38), ("C", 50, 54, 46, 64, 34, 66)]), "#F2545B", 5)
    c.flat(circle(26, 38, 4), kit.LEAF)
    pen = rrect(66, 8, 14, 62, 6).rotate(28, 73, 40)
    c.vinyl(pen, kit.YELLOW, rim=2, hl=None)
    c.vinyl(poly([(52.5, 64), (62.5, 70), (51, 80)]), "#F7D7B0", rim=1.6, hl=None, shadow=False)
    c.flat(circle(52.5, 77, 2.4), kit.INK)
    return c.svg()


def icon_rhyme():
    c = kit.Ctx(96, 96)
    mini_carriage(c, 4, 44, 40, kit.ORANGE)
    mini_carriage(c, 50, 44, 40, kit.ORANGE)
    c.vinyl(rrect(40, 57, 14, 6, 3), kit.STEEL, rim=1.2, hl=None, shadow=False)
    for x, y, col in ((30, 22, kit.ROSE), (62, 14, kit.BLUE)):
        c.vinyl(ellipse(x, y + 16, 7, 5.5).rotate(-20, x, y + 16), col, rim=1.6, hl=None, shadow=False)
        c.flat(rect(x + 5, y - 2, 3, 18), col)
        c.flat(Shape([("M", x + 8, y - 2), ("C", x + 18, y + 2, x + 16, y + 8, x + 12, y + 10), ("L", x + 8, y + 4), ("Z",)]), col)
    return c.svg()


def icon_find():
    c = kit.Ctx(96, 96)
    house = Shape([("M", 10, 46), ("L", 40, 18), ("L", 70, 46), ("Z",)])
    c.vinyl(rrect(16, 42, 48, 40, 6), "#FFE6A0", rim=2, hl=None)
    c.vinyl(house, kit.RED, rim=2.2, hl=(.3, .5))
    c.vinyl(rrect(32, 58, 16, 24, 5), kit.BROWN, rim=1.6, hl=None, shadow=False)
    c.vinyl(rrect(66, 64, 10, 30, 5).rotate(-40, 70, 70), kit.BROWN, rim=1.8, hl=None)
    c.vinyl(circle(62, 56, 20), "#CFEFFF", rim=3, hl=(.28, .25), rim_col="#3A4E8C")
    return c.svg()


def icon_lock():
    c = kit.Ctx(64, 64)
    c.stroke(Shape([("M", 20, 30), ("L", 20, 22), ("C", 20, 8, 44, 8, 44, 22), ("L", 44, 30)]), "#7E7A96", 7)
    c.vinyl(rrect(12, 28, 40, 30, 8), kit.GOLD, rim=2, hl=(.2, .2))
    c.flat(circle(32, 40, 4), kit.INK)
    c.flat(rrect(30.5, 42, 3, 8, 1.5), kit.INK)
    return c.svg()


def icon_check():
    c = kit.Ctx(48, 48)
    c.vinyl(circle(24, 24, 20), kit.LEAF, rim=2, hl=(.25, .2), shadow=False)
    c.stroke(Shape([("M", 14, 25), ("L", 21, 32), ("L", 34, 17)]), kit.WHITE, 5)
    return c.svg()


def icon_star():
    c = kit.Ctx(64, 64)
    c.vinyl(star(32, 34, 28, 13), kit.YELLOW, rim=2.4, hl=(.3, .3))
    return c.svg()


def icon_speaker():
    c = kit.Ctx(96, 96)
    speaker(c, 48, 48, 40)
    return c.svg()




# ---------------------------------------------------------------- scenery
def sun():
    c = kit.Ctx(100, 100)
    for k in range(10):
        a = math.radians(k * 36)
        c.vinyl(ellipse(50 + 40 * math.cos(a), 50 + 40 * math.sin(a), 7, 5).rotate(k * 36, 50 + 40 * math.cos(a), 50 + 40 * math.sin(a)), kit.ORANGE, rim=1.4, hl=None, shadow=False)
    c.vinyl(circle(50, 50, 30), kit.YELLOW, rim=2.4, hl=(.28, .25), shadow=False)
    c.face(50, 52, 16)
    return c.svg()


def cloud(w=120, h=64):
    c = kit.Ctx(w, h)
    s = circle(w * .3, h * .62, h * .3) + circle(w * .52, h * .45, h * .38) + circle(w * .74, h * .62, h * .28) + rrect(w * .1, h * .55, w * .8, h * .38, h * .19)
    c.vinyl(s, kit.WHITE, rim=2, hl=(.3, .25), shadow=False, rim_col="#B7C8E6")
    return c.svg()


def moon():
    c = kit.Ctx(100, 100)
    m = Shape([("M", 62, 8), ("C", 30, 10, 14, 40, 22, 66), ("C", 30, 92, 70, 100, 92, 74), ("C", 58, 80, 36, 50, 62, 8), ("Z",)])
    c.vinyl(m, "#FFE68A", rim=2.4, hl=(.3, .3), shadow=False)
    c.eyes(40, 56, 12, closed=True)
    c.cheeks(40, 64, 22, 3.5)
    return c.svg()


def night_star():
    c = kit.Ctx(40, 40)
    c.vinyl(star(20, 21, 17, 8), "#FFE68A", rim=1.6, hl=(.3, .3), shadow=False)
    return c.svg()


def hills():
    """A long strip of hills (400 x 90) for the bottom of a screen."""
    c = kit.Ctx(400, 90)
    back = Shape([("M", 0, 90), ("L", 0, 50), ("C", 50, 20, 110, 20, 160, 46), ("C", 210, 18, 290, 14, 340, 44), ("C", 365, 34, 385, 34, 400, 40),
                  ("L", 400, 90), ("Z",)])
    c.vinyl(back, "#A6E08F", rim=2, hl=None, shadow=False)
    front = Shape([("M", 0, 90), ("L", 0, 66), ("C", 60, 48, 120, 52, 200, 66), ("C", 260, 50, 340, 46, 400, 62), ("L", 400, 90), ("Z",)])
    c.vinyl(front, "#7FD08A", rim=2, hl=None, shadow=False)
    for x, y in ((60, 40), (250, 34), (330, 42)):
        c.vinyl(circle(x, y, 10), kit.LEAF, rim=1.4, hl=(.3, .3), shadow=False)
        c.flat(rect(x - 1.5, y + 8, 3, 8), kit.BROWN)
    return c.svg()


def tunnel():
    """The tunnel the train goes through between stations (160 x 120)."""
    c = kit.Ctx(160, 120)
    hill = Shape([("M", 0, 120), ("C", 0, 30, 40, 4, 80, 4), ("C", 120, 4, 160, 30, 160, 120), ("Z",)])
    c.vinyl(hill, "#7FD08A", rim=2.4, hl=(.25, .15), shadow=False)
    c.vinyl(Shape([("M", 34, 120), ("C", 34, 54, 126, 54, 126, 120), ("Z",)]), "#B9A99A", rim=2.2, hl=None, shadow=False)
    c.flat(Shape([("M", 46, 120), ("C", 46, 68, 114, 68, 114, 120), ("Z",)]), "#3B3550")
    return c.svg()


def build():
    for name, fn in (("see", icon_see), ("listen", icon_listen), ("spell", icon_spell), ("write", icon_write), ("rhyme", icon_rhyme),
                     ("find", icon_find), ("lock", icon_lock), ("check", icon_check), ("star", icon_star), ("speaker", icon_speaker)):
        kit.write_svg(ICONS / f"{name}.svg", fn())
    kit.write_svg(HOME / "sun.svg", sun())
    kit.write_svg(HOME / "cloud.svg", cloud())
    kit.write_svg(HOME / "moon.svg", moon())
    kit.write_svg(HOME / "star.svg", night_star())
    kit.write_svg(HOME / "hills.svg", hills())
    kit.write_svg(HOME / "tunnel.svg", tunnel())
    print("ui: done")


if __name__ == "__main__":
    build()
