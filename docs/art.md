# 圖和程式的約定（ㄅㄆㄇ小火車）

畫風是**軟膠公仔風**（`docs/design.md`「畫風」）：每一塊像亮亮的軟膠玩具。全部的圖用 Python 畫成 SVG（`design/art/`），
APP 用 flutter_svg 顯示。注音符號**不畫在圖裡**：APP 用字型（jf open 粉圓）寫在車廂的白色面板上。

## 怎麼畫（`design/art/kit.py`）
- 每一塊：由上到下的漸層（上面亮、下面暗）、外面一圈 2～3 單位的深色邊（畫在身體後面的描邊，所以合併的形狀裡面不會有線）、
  往邊緣暗一點的圓弧感（放射漸層）、左上兩個白色反光（一個大的半透明、一個小的全白）、往右下移一點的淡影子。
- flutter_svg 畫不出來的東西都不用：`<filter>`、`<mask>`、`<clipPath>`、`<style>`、`<text>`、`<image>`、`<pattern>`。
  `python3 build.py check` 檢查規則，`python3 build.py fluttercheck` 用真的 flutter_svg 和 Chromium 各畫一次比對。
- 每個檔案小於 70 KB；同樣的程式畫兩次，檔案一模一樣。

## 檔案和位置（APP 用的數字要和這裡一樣）
| 檔案 | 大小（viewBox） | APP 怎麼用 |
|---|---|---|
| `train/carriage_<0..6>.svg` | 120 × 100 | 每一站一個顏色。白色面板 x 22～98、y 18～70，符號寫在中間（60, 44）。輪子 `wheel.svg` 在 x 32、88，y 86，直徑 26，APP 畫、會轉 |
| `train/carriage_ghost.svg` | 120 × 100 | 還沒掛上的車廂（灰灰的輪廓） |
| `train/locomotive.svg` | 200 × 140 | 火車頭，朝右。駕駛室的窗 x 20～66、y 30～70（司機放這裡）；煙囪口 (151, 22)；輪子 x 42（半徑 21）、108、152（半徑 17），y 116 |
| `train/wheel.svg` | 40 × 40 | 會轉的輪子 |
| `train/smoke.svg` | 44 × 32 | 煙，APP 一團一團飄上去 |
| `train/driver_<bear,rabbit,cat,penguin>.svg` | 100 × 100 | 司機的頭和肩膀（戴司機帽），臉的中心 (50, 52) |
| `train/track.svg` | 120 × 22 | 一段鐵軌，一段接一段排 |
| `train/flag.svg`、`sign.svg`、`station.svg` | | 走過的站插旗子；站牌（APP 寫站名，x 10～150、y 6～44）；休息畫面的車站 |
| `map/taiwan.svg` | 260 × 420 | 台灣地圖和西部鐵路。七個車站的位置寫在 `app/lib/app/map_layout.dart`（`mapart.py` 產生，圖的比例） |
| `words/<詞的 id>.svg` | 120 × 120 | 每個詞一張（`assets/bopomofo.json` 的 words），東西大大的放中間 |
| `icons/<see,listen,spell,write,rhyme,find>.svg` | 96 × 96 | 首頁六個大按鈕 |
| `icons/<lock,check,star,speaker>.svg` | | 鎖、打勾、貼紙星星、大喇叭 |
| `home/<sun,cloud,moon,star,hills,tunnel>.svg` | | 背景的太陽、雲、月亮、星星、山坡、山洞 |

## 顏色
- 七站：台北淡藍 `#8CCBF2`、桃園粉紅 `#F59BC2`、新竹綠 `#7FD08A`、台中黃 `#FFD44F`、嘉義橘 `#FFA35C`、台南紫 `#B79AF0`、高雄青綠 `#4FD1C5`（和 `assets/bopomofo.json` 的 stations 一樣）。
- 火車頭紅 `#F2545B`；字和眼睛是深紫藍 `#2E2440`（不用純黑）；背景奶油色 `#FFF6E6`。
- 符號：白色面板上用深色字（`#2E2440`），首頁小車廂上的符號也一樣，手機小螢幕一眼看得到。

## APP 圖示
`python3 design/art/icon.py preview 輸出.png` 看大圖、手機裁切和兄弟 APP 放在一起的樣子；`export` 寫進 Android（含 adaptive）和 iOS。
粉紅車廂上寫ㄅ（字型寫上去的），小熊司機從車頂探出頭，藍天和鐵軌。
