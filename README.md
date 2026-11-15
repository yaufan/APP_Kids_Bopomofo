# ㄅㄆㄇ小火車

給 **4～6 歲**的小朋友，在台灣，國語為主：學注音符號。一列小火車，每個符號是一節車廂，學會就掛上去；火車沿台灣地圖七站開（台北→高雄）。

- 設計：[docs/design.md](docs/design.md)，草圖在 `docs/mockups/`。
- 和「畫畫小鎮」「字母寵物」「動物小餐廳」「小卡認天下」「想一想樂園」「眼尖尖大挑戰」「迷宮小冒險」「小小生活家」「小小音樂家」「心情小屋」「晚安小鎮」是兄弟 APP：同一個作者、同一套技術、不同畫風。
- 不連網、不定位、沒有廣告、沒有帳號。

## 下載（Android）
- 最新版：[Releases](https://github.com/yaufan/APP_Kids_Bopomofo/releases/latest)，一般手機下載 `bopomofo-train-版本-arm64.apk`。
- 用手機掃描 [docs/download-qr.png](docs/download-qr.png)。

## 目前進度
- 0.1.0（測試版）：火車站和台灣地圖、七站 37 個符號（兩種順序）的圖和詞、認符號、聽聽找找、寫寫看（看、點、描）、押韻接龍（開頭和押韻）、家裡找找、車廂和車站的獎勵、休息時間、家長關卡和家長模式（含語音試聽）、音樂和音效、APP 圖示。軟膠公仔風。版本紀錄在 [CHANGELOG.md](CHANGELOG.md)。

## 程式和素材在哪裡
- `app/`：Flutter 程式。`lib/core/` 是符號和詞（`book.dart`，讀 `assets/bopomofo.json`）、出題（`quiz.dart`）、存檔和規則（`game.dart`）、念的句子（`lines.dart`）、描字（`writing.dart`）、同音國字表和語音（`voice.dart`）、聲音；`lib/app/` 是火車（`train.dart`）、地圖的位置和共用的元件；`lib/features/` 是選司機、火車站、認符號、聽聽找找、寫寫看、押韻接龍、家裡找找、休息、家長模式。
- `design/bopomofo.py`：37 個符號、詞、筆順，寫成 `app/assets/bopomofo.json`（說明在 `docs/bopomofo.md`）。
- `design/art/`：用 Python 畫的圖（軟膠公仔風），`python3 build.py all` 全部重畫，`fluttercheck` 用真的 flutter_svg 比對；`icon.py` 是 APP 圖示。
- `design/sounds/make_sounds.py`：合成全部的音樂和聲音。
- 測試：在 `app/` 裡 `flutter test`；完整流程 `flutter test test/flow_test.dart`，截圖在 `app/build/screenshots/`；示範影片 `flutter test test/demo/demo_video_test.dart --dart-define=DEMO=true`，再 `python3 tools/demo_audio.py`。

## 授權
- 非商業使用授權：自己、家人使用，或學校、非營利團體的教學，都可以免費使用、修改、分享，要註明出處。
- 商業用途（販賣、收費、廣告、上架）要先取得作者書面同意。也不可以拿來訓練 AI。
- 細節見 [LICENSE](LICENSE)；別人做的部分（字型）見 [NOTICE.md](NOTICE.md)。
