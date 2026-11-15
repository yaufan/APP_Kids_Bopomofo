"""Design-stage sketches for 「ㄅㄆㄇ小火車」 (learning 注音符號, ages 4-6).

    python3 make_mockups.py          # writes docs/mockups/*.png (needs Node.js + Playwright's Chromium)
    python3 make_mockups.py 3        # only one page: 0 = style page, 1..8 = a screen, c = contact sheet

Every picture is drawn here as SVG by code: no outside pictures, no emoji. The 注音 glyphs come from the
font jf open 粉圓 2.1 (it has all 37 symbols and the tone marks), taken from a sibling app's checkout.
render.js turns each page into a PNG with Playwright's Chromium at 390x844, device scale 2.

    0_畫風選擇.png     the same scene (the engine and three carriages ㄅㄆㄇ at a little station) in
                       three styles: A 軟膠公仔風 (chosen 2026-11-15), B 糖霜餅乾風, C 色鉛筆手繪風.
                       Screens 1-8 are drawn in A. The round-1 candidates 木頭玩具風 / 磁磚馬賽克風 /
                       夜光霓虹風 were turned down; their code is still here as "wood", "mosaic" and "neon".
    1_火車站.png       home: the map of Taiwan with the seven stations, the child's own train, six buttons
    2_認符號.png       one big carriage ㄅ, the picture word 爸爸, the symbols of this station below
    3_聽聽找找.png     hear 媽媽, pick the carriage among ㄇ ㄅ ㄈ
    4_拼拼看.png       drag ㄚ onto ㄅ, four tone flags, the result 爸 boards the train
    5_寫寫看.png       trace ㄅ on a carriage: the wide grey path, the green start dot, the arrow
    6_押韻接龍.png     which two rhyme? 貓 包 魚 -> 貓 and 包 couple together
    7_家裡找找.png     the off-screen task card: find things at home that start with ㄅ
    8_家長模式.png     parents' settings and the carriage progress chart
    contact_sheet.png  screens 1-8 small, with titles

Style A 「木頭玩具風」: every piece is a sanded wooden block under a thin coat of paint. One SVG filter
does it: fractal noise stretched along the grain streaks the paint, a blurred copy of the piece's own
shape is lit from the top left so the edges look rounded, and the piece throws a soft shadow.
Style B 「磁磚馬賽克風」: the same shapes filled with small square tiles and pale grout.
Style C 「夜光霓虹風」: a night-blue background; the shapes are glowing coloured outlines.
The three new candidates use nothing a flutter_svg file cannot do (no filters):
「軟膠公仔風」 (vinyl): a strong flat colour, a dark rim stroke, a top-to-bottom gradient and two white
ellipses clipped to the shape as the glossy highlight. 「糖霜餅乾風」 (cookie): a biscuit-coloured base, a
thick pastel icing stroke clipped to the shape's edge with a thin white shine stroke inside it, a few
sprinkles; the 注音 symbols are piped in icing (a white stroke under a coloured fill). 「色鉛筆手繪風」
(pencil): a pale fill, many short hatching lines clipped to the shape, and a double slightly offset
outline so it looks hand-drawn; the paper is a dotted pattern.
"""
import hashlib
import math
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
FONT = None
for _c in ("app_kids_falsecharge", "app_kids_maze", "app_kids_live_circ", "app_kids_brainstorming", "app_kids_paint_for_learning_writing", "app_kids_card_game", "app_kids_cook"):
    for _p in (HERE.parents[3] / _c / "app" / "assets" / "fonts" / "jf-openhuninn-2.1.ttf",
               pathlib.Path("/home/user") / _c / "app" / "assets" / "fonts" / "jf-openhuninn-2.1.ttf"):
        if _p.exists():
            FONT = _p
            break
    if FONT:
        break
if FONT is None:
    sys.exit("font jf-openhuninn-2.1.ttf not found in a sibling app's checkout")
SCRATCH = pathlib.Path("/dev/shm") if pathlib.Path("/dev/shm").is_dir() else pathlib.Path(tempfile.gettempdir())
W, H = 390, 844

# ---------------------------------------------------------------- colours (style A: wood and paint)
INK = "#4A3728"
SOFT = "#9A826E"
WOOD = "#F2D7AE"
WOOD2 = "#E4BE8C"
WALNUT = "#A6764F"
DARK = "#3B2A26"
RED = "#E9655B"
YEL = "#F7C948"
ORA = "#F5924E"
BLUE = "#5FA8E0"
GRN = "#7CC26B"
PINK = "#F2A3BE"
TEAL = "#5EC4B6"
LILAC = "#B9A3E3"
CREAM = "#FFF6E3"
WHITE = "#FBF7F0"
SKY = "#CDE9F7"
GRASS = "#BFE3A0"
GREY = "#D9D2C8"
CHEEK = "#FFA8B4"
SKIN = "#FBE0CB"
BEAR = "#C98B5A"
STATION_COL = {"台北": "#9CC9EE", "桃園": PINK, "新竹": "#A9D98F", "台中": YEL, "嘉義": ORA, "台南": LILAC, "高雄": TEAL}
STATIONS = [("台北", "ㄚㄧㄨㄛㄜ"), ("桃園", "ㄅㄆㄇㄈ"), ("新竹", "ㄉㄊㄋㄌ"), ("台中", "ㄍㄎㄏ"),
            ("嘉義", "ㄞㄟㄠㄡㄢㄣㄤㄥ"), ("台南", "ㄐㄑㄒㄩㄝ"), ("高雄", "ㄓㄔㄕㄖㄗㄘㄙㄦ")]
STYLE = "vinyl"      # the chosen 軟膠公仔風. Also kept: "wood", "mosaic", "neon" (round 1) and "cookie", "pencil" (round 2), not chosen


# ---------------------------------------------------------------- defs registry and small maths
class Defs:
    def __init__(self):
        self.d = {}

    def add(self, key, svg):
        self.d.setdefault(key, svg)
        return key

    def svg(self):
        return "<defs>" + "".join(self.d.values()) + "</defs>"


D = Defs()


