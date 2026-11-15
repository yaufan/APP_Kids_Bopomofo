"""Everything the app knows about the 37 symbols, as app/assets/bopomofo.json.

For each symbol: its station in both orders (常用先 and 課本), whether it is an initial or a final,
its example word, a short shape story for 大火車, the 家裡找找 hints and
its strokes in writing order (docs/bopomofo.md). Plus every picture word: its zhuyin (toneless, one
string per syllable), which syllable is the "key" one for words that teach a final at their end,
and whether it is a thing found at home.

    python3 design/bopomofo.py              # writes app/assets/bopomofo.json, checks it, prints a summary
    python3 design/bopomofo.py preview OUT.png   # every symbol's strokes over the font (numbered, start dots)

A symbol sits in a 100 x 100 box, y growing down. Each stroke is a list of points about 2.5 apart,
from where the pen starts to where it lifts (the same format as 字母寵物's glyphs.json).
"""
import json
import math
import pathlib
import sys

sys.dont_write_bytecode = True

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "app" / "assets" / "bopomofo.json"
FONT = ROOT / "app" / "assets" / "fonts" / "jf-openhuninn-2.1.ttf"
STEP = 2.5

INITIALS = "ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙ"
FINALS = "ㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦㄧㄨㄩ"

# ---------------------------------------------------------------- stations
STATIONS = [  # name, colour (docs/design.md 「顏色」)
    ("台北", "#8CCBF2"),  # light blue
    ("桃園", "#F59BC2"),  # pink
    ("新竹", "#7FD08A"),  # green
    ("台中", "#FFD44F"),  # yellow
    ("嘉義", "#FFA35C"),  # orange
    ("台南", "#B79AF0"),  # purple
    ("高雄", "#4FD1C5"),  # teal
]
ORDERS = {
    # 常用的先 (the default): the five easiest finals, lips, tongue tip, throat, the other finals,
    # ㄐㄑㄒ with ㄩㄝ, and the hard 捲舌音 and 平舌音 last.
    "common": ["ㄚㄧㄨㄛㄜ", "ㄅㄆㄇㄈ", "ㄉㄊㄋㄌ", "ㄍㄎㄏ", "ㄞㄟㄠㄡㄢㄣㄤㄥ", "ㄐㄑㄒㄩㄝ", "ㄓㄔㄕㄖㄗㄘㄙㄦ"],
    # 課本順序 (a parent's switch).
    "textbook": ["ㄅㄆㄇㄈ", "ㄉㄊㄋㄌ", "ㄍㄎㄏㄐㄑㄒ", "ㄓㄔㄕㄖㄗㄘㄙ", "ㄧㄨㄩㄚㄛㄜㄝ", "ㄞㄟㄠㄡ", "ㄢㄣㄤㄥㄦ"],
}

# ---------------------------------------------------------------- the words (and pictures)
# id: (詞, zhuyin syllables, at home?, key syllable or None). Toneless zhuyin; a syllable with no
# final (子 ㄗ, 紙 ㄓ) gives the word no rhyme. Every id is a picture in app/assets/art/words/.
W = {}


def word(wid, zh, zy, home=False, key=None):
    W[wid] = {"id": wid, "zh": zh, "zy": zy.split(), "home": home, **({"key": key} if key is not None else {})}


