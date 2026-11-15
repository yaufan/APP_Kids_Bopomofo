"""Soft-vinyl toy drawing kit for ㄅㄆㄇ小火車 (軟膠公仔風).

Everything is a glossy vinyl toy (Sonny Angel, Playmobil): saturated colour with a top-to-bottom
gradient, a 2–3 unit darker rim, a soft roundness towards the edges, one big and one small white
highlight near the top left, and a plain offset shadow below and to the right. Only plain paths with
fill / stroke / opacity and linear / radial gradients, so flutter_svg draws what Chromium draws (no
filter, mask, clipPath, style, text, image or pattern; docs/art.md). The 注音 symbols are never drawn
here: the app writes them with the font on top of the art.

    import kit
    c = kit.Ctx(120, 100)                                # viewBox 0 0 120 100
    c.vinyl(kit.rrect(10, 20, 100, 60, 18), kit.PINK)    # shadow + rim + glossy body + highlights
    c.vinyl(kit.circle(60, 30, 12), kit.YELLOW, shadow=False, hl=(.3, .25))
    c.flat(kit.circle(60, 30, 4), kit.WHITE, op=.8)      # flat paint
    c.stroke(kit.arc(60, 50, 8, 20, 160), kit.INK, 3)    # a line
    c.eyes(60, 40, 10); c.smile(60, 48, 6)               # a toy's face
    kit.write_svg(path, c.svg())                         # checks the rules, then writes

Shapes (`Shape`) are lists of path commands; `+` unions them (all clockwise, nonzero fill),
`.move .scale .flip .rotate`. A union's rim is a stroke drawn behind the body, so the seams inside
it never show. Deterministic: gradient ids are hashes, randomness only via `rnd(key)`.
"""
import colorsys
import hashlib
import math
import pathlib
import random
import re
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ART = ROOT / "app" / "assets" / "art"

# ---------------------------------------------------------------- palette (saturated toy colours)
INK = "#2E2440"        # eyes, lines: a deep plum-navy (never pure black)
CREAM = "#FFF6E6"
WHITE = "#FFFFFF"
RED = "#F2545B"        # the locomotive
PINK = "#F59BC2"
ROSE = "#EE6E9C"
ORANGE = "#FFA35C"
YELLOW = "#FFD44F"
GOLD = "#FFB627"
GREEN = "#7FD08A"
LEAF = "#4DBA6A"
TEAL = "#4FD1C5"
SKY = "#8CCBF2"
BLUE = "#4E9DF0"
NAVY = "#3A4E8C"
PURPLE = "#B79AF0"
BROWN = "#B9784A"
TAN = "#E8B98A"
SKIN = "#FFD3B0"
GREY = "#B8B4C4"
STEEL = "#7E8AA6"
CHEEK = "#FF8FA3"
MOUTH = "#C93D5A"
SEA = "#7CCDF0"
SHADOW = "#2E2440"

STATIONS = ["#8CCBF2", "#F59BC2", "#7FD08A", "#FFD44F", "#FFA35C", "#B79AF0", "#4FD1C5"]


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def _hex(r, g, b):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in (r, g, b))


def mix(a, b, t):
    """Colour a moved t (0..1) of the way to colour b."""
    return _hex(*[x + (y - x) * t for x, y in zip(_rgb(a), _rgb(b))])


def lt(c, t):
    return mix(c, "#FFFFFF", t)


def dk(c, t):
    return mix(c, INK, t)


def rim_of(c):
    """The darker rim colour of a toy part."""
    return tone(mix(c, INK, .48), s=1.15)


def tone(c, l=1.0, s=1.0, dh=0.0):
    h, L, S = colorsys.rgb_to_hls(*[x / 255 for x in _rgb(c)])
    r, g, b = colorsys.hls_to_rgb((h + dh) % 1, max(0, min(1, L * l)), max(0, min(1, S * s)))
    return _hex(r * 255, g * 255, b * 255)


def rnd(*key):
    h = hashlib.md5("|".join(map(str, key)).encode()).hexdigest()
    return random.Random(int(h[:12], 16))


# ---------------------------------------------------------------- numbers
def n(v):
    """A number, short: one decimal, no trailing .0, no -0."""
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    if s == "-0":
        s = "0"
    return s


# ---------------------------------------------------------------- shapes
KAPPA = 0.5522847498