def _h(*parts):
    return hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:10]


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mixc(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return "#%02X%02X%02X" % tuple(round(ra[i] + (rb[i] - ra[i]) * t) for i in range(3))


def darker(c, t=.25):
    return mixc(c, "#2A1A10", t)


def lighter(c, t=.35):
    return mixc(c, "#FFFFFF", t)


def lg(stops, x1=0, y1=0, x2=0, y2=1):
    k = "lg" + _h(stops, x1, y1, x2, y2)
    D.add(k, f'<linearGradient id="{k}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">' + "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops) + "</linearGradient>")
    return f"url(#{k})"


def rg(stops):
    k = "rg" + _h(stops)
    D.add(k, f'<radialGradient id="{k}">' + "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops) + "</radialGradient>")
    return f"url(#{k})"


def blur(sd):
    k = "bl" + str(sd).replace(".", "_")
    D.add(k, f'<filter id="{k}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{sd}"/></filter>')
    return f"url(#{k})"


# ---------------------------------------------------------------- shapes: a path string with its bounding box
class Sh:
    def __init__(self, d, b):
        self.d, self.b = d, b

    def __add__(self, o):
        return Sh(self.d + " " + o.d, (min(self.b[0], o.b[0]), min(self.b[1], o.b[1]), max(self.b[2], o.b[2]), max(self.b[3], o.b[3])))


def rr(x, y, w, h, r=6):
    r = min(r, w / 2, h / 2)
    d = (f"M{x + r:.1f},{y:.1f} h{w - 2 * r:.1f} a{r},{r} 0 0 1 {r},{r} v{h - 2 * r:.1f} a{r},{r} 0 0 1 {-r},{r} "
         f"h{-(w - 2 * r):.1f} a{r},{r} 0 0 1 {-r},{-r} v{-(h - 2 * r):.1f} a{r},{r} 0 0 1 {r},{-r}Z")
    return Sh(d, (x, y, x + w, y + h))


def circ(cx, cy, r):
    return Sh(f"M{cx - r:.1f},{cy:.1f} a{r},{r} 0 1 0 {2 * r},0 a{r},{r} 0 1 0 {-2 * r},0Z", (cx - r, cy - r, cx + r, cy + r))


def ell(cx, cy, rx, ry):
    return Sh(f"M{cx - rx:.1f},{cy:.1f} a{rx},{ry} 0 1 0 {2 * rx},0 a{rx},{ry} 0 1 0 {-2 * rx},0Z", (cx - rx, cy - ry, cx + rx, cy + ry))


def poly(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return Sh("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z", (min(xs), min(ys), max(xs), max(ys)))


def smooth(pts, closed=True):
    """A closed smooth curve through points (Catmull-Rom turned into cubic beziers)."""
    n = len(pts)
    out = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        if not closed:
            p0, p3 = pts[max(i - 1, 0)], pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}")
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return Sh(" ".join(out) + ("Z" if closed else ""), (min(xs), min(ys), max(xs), max(ys)))


def star(cx, cy, R, r=None, n=5):
    r = r or R * .5
    pts = []
    for i in range(2 * n):
        a = math.radians(-90 + i * 180 / n)
        rad = R if i % 2 == 0 else r
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return poly(pts)


def heart(cx, cy, s):
    d = (f"M{cx},{cy + s} C{cx - s * 1.6},{cy - s * .2} {cx - s * .9},{cy - s * 1.2} {cx},{cy - s * .4} "
         f"C{cx + s * .9},{cy - s * 1.2} {cx + s * 1.6},{cy - s * .2} {cx},{cy + s}Z")
    return Sh(d, (cx - s * 1.2, cy - s, cx + s * 1.2, cy + s))


# ---------------------------------------------------------------- the three ways to paint a shape
def wood_f(grain=.12, sh=1, m=.25, bevel=1.0):
    """The wood filter. grain: how much the streaks show. sh: 0 no shadow, 1 resting, 2 lifted, 3 big card."""
    key = "wd" + _h(grain, sh, m, bevel)
    dy, sd, op = {0: (0, 0, 0), 1: (1.6, 1.4, .35), 2: (3.4, 3.4, .28), 3: (5, 6, .22)}[sh]
    shadow, merge = "", '<feMergeNode in="top"/>'
    if sh:
        shadow = (f'<feGaussianBlur in="SourceAlpha" stdDeviation="{sd}" result="sb"/>'
                  f'<feOffset in="sb" dx="{dy * .35:.2f}" dy="{dy}" result="so"/>'
                  f'<feColorMatrix in="so" type="matrix" values="0 0 0 0 0.25  0 0 0 0 0.14  0 0 0 0 0.06  0 0 0 {op} 0" result="sh"/>')
        merge = '<feMergeNode in="sh"/>' + merge
    D.add(key, f'<filter id="{key}" x="{-m}" y="{-m}" width="{1 + 2 * m}" height="{1 + 2.4 * m}" color-interpolation-filters="sRGB">'
               f'<feTurbulence type="fractalNoise" baseFrequency="0.012 0.30" numOctaves="3" seed="7" result="n"/>'
               f'<feColorMatrix in="n" type="matrix" values="1 0 0 0 0  1 0 0 0 0  1 0 0 0 0  0 0 0 0 1" result="ng"/>'
               f'<feComposite in="SourceGraphic" in2="ng" operator="arithmetic" k1="{grain:.3f}" k2="{1 - grain / 2:.3f}" result="mot"/>'
               f'<feGaussianBlur in="SourceAlpha" stdDeviation="{2.4 * bevel:.2f}" result="ba"/>'
               f'<feDiffuseLighting in="ba" surfaceScale="{4.5 * bevel:.2f}" diffuseConstant="1" lighting-color="#ffffff" result="l">'
               f'<feDistantLight azimuth="235" elevation="58"/></feDiffuseLighting>'
               f'<feComposite in="mot" in2="l" operator="arithmetic" k1="0.86" k2="0.27" result="lit"/>'
               f'<feComposite in="lit" in2="SourceGraphic" operator="in" result="top"/>'
               f'{shadow}<feMerge>{merge}</feMerge></filter>')
    return f"url(#{key})"


def shadow_f(sh=1):
    key = "sf" + str(sh)
    dy, sd, op = {0: (0, 0, 0), 1: (1.6, 1.4, .3), 2: (3.4, 3.4, .25), 3: (5, 6, .2)}[sh]
    D.add(key, f'<filter id="{key}" x="-25%" y="-25%" width="150%" height="160%">'
               f'<feGaussianBlur in="SourceAlpha" stdDeviation="{sd}" result="sb"/><feOffset in="sb" dx="{dy * .35:.2f}" dy="{dy}" result="so"/>'
               f'<feColorMatrix in="so" type="matrix" values="0 0 0 0 0.1  0 0 0 0 0.08  0 0 0 0 0.12  0 0 0 {op} 0" result="sh"/>'
               f'<feMerge><feMergeNode in="sh"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    return f"url(#{key})"


def glow_f(sd=3.0):
    key = "gl" + str(sd).replace(".", "_")
    D.add(key, f'<filter id="{key}" x="-40%" y="-40%" width="180%" height="180%">'
               f'<feGaussianBlur in="SourceGraphic" stdDeviation="{sd}" result="b"/>'
               f'<feColorMatrix in="b" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 1.6 0" result="g"/>'
               f'<feMerge><feMergeNode in="g"/><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    return f"url(#{key})"


def tile_pat():
    """Mosaic: a 4x4 block of small tiles with grout; each tile a little lighter or darker."""
    key = "tiles"
    if key not in D.d:
        o = [f'<pattern id="{key}" width="32" height="32" patternUnits="userSpaceOnUse">']
        for i in range(4):
            for j in range(4):
                v = ((i * 7 + j * 13) % 5) / 5
                col, op = ("#FFFFFF", .05 + v * .22) if (i + j) % 2 else ("#000000", .03 + v * .12)
                o.append(f'<rect x="{i * 8 + .9}" y="{j * 8 + .9}" width="6.2" height="6.2" rx="1" fill="{col}" opacity="{op:.2f}"/>')
        o.append('<path d="M0,0 H32 M0,8 H32 M0,16 H32 M0,24 H32 M0,0 V32 M8,0 V32 M16,0 V32 M24,0 V32" stroke="#FFFFFF" stroke-opacity=".7" stroke-width="1.8"/></pattern>')
        D.add(key, "".join(o))
    return f"url(#{key})"


def _rand(seed, i):
    """A repeatable 0..1 number from a seed and an index."""
    return int(hashlib.md5(f"{seed}|{i}".encode()).hexdigest()[:6], 16) / 0xFFFFFF


def vinyl_piece(sh, col, shade=1, extra=""):
    """軟膠公仔: a strong colour, a dark rim, a vertical gradient and two glossy highlights clipped to the shape."""
    x0, y0, x1, y1 = sh.b
    w, h = max(1, x1 - x0), max(1, y1 - y0)
    k = _clip(sh)
    o = []
    if shade:
        o.append(f'<path d="{sh.d}" fill="#000" opacity=".{12 if shade < 3 else 8}" transform="translate(1.5 {2 + shade})"{extra}/>')
    o.append(f'<path d="{sh.d}" fill="{lg([(0, lighter(col, .18)), (.55, col), (1, darker(col, .22))])}"{extra}/>')
    o.append(f'<g clip-path="url(#{k})"{extra}>'
             f'<ellipse cx="{x0 + w * .32:.1f}" cy="{y0 + h * .24:.1f}" rx="{min(w * .22, 36):.1f}" ry="{min(h * .13, 14):.1f}" fill="#FFFFFF" opacity=".55" transform="rotate(-18 {x0 + w * .32:.1f} {y0 + h * .24:.1f})"/>'
             f'<ellipse cx="{x0 + w * .26:.1f}" cy="{y0 + h * .2:.1f}" rx="{min(w * .09, 14):.1f}" ry="{min(h * .06, 6):.1f}" fill="#FFFFFF" opacity=".9"/>'
             f'<ellipse cx="{x0 + w * .5:.1f}" cy="{y1 + h * .18:.1f}" rx="{w * .5:.1f}" ry="{h * .3:.1f}" fill="#000" opacity=".12"/></g>')
    o.append(f'<path d="{sh.d}" fill="none" stroke="{darker(col, .55)}" stroke-width="2.4" stroke-linejoin="round"{extra}/>')
    return "".join(o)


def cookie_piece(sh, col, shade=1, extra=""):
    """糖霜餅乾: a biscuit base, thick pastel icing along the edge with a white shine inside it, a few sprinkles."""
    x0, y0, x1, y1 = sh.b
    k = _clip(sh)
    ice = lighter(col, .42)
    o = []
    if shade:
        o.append(f'<path d="{sh.d}" fill="#B98A55" opacity=".35" transform="translate(1 {1.5 + shade})"{extra}/>')
    o.append(f'<path d="{sh.d}" fill="{ice}" stroke="#C99B63" stroke-width="1.6" stroke-linejoin="round"{extra}/>')
    w, h = x1 - x0, y1 - y0
    o.append(f'<g clip-path="url(#{k})"{extra}><path d="{sh.d}" fill="none" stroke="#E6BC84" stroke-width="11" stroke-linejoin="round"/>'
             f'<path d="{sh.d}" fill="none" stroke="{col}" stroke-width="4.5" stroke-linejoin="round"/>'
             f'<path d="{sh.d}" fill="none" stroke="#FFFFFF" stroke-width="1.6" stroke-opacity=".8" stroke-linejoin="round"/>'
             f'<ellipse cx="{x0 + w * .3:.1f}" cy="{y0 + h * .28:.1f}" rx="{min(w * .16, 30):.1f}" ry="{min(h * .09, 12):.1f}" fill="#FFFFFF" opacity=".5"/>')
    n = int(min(12, (w * h) / 900))
    for i in range(n):
        px, py = x0 + 6 + _rand(sh.d, i) * (w - 12), y0 + 6 + _rand(sh.d, i + 50) * (h - 12)
        c = (RED, YEL, BLUE, GRN, PINK, "#FFFFFF")[i % 6]
        o.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="5" height="2.2" rx="1.1" fill="{c}" transform="rotate({_rand(sh.d, i + 90) * 180:.0f} {px:.1f} {py:.1f})"/>')
    o.append("</g>")
    return "".join(o)


def hatch_pat(col, ang=38, gap=4.2):
    k = "ht" + _h(col, ang, gap)
    D.add(k, f'<pattern id="{k}" width="{gap}" height="24" patternUnits="userSpaceOnUse" patternTransform="rotate({ang})">'
             f'<path d="M{gap / 2:.1f},1 v8 M{gap / 2:.1f},12 v10" stroke="{col}" stroke-width="1.5" stroke-linecap="round" stroke-opacity=".8"/></pattern>')
    return f"url(#{k})"


def pencil_piece(sh, col, shade=1, extra=""):
    """色鉛筆: a pale fill, hatching clipped to the shape, and a double, slightly offset outline."""
    x0, y0, x1, y1 = sh.b
    k = _clip(sh)
    o = [f'<path d="{sh.d}" fill="{lighter(col, .45)}" opacity=".9"{extra}/>']
    o.append(f'<g clip-path="url(#{k})"{extra}><rect x="{x0 - 10}" y="{y0 - 10}" width="{x1 - x0 + 20}" height="{y1 - y0 + 20}" fill="{hatch_pat(darker(col, .1), 38)}"/>'
             f'<rect x="{x0 - 10}" y="{y0 - 10}" width="{x1 - x0 + 20}" height="{y1 - y0 + 20}" fill="{hatch_pat(darker(col, .3), 130, 7)}" opacity=".45"/></g>')
    d = darker(col, .5)
    o.append(f'<path d="{sh.d}" fill="none" stroke="{d}" stroke-width="1.8" stroke-linejoin="round" stroke-opacity=".85"{extra}/>')
    o.append(f'<path d="{sh.d}" fill="none" stroke="{d}" stroke-width="1.2" stroke-linejoin="round" stroke-opacity=".55" transform="translate(1.2 -0.8) rotate(0.6 {(x0 + x1) / 2:.1f} {(y0 + y1) / 2:.1f})"{extra}/>')
    return "".join(o)


def _margin(b):
    w, h = max(1, b[2] - b[0]), max(1, b[3] - b[1])
    need = 14 / min(w, h)
    for m in (.08, .15, .25, .5, 1.0, 2.0):
        if need <= m:
            return m
    return 3.0


def piece(sh, col, shade=1, grain=.12, bevel=1.0, extra=""):
    """One solid piece in the current style."""
    if STYLE == "vinyl":
        return vinyl_piece(sh, col, shade, extra)
    if STYLE == "cookie":
        return cookie_piece(sh, col, shade, extra)
    if STYLE == "pencil":
        return pencil_piece(sh, col, shade, extra)
    if STYLE == "mosaic":
        return (f'<path d="{sh.d}" fill="{col}" filter="{shadow_f(shade)}"{extra}/>'
                f'<path d="{sh.d}" fill="{tile_pat()}"{extra}/>')
    if STYLE == "neon":
        return (f'<path d="{sh.d}" fill="{col}" fill-opacity=".16"{extra}/>'
                f'<path d="{sh.d}" fill="none" stroke="{lighter(col, .2)}" stroke-width="2.6" stroke-linejoin="round" filter="{glow_f(2.6)}"{extra}/>')
    return f'<path d="{sh.d}" fill="{col}" filter="{wood_f(grain, shade, _margin(sh.b), bevel)}"{extra}/>'


def wood(sh, col=WOOD, shade=1, bevel=1.0, extra=""):
    """Natural wood: lots of grain."""
    return piece(sh, col, shade, .4, bevel, extra)


def flat(sh, col, extra=""):
    """Painted-on detail with no body of its own: eyes, stripes, windows."""
    if STYLE == "neon":
        return f'<path d="{sh.d}" fill="{col}" opacity=".9"{extra}/>'
    return f'<path d="{sh.d}" fill="{col}"{extra}/>'


def stroke(d, col, w, dash=None, op=1.0, cap="round"):
    da = f' stroke-dasharray="{dash[0]} {dash[1]}"' if dash else ""
    g = f' filter="{glow_f(2)}"' if STYLE == "neon" else ""
    if STYLE == "pencil":
        return (f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity="{op * .85:.2f}" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="round"{da}/>'
                f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity="{op * .5:.2f}" stroke-width="{max(1, w * .7):.1f}" stroke-linecap="{cap}" stroke-linejoin="round"{da} transform="translate(1 -0.8)"/>')
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity="{op}" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="round"{da}{g}/>'


def place(x, y, s, fn, *a, rot=0.0, **kw):
    t = f"translate({x:.1f} {y:.1f})" + (f" rotate({rot})" if rot else "") + (f" scale({s})" if s != 1 else "")
    return f'<g transform="{t}">{fn(*a, **kw)}</g>'


# ---------------------------------------------------------------- words and glyphs
def tx(x, y, s, size=16, color=INK, anchor="middle", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-family="Huninn, sans-serif" {extra}>{s}</text>'


def txo(x, y, s, size, color, ol="#FFFFFF", ow=6, anchor="middle"):
    return tx(x, y, s, size, color, anchor, f'stroke="{ol}" stroke-width="{ow}" stroke-linejoin="round" paint-order="stroke"')


def glyph(x, y, s, size, col):
    """A 注音 symbol painted on a piece. y is the text baseline."""
    if STYLE == "vinyl":
        return tx(x, y, s, size, "#FFFFFF", extra=f'stroke="{darker(col, .55)}" stroke-width="{max(3.0, size * .075):.1f}" stroke-linejoin="round" paint-order="stroke"')
    if STYLE == "cookie":
        return (tx(x, y + 1, s, size, "#FFFFFF", extra=f'stroke="#FFFFFF" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"')
                + tx(x, y, s, size, darker(col, .35), extra=f'stroke="{darker(col, .35)}" stroke-width="1.5" stroke-linejoin="round"'))
    if STYLE == "pencil":
        d = darker(col, .5)
        return (tx(x, y, s, size, d, extra='opacity=".85"') + tx(x, y, s, size, "none", extra=f'stroke="{d}" stroke-width="1.6" stroke-opacity=".85"')
                + tx(x + 1, y - .8, s, size, "none", extra=f'stroke="{d}" stroke-width="1.1" stroke-opacity=".5"'))
    if STYLE == "mosaic":
        return tx(x, y, s, size, col) + tx(x, y, s, size, tile_pat())
    if STYLE == "neon":
        return tx(x, y, s, size, "#FFFFFF", extra=f'stroke="{lighter(col, .5)}" stroke-width="2" filter="{glow_f(3)}"') + tx(x, y, s, size, "#FFFFFF")
    return tx(x + .8, y + 1.6, s, size, darker(col, .5), extra='opacity=".35"') + tx(x, y, s, size, col)


# ---------------------------------------------------------------- faces
def eye(cx, cy, r):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{DARK}"/>'
            f'<circle cx="{cx - r * .32:.1f}" cy="{cy - r * .32:.1f}" r="{r * .38:.1f}" fill="#FFFFFF"/>')


def happy_eye(cx, cy, r):
    return stroke(f"M{cx - r:.1f},{cy + r * .3:.1f} Q{cx:.1f},{cy - r * 1.1:.1f} {cx + r:.1f},{cy + r * .3:.1f}", DARK, 2.2)


def cheeks(cx, cy, dx, r):
    return f'<circle cx="{cx - dx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{CHEEK}" opacity=".7"/><circle cx="{cx + dx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{CHEEK}" opacity=".7"/>'


def smile(cx, cy, w, open_=False):
    if open_:
        return f'<path d="M{cx - w:.1f},{cy:.1f} Q{cx:.1f},{cy + w * 1.6:.1f} {cx + w:.1f},{cy:.1f}Z" fill="#C9546A"/>'
    return stroke(f"M{cx - w:.1f},{cy:.1f} Q{cx:.1f},{cy + w:.1f} {cx + w:.1f},{cy:.1f}", DARK, 1.8)


def face(cx, cy, s=1.0, mood="smile"):
    o = []
    if mood == "happy":
        o.append(happy_eye(cx - 5 * s, cy, 2.6 * s) + happy_eye(cx + 5 * s, cy, 2.6 * s))
        o.append(smile(cx, cy + 3.5 * s, 3.2 * s, True))
    else:
        o.append(eye(cx - 5 * s, cy, 2.1 * s) + eye(cx + 5 * s, cy, 2.1 * s))
        o.append(smile(cx, cy + 4 * s, 2.8 * s))
    o.append(cheeks(cx, cy + 4 * s, 9 * s, 2.2 * s))
    return "".join(o)


# ---------------------------------------------------------------- the train (drawn round (0, 0) = the rail top, pieces about 70 tall)
def wheel(cx, cy, r, col=WALNUT):
    o = [wood(circ(cx, cy, r), col, bevel=1.2)]
    o.append(flat(circ(cx, cy, r * .62), lighter(col, .25)))
    o.append(piece(circ(cx, cy, r * .22), WOOD2, shade=0))
    return "".join(o)


def coupler(x, y, col=WALNUT):
    return piece(rr(x - 7, y - 3, 14, 6, 3), col, shade=0) + piece(circ(x, y, 4.5), col, shade=1)


def carriage(x, y, w, h, col, sym="", sym_col=None, grey=False, flag=None, passenger=None, sym_size=None):
    """A carriage standing on the rail at y. (x, y) is its bottom-left corner. Symbol painted in the middle."""
    o = []
    if grey:
        o.append(f'<path d="{rr(x, y - h - 10, w, h, 10).d}" fill="none" stroke="{GREY}" stroke-width="3" stroke-dasharray="7 6"/>')
        o.append(f'<circle cx="{x + w * .25:.1f}" cy="{y - 8}" r="8" fill="none" stroke="{GREY}" stroke-width="3" stroke-dasharray="4 4"/>'
                 f'<circle cx="{x + w * .75:.1f}" cy="{y - 8}" r="8" fill="none" stroke="{GREY}" stroke-width="3" stroke-dasharray="4 4"/>')
        if sym:
            o.append(tx(x + w / 2, y - h / 2 + 4, sym, h * .5, GREY))
        return "".join(o)
    body = rr(x, y - h - 10, w, h, 10)
    o.append(piece(body, col, shade=2, bevel=1.3))
    o.append(piece(rr(x + 6, y - h - 16, w - 12, 8, 4), darker(col, .18), shade=0))      # the roof strip
    if sym:
        o.append(glyph(x + w / 2, y - h / 2 + (sym_size or h * .52) * .36 - 2, sym, sym_size or h * .52, sym_col or darker(col, .55)))
    if passenger:
        o.append(place(x + w / 2, y - h - 12, .55, passenger))
    o.append(wheel(x + w * .25, y - 8, 9) + wheel(x + w * .75, y - 8, 9))
    if flag:
        o.append(tone_flag(x + w - 8, y - h - 16, flag))
    return "".join(o)


def tone_flag(x, y, tone, s=1.0, col=RED, up=True, mcol="#FFFFFF"):
    """A little flag on a pole: the tone mark painted on it (1 = a flat bar, 2..4 the marks, 5 = light tone dot)."""
    marks = {1: "", 2: "ˊ", 3: "ˇ", 4: "ˋ", 5: "˙"}
    hgt = 30 * s if up else 16 * s
    o = [piece(rr(x - 1.5 * s, y - hgt, 3 * s, hgt, 1.5), WALNUT, shade=0)]
    o.append(piece(poly([(x, y - hgt), (x + 22 * s, y - hgt + 7 * s), (x, y - hgt + 14 * s)]), col, shade=1))
    m = marks[tone]
    if tone == 1:
        o.append(stroke(f"M{x + 4 * s:.1f},{y - hgt + 7 * s:.1f} h{8 * s:.1f}", mcol, 2.2 * s))
    else:
        o.append(tx(x + 9 * s, y - hgt + 12 * s, m, 16 * s, mcol))
    return "".join(o)


def engine(col=RED, driver=None, smoke=True, s=1.0):
    """The locomotive, facing right, standing on the rail at y = 0, its back at x = 0."""
    o = []
    o.append(piece(rr(0, -62, 46, 52, 8), darker(col, .1), shade=2, bevel=1.3))          # the cab
    o.append(piece(rr(-4, -70, 54, 10, 5), darker(col, .3), shade=1))                       # the cab roof
    o.append(flat(rr(8, -54, 30, 22, 5), SKY))                                               # the cab window
    if driver:
        o.append(f'<g clip-path="url(#{_clip(rr(8, -54, 30, 22, 5))})">' + place(23, -30, .55, driver) + "</g>")
    o.append(piece(rr(40, -44, 60, 32, 12), col, shade=2, bevel=1.4))                       # the boiler
    o.append(piece(rr(96, -40, 12, 26, 4), darker(col, .25), shade=1))                      # the front
    o.append(piece(poly([(104, -12), (122, 0), (104, 0)]), WALNUT, shade=1))                # the cow catcher
    o.append(piece(rr(72, -64, 16, 24, 4), WALNUT, shade=1))                                # the chimney
    o.append(piece(rr(68, -68, 24, 8, 4), darker(WALNUT, .2), shade=1))
    o.append(piece(circ(58, -56, 7), YEL, shade=1))                                          # the bell
    o.append(wood(rr(-2, -14, 110, 6, 3), WALNUT, shade=1))                                  # the chassis
    o.append(wheel(14, -8, 11, WALNUT) + wheel(48, -8, 9, WALNUT) + wheel(78, -8, 9, WALNUT))
    o.append(stroke("M14,-8 L48,-8 L78,-8", darker(WALNUT, .3), 3))
    if smoke:
        for i, (dx, dy, r) in enumerate(((80, -84, 9), (92, -100, 12), (108, -116, 15))):
            o.append(piece(circ(dx, dy, r), "#FFFFFF", shade=0, extra=f' opacity="{.95 - i * .22:.2f}"'))
    return "".join(o)


def _clip(sh):
    k = "cp" + _h(sh.d)
    D.add(k, f'<clipPath id="{k}"><path d="{sh.d}"/></clipPath>')
    return k


def track(x0, x1, y, step=26):
    o = []
    for x in range(int(x0), int(x1), step):
        o.append(wood(rr(x, y - 2, 16, 10, 2), WOOD2, shade=1))
    o.append(piece(rr(x0, y - 2, x1 - x0, 4, 2), WALNUT, shade=0))
    return "".join(o)


def train(x, y, cars, s=1.0, driver=None, car_w=54, car_h=48, gap=10):
    """The engine then the carriages, all standing on the rail at y; the engine's front is at x.
    cars: list of (symbol, colour) or (symbol, colour, dict of carriage options)."""
    o = [place(x - 122 * s, y, s, engine, RED, driver)]
    cx = x - 122 * s
    for sym, col, *opt in cars:
        o.append(place(cx - 8 * s, y - 10 * s, s, lambda: coupler(0, 0)))
        cx -= (car_w + gap) * s
        o.append(place(cx, y, s, lambda sym=sym, col=col, opt=opt: carriage(0, 0, car_w, car_h, col, sym, **(opt[0] if opt else {}))))
    return "".join(o)


# ---------------------------------------------------------------- characters and picture words (drawn round (0, 0) = the feet, about 60 tall)
def bear(mood="smile", hat=True, wave=False):
    o = [piece(ell(0, -22, 17, 19), BEAR, bevel=1.2)]                       # body
    o.append(flat(ell(0, -18, 10, 11), lighter(BEAR, .5)))                   # tummy
    o.append(piece(circ(-14, -58, 7), BEAR) + piece(circ(14, -58, 7), BEAR))  # ears
    o.append(flat(circ(-14, -58, 3.5), lighter(BEAR, .5)) + flat(circ(14, -58, 3.5), lighter(BEAR, .5)))
    o.append(piece(circ(0, -46, 18), BEAR, bevel=1.3))                        # head
    o.append(flat(ell(0, -40, 8, 6), lighter(BEAR, .55)))                     # muzzle
    o.append(flat(ell(0, -42, 3, 2.2), DARK))
    o.append(face(0, -48, .9, mood))
    if wave:
        o.append(piece(ell(22, -40, 6, 9), BEAR, shade=1))
    if hat:
        o.append(piece(rr(-14, -66, 28, 7, 3), BLUE, shade=1) + piece(rr(-9, -76, 18, 11, 4), BLUE, shade=1))
    return "".join(o)


def peg_person(shirt=RED, hair="short", glasses=False, skirt=False, wave=False):
    """A wooden peg doll: a round head, a short round body."""
    o = []
    body = rr(-16, -40, 32, 40, 12) if not skirt else poly([(-10, -40), (10, -40), (18, 0), (-18, 0)])
    o.append(piece(body, shirt, bevel=1.2))
    o.append(piece(circ(0, -56, 18), SKIN, bevel=1.3))
    if hair == "short":
        o.append(piece(Sh(f"M-18,-60 a18,18 0 0 1 36,0 v4 h-36Z", (-18, -78, 18, -56)), DARK, shade=0))
    else:
        o.append(piece(Sh(f"M-19,-58 a19,19 0 0 1 38,0 v6 h-38Z", (-19, -78, 19, -52)), "#5A3A2E", shade=0))
        o.append(piece(circ(0, -78, 8), "#5A3A2E", shade=1))
    o.append(face(0, -54, 1.0))
    if glasses:
        o.append(stroke("M-10,-54 m-5,0 a5,5 0 1 0 10,0 a5,5 0 1 0 -10,0 M10,-54 m-5,0 a5,5 0 1 0 10,0 a5,5 0 1 0 -10,0 M-5,-54 h10", DARK, 1.5))
    if wave:
        o.append(piece(ell(22, -34, 5, 8), SKIN, shade=1))
    return "".join(o)


def dad():
    return peg_person(BLUE, "short", glasses=True, wave=True)


def mom():
    return peg_person(PINK, "bun", skirt=True, wave=True)


def cat(col=ORA):
    o = [piece(ell(0, -16, 18, 15), col)]
    o.append(piece(poly([(-16, -40), (-8, -56), (0, -42)]), col, shade=0) + piece(poly([(0, -42), (8, -56), (16, -40)]), col, shade=0))
    o.append(piece(circ(0, -36, 16), col, bevel=1.3))
    o.append(face(0, -38, .9))
    o.append(stroke("M-24,-34 h9 M-24,-29 h9 M15,-34 h9 M15,-29 h9", DARK, 1.2))
    o.append(stroke("M18,-14 q14,-4 10,-18", col, 5))
    return "".join(o)


def dog(col=WOOD2):
    o = [piece(ell(0, -16, 19, 15), col)]
    o.append(piece(ell(-16, -36, 6, 12), WALNUT, shade=0) + piece(ell(16, -36, 6, 12), WALNUT, shade=0))
    o.append(piece(circ(0, -38, 16), col, bevel=1.3))
    o.append(flat(ell(0, -32, 7, 5), lighter(col, .5)) + flat(ell(0, -34, 3.5, 2.5), DARK))
    o.append(face(0, -42, .85))
    o.append(stroke("M18,-18 q12,-8 8,-20", WALNUT, 5))
    return "".join(o)


def bun():
    o = [piece(Sh("M-20,0 h40 a4,4 0 0 0 4,-4 a24,24 0 0 0 -48,0 a4,4 0 0 0 4,4Z", (-24, -28, 24, 0)), "#FFF3E0", bevel=1.3)]
    o.append(stroke("M0,-24 q-10,6 -14,14 M0,-24 q10,6 14,14 M0,-24 q-3,8 -4,14 M0,-24 q3,8 4,14", "#E8D2B5", 1.6))
    o.append(face(0, -10, .8))
    return "".join(o)


def fish(col=BLUE):
    o = [piece(poly([(18, -20), (34, -32), (34, -8)]), col, shade=1)]
    o.append(piece(ell(0, -20, 24, 15), col, bevel=1.3))
    o.append(flat(ell(2, -14, 12, 5), lighter(col, .45)))
    o.append(eye(-12, -23, 3.2))
    o.append(stroke("M-8,-13 q4,3 8,0", DARK, 1.4))
    return "".join(o)


def apple():
    o = [piece(circ(0, -22, 20), RED, bevel=1.3)]
    o.append(piece(rr(-2, -48, 4, 10, 2), WALNUT, shade=0))
    o.append(piece(ell(9, -44, 9, 4.5), GRN, shade=1, extra=' transform="rotate(-30 9 -44)"'))
    o.append(flat(ell(-7, -30, 4, 6), "#FFFFFF", ' opacity=".5"'))
    return "".join(o)


def plane():
    o = [piece(poly([(-8, -22), (-22, -42), (-10, -42)]), BLUE, shade=1)]
    o.append(piece(ell(0, -22, 30, 10), SKY, bevel=1.3))
    o.append(piece(poly([(-4, -22), (-18, -4), (8, -4)]), BLUE, shade=1) + piece(poly([(-4, -24), (-16, -40), (6, -40)]), BLUE, shade=1))
    o.append(flat(circ(8, -24, 3), DARK) + flat(circ(18, -24, 3), DARK))
    return "".join(o)


def ball():
    o = [piece(circ(0, -22, 20), YEL, bevel=1.3)]
    o.append(stroke("M-18,-30 q18,-6 36,0 M-18,-14 q18,6 36,0", RED, 4))
    return "".join(o)


def cup():
    o = [piece(rr(-14, -34, 28, 34, 5), TEAL, bevel=1.2)]
    o.append(stroke("M14,-26 q14,0 12,10 q-2,8 -12,8", TEAL, 5))
    o.append(flat(rr(-9, -30, 18, 6, 3), lighter(TEAL, .5)))
    return "".join(o)


def pen():
    o = [piece(rr(-6, -46, 12, 40, 4), YEL, bevel=1.1, extra=' transform="rotate(25 0 -26)"')]
    o.append(piece(poly([(-6, -6), (6, -6), (0, 4)]), SKIN, shade=0, extra=' transform="rotate(25 0 -26)"'))
    return "".join(o)


def bag():
    o = [piece(rr(-18, -30, 36, 30, 8), PINK, bevel=1.2)]
    o.append(stroke("M-10,-30 q0,-16 10,-16 q10,0 10,16", darker(PINK, .3), 4))
    o.append(piece(circ(0, -18, 4), YEL, shade=0))
    return "".join(o)


def speaker_icon(cx, cy, s=1.0, col="#FFFFFF"):
    o = [flat(poly([(cx - 9 * s, cy - 4 * s), (cx - 4 * s, cy - 4 * s), (cx + 3 * s, cy - 10 * s), (cx + 3 * s, cy + 10 * s), (cx - 4 * s, cy + 4 * s), (cx - 9 * s, cy + 4 * s)]), col)]
    o.append(stroke(f"M{cx + 7 * s},{cy - 5 * s} q5,5 0,10 M{cx + 11 * s},{cy - 9 * s} q8,9 0,18", col, 2.2 * s))
    return "".join(o)


def finger(x, y, rot=-20.0):
    o = [f'<g transform="translate({x} {y}) rotate({rot})">']
    o.append(f'<path d="M-9,46 V12 a9,9 0 0 1 18,0 v10 l4,-2 a6,6 0 0 1 8,4 l4,-1 a6,6 0 0 1 8,6 l2,1 a6,6 0 0 1 7,6 v18 a24,24 0 0 1 -24,24 h-16 a14,14 0 0 1 -11,-20Z" fill="{SKIN}" stroke="{darker(SKIN, .35)}" stroke-width="2" stroke-linejoin="round"/>')
    o.append(f'<circle cx="0" cy="0" r="16" fill="none" stroke="{YEL}" stroke-width="3" opacity=".9"/><circle cx="0" cy="0" r="26" fill="none" stroke="{YEL}" stroke-width="2" opacity=".5"/></g>')
    return "".join(o)


def sparkle(cx, cy, r, c=YEL, op=1.0):
    return (f'<path d="M{cx},{cy - r} Q{cx + r * .16},{cy - r * .16} {cx + r},{cy} Q{cx + r * .16},{cy + r * .16} {cx},{cy + r} '
            f'Q{cx - r * .16},{cy + r * .16} {cx - r},{cy} Q{cx - r * .16},{cy - r * .16} {cx},{cy - r}Z" fill="{c}" opacity="{op}"/>')


# ---------------------------------------------------------------- UI pieces
def board(x=0, y=0, w=W, h=H, col=None):
    """The page background: a wooden table top with a soft wallpaper."""
    if STYLE == "neon":
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#121A33"/>'
    if STYLE == "pencil":
        k = "paper"
        D.add(k, '<pattern id="paper" width="9" height="9" patternUnits="userSpaceOnUse"><rect width="9" height="9" fill="#FBF5E6"/>'
                 '<circle cx="2" cy="3" r=".7" fill="#E2D6BC"/><circle cx="6.5" cy="7" r=".6" fill="#E8DCC4"/></pattern>')
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#paper)"/>'
    k = "wp" + _h(col)
    base, dot = ("#F7EEDC", "#EADBBF") if not col else (col, darker(col, .06))
    D.add(k, f'<pattern id="{k}" width="28" height="28" patternUnits="userSpaceOnUse"><rect width="28" height="28" fill="{base}"/>'
             f'<circle cx="7" cy="7" r="2" fill="{dot}"/><circle cx="21" cy="21" r="2" fill="{dot}"/></pattern>')
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{k})"/>'


def wbtn(cx, cy, r, col, icon=""):
    return piece(circ(cx, cy, r), col, shade=2, bevel=1.3) + icon


def wpill(cx, cy, w, h, col, label="", size=19, tcol=None):
    o = piece(rr(cx - w / 2, cy - h / 2, w, h, h / 2), col, shade=2, bevel=1.3)
    if label:
        o += tx(cx, cy + size * .36, label, size, tcol or darker(col, .5))
    return o


def sign(cx, cy, w, text, size=22, col=WOOD):
    """A wooden station sign hanging on two little posts."""
    o = [piece(rr(cx - w / 2, cy - 22, w, 44, 10), col, shade=2)]
    o.append(piece(circ(cx - w / 2 + 14, cy - 12, 3.5), WALNUT, shade=0) + piece(circ(cx + w / 2 - 14, cy - 12, 3.5), WALNUT, shade=0))
    o.append(tx(cx, cy + size * .36, text, size, INK if STYLE != "neon" else "#FFF4C8"))
    return "".join(o)


def bubble(x, y, w, h, text, size=17, tail=None, fill=WHITE):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" filter="{shadow_f(2)}"/>']
    if tail == "down":
        o.append(f'<path d="M{x + 30},{y + h - 1} l10,16 l10,-16Z" fill="{fill}"/>')
    elif tail == "left":
        o.append(f'<path d="M{x + 1},{y + h / 2 - 10} l-14,10 l14,10Z" fill="{fill}"/>')
    elif tail == "up":
        o.append(f'<path d="M{x + 30},{y + 1} l10,-16 l10,16Z" fill="{fill}"/>')
    o.append(tx(x + w / 2, y + h / 2 + size * .36, text, size, INK))
    return "".join(o)


def lock_chip(x=14, y=14):
    o = [piece(rr(x, y, 42, 30, 10), WOOD2, shade=2)]
    o.append(stroke(f"M{x + 21},{y + 7} m-5,7 v-3 a5,5 0 0 1 10,0 v3", "#8A8F9C", 2.2))
    o.append(flat(rr(x + 13, y + 14, 16, 11, 3), "#8A8F9C"))
    return "".join(o)


def home_btn(cx=36, cy=36):
    o = [wbtn(cx, cy, 20, WOOD2)]
    o.append(flat(poly([(cx - 11, cy), (cx, cy - 11), (cx + 11, cy)]), RED) + flat(rr(cx - 8, cy - 1, 16, 10, 2), RED))
    return "".join(o)


def topbar(title, station=None):
    o = [home_btn(36, 38)]
    o.append(sign(195, 40, 210, title, 22))
    if station:
        o.append(piece(rr(302, 20, 76, 36, 18), STATION_COL[station], shade=2))
        o.append(tx(340, 47, station + "站", 16, INK))
    return "".join(o)


def card(x, y, w, h, col=WHITE, shade=2, r=18):
    if STYLE == "neon":
        return piece(rr(x, y, w, h, r), col, shade=0)
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{col}" filter="{shadow_f(shade)}"/>'


def picture_card(cx, cy, fn, label, size=92, sel=False, glow=False):
    o = []
    if glow:
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{size * .72}" fill="{rg([(0, "#FFF4B0", .95), (.6, "#FFE26B", .7), (1, "#FFE26B", 0)])}"/>')
    o.append(piece(rr(cx - size / 2, cy - size / 2, size, size, 16), CREAM if not sel else "#FFF0B5", shade=2))
    if sel:
        o.append(f'<rect x="{cx - size / 2}" y="{cy - size / 2}" width="{size}" height="{size}" rx="16" fill="none" stroke="{GRN}" stroke-width="4"/>')
    o.append(place(cx, cy + size * .32, size / 92 * 1.05, fn))
    o.append(tx(cx, cy + size / 2 + 20, label, 16, INK))
    return "".join(o)


def toggle(x, y, on=True):
    col = GRN if on else GREY
    return piece(rr(x, y, 46, 26, 13), col, shade=1) + piece(circ(x + (33 if on else 13), y + 13, 10), "#FFFFFF", shade=1)


def row(y, label, right, h=46):
    return card(16, y, 358, h, WHITE, 1, 14) + tx(32, y + h / 2 + 6, label, 16, INK, "start") + right


# ---------------------------------------------------------------- the map of Taiwan
TAIWAN = [(.55, .0), (.68, .06), (.78, .22), (.84, .40), (.80, .58), (.70, .76), (.58, .92), (.50, 1.0), (.42, .94),
          (.32, .80), (.20, .64), (.12, .50), (.14, .36), (.24, .22), (.36, .10), (.45, .03)]
STATION_XY = {"台北": (.60, .10), "桃園": (.46, .15), "新竹": (.36, .25), "台中": (.28, .40), "嘉義": (.24, .55), "台南": (.26, .67), "高雄": (.34, .80)}


def taiwan_map(x, y, w, h, at="桃園", done=("台北",)):
    o = []
    pts = [(x + px * w, y + py * h) for px, py in TAIWAN]
    o.append(piece(smooth(pts), GRASS, shade=2, grain=.08))
    o.append(flat(smooth([(x + w * .58, y + h * .22), (x + w * .66, y + h * .40), (x + w * .60, y + h * .62), (x + w * .50, y + h * .70), (x + w * .46, y + h * .45)]), darker(GRASS, .12)))
    # the railway through the seven stations
    rail = [(x + px * w, y + py * h) for px, py in (STATION_XY[n] for n, _ in STATIONS)]
    d = smooth(rail, closed=False).d
    o.append(stroke(d, WALNUT, 5) + stroke(d, CREAM, 2, dash=(6, 6)))
    for name, _ in STATIONS:
        px, py = x + STATION_XY[name][0] * w, y + STATION_XY[name][1] * h
        is_at = name == at
        o.append(piece(circ(px, py, 9 if is_at else 7), STATION_COL[name], shade=1))
        if name in done:
            o.append(piece(rr(px - 1.5, py - 26, 3, 20, 1.5), WALNUT, shade=0) + piece(poly([(px, py - 26), (px + 14, py - 21), (px, py - 16)]), RED, shade=0))
        o.append(txo(px + 15, py + 5, name, 13, INK, CREAM, 4, "start"))
        if is_at:
            o.append(f'<circle cx="{px}" cy="{py}" r="16" fill="none" stroke="{RED}" stroke-width="3" opacity=".9"/>')
            o.append(place(px - 46, py + 6, .26, lambda: engine(RED, None, True)))
    return "".join(o)


# ---------------------------------------------------------------- page and render
def page(body, bg=None, w=W, h=H):
    css = (f"@font-face {{ font-family: Huninn; src: url('file://{FONT}'); }}"
           f"* {{ margin: 0; padding: 0; }} body {{ width: {w}px; height: {h}px; overflow: hidden; background: {bg or '#F7EEDC'}; }}")
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{D.svg()}{body}</svg>'
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{svg}</body></html>'


def render(html, out, w, h, scale):
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        p = pathlib.Path(tmp) / "page.html"
        p.write_text(html)
        subprocess.run(["node", str(HERE / "render.js"), str(p), str(out), str(w), str(h), str(scale)], check=True)
    if pathlib.Path(out).stat().st_size > 450_000:
        from PIL import Image
        im = Image.open(out).convert("RGB")
        im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, kmeans=2, dither=Image.Dither.FLOYDSTEINBERG).save(out, optimize=True)


# ================================================================ SCREEN 1: the station (home)
def screen_station():
    o = [board()]
    o.append(lock_chip(14, 16))
    o.append(sign(195, 42, 230, "ㄅㄆㄇ小火車", 24))
    # the map
    o.append(card(16, 78, 358, 250, "#E3F2FA", 2))
    o.append(taiwan_map(150, 90, 172, 230, at="桃園", done=("台北",)))
    o.append(tx(66, 112, "第 2 站", 15, SOFT) + tx(66, 136, "桃園", 24, INK))
    o.append(tx(66, 162, "ㄅ ㄆ ㄇ ㄈ", 17, darker(PINK, .4)))
    o.append(bubble(30, 266, 124, 44, "嘟嘟—出發！", 15, None))
    # the child's own train
    fy = 428
    o.append(card(16, 344, 358, 110, CREAM, 2))
    o.append(track(24, 366, fy))
    cars = [("ㄅ", STATION_COL["桃園"]), ("ㄜ", STATION_COL["台北"]), ("ㄛ", STATION_COL["台北"]), ("ㄆ", GREY, {"grey": True})]
    o.append(train(362, fy, cars, .9, driver=lambda: bear("happy")))
    o.append(tx(195, 360, "我的火車：9 節車廂，第 10 節是ㄆ", 12.5, SOFT))
    # the six buttons
    btns = [("認符號", BLUE, lambda: place(0, 8, .62, lambda: carriage(-27, 0, 54, 48, STATION_COL["桃園"], "ㄅ"))),
            ("聽聽找找", ORA, lambda: speaker_icon(0, -8, 1.4, "#FFFFFF")),
            ("拼拼看", TEAL, lambda: place(0, 8, .5, lambda: carriage(-56, 0, 50, 46, PINK, "ㄅ") + coupler(0, -10) + carriage(6, 0, 50, 46, BLUE, "ㄚ"))),
            ("寫寫看", GRN, lambda: tx(0, 6, "ㄅ", 34, "#FFFFFF") + stroke("M-22,-12 q-6,16 6,22", "#FFFFFF", 3, dash=(4, 4))),
            ("押韻接龍", PINK, lambda: place(-16, 10, .45, cat) + place(16, 10, .45, bun)),
            ("家裡找找", YEL, lambda: place(-14, 8, .5, cup) + place(14, 8, .5, pen))]
    for i, (lab, col, icon) in enumerate(btns):
        r_, c_ = divmod(i, 3)
        cx, cy = 76 + c_ * 119, 520 + r_ * 150
        o.append(piece(rr(cx - 54, cy - 56, 108, 118, 20), col, shade=2, bevel=1.4))
        o.append(flat(rr(cx - 44, cy - 46, 88, 62, 14), lighter(col, .55)))
        o.append(place(cx, cy - 16, 1.0, icon))
        o.append(tx(cx, cy + 44, lab, 17, "#FFFFFF" if col not in (YEL,) else INK))
        if lab == "拼拼看":
            o.append(f'<rect x="{cx + 18}" y="{cy - 66}" width="44" height="22" rx="11" fill="#FFFFFF" stroke="{darker(col, .4)}" stroke-width="2"/>' + tx(cx + 40, cy - 50, "0.2", 13, darker(col, .5)))
    o.append(place(338, 800, 1.0, lambda: bear("happy", wave=True)))
    o.append(bubble(170, 772, 150, 40, "今天想玩哪個？", 14, "left"))
    return page("".join(o))


# ================================================================ SCREEN 2: 認符號
def screen_learn():
    o = [board()]
    o.append(topbar("認符號", "桃園"))
    fy = 330
    o.append(card(16, 86, 358, 300, CREAM, 2))
    o.append(track(24, 366, fy))
    o.append(place(250, fy, 1.0, lambda: carriage(0, 0, 112, 100, STATION_COL["桃園"], "ㄅ", sym_size=78)))
    o.append(place(250 + 56, fy - 112, 1.0, lambda: tone_flag(0, 0, 1, .8, RED)))
    o.append(place(120, fy - 4, 1.15, dad))
    o.append(bubble(34, 106, 170, 44, "播，爸爸！", 18, "down"))
    o.append(sparkle(224, 190, 7, YEL) + sparkle(352, 150, 6, PINK) + sparkle(100, 250, 5, YEL))
    o.append(wbtn(330, 120, 24, ORA, speaker_icon(330, 120, 1.1)))
    o.append(tx(195, 408, "點車廂再聽一次；點爸爸，他會揮手", 13.5, SOFT))
    # the station's symbols
    o.append(tx(195, 450, "桃園站的車廂", 16, INK))
    fy2 = 540
    o.append(track(16, 374, fy2))
    for i, s in enumerate("ㄅㄆㄇㄈ"):
        x = 30 + i * 88
        o.append(place(x, fy2, 1.0, lambda s=s, i=i: carriage(0, 0, 72, 62, STATION_COL["桃園"] if i == 0 else WOOD, s, sym_size=40)))
        if i == 0:
            o.append(f'<rect x="{x}" y="{fy2 - 72}" width="72" height="62" rx="10" fill="none" stroke="{GRN}" stroke-width="4"/>')
            o.append(piece(circ(x + 64, fy2 - 70, 11), GRN, shade=1) + stroke(f"M{x + 59},{fy2 - 70} l4,4 l7,-8", "#FFFFFF", 2.5))
    o.append(tx(150, 574, "都點過一遍，火車頭就來接車廂", 13.5, SOFT, "start"))
    # the three other words of this station
    words = [("ㄆ 蘋果", apple), ("ㄇ 媽媽", mom), ("ㄈ 飛機", plane)]
    for i, (lab, fn) in enumerate(words):
        cx = 76 + i * 119
        o.append(picture_card(cx, 660, fn, lab, 92))
    o.append(finger(66, 500, -15))
    return page("".join(o))


# ================================================================ SCREEN 3: 聽聽找找
def screen_listen():
    o = [board()]
    o.append(topbar("聽聽找找", "桃園"))
    o.append(card(16, 86, 358, 230, CREAM, 2))
    o.append(wbtn(80, 200, 44, ORA, speaker_icon(80, 200, 2.0)))
    o.append(stroke("M132,180 q10,20 0,40 M146,168 q18,32 0,64", ORA, 3))
    o.append(place(250, 268, 1.5, mom))
    o.append(bubble(170, 100, 180, 44, "媽媽", 22, "down"))
    o.append(tx(195, 346, "媽媽的開頭是哪一節車廂？", 17, INK))
    fy = 500
    o.append(track(16, 374, fy))
    for i, (s, col) in enumerate((("ㄇ", STATION_COL["桃園"]), ("ㄅ", WOOD), ("ㄈ", WOOD))):
        x = 30 + i * 118
        if i == 0:
            o.append(f'<rect x="{x - 10}" y="{fy - 100}" width="112" height="112" rx="20" fill="{rg([(0, "#FFF4B0", .95), (.6, "#FFE26B", .6), (1, "#FFE26B", 0)])}"/>')
        o.append(place(x, fy, 1.0, lambda s=s, col=col: carriage(0, 0, 92, 78, col, s, sym_size=50)))
    o.append(finger(112, 486, -15))
    o.append(stroke("M196,580 q-40,-6 -64,-34", DARK, 2, dash=(5, 5)) + tx(214, 586, "媽媽走過去上車", 12.5, SOFT, "start"))
    # the counter
    o.append(tx(195, 630, "這一站：第 4 題，共 10 題", 14, SOFT))
    for i in range(10):
        cx = 60 + i * 30
        o.append(piece(circ(cx, 656, 8), GRN if i < 3 else (YEL if i == 3 else GREY), shade=1))
    o.append(card(16, 690, 358, 72, "#FFF0B5", 1))
    o.append(tx(32, 720, "點錯了：輕輕晃一下，念「這是ㄅ，爸爸的ㄅ」", 13.5, INK, "start"))
    o.append(tx(32, 744, "不扣分。小火車 2 選 1，大火車 3 選 1。", 13.5, SOFT, "start"))
    o.append(place(340, 836, .85, lambda: bear("smile")))
    return page("".join(o))


# ================================================================ SCREEN 4: 拼拼看
def screen_spell():
    o = [board()]
    o.append(topbar("拼拼看", "桃園"))
    o.append(card(16, 86, 358, 300, CREAM, 2))
    fy = 300
    o.append(track(24, 366, fy))
    o.append(place(60, fy, 1.0, lambda: carriage(0, 0, 100, 90, STATION_COL["桃園"], "ㄅ", sym_size=58)))
    o.append(place(60 + 108, fy - 10, 1.0, lambda: coupler(0, 0)))
    o.append(place(226, fy - 14, 1.0, lambda: carriage(0, 0, 100, 90, STATION_COL["台北"], "ㄚ", sym_size=58)))
    o.append(stroke("M250,186 q-30,-30 -60,-10", DARK, 2.5, dash=(6, 5)) + flat(poly([(186, 168), (192, 182), (176, 182)]), DARK))
    o.append(finger(318, 262, -15))
    o.append(tx(195, 120, "把ㄚ推過去，接起來（0.2 版）", 16, SOFT))
    o.append(tx(195, 362, "ㄅ — ㄚ — ㄅㄚ", 20, INK))
    # the tone flags
    o.append(tx(195, 430, "四面小旗子是四聲（家長打開才能換）", 14, SOFT))
    for i, t in enumerate((1, 2, 3, 4)):
        x = 90 + i * 70
        o.append(tone_flag(x, 500, t, 1.2, RED if t == 4 else "#E8D3AE", mcol="#FFFFFF" if t == 4 else INK))
        o.append(tx(x + 10, 524, ("一聲", "二聲", "三聲", "四聲")[i], 13, INK if t == 4 else SOFT))
    o.append(piece(circ(300, 462, 14), GRN, shade=1) + stroke("M293,462 l5,5 l9,-10", "#FFFFFF", 2.6))
    # the result
    o.append(card(16, 548, 358, 190, "#FFF0B5", 2))
    o.append(tx(80, 590, "ㄅㄚˋ", 30, INK) + tx(80, 650, "爸", 52, RED))
    o.append(place(200, 700, 1.2, dad))
    o.append(bubble(236, 560, 124, 40, "爸爸上車！", 15, None))
    o.append(place(330, 722, .9, lambda: carriage(-30, 0, 60, 52, STATION_COL["桃園"], "", passenger=dad)))
    o.append(tx(195, 772, "拼出來的字變成乘客，火車站看得到他坐在車廂裡", 12.5, SOFT))
    o.append(tx(195, 800, "三拼（ㄒ＋ㄧ＋ㄚ＝蝦）以後再加", 12.5, SOFT))
    return page("".join(o))


# ================================================================ SCREEN 5: 寫寫看
def screen_write():
    o = [board()]
    o.append(topbar("寫寫看", "桃園"))
    # the four stages
    for i, (lab, on) in enumerate((("看", 2), ("點", 2), ("描", 1), ("寫", 0))):
        cx = 62 + i * 88
        col = GRN if on == 2 else (YEL if on == 1 else GREY)
        o.append(wpill(cx, 96, 74, 34, col, lab, 17, INK if on else SOFT))
    # the big carriage to write on
    fy = 560
    o.append(track(24, 366, fy))
    o.append(place(45, fy, 1.0, lambda: carriage(0, 0, 300, 390, STATION_COL["桃園"], "", sym_size=1)))
    o.append(flat(rr(70, 180, 250, 330, 14), CREAM))
    big = 'font-size="270"'
    # the wide grey path, then the traced part in colour (clipped), then the start dot and the arrow
    o.append(f'<text x="195" y="440" text-anchor="middle" font-family="Huninn, sans-serif" {big} fill="none" stroke="{GREY}" stroke-width="34" stroke-linejoin="round" stroke-linecap="round">ㄅ</text>')
    o.append(f'<text x="195" y="440" text-anchor="middle" font-family="Huninn, sans-serif" {big} fill="none" stroke="#FFFFFF" stroke-width="20" stroke-linejoin="round" stroke-linecap="round" opacity=".7">ㄅ</text>')
    k = _clip(rr(70, 180, 250, 130, 0))
    o.append(f'<g clip-path="url(#{k})"><text x="195" y="440" text-anchor="middle" font-family="Huninn, sans-serif" {big} fill="none" stroke="{RED}" stroke-width="22" stroke-linejoin="round" stroke-linecap="round">ㄅ</text></g>')
    o.append(f'<text x="195" y="440" text-anchor="middle" font-family="Huninn, sans-serif" {big} fill="none" stroke="{darker(GREY, .15)}" stroke-width="1.5" stroke-dasharray="6 5">ㄅ</text>')
    o.append(piece(circ(126, 236, 14), GRN, shade=1) + flat(circ(126, 236, 6), "#FFFFFF"))
    o.append(stroke("M150,236 h40", GRN, 4) + flat(poly([(190, 228), (204, 236), (190, 244)]), GRN))
    o.append(finger(262, 262, -15))
    o.append(tx(195, 620, "從綠點開始，沿著小路描；描出去就停在那裡，回來再接著描", 12.5, SOFT))
    # the driver cheering, and the strokes done
    o.append(place(70, 760, 1.1, lambda: bear("happy", wave=True)))
    o.append(bubble(118, 672, 150, 40, "第一筆，往右！", 14, "left"))
    o.append(tx(260, 752, "第 1 筆／共 2 筆", 15, INK, "start"))
    o.append(piece(rr(260, 766, 50, 10, 5), RED, shade=0) + piece(rr(318, 766, 50, 10, 5), GREY, shade=0))
    o.append(tx(260, 806, "小火車：描完就好", 13, SOFT, "start") + tx(260, 826, "大火車：還要自己寫", 13, SOFT, "start"))
    return page("".join(o))


# ================================================================ SCREEN 6: 押韻接龍
def screen_rhyme():
    o = [board()]
    o.append(topbar("押韻接龍", "嘉義"))
    o.append(card(16, 86, 358, 70, CREAM, 2))
    o.append(wbtn(56, 121, 24, ORA, speaker_icon(56, 121, 1.1)))
    o.append(tx(210, 128, "哪兩個的尾巴一樣？", 20, INK))
    o.append(picture_card(76, 230, cat, "貓", 100, sel=True) + picture_card(195, 230, bun, "包", 100, sel=True) + picture_card(314, 230, fish, "魚", 100))
    o.append(finger(216, 266, -15))
    # the two couple together
    fy = 420
    o.append(track(16, 374, fy))
    o.append(place(60, fy, 1.0, lambda: carriage(0, 0, 100, 80, STATION_COL["嘉義"], "", passenger=cat)))
    o.append(place(168, fy - 10, 1.0, lambda: coupler(0, 0)))
    o.append(place(176, fy, 1.0, lambda: carriage(0, 0, 100, 80, STATION_COL["嘉義"], "", passenger=bun)))
    o.append(piece(circ(330, 372, 24), YEL, shade=2) + tx(330, 382, "ㄠ", 28, darker(ORA, .45)))
    o.append(sparkle(356, 346, 6, PINK) + sparkle(302, 342, 5, YEL))
    o.append(bubble(40, 440, 310, 44, "貓—包，尾巴都是ㄠ！", 18, "up"))
    # the other two kinds of questions
    o.append(tx(195, 530, "另外兩種題目", 16, INK))
    o.append(card(16, 546, 172, 170, "#E9F5FF", 1))
    o.append(tx(102, 572, "哪個是ㄇ開頭？", 14, INK))
    o.append(place(50, 670, .62, mom) + place(102, 670, .62, plane) + place(154, 670, .62, cat))
    o.append(f'<rect x="30" y="606" width="40" height="70" rx="10" fill="none" stroke="{GRN}" stroke-width="3"/>')
    o.append(tx(102, 702, "小火車先玩這種", 11.5, SOFT))
    o.append(card(202, 546, 172, 170, "#FFF0E0", 1))
    o.append(tx(288, 572, "接龍（大火車）", 14, INK))
    o.append(place(222, 646, .5, lambda: carriage(0, 0, 54, 48, STATION_COL["嘉義"], "", passenger=dog)))
    o.append(place(250, 641, .5, lambda: coupler(0, 0)))
    o.append(place(256, 646, .5, lambda: carriage(0, 0, 54, 48, STATION_COL["嘉義"], "", passenger=ball)))
    o.append(tx(330, 636, "狗→球→?", 13, INK))
    o.append(place(236, 696, .42, cup) + place(288, 696, .42, bear) + place(340, 696, .42, dad))
    o.append(tx(288, 708, "接對了火車變長", 11.5, SOFT))
    o.append(card(16, 726, 358, 60, "#FFF0B5", 1))
    o.append(tx(32, 750, "答對會說出為什麼；答錯再念一次兩個詞，不扣分。", 13, INK, "start"))
    o.append(tx(32, 772, "這是研究說最有用的練習：聽得出押韻、聽得出開頭音。", 13, SOFT, "start"))
    return page("".join(o))


# ================================================================ SCREEN 7: 家裡找找
def screen_home_task():
    o = [board()]
    o.append(topbar("家裡找找", "桃園"))
    o.append(place(80, 220, 1.4, lambda: bear("happy", wave=True)))
    o.append(bubble(150, 110, 220, 56, "今天的任務來囉！", 18, "left"))
    # the task card: a wooden luggage tag
    o.append(piece(rr(30, 250, 330, 380, 22), CREAM, shade=3, grain=.06))
    o.append(piece(circ(195, 276, 9), WALNUT, shade=0) + stroke("M195,276 q0,-30 0,-40", WALNUT, 3))
    o.append(tx(195, 330, "找找家裡有什麼", 24, INK))
    o.append(tx(195, 372, "ㄅ 開頭的東西？", 30, RED))
    o.append(place(100, 480, 1.0, cup) + place(195, 480, 1.0, pen) + place(290, 480, 1.0, bag))
    o.append(tx(100, 506, "杯子", 15, INK) + tx(195, 506, "筆", 15, INK) + tx(290, 506, "包包", 15, INK))
    o.append(tx(195, 548, "和爸爸媽媽一起找。這一頁沒有東西可以點，", 13, SOFT))
    o.append(tx(195, 568, "放下手機去找，找到再回來按。", 13, SOFT))
    o.append(wpill(195, 606, 200, 50, GRN, "找到了！", 22, "#FFFFFF"))
    # what you get
    o.append(tx(195, 680, "找到了，火車頭多一個貼紙", 15, INK))
    o.append(track(60, 330, 790))
    o.append(place(330, 790, .95, lambda: engine(RED, lambda: bear("happy"))))
    o.append(piece(circ(282, 748, 14), YEL, shade=1) + place(282, 760, .36, cup))
    o.append(sparkle(300, 724, 7, YEL) + sparkle(262, 732, 5, PINK))
    o.append(tx(130, 760, "每個符號有 3～5 個", 13, SOFT) + tx(130, 780, "家裡找得到的提示", 13, SOFT))
    return page("".join(o))


# ================================================================ SCREEN 8: 家長模式
def screen_parents():
    o = [board(col="#F2EBE0")]
    o.append(home_btn(36, 38))
    o.append(sign(195, 40, 200, "家長模式", 22))
    o.append(lock_chip(334, 24))
    y = 84
    o.append(tx(16, y + 14, "難度和時間", 14, SOFT, "start"))
    y += 24
    o.append(row(y, "難度", wpill(250, y + 23, 92, 32, GRN, "小火車", 14, "#FFFFFF") + wpill(330, y + 23, 60, 32, GREY, "大", 14, SOFT)))
    y += 52
    o.append(row(y, "每次玩多久", tx(300, y + 29, "15 分鐘", 16, INK) + wbtn(260, y + 23, 13, WOOD2, tx(260, y + 28, "－", 15, INK)) + wbtn(344, y + 23, 13, WOOD2, tx(344, y + 28, "＋", 15, INK))))
    y += 52
    o.append(row(y, "聲調旗子（0.2）", wpill(236, y + 23, 50, 30, GREY, "關", 13, SOFT) + wpill(292, y + 23, 56, 30, GRN, "固定", 13, "#FFFFFF") + wpill(348, y + 23, 50, 30, GREY, "換", 13, SOFT)))
    y += 60
    o.append(tx(16, y + 14, "要哪幾站", 14, SOFT, "start"))
    y += 24
    o.append(card(16, y, 358, 96, WHITE, 1, 14))
    for i, (name, syms) in enumerate(STATIONS):
        cx = 40 + i * 52
        on = i < 4
        o.append(piece(circ(cx, y + 30, 16), STATION_COL[name] if on else GREY, shade=1))
        if on:
            o.append(stroke(f"M{cx - 6},{y + 30} l4,4 l8,-9", "#FFFFFF", 2.5))
        o.append(tx(cx, y + 62, name, 11.5, INK if on else SOFT))
        o.append(tx(cx, y + 80, syms[:3] + ("…" if len(syms) > 3 else ""), 10, SOFT))
    y += 104
    o.append(row(y, "符號順序", wpill(258, y + 23, 74, 30, GRN, "常用先", 13, "#FFFFFF") + wpill(334, y + 23, 66, 30, GREY, "課本", 13, SOFT)))
    y += 60
    o.append(tx(16, y + 14, "語音", 14, SOFT, "start"))
    y += 24
    o.append(row(y, "試聽：播，爸爸", wbtn(330, y + 23, 18, ORA, speaker_icon(330, y + 23, .85)) + tx(286, y + 28, "慢一點", 13, SOFT)))
    y += 60
    o.append(tx(16, y + 14, "進度（37 節車廂）", 14, SOFT, "start"))
    y += 24
    o.append(card(16, y, 358, 168, WHITE, 1, 14))
    all_syms = [(s, n) for n, syms in STATIONS for s in syms]
    for i, (s, n) in enumerate(all_syms):
        r_, c_ = divmod(i, 10)
        cx, cy = 38 + c_ * 35, y + 26 + r_ * 32
        st = 3 if i < 7 else (2 if i < 9 else (1 if i < 10 else 0))
        col = STATION_COL[n] if st >= 2 else (lighter(STATION_COL[n], .6) if st == 1 else "#EFEAE2")
        o.append(piece(rr(cx - 14, cy - 11, 28, 22, 5), col, shade=1 if st else 0))
        o.append(tx(cx, cy + 5, s, 13, INK if st else GREY))
        if st == 3:
            o.append(piece(circ(cx + 12, cy - 9, 5), GRN, shade=0))
    o.append(tx(32, y + 158, "顏色＝聽對 3 次；綠點＝描過；淡色＝認過。押韻題答對 8／10。", 11.5, SOFT, "start"))
    y += 176
    o.append(row(y, "家裡找找：今天是ㄅ（杯子、筆、包包）", tx(356, y + 29, "", 13, SOFT, "end")))
    y += 52
    o.append(row(y, "左撇子、音樂、音效、完整版", tx(350, y + 29, "›", 20, SOFT)))
    return page("".join(o), "#F2EBE0")


# ================================================================ PAGE 0: THE SAME SCENE IN THREE STYLES
def station_scene(x, y, w=330, h=240):
    """A little station: a hill, the sun, the platform sign, the engine with the driver bear and three carriages ㄅㄆㄇ."""
    o = []
    sky = {"neon": "#1A2447", "cookie": "#FBEFD8", "pencil": "#EAF3F8"}.get(STYLE, SKY)
    hill = {"neon": "#2B3A5C", "cookie": "#CFE3A6"}.get(STYLE, GRASS)
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{sky}"/>')
    if STYLE == "pencil":
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{hatch_pat("#9CC5DD", 38, 5)}" opacity=".5"/>')
    k = _clip(rr(x, y, w, h, 14))
    o.append(f'<g clip-path="url(#{k})">')
    o.append(piece(ell(x + w * .3, y + h * .78, w * .55, h * .36), hill, shade=0, grain=.08))
    o.append(piece(ell(x + w * .85, y + h * .82, w * .4, h * .3), darker(hill, .1), shade=0, grain=.08))
    o.append(piece(circ(x + w - 50, y + 44, 22), YEL, shade=1))
    o.append(face(x + w - 50, y + 42, 1.0, "happy"))
    for i in range(8):
        a = math.radians(i * 45)
        o.append(stroke(f"M{x + w - 50 + 30 * math.cos(a):.1f},{y + 44 + 30 * math.sin(a):.1f} l{8 * math.cos(a):.1f},{8 * math.sin(a):.1f}", YEL, 3))
    o.append(piece(circ(x + 60, y + 60, 16), "#FFFFFF", shade=0) + piece(circ(x + 80, y + 54, 20), "#FFFFFF", shade=0) + piece(circ(x + 100, y + 62, 14), "#FFFFFF", shade=0))
    o.append(sign(x + 84, y + 100, 96, "桃園", 18))
    o.append(piece(rr(x + 84 - 4, y + 118, 8, 50, 3), WALNUT, shade=1))
    fy = y + h - 34
    o.append(wood(rr(x - 10, fy, w + 20, 40, 0), WOOD2, shade=0))
    o.append(track(x - 10, x + w + 10, fy))
    cars = [("ㄅ", PINK, {"sym_size": 34}), ("ㄆ", BLUE, {"sym_size": 34}), ("ㄇ", GRN, {"sym_size": 34})]
    o.append(train(x + w + 4, fy, cars, .8, driver=lambda: bear("happy")))
    o.append("</g>")
    return "".join(o)


def style_sheet():
    global STYLE
    ph = 1226
    o = [f'<rect width="{W}" height="{ph}" fill="#F7F2EA"/>']
    o.append(tx(195, 58, "畫風：選好了", 30, INK))
    o.append(tx(195, 90, "同一個車站，三種畫法；2026-11-15 選 A", 16, SOFT))
    bands = [("A 軟膠公仔風", "像軟膠玩具公仔：圓滾滾亮亮的，大反光、深色邊。", "vinyl"),
             ("B 糖霜餅乾風", "每樣東西都是糖霜餅乾：餅乾邊、糖霜、糖珠。", "cookie"),
             ("C 色鉛筆手繪風", "色鉛筆畫在米色紙上：一筆一筆的斜線、歪歪的框。", "pencil")]
    y = 116
    for title, desc, st in bands:
        h = 346
        if st == "vinyl":
            o.append(f'<rect x="12" y="{y - 4}" width="366" height="{h + 8}" rx="28" fill="#5DB86A"/>')
            o.append(f'<rect x="16" y="{y}" width="358" height="{h}" rx="24" fill="#FFFFFF"/>')
            o.append(f'<rect x="262" y="{y - 14}" width="100" height="30" rx="15" fill="#5DB86A"/>'
                     + stroke(f"M276,{y + 1} l5,5 l9,-10", "#FFFFFF", 3) + tx(326, y + 7, "選這個", 14, "#FFFFFF"))
        else:
            o.append(f'<rect x="16" y="{y + 4}" width="358" height="{h}" rx="24" fill="#E9DED3"/><rect x="16" y="{y}" width="358" height="{h}" rx="24" fill="#FFFFFF"/>')
        o.append(tx(34, y + 40, title, 22, INK, "start"))
        o.append(tx(34, y + 68, desc, 13.5, "#6E5C52", "start"))
        STYLE = st
        o.append(station_scene(30, y + 88, 330, 240))
        STYLE = "vinyl"
        if st != "vinyl":
            o.append(f'<rect x="16" y="{y}" width="358" height="{h}" rx="24" fill="#F7F2EA" opacity=".55"/>')
            o.append(f'<rect x="276" y="{y + 18}" width="82" height="28" rx="14" fill="#D9D2C8"/>' + tx(317, y + 37, "沒有選", 14, "#6E5C52"))
        y += h + 22
    return page("".join(o), "#F7F2EA", W, ph), ph


# ================================================================ CONTACT SHEET AND MAIN
def contact_sheet(names):
    cw_, ch_, gap, m = 232, 502, 24, 30
    per = 4
    rows = (len(names) + per - 1) // per
    w = per * cw_ + (per - 1) * gap + 2 * m
    rowh = ch_ + 64
    h = rows * rowh + 40
    items = []
    for i, n in enumerate(names):
        r, c = divmod(i, per)
        x = m + c * (cw_ + gap)
        y = 28 + r * rowh
        items.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{cw_}px;text-align:center">'
                     f'<img src="file://{HERE / (n + ".png")}" style="width:{cw_}px;height:{ch_}px;border-radius:18px;box-shadow:0 6px 16px rgba(90,60,40,.2)">'
                     f'<div style="font:19px Huninn, sans-serif;color:{INK};margin-top:10px">{n.replace("_", " ")}</div></div>')
    css = f"@font-face {{ font-family: Huninn; src: url('file://{FONT}'); }} * {{ margin:0; padding:0 }} body {{ width:{w}px; height:{h}px; background:#F7F1E8; position:relative }}"
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(items)}</body></html>', w, h


SCREENS = {"1_火車站": screen_station, "2_認符號": screen_learn, "3_聽聽找找": screen_listen, "4_拼拼看": screen_spell,
           "5_寫寫看": screen_write, "6_押韻接龍": screen_rhyme, "7_家裡找找": screen_home_task, "8_家長模式": screen_parents}


def main(only=None):
    global D
    if only in (None, "0"):
        D = Defs()
        html, ph = style_sheet()
        render(html, HERE / "0_畫風選擇.png", W, ph, 2)
        print("0_畫風選擇")
    for name, make in SCREENS.items():
        if only not in (None, name.split("_")[0]):
            continue
        D = Defs()
        render(make(), HERE / f"{name}.png", W, H, 2)
        print(name)
    if only in (None, "c"):
        html, w, h = contact_sheet(list(SCREENS))
        render(html, HERE / "contact_sheet.png", w, h, 1.25)
        print("contact_sheet")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