# The 37 example words (docs/design.md 「每個符號的圖和詞」; ㄍ is 鴿子 so 狗 can be ㄡ's, ㄖ 熱狗,
# ㄙ 松鼠 and ㄝ 椰子 because they draw better than 日, 三 and 「耶！」).
word("baba", "爸爸", "ㄅㄚ ㄅㄚ", True)
word("apple", "蘋果", "ㄆㄧㄥ ㄍㄨㄛ", True)
word("mama", "媽媽", "ㄇㄚ ㄇㄚ", True)
word("plane", "飛機", "ㄈㄟ ㄐㄧ")
word("didi", "弟弟", "ㄉㄧ ㄉㄧ", True)
word("rabbit", "兔子", "ㄊㄨ ㄗ")
word("milk", "牛奶", "ㄋㄧㄡ ㄋㄞ", True)
word("mouse", "老鼠", "ㄌㄠ ㄕㄨ")
word("pigeon", "鴿子", "ㄍㄜ ㄗ")
word("dino", "恐龍", "ㄎㄨㄥ ㄌㄨㄥ", True)
word("flower", "花", "ㄏㄨㄚ", True)
word("chicken", "雞", "ㄐㄧ")
word("balloon", "氣球", "ㄑㄧ ㄑㄧㄡ", True)
word("melon", "西瓜", "ㄒㄧ ㄍㄨㄚ", True)
word("pig", "豬", "ㄓㄨ")
word("car", "車子", "ㄔㄜ ㄗ", True)
word("lion", "獅子", "ㄕ ㄗ")
word("hotdog", "熱狗", "ㄖㄜ ㄍㄡ", True)
word("mouth", "嘴巴", "ㄗㄨㄟ ㄅㄚ", True)
word("strawberry", "草莓", "ㄘㄠ ㄇㄟ", True)
word("squirrel", "松鼠", "ㄙㄨㄥ ㄕㄨ")
word("grandma", "阿嬤", "ㄚ ㄇㄚ", True)
word("rooster", "喔喔喔", "ㄛ ㄛ ㄛ")
word("goose", "鵝", "ㄜ")
word("coconut", "椰子", "ㄧㄝ ㄗ", key=0)
word("heart", "愛心", "ㄞ ㄒㄧㄣ")
word("cup", "杯子", "ㄅㄟ ㄗ", True, key=0)
word("cat", "貓", "ㄇㄠ")
word("dog", "狗", "ㄍㄡ")
word("helmet", "安全帽", "ㄢ ㄑㄩㄢ ㄇㄠ", True)
word("door", "門", "ㄇㄣ", True)
word("candy", "糖", "ㄊㄤ", True)
word("lamp", "燈", "ㄉㄥ", True)
word("ear", "耳朵", "ㄦ ㄉㄨㄛ", True)
word("clothes", "衣服", "ㄧ ㄈㄨ", True)
word("turtle", "烏龜", "ㄨ ㄍㄨㄟ")
word("fish", "魚", "ㄩ")
# More words for 押韻接龍 and 家裡找找.
word("bag", "包包", "ㄅㄠ ㄅㄠ", True)
word("ball", "球", "ㄑㄧㄡ", True)
word("hand", "手", "ㄕㄡ", True)
word("book", "書", "ㄕㄨ", True)
word("bowl", "碗", "ㄨㄢ", True)
word("umbrella", "傘", "ㄙㄢ", True)
word("bed", "床", "ㄔㄨㄤ", True)
word("cloud", "雲", "ㄩㄣ")
word("rain", "雨", "ㄩ")
word("plate", "盤子", "ㄆㄢ ㄗ", True)
word("bottle", "瓶子", "ㄆㄧㄥ ㄗ", True)
word("hat", "帽子", "ㄇㄠ ㄗ", True)
word("soap", "肥皂", "ㄈㄟ ㄗㄠ", True)
word("fan", "風扇", "ㄈㄥ ㄕㄢ", True)
word("pineapple", "鳳梨", "ㄈㄥ ㄌㄧ", True)
word("egg", "蛋", "ㄉㄢ", True)
word("spoon", "湯匙", "ㄊㄤ ㄔ", True)
word("peach", "桃子", "ㄊㄠ ㄗ", True)
word("clock", "鬧鐘", "ㄋㄠ ㄓㄨㄥ", True)
word("lemon", "檸檬", "ㄋㄧㄥ ㄇㄥ", True)
word("pear", "梨子", "ㄌㄧ ㄗ", True)
word("basket", "籃子", "ㄌㄢ ㄗ", True)
word("stairs", "樓梯", "ㄌㄡ ㄊㄧ", True)
word("pot", "鍋子", "ㄍㄨㄛ ㄗ", True)
word("gege", "哥哥", "ㄍㄜ ㄍㄜ", True)
word("juice", "果汁", "ㄍㄨㄛ ㄓ", True)
word("chopsticks", "筷子", "ㄎㄨㄞ ㄗ", True)
word("pants", "褲子", "ㄎㄨ ㄗ", True)
word("box", "盒子", "ㄏㄜ ㄗ", True)
word("train", "火車", "ㄏㄨㄛ ㄔㄜ", True)
word("blocks", "積木", "ㄐㄧ ㄇㄨ", True)
word("scissors", "剪刀", "ㄐㄧㄢ ㄉㄠ", True)
word("jiejie", "姊姊", "ㄐㄧㄝ ㄐㄧㄝ", True)
word("banana", "香蕉", "ㄒㄧㄤ ㄐㄧㄠ", True)
word("shoes", "鞋子", "ㄒㄧㄝ ㄗ", True)
word("skirt", "裙子", "ㄑㄩㄣ ㄗ", True)
word("table", "桌子", "ㄓㄨㄛ ㄗ", True)
word("pillow", "枕頭", "ㄓㄣ ㄊㄡ", True)
word("paper", "紙", "ㄓ", True)
word("ruler", "尺", "ㄔ", True)
word("comb", "梳子", "ㄕㄨ ㄗ", True)
word("calendar", "日曆", "ㄖ ㄌㄧ", True)
word("meat", "肉", "ㄖㄡ", True)
word("soccer", "足球", "ㄗㄨ ㄑㄧㄡ", True)
word("zongzi", "粽子", "ㄗㄨㄥ ㄗ", True)
word("onion", "蔥", "ㄘㄨㄥ", True)
word("magnet", "磁鐵", "ㄘ ㄊㄧㄝ", True)
word("broom", "掃把", "ㄙㄠ ㄅㄚ", True)
word("garlic", "蒜頭", "ㄙㄨㄢ ㄊㄡ", True)
word("yeye", "爺爺", "ㄧㄝ ㄧㄝ", True)
word("cabbage", "白菜", "ㄅㄞ ㄘㄞ", True)
word("headphones", "耳機", "ㄦ ㄐㄧ", True)
word("earring", "耳環", "ㄦ ㄏㄨㄢ", True)
word("corn", "玉米", "ㄩ ㄇㄧ", True)
word("raincoat", "雨衣", "ㄩ ㄧ", True)