class Shape:
    """Path commands: ('M', x, y) ('L', x, y) ('C', x1, y1, x2, y2, x, y) ('Z',). All shapes the kit
    makes wind clockwise on screen, so unions (`a + b`) fill with the default nonzero rule."""

    def __init__(self, cmds=None):
        self.cmds = list(cmds or [])

    def __add__(self, other):
        return Shape(self.cmds + other.cmds)

    def move(self, dx, dy):
        return self.map(lambda x, y: (x + dx, y + dy))

    def scale(self, s, cx=0.0, cy=0.0, sy=None):
        sy = s if sy is None else sy
        return self.map(lambda x, y: (cx + (x - cx) * s, cy + (y - cy) * sy))

    def flip(self, cx):
        """Mirror left-right about x = cx (winding is fixed afterwards)."""
        return self.map(lambda x, y: (2 * cx - x, y)).reverse()

    def rotate(self, deg, cx, cy):
        a = math.radians(deg)
        ca, sa = math.cos(a), math.sin(a)
        return self.map(lambda x, y: (cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca))

    def map(self, f):
        out = []
        for c in self.cmds:
            if c[0] == "Z":
                out.append(c)
            else:
                pts = [f(c[i], c[i + 1]) for i in range(1, len(c), 2)]
                out.append((c[0],) + tuple(v for p in pts for v in p))
        return Shape(out)

    def reverse(self):
        """The same outline the other way round (one subpath at a time)."""
        out = []
        for sub in self.subpaths():
            pts = []   # (point, incoming control pair or None)
            cur = None
            for c in sub:
                if c[0] == "M":
                    cur = (c[1], c[2])
                    pts.append((cur, None))
                elif c[0] == "L":
                    cur = (c[1], c[2])
                    pts.append((cur, None))
                elif c[0] == "C":
                    cur = (c[5], c[6])
                    pts.append((cur, (c[1], c[2], c[3], c[4])))
            rev = pts[::-1]
            out.append(("M",) + rev[0][0])
            for i in range(1, len(rev)):
                p, _ = rev[i]
                _, ctrl = rev[i - 1]      # the control pair that led INTO rev[i-1] from rev[i]
                if ctrl is None:
                    out.append(("L",) + p)
                else:
                    out.append(("C", ctrl[2], ctrl[3], ctrl[0], ctrl[1]) + p)
            out.append(("Z",))
        return Shape(out)

    def subpaths(self):
        subs, cur = [], []
        for c in self.cmds:
            if c[0] == "M" and cur:
                subs.append(cur)
                cur = []
            cur.append(c)
        if cur:
            subs.append(cur)
        return subs

    def bbox(self):
        xs = [c[i] for c in self.cmds if c[0] != "Z" for i in range(1, len(c), 2)]
        ys = [c[i] for c in self.cmds if c[0] != "Z" for i in range(2, len(c), 2)]
        return min(xs), min(ys), max(xs), max(ys)

    def d(self, dx=0.0, dy=0.0):
        out = []
        for c in self.cmds:
            if c[0] == "Z":
                out.append("Z")
            else:
                nums = [n(c[i] + (dx if i % 2 else dy)) for i in range(1, len(c))]
                out.append(c[0] + " ".join(nums))
        return "".join(out)


def poly(points, close=True):
    """A polygon through points (any winding; it is made clockwise)."""
    pts = [tuple(p) for p in points]
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area < 0:      # counter-clockwise on screen (y down) -> reverse
        pts = pts[::-1]
    cmds = [("M",) + pts[0]] + [("L",) + p for p in pts[1:]]
    if close:
        cmds.append(("Z",))
    return Shape(cmds)


def rrect(x, y, w, h, r=8.0, rtl=None, rtr=None, rbr=None, rbl=None):
    """A rounded rectangle; corner radii can differ."""
    r = min(r, w / 2, h / 2)
    a, b, c_, d = [min(v if v is not None else r, w / 2, h / 2) for v in (rtl, rtr, rbr, rbl)]
    k = KAPPA
    cmds = [("M", x + a, y), ("L", x + w - b, y)]
    if b:
        cmds.append(("C", x + w - b + b * k, y, x + w, y + b - b * k, x + w, y + b))
    cmds.append(("L", x + w, y + h - c_))
    if c_:
        cmds.append(("C", x + w, y + h - c_ + c_ * k, x + w - c_ + c_ * k, y + h, x + w - c_, y + h))
    cmds.append(("L", x + d, y + h))
    if d:
        cmds.append(("C", x + d - d * k, y + h, x, y + h - d + d * k, x, y + h - d))
    cmds.append(("L", x, y + a))
    if a:
        cmds.append(("C", x, y + a - a * k, x + a - a * k, y, x + a, y))
    cmds.append(("Z",))
    return Shape(cmds)


