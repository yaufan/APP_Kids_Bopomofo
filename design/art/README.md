# design/art：ㄅㄆㄇ小火車的圖（軟膠公仔風）

Every picture is a glossy soft-vinyl toy: a saturated colour lit from the top, a darker rim, a soft
roundness towards the edges, two white highlights and a plain offset shadow. The contract with the app
(sizes, where the symbol and the driver go) is `docs/art.md`. The 注音 symbols are never drawn here.

## Draw
```python
import kit
c = kit.Ctx(120, 100)                                # viewBox 0 0 120 100
c.vinyl(kit.rrect(10, 20, 100, 60, 18), kit.PINK)    # shadow + rim + glossy body + highlights
c.vinyl(kit.circle(60, 30, 12), kit.YELLOW, shadow=False, hl=None)
c.flat(kit.circle(60, 30, 4), kit.WHITE, op=.8)      # flat paint
c.face(60, 50, 12)                                   # eyes, cheeks, a smile
kit.write_svg(path, c.svg())                         # checks the rules, then writes
```
Shapes: `rrect ellipse circle poly smooth blob star heart path arc`; `+` is a union. Colours: `INK RED PINK
ROSE ORANGE YELLOW GOLD GREEN LEAF TEAL SKY BLUE NAVY PURPLE BROWN TAN SKIN GREY STEEL` and `lt dk mix tone
rim_of`; `STATIONS` are the seven station colours.

## Modules
- `train.py`: locomotive, carriages, wheel, smoke, drivers, track, flag, sign, station.
- `mapart.py`: the map of Taiwan and `app/lib/app/map_layout.dart` (where the stations are).
- `words.py`: one picture per word in `app/assets/bopomofo.json` (it stops if a word has none).
- `ui.py`: the six button icons, lock, check, star, speaker; sun, cloud, moon, star, hills, tunnel.
- `icon.py`: the app icon.

## Commands (run in this folder)
```
python3 build.py all                    # every module, then check
python3 build.py sheet OUT.png [dir]    # a contact sheet (train / map / words / icons / home)
python3 build.py fluttercheck           # real flutter_svg vs Chromium
python3 icon.py preview OUT.png         # the app icon with the sibling apps' icons
python3 icon.py export                  # the Android and iOS icons
```
Look at the sheet (Read tool) after every change. Deterministic: build twice, same bytes. No
`__pycache__` (every script sets `sys.dont_write_bytecode`). Do not run git here.