# ---------------------------------------------------------------- strokes


def L(*pts):
    """A straight polyline through [pts]."""
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        k = max(1, math.ceil(math.dist(a, b) / STEP))
        out += [(a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k) for i in range(1, k + 1)]
    return out


def C(*pts):
    """A smooth curve through [pts] (Catmull-Rom)."""
    p = [pts[0]] + list(pts) + [pts[-1]]
    out = [pts[0]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        k = max(2, math.ceil(math.dist(p1, p2) / STEP))
        for j in range(1, k + 1):
            t = j / k
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * t + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t2
                                    + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t3) for d in (0, 1)))
    return out


def J(*parts):
    """One stroke made of pieces that follow on from each other."""
    out = list(parts[0])
    for q in parts[1:]:
        out += q[1:] if math.dist(out[-1], q[0]) < 1e-6 else L(out[-1], q[0])[1:] + q[1:]
    return out


# Shapes follow jf open 粉圓 (the font the app writes the symbols in); order and directions are in
# docs/bopomofo.md, with the ones not checked against the 教育部 manual marked there.
STROKES = {
    "ㄅ": [L((28, 7), (20, 29)), J(L((20, 29), (78, 29)), C((79, 31), (77, 55), (72, 78), (63, 86), (47, 87)))],
    "ㄆ": [L((31, 7), (22, 29)), J(L((22, 29), (76, 29)), C((77, 31), (62, 57), (40, 77), (10, 92))), C((28, 47), (52, 66), (79, 91))],
    "ㄇ": [L((13, 12), (13, 90)), L((13, 12), (85, 12), (85, 90))],
    "ㄈ": [L((14, 12), (86, 12)), L((14, 12), (14, 83), (88, 83))],
    "ㄉ": [L((28, 7), (20, 29)), J(L((20, 29), (79, 29)), C((80, 31), (78, 60), (73, 82), (63, 88), (50, 88))), C((44, 30), (39, 56), (27, 77), (9, 91))],
    "ㄊ": [L((5, 30), (93, 30)), J(C((50, 5), (42, 35), (30, 62), (15, 86)), L((15, 86), (79, 77))), C((64, 59), (75, 74), (86, 91))],
    "ㄋ": [J(L((12, 12), (58, 12), (39, 37), (80, 38)), C((81, 40), (78, 68), (71, 86), (60, 90), (46, 90)))],
    "ㄌ": [L((24, 6), (17, 29)), J(L((17, 30), (81, 30)), C((82, 32), (80, 60), (75, 84), (65, 89), (52, 89))), C((51, 5), (48, 34), (39, 61), (25, 80), (8, 91))],
    "ㄍ": [L((39, 6), (12, 46), (45, 91)), L((73, 6), (56, 46), (84, 91))],
    "ㄎ": [L((5, 12), (92, 12)), J(L((38, 15), (23, 44), (77, 44)), C((78, 46), (75, 70), (69, 85), (58, 90), (38, 90)))],
    "ㄏ": [L((13, 15), (88, 15)), C((13, 16), (13, 45), (10, 70), (3, 89))],
    "ㄐ": [L((23, 8), (23, 70), (65, 58)), L((71, 5), (71, 92))],
    "ㄑ": [L((65, 6), (25, 47), (68, 92))],
    "ㄒ": [L((6, 12), (92, 12)), L((48, 12), (48, 92))],
    "ㄓ": [L((48, 5), (48, 82)), L((13, 12), (13, 58), (85, 58)), L((85, 12), (85, 58)), L((5, 83), (92, 83))],
    "ㄔ": [C((60, 4), (40, 22), (18, 33)), C((75, 18), (48, 45), (9, 63)), L((49, 44), (49, 92))],
    "ㄕ": [L((13, 12), (84, 12), (84, 46)), L((25, 46), (84, 46)), C((25, 47), (23, 66), (15, 82), (5, 92))],
    "ㄖ": [L((14, 10), (14, 88)), L((14, 10), (84, 10), (84, 88)), L((40, 35), (54, 60)), L((14, 88), (84, 88))],
    "ㄗ": [J(L((8, 13), (79, 13)), C((80, 15), (79, 38), (76, 54), (68, 59), (57, 59))), L((40, 14), (40, 93))],
    "ㄘ": [L((5, 22), (92, 22)), J(L((47, 4), (24, 52), (77, 52)), C((78, 54), (70, 75), (57, 92)))],
    "ㄙ": [J(C((44, 5), (31, 38), (20, 62), (10, 81)), L((10, 81), (74, 73))), C((65, 52), (77, 71), (86, 90))],
    "ㄚ": [L((12, 8), (48, 42)), L((84, 8), (48, 42)), L((48, 42), (48, 92))],
    "ㄛ": [L((7, 18), (90, 18)), J(L((47, 19), (47, 42)), C((47, 42), (28, 44), (14, 55), (13, 70), (24, 83), (45, 88), (67, 85), (85, 73)))],
    "ㄜ": [L((5, 25), (88, 25)), J(L((46, 5), (46, 47)), C((46, 47), (28, 48), (14, 58), (13, 72), (25, 84), (46, 89), (68, 86), (86, 74)))],
    "ㄝ": [L((3, 38), (93, 38)), J(L((21, 10), (21, 80)), C((21, 80), (23, 86), (30, 88)), L((30, 88), (80, 88))), C((69, 7), (68, 40), (65, 58), (60, 68))],
    "ㄞ": [L((5, 10), (88, 10)), J(L((22, 25), (12, 50), (80, 50)), C((81, 52), (75, 75), (68, 92))), C((50, 11), (46, 40), (35, 63), (12, 90))],
    "ㄟ": [J(L((8, 30), (30, 13)), C((30, 13), (43, 42), (60, 68), (85, 88)))],
    "ㄠ": [J(C((50, 5), (35, 28), (15, 48)), L((15, 48), (57, 45))), J(C((70, 28), (50, 52), (30, 71), (12, 88)), L((12, 88), (78, 80))), C((62, 61), (73, 76), (81, 91))],
    "ㄡ": [J(L((13, 15), (80, 15)), C((81, 17), (68, 46), (48, 70), (9, 92))), C((28, 38), (52, 57), (83, 91))],
    "ㄢ": [L((5, 12), (66, 12), (53, 44)), J(L((19, 25), (12, 50), (77, 50)), C((78, 52), (70, 75), (57, 92)))],
    "ㄣ": [J(C((27, 5), (19, 25), (13, 42)), L((13, 42), (80, 44)), C((80, 46), (74, 68), (66, 89)))],
    "ㄤ": [L((5, 28), (90, 28)), C((44, 5), (43, 35), (36, 60), (22, 78), (5, 90)), J(L((52, 45), (52, 80)), C((52, 80), (55, 87), (62, 88)), L((62, 88), (90, 87)))],
    "ㄥ": [J(C((50, 5), (36, 38), (21, 64), (10, 82)), L((10, 82), (88, 80)))],
    "ㄦ": [C((30, 5), (29, 40), (25, 64), (15, 80), (5, 90)), J(L((61, 5), (61, 80)), C((61, 80), (64, 87), (71, 88)), L((71, 88), (90, 88)))],
    "ㄧ": [L((5, 50), (93, 50))],
    "ㄨ": [C((77, 5), (55, 45), (30, 73), (8, 90)), C((18, 12), (50, 45), (83, 90))],
    "ㄩ": [L((12, 8), (12, 88), (82, 88)), L((82, 8), (82, 88))],
}