def rect(x, y, w, h):
    return rrect(x, y, w, h, 0)


def ellipse(cx, cy, rx, ry=None):
    ry = rx if ry is None else ry
    k = KAPPA
    return Shape([
        ("M", cx + rx, cy),
        ("C", cx + rx, cy + ry * k, cx + rx * k, cy + ry, cx, cy + ry),
        ("C", cx - rx * k, cy + ry, cx - rx, cy + ry * k, cx - rx, cy),
        ("C", cx - rx, cy - ry * k, cx - rx * k, cy - ry, cx, cy - ry),
        ("C", cx + rx * k, cy - ry, cx + rx, cy - ry * k, cx + rx, cy),
        ("Z",)])


def circle(cx, cy, r):
    return ellipse(cx, cy, r, r)


def smooth(points, tension=0.5):
    """A closed, smooth (Catmull-Rom) curve through points, clockwise."""
    pts = [tuple(p) for p in points]
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area < 0:
        pts = pts[::-1]
    m = len(pts)
    cmds = [("M",) + pts[0]]
    for i in range(m):
        p0, p1, p2, p3 = pts[(i - 1) % m], pts[i], pts[(i + 1) % m], pts[(i + 2) % m]
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 3, p1[1] + (p2[1] - p0[1]) * tension / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 3, p2[1] - (p3[1] - p1[1]) * tension / 3)
        cmds.append(("C",) + c1 + c2 + p2)
    cmds.append(("Z",))
    return Shape(cmds)


def blob(cx, cy, rx, ry=None, lumps=7, wobble=0.12, key="blob"):
    """A soft potato shape (a bush, a cushion, a cloud body): an ellipse with seeded bumps."""
    ry = rx if ry is None else ry
    r = rnd("blob", key, lumps)
    pts = []
    for i in range(lumps):
        a = 2 * math.pi * i / lumps
        f = 1 + r.uniform(-wobble, wobble)
        pts.append((cx + rx * f * math.cos(a), cy + ry * f * math.sin(a)))
    return smooth(pts, 0.9)


def cloud(cx, cy, w, h, puffs=4):
    """A cloud / bush: a flat base with round puffs on top (a union of shapes)."""
    s = rrect(cx - w / 2, cy - h * .1, w, h * .6, h * .3)
    for i in range(puffs):
        t = (i + .5) / puffs
        px = cx - w / 2 + w * t
        pr = h * (.42 if i % 2 == 0 else .34)
        s = s + circle(px, cy - h * .15 + (0 if i % 2 == 0 else h * .1), pr)
    return s


def star(cx, cy, R, r=None, points=5, rot=-90.0):
    r = R * .48 if r is None else r
    pts = []
    for i in range(points * 2):
        a = math.radians(rot + 180.0 * i / points)
        rad = R if i % 2 == 0 else r
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return poly(pts)


def heart(cx, cy, s):
    """A heart about s wide, centred on cx, cy."""
    w, h = s, s * .95
    x0, y0 = cx, cy - h * .3          # the notch
    return Shape([
        ("M", x0, y0),
        ("C", x0 + w * .1, y0 - h * .3, x0 + w * .5, y0 - h * .3, x0 + w * .5, y0 + h * .05),
        ("C", x0 + w * .5, y0 + h * .4, x0 + w * .15, y0 + h * .55, x0, y0 + h * .75),
        ("C", x0 - w * .15, y0 + h * .55, x0 - w * .5, y0 + h * .4, x0 - w * .5, y0 + h * .05),
        ("C", x0 - w * .5, y0 - h * .3, x0 - w * .1, y0 - h * .3, x0, y0),
        ("Z",)])


def path(points, closed=False):
    """An open polyline (for strokes) or closed polygon."""
    pts = [tuple(p) for p in points]
    cmds = [("M",) + pts[0]] + [("L",) + p for p in pts[1:]]
    if closed:
        cmds.append(("Z",))
    return Shape(cmds)


