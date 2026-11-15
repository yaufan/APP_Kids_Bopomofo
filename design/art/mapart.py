"""The map of Taiwan (docs/art.md 「地圖」): the island as a soft green vinyl toy with its mountains,
and the railway from 台北 down the west to 高雄. The sea is the app's background; the stations,
flags and the little train are drawn by the app on top, at the places this writes into
app/lib/app/map_layout.dart (fractions of the picture).
"""
import sys

sys.dont_write_bytecode = True

import kit  # noqa: E402
from kit import smooth, circle, ellipse, Shape  # noqa: E402

OUT = kit.ART / "map"
DART = kit.ROOT / "app" / "lib" / "app" / "map_layout.dart"
W, H = 260, 420

# Taiwan's coast (longitude, latitude), clockwise from the northern tip.
COAST = [
    (121.54, 25.30), (121.74, 25.16), (121.95, 25.04), (121.85, 24.80), (121.86, 24.56), (121.66, 24.10),
    (121.55, 23.70), (121.42, 23.30), (121.22, 22.90), (120.98, 22.50), (120.86, 21.92), (120.70, 21.96),
    (120.60, 22.36), (120.30, 22.56), (120.12, 22.96), (120.12, 23.40), (120.28, 23.90), (120.48, 24.25),
    (120.86, 24.70), (121.02, 25.02), (121.38, 25.18),
]
# The stations: 台北 桃園 新竹 台中 嘉義 台南 高雄.
STATIONS = [(121.52, 25.04), (121.30, 24.97), (120.97, 24.79), (120.68, 24.15), (120.45, 23.48), (120.21, 23.00), (120.31, 22.63)]
NAMES = ["台北", "桃園", "新竹", "台中", "嘉義", "台南", "高雄"]


def at(lon, lat):
    """Longitude, latitude to the picture (about 100 units per 100 km, 20 units of sea around)."""
    return 30 + (lon - 119.98) * 102 * .95, 14 + (25.36 - lat) * 111 * 1.0


def track_points():
    pts = [at(*s) for s in STATIONS]
    # Inland of the coast a little, a gentle curve through every station.
    return pts


def island():
    c = kit.Ctx(W, H)
    coast = smooth([at(*p) for p in COAST], .8)
    c.vinyl(coast, "#8FD67E", rim=3, hl=(.62, .1), hl_size=.55, sh=(4, 6))
    # The mountains down the middle (the Central Range), lighter and darker greens.
    for lon, lat, r, col in ((121.30, 24.45, 20, "#6CC46A"), (121.14, 24.0, 24, "#5DB860"), (121.02, 23.55, 24, "#6CC46A"),
                             (120.92, 23.12, 20, "#5DB860"), (120.80, 22.70, 15, "#6CC46A")):
        x, y = at(lon, lat)
        peak = Shape([("M", x - r * 1.2, y + r * .55), ("C", x - r * .6, y - r * .2, x - r * .3, y - r * .9, x, y - r * .95),
                      ("C", x + r * .3, y - r * .9, x + r * .6, y - r * .2, x + r * 1.2, y + r * .55), ("Z",)])
        c.vinyl(peak, col, rim=2, hl=(.4, .3), hl_size=.6, shadow=False)
        c.flat(Shape([("M", x - r * .32, y - r * .62), ("C", x - r * .15, y - r * .9, x + r * .15, y - r * .9, x + r * .32, y - r * .62),
                       ("C", x + r * .1, y - r * .52, x - r * .1, y - r * .52, x - r * .32, y - r * .62), ("Z",)]), "#FFFFFF", op=.85)
    # Little trees on the plains.
    for lon, lat in ((121.15, 24.70), (120.62, 23.80), (120.40, 23.20), (120.50, 22.40), (121.60, 24.85)):
        x, y = at(lon, lat)
        c.vinyl(circle(x, y, 6), kit.LEAF, rim=1.4, hl=(.3, .25), shadow=False)
    # The railway: a double line with sleepers, through every station.
    pts = track_points()
    line = Shape([("M",) + pts[0]] + [("L",) + p for p in pts[1:]])
    c.stroke(line, "#7A5A40", 9)
    c.stroke(line, "#F6E3C4", 5.5)
    c.stroke(line, "#9C7A5A", 1.2)
    # Waves in the sea.
    for x, y in ((40, 60), (200, 330), (32, 300), (220, 140), (60, 380)):
        c.stroke(Shape([("M", x - 10, y), ("C", x - 6, y - 4, x - 2, y - 4, x, y), ("C", x + 2, y + 4, x + 6, y + 4, x + 10, y)]), "#FFFFFF", 2.4, op=.7)
    return c.svg()


def write_layout():
    pts = [at(*s) for s in STATIONS]
    lines = ",\n".join(f"  ({x / W:.4f}, {y / H:.4f})" for x, y in pts)
    DART.write_text(f"""// Written by design/art/mapart.py: do not edit by hand.

/// The map picture's width / height (assets/art/map/taiwan.svg).
const mapAspect = {W} / {H};

/// Where each station is on the map, as fractions of the picture (台北 to 高雄).
const mapStations = [
{lines},
];
""")


def build():
    kit.write_svg(OUT / "taiwan.svg", island())
    write_layout()
    print("map: done")


if __name__ == "__main__":
    build()