# Stroke counts checked against the 教育部《國語注音符號手冊》; the others (docs/bopomofo.md 「還沒確定
# 的筆順」) follow the rules for characters and the font's shape until someone checks the manual.
SURE = {"ㄇ": 2, "ㄈ": 2, "ㄍ": 2, "ㄎ": 2, "ㄏ": 2, "ㄐ": 2, "ㄑ": 1, "ㄒ": 2, "ㄔ": 3, "ㄕ": 3, "ㄖ": 4,
        "ㄗ": 2, "ㄙ": 2, "ㄊ": 3, "ㄟ": 1, "ㄡ": 2, "ㄤ": 3, "ㄥ": 1, "ㄦ": 2, "ㄧ": 1, "ㄨ": 2, "ㄩ": 2}

# ---------------------------------------------------------------- the symbols
# symbol: (id, example word id, shape story for 大火車). The 同音國字 the voice reads for each symbol
# is the table in app/lib/core/voice.dart (docs/design.md 「語音」).
SYMBOLS = {
    "ㄅ": ("b", "baba", "ㄅ像爸爸彎彎的手臂，抱抱你。"),
    "ㄆ": ("p", "apple", "ㄆ像一個人，跨大步往前走。"),
    "ㄇ": ("m", "mama", "ㄇ像一扇門，媽媽從門走進來。"),
    "ㄈ": ("f", "plane", "ㄈ像一個打開的盒子，飛機停進去。"),
    "ㄉ": ("d", "didi", "ㄉ像一把小刀，切蛋糕給弟弟。"),
    "ㄊ": ("t", "rabbit", "ㄊ上面一條路，下面一個小三角。"),
    "ㄋ": ("n", "milk", "ㄋ像彎來彎去的溜滑梯。"),
    "ㄌ": ("l", "mouse", "ㄌ像「力」字，用力拉！"),
    "ㄍ": ("g", "pigeon", "ㄍ像兩隻鴿子的尖嘴巴。"),
    "ㄎ": ("k", "dino", "ㄎ上面一條線，下面一個彎彎的掛鉤。"),
    "ㄏ": ("h", "flower", "ㄏ像山邊的小屋簷，花在下面。"),
    "ㄐ": ("j", "chicken", "ㄐ像一張高高的小椅子。"),
    "ㄑ": ("q", "balloon", "ㄑ像一個尖尖的箭頭，往左邊看。"),
    "ㄒ": ("x", "melon", "ㄒ像一張小桌子，放著西瓜。"),
    "ㄓ": ("zh", "pig", "ㄓ像一棵小草，長出兩片葉子。"),
    "ㄔ": ("ch", "car", "ㄔ像一個人在跑步，頭髮飛起來。"),
    "ㄕ": ("sh", "lion", "ㄕ像一個人站著，伸出手。"),
    "ㄖ": ("r", "hotdog", "ㄖ像一扇窗戶，太陽照進來。"),
    "ㄗ": ("z", "mouth", "ㄗ像一面小旗子。"),
    "ㄘ": ("c", "strawberry", "ㄘ一條長長的線，下面一個彎彎的勾。"),
    "ㄙ": ("s", "squirrel", "ㄙ像一個三角形的飯糰。"),
    "ㄚ": ("a", "grandma", "ㄚ像一根樹枝，分成兩邊。"),
    "ㄛ": ("o", "rooster", "ㄛ像公雞張開嘴巴，喔喔喔！"),
    "ㄜ": ("e", "goose", "ㄜ像一隻鵝，伸長脖子。"),
    "ㄝ": ("eh", "coconut", "ㄝ像一個小籃子，裝著椰子。"),
    "ㄞ": ("ai", "heart", "ㄞ像一個人，背著大包包。"),
    "ㄟ": ("ei", "cup", "ㄟ像一座溜滑梯，咻！"),
    "ㄠ": ("ao", "cat", "ㄠ像兩座疊起來的小山。"),
    "ㄡ": ("ou", "dog", "ㄡ像「又」字，打一個叉叉。"),
    "ㄢ": ("an", "helmet", "ㄢ像一個人坐在小椅子上。"),
    "ㄣ": ("en", "door", "ㄣ像一條彎彎的小路。"),
    "ㄤ": ("ang", "candy", "ㄤ像一個人翹著腳坐著。"),
    "ㄥ": ("eng", "lamp", "ㄥ像一個小斜坡。"),
    "ㄦ": ("er", "ear", "ㄦ像一個人的兩條腿。"),
    "ㄧ": ("i", "clothes", "ㄧ一條直直的線，像一根筷子躺著。"),
    "ㄨ": ("u", "turtle", "ㄨ像一個大叉叉。"),
    "ㄩ": ("yu", "fish", "ㄩ像一個杯子，可以裝水。"),
}