def arc(cx, cy, r, a0, a1, steps=None):
    """An open arc (degrees, clockwise on screen) made of cubic pieces, for smiles and the like."""
    span = a1 - a0
    steps = steps or max(1, int(abs(span) / 90) + 1)
    cmds = []
    for i in range(steps):
        t0 = math.radians(a0 + span * i / steps)
        t1 = math.radians(a0 + span * (i + 1) / steps)
        k = 4 / 3 * math.tan((t1 - t0) / 4)
        p0 = (cx + r * math.cos(t0), cy + r * math.sin(t0))
        p3 = (cx + r * math.cos(t1), cy + r * math.sin(t1))
        p1 = (p0[0] - k * r * math.sin(t0), p0[1] + k * r * math.cos(t0))
        p2 = (p3[0] + k * r * math.sin(t1), p3[1] - k * r * math.cos(t1))
        if i == 0:
            cmds.append(("M",) + p0)
        cmds.append(("C",) + p1 + p2 + p3)
    return Shape(cmds)


def ring(cx, cy, r_out, r_in):
    """A ring (needs even-odd: pass rule='evenodd' to flat())."""
    return circle(cx, cy, r_out) + circle(cx, cy, r_in)


def soft_rect(x, y, w, h):
    """A pill / very round rectangle (the usual marshmallow block)."""
    return rrect(x, y, w, h, min(w, h) * .45)


def puffs(cx, cy, w, h, n=5, key="puffs"):
    """A cloud: a soft base with round puffs on top, n puffs, seeded sizes."""
    r = rnd("puffs", key, n)
    s = rrect(cx - w / 2, cy - h * .05, w, h * .55, h * .27)
    for i in range(n):
        t = (i + .5) / n
        px = cx - w / 2 + w * (.08 + .84 * t)
        pr = h * (.30 + .14 * math.sin(math.pi * t)) * r.uniform(.9, 1.1)
        s = s + circle(px, cy - h * .02 - pr * .35, pr)
    return s