def head(w):
    """The first symbol of the word's first syllable."""
    return w["zy"][0][0]


def tail(w):
    """The last symbol of the word's key syllable (default: the last), if it is a final."""
    s = w["zy"][w.get("key", len(w["zy"]) - 1)]
    return s[-1] if s[-1] in FINALS else None


def has(w, sym):
    """家裡找找: an initial starts the word; a final is heard in it."""
    return head(w) == sym if sym in INITIALS else any(sym in s for s in w["zy"])


def hints(sym, example):
    """Three to five things at home with the sound (the example word last, if it is at home)."""
    def rank(w):  # the sound at the start first, then at the end, then the first syllable, then anywhere
        last = w["zy"][-1]
        return 0 if head(w) == sym else 1 if last[-1] == sym else 2 if sym in w["zy"][0] else 3
    found = sorted((wid for wid, w in W.items() if w["home"] and has(w, sym) and wid != example), key=lambda i: rank(W[i]))
    if W[example]["home"]:
        found.append(example)
    return found[:5]


def build():
    assert len(SYMBOLS) == 37 and set(SYMBOLS) == set(INITIALS + FINALS)
    for order, rows in ORDERS.items():
        flat = "".join(rows)
        assert len(rows) == 7 and sorted(flat) == sorted(INITIALS + FINALS), order
    symbols = []
    for sym, (sid, ex, story) in SYMBOLS.items():
        w = W[ex]
        key = head(w) if "key" not in w and head(w) == sym else tail(w)
        assert key == sym, (sym, ex, key)
        hs = hints(sym, ex)
        assert len(hs) >= 3, (sym, hs)
        strokes = STROKES[sym]
        for s in strokes:
            for x, y in s:
                assert -1 <= x <= 101 and -1 <= y <= 101, (sym, x, y)
        if sym in SURE:
            assert len(strokes) == SURE[sym], sym
        symbols.append({
            "sym": sym, "id": sid, "kind": "initial" if sym in INITIALS else "final", "word": ex,
            "at": "start" if head(w) == sym and "key" not in w else "end", "story": story, "hints": hs,
            "strokes": [[[round(x, 1), round(y, 1)] for x, y in s] for s in strokes],
        })
    data = {
        "version": 1,
        "stations": [{"name": n, "color": c} for n, c in STATIONS],
        "orders": {k: [list(r) for r in v] for k, v in ORDERS.items()},
        "symbols": symbols,
        "words": list(W.values()),
        "sure": SURE,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n")
    rhymes = {}
    for wid, w in W.items():
        if tail(w):
            rhymes.setdefault(tail(w), []).append(w["zh"])
    print(f"{OUT.relative_to(ROOT)}: 37 symbols, {len(W)} words, {OUT.stat().st_size // 1024} KB")
    print("rhymes:", {k: len(v) for k, v in rhymes.items()})


def preview(out):
    from PIL import Image, ImageDraw, ImageFont
    cell, s = 220, 2.0
    f = ImageFont.truetype(str(FONT), 220)
    lab = ImageFont.truetype(str(FONT), 16)
    syms = list(SYMBOLS)
    cols = 8
    im = Image.new("RGB", (cols * cell, math.ceil(len(syms) / cols) * cell), "white")
    d = ImageDraw.Draw(im)
    colours = [(220, 60, 60), (40, 120, 220), (30, 160, 80), (200, 120, 0)]
    for i, sym in enumerate(syms):
        x0, y0 = (i % cols) * cell + 10, (i // cols) * cell + 10
        d.rectangle([x0, y0, x0 + 200, y0 + 200], outline="#ddd")
        d.text((x0 + 100, y0 + 100), sym, font=f, fill=(215, 215, 215), anchor="mm")
        for k, st in enumerate(STROKES[sym]):
            c = colours[k % 4]
            pts = [(x0 + x * s, y0 + y * s) for x, y in st]
            d.line(pts, fill=c, width=5, joint="curve")
            sx, sy = pts[0]
            d.ellipse([sx - 8, sy - 8, sx + 8, sy + 8], fill=c)
            d.text((sx, sy), str(k + 1), font=lab, fill="white", anchor="mm")
            ex, ey = pts[-1]
            d.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill="black")
        d.text((x0 + 4, y0 + 182), f"{sym} {len(STROKES[sym])}{'' if sym in SURE else ' ?'}", font=lab, fill="black")
    im.save(out)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "preview":
        preview(sys.argv[2])
    else:
        build()