# ---------------------------------------------------------------- the SVG writer
class Ctx:
    """One SVG file being drawn: viewBox 0 0 w h. Gradients go into <defs> (ids are hashes of their
    content, so files are deterministic)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.body = []
        self.defs = {}
        self._open = 0

    # ---- gradients
    def _grad(self, kind, attrs, stops):
        st = "".join(f'<stop offset="{o:g}" stop-color="{c}"' + (f' stop-opacity="{a:.2f}"' if a < 1 else "") + "/>"
                     for o, c, a in stops)
        key = hashlib.md5((kind + attrs + st).encode()).hexdigest()[:8]
        gid = f"g{key}"
        self.defs.setdefault(gid, f'<{kind} id="{gid}" gradientUnits="userSpaceOnUse" {attrs}>{st}</{kind}>')
        return f"url(#{gid})"

    def linear(self, x1, y1, x2, y2, stops):
        """stops: [(offset, colour, opacity)]."""
        return self._grad("linearGradient", f'x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}"', stops)

    def radial(self, cx, cy, r, stops):
        return self._grad("radialGradient", f'cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"', stops)

    # ---- raw
    def path_el(self, d, fill="none", stroke=None, sw=0.0, op=1.0, cap="round"):
        a = [f'd="{d}"', f'fill="{fill}"']
        if stroke:
            a += [f'stroke="{stroke}"', f'stroke-width="{n(sw)}"', f'stroke-linecap="{cap}"', 'stroke-linejoin="round"']
        if op < 1:
            a.append(f'fill-opacity="{op:.2f}"' if fill != "none" else f'stroke-opacity="{op:.2f}"')
        self.body.append("<path " + " ".join(a) + "/>")

    # ---- the vinyl toy
    def shadow(self, shape, dx=2.5, dy=3.5, op=.16):
        """The same shape moved down and right, faint (docs/design.md 「影子」)."""
        self.path_el(shape.d(dx, dy), SHADOW, op=op)

    def vinyl(self, shape, col, rim=2.4, shadow=True, hl=(.3, .22), hl_size=1.0, gloss=True, round_=True, op=1.0,
              sh=(2.5, 3.5), rim_col=None):
        """One glossy vinyl part: offset shadow, darker rim (a stroke behind the body), a body lit
        from the top (linear gradient), roundness towards the edges (a radial overlay) and two white
        highlights at hl (fractions of the bounding box; None for none)."""
        if shadow:
            self.shadow(shape, *sh)
        d = shape.d()
        x0, y0, x1, y1 = shape.bbox()
        w, h = x1 - x0, y1 - y0
        if rim:
            self.path_el(d, "none", rim_col or rim_of(col), rim * 2, op=op)
        self.path_el(d, self.linear(0, y0, 0, y1, [(0, lt(col, .32), 1), (.45, col, 1), (1, tone(dk(col, .14), s=1.1), 1)]), op=op)
        if round_:
            r = max(w, h) * .62
            self.path_el(d, self.radial(x0 + w * .42, y0 + h * .4, r, [(.55, INK, 0), (1, INK, .2)]), op=op)
        if hl and gloss:
            self.highlight(x0 + w * hl[0], y0 + h * hl[1], min(w, h) * .2 * hl_size, op=op)

    def highlight(self, cx, cy, r, op=1.0, tilt=-28):
        """The big soft gleam and the small bright dot of a glossy toy."""
        big = ellipse(cx, cy, r * 1.25, r * .62).rotate(tilt, cx, cy)
        self.path_el(big.d(), WHITE, op=.42 * op)
        small = ellipse(cx - r * .55, cy - r * .02, r * .3, r * .22).rotate(tilt, cx - r * .55, cy)
        self.path_el(small.d(), WHITE, op=.95 * op)

    def flat(self, shape, col, op=1.0):
        self.path_el(shape.d(), col, op=op)

    def fill(self, shape, paint, op=1.0):
        """Fill with any paint (a gradient url)."""
        self.path_el(shape.d(), paint, op=op)

    def stroke(self, shape, col=INK, w=3.0, op=1.0, cap="round"):
        self.path_el(shape.d(), "none", col, w, op=op, cap=cap)

    def dots(self, points, r, col, op=1.0):
        s = Shape()
        for x, y in points:
            s = s + circle(x, y, r)
        self.flat(s, col, op)

    def sparkle(self, cx, cy, r, col=YELLOW, op=1.0):
        k = .16
        self.flat(Shape([("M", cx, cy - r), ("C", cx + r * k, cy - r * k, cx + r * k, cy - r * k, cx + r, cy),
                         ("C", cx + r * k, cy + r * k, cx + r * k, cy + r * k, cx, cy + r),
                         ("C", cx - r * k, cy + r * k, cx - r * k, cy + r * k, cx - r, cy),
                         ("C", cx - r * k, cy - r * k, cx - r * k, cy - r * k, cx, cy - r), ("Z",)]), col, op)

    # ---- a toy's face
    def eyes(self, cx, cy, gap, r=None, closed=False):
        """Two shiny black-plum eyes gap apart (or two closed arcs)."""
        r = r or gap * .2
        for x in (cx - gap / 2, cx + gap / 2):
            if closed:
                self.stroke(arc(x, cy - r * .3, r * 1.1, 200, 340), INK, r * .7)
            else:
                self.flat(ellipse(x, cy, r, r * 1.15), INK)
                self.flat(circle(x - r * .3, cy - r * .4, r * .38), WHITE)

    def cheeks(self, cx, cy, gap, r, op=.55):
        for x in (cx - gap / 2, cx + gap / 2):
            self.flat(ellipse(x, cy, r, r * .62), CHEEK, op)

    def smile(self, cx, cy, w, open_=False, col=INK):
        if open_:
            self.flat(Shape([("M", cx - w / 2, cy), ("C", cx - w * .4, cy + w * .75, cx + w * .4, cy + w * .75, cx + w / 2, cy),
                             ("Z",)]), MOUTH)
        else:
            self.stroke(arc(cx, cy - w * .45, w * .55, 35, 145), col, max(1.2, w * .16))

    def face(self, cx, cy, gap, open_=False, blush=True, closed=False):
        """Eyes, cheeks and a smile for a toy (gap: between the eyes)."""
        self.eyes(cx, cy, gap, closed=closed)
        if blush:
            self.cheeks(cx, cy + gap * .42, gap * 1.5, gap * .2)
        self.smile(cx, cy + gap * .4, gap * .55, open_)

    # ---- groups
    def begin(self, transform=None, op=None):
        a = ""
        if transform:
            a += f' transform="{transform}"'
        if op is not None:
            a += f' opacity="{op:.2f}"'
        self.body.append(f"<g{a}>")
        self._open += 1

    def end(self):
        self.body.append("</g>")
        self._open -= 1

    def svg(self):
        if self._open:
            raise SystemExit("Ctx: a <g> was not closed")
        defs = f"<defs>{''.join(self.defs[k] for k in sorted(self.defs))}</defs>" if self.defs else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n(self.w)} {n(self.h)}">'
                f'{defs}{"".join(self.body)}</svg>\n')


# ---------------------------------------------------------------- checks (docs/art.md: flutter_svg)
FORBIDDEN = ("<filter", "<mask", "<style", "style=", "class=", "<text", "<image", "<foreignObject", "<pattern",
             "mix-blend-mode", "mask=", "filter=", "vector-effect", "<symbol", "<marker", "@import", "<clipPath",
             "clip-path=")
_TOK = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_NARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}
DRAWN = {"path", "ellipse", "circle", "rect", "polygon", "polyline", "line", "use"}
MAX_KB = 70


def check_path(d):
    """ValueError unless d is path data flutter_svg reads (it drops the WHOLE picture over one bad
    path, where Chromium only skips that path)."""
    toks = _TOK.findall(d)
    if not toks or toks[0] not in "Mm":
        raise ValueError(f"path does not start with M: {d[:40]!r}")
    if len("".join(toks)) != len(re.sub(r"[\s,]", "", d)):
        raise ValueError(f"stray characters in path: {d[:60]!r}")
    i = 0
    while i < len(toks):
        cmd = toks[i]
        if not cmd.isalpha():
            raise ValueError(f"numbers without a command: {d[:60]!r}")
        i += 1
        k = _NARGS[cmd.upper()]
        j = i
        while j < len(toks) and not toks[j].isalpha():
            j += 1
        cnt = j - i
        if (k == 0 and cnt) or (k and (cnt == 0 or cnt % k)):
            raise ValueError(f"command {cmd} has {cnt} numbers: {d[:60]!r}")
        i = j


def check_svg(name, text, size=None):
    """docs/art.md's rules: no filter/mask/style/text/image/pattern/blend, every drawn element has
    fill or stroke, under 70 KB, well-formed XML ending in </svg>, viewBox 0 0 w h (= size if given),
    parseable path data. Returns the size in KB; SystemExit on a problem."""
    bad = [f for f in FORBIDDEN if f in text]
    if bad:
        raise SystemExit(f"{name}: uses {bad} (flutter_svg cannot draw these)")
    kb = len(text.encode()) / 1024
    if kb > MAX_KB:
        raise SystemExit(f"{name}: {kb:.0f} KB (keep under {MAX_KB} KB)")
    if not text.rstrip().endswith("</svg>"):
        raise SystemExit(f"{name}: does not end with </svg>")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        raise SystemExit(f"{name}: not well-formed XML: {e}")
    ns = "{http://www.w3.org/2000/svg}"
    if root.tag != f"{ns}svg":
        raise SystemExit(f"{name}: root is not <svg xmlns=...>")
    vb = root.get("viewBox")
    if not vb:
        raise SystemExit(f"{name}: no viewBox")
    vb = [float(v) for v in vb.split()]
    if vb[0] or vb[1]:
        raise SystemExit(f"{name}: viewBox must start at 0 0")
    if size and (abs(vb[2] - size[0]) > .01 or abs(vb[3] - size[1]) > .01):
        raise SystemExit(f"{name}: viewBox {vb[2]:g} x {vb[3]:g}, expected {size[0]:g} x {size[1]:g}")
    defs = root.find(f"{ns}defs")
    in_defs = {id(el) for el in defs.iter()} if defs is not None else set()
    for el in root.iter():
        tag = el.tag.replace(ns, "")
        d = el.get("d")
        if d is not None:
            try:
                check_path(d)
            except ValueError as e:
                raise SystemExit(f"{name}: {e}")
        if tag in DRAWN and id(el) not in in_defs and el.get("fill") is None and el.get("stroke") is None:
            raise SystemExit(f"{name}: a <{tag}> without fill/stroke")
        for a in ("fill", "stroke"):
            v = el.get(a)
            if v and v.startswith("url(#") and root.find(f".//*[@id='{v[5:-1]}']") is None:
                raise SystemExit(f"{name}: {a} points to a missing {v}")
    return kb


def viewbox_of(path):
    """(w, h) of an SVG file's viewBox."""
    vb = [float(v) for v in ET.parse(path).getroot().get("viewBox").split()]
    return vb[2], vb[3]


def write_svg(path, text, size=None):
    """Check, then write. Returns the size in KB."""
    path = pathlib.Path(path)
    name = str(path.relative_to(ROOT)) if ROOT in path.parents else str(path)
    kb = check_svg(name, text, size)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return kb
