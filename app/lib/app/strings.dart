import '../core/book.dart';
import '../core/game.dart';

/// Everything the app says and shows, in Traditional Chinese (Taiwan).
/// Lines with symbols in them are fine: the voice gets speakable() of them.
abstract final class Strings {
  static const appName = 'ㄅㄆㄇ小火車';

  // Choosing the driver.
  static const pickDriver = '選一個小司機，和你一起開火車！';
  static String driverPicked(Driver d) => '${d.zh}來開火車囉！嘟嘟—出發！';

  // The station (home).
  static String hello(String station) => '嘟嘟！我們在$station站。今天想玩哪個？';
  static const whatToPlay = '今天想玩哪個？';
  static String stationNo(int i) => '第 ${i + 1} 站';
  static String goStation(String s) => '到$s站玩！';
  static String arrived(String s) => '嘟嘟—到$s站囉！';
  static const allDone = '火車開完全部的站了！好棒！';
  static const notYet = '這一站還沒到喔，先把這一站玩完吧。';
  static const lockedStation = '這一站在完整版裡，請爸爸媽媽看看。';
  static const seeFirst = '先去認符號吧！';
  static const locked = '完整版才有喔，請爸爸媽媽看看。';
  static const spellSoon = '拼拼看 0.2 版才有喔！';
  static const soon = '0.2 版會有';
  static const taskReady = '我有一個任務給你！';
  static String myTrain(int n) => '我的火車：$n 節車廂';
  static const choo = '嘟嘟—';
  static const parent = '家長';
  static const home = '回火車站';
  static const back = '回去';
  static const again = '再聽一次';

  // Modules.
  static String module(Module m) => m.zh;
  static const spell = '拼拼看';

  // 認符號.
  static const seeTap = '點車廂，聽聽看';
  static const story = '小故事';
  static String storyOf(String sym) => '$sym的小故事';
  static const seeAll = '這一站的車廂都認識了！掛上火車囉！';

  // 聽聽找找.
  static String listenHead(String word) => '$word，開頭是哪一節車廂？';
  static String listenTail(String word, String spelled) => '$word，$spelled。尾巴是哪一節車廂？';
  static String listenRightHead(String word, String sym) => '對！$word，$sym開頭！';
  static String listenRightTail(String word, String sym) => '對！$word的尾巴是$sym！';
  static String questionNo(int i, int n) => '第 $i 題，共 $n 題';
  static const listenDone = '這一站聽完了！你的耳朵好厲害！';

  // 寫寫看.
  static const stepWatch = '看';
  static const stepTap = '點';
  static const stepTrace = '描';
  static String watch(String sym) => '看看$sym怎麼寫。';
  static const tapStars = '點點看，每一筆從哪裡開始？';
  static const traceRoad = '從綠色的點開始，沿著小路描。';
  static const startAtDot = '從綠色的點開始喔。';
  static const backOnRoad = '回到小路上，繼續描。';
  static const startAtStar = '點亮亮的星星。';
  static String traced(String line) => '描好了！$line';
  static const watchAgain = '再看一次';
  static const writeDone = '這一站的符號都描好了！';
  static String strokeNo(int i, int n) => '第 $i 筆，共 $n 筆';

  // 押韻接龍.
  static String whichStarts(String sym) => '哪個是$sym開頭？';
  static const whichRhyme = '哪兩個押韻？尾巴一樣的。';
  static String headRight(String word, String sym) => '對！$word，$sym開頭！';
  static String headWrong(String word, String head, String sym) => '$word是$head開頭喔。再聽一次：哪個是$sym開頭？';
  static String pairRight(String a, String b, String rhyme) => '對！$a和$b，尾巴都是$rhyme！';
  static String pairWrong(String a, String b) => '$a、$b，尾巴不一樣喔。再聽聽看。';
  static const rhymeDone = '火車接得好長！你聽得出押韻了！';

  // 家裡找找.
  static const findHello = '今天的任務來囉！';
  static const findLook = '找找家裡有什麼';
  static const findStartAfter = '開頭的東西？';
  static const findSoundBefore = '有';
  static const findSoundAfter = '的聲音的東西？';
  static String findSay(String sym, bool initial) => initial ? '找找家裡有什麼$sym開頭的東西？和爸爸媽媽一起找！' : '找找家裡有什麼東西，有$sym的聲音？和爸爸媽媽一起找！';
  static const findTogether = '和爸爸媽媽一起找。這一頁沒有東西可以點，放下手機去找吧，找到了回來按。';
  static const found = '找到了！';
  static const pickSticker = '找到什麼？選一張貼紙。';
  static const stickerOn = '貼紙貼在火車頭上囉！';
  static const foundToday = '今天的任務完成了！明天還有新的任務。';

  // Done panels.
  static const playAgain = '再玩一次';
  static const taskCard = '任務卡';

  // Resting.
  static const restTitle = '火車休息囉';
  static String restLine(String sym) => '換你去做了！\n去找找家裡的$sym吧！';

  // Parent gate (as in the sibling apps).
  static const callParent = '請爸爸媽媽來幫忙喔！';
  static const parentGateTitle = '家長確認';
  static String gateQuestion(String a, String b) => '$a 加 $b 等於多少？';
  static const gateRules = '答錯三次要等一分鐘。';
  static const wrongAnswer = '不對喔，換一題。';
  static String gateWait(int s) => '請等 $s 秒再試';
  static const backspace = '刪掉';
  static const cancel = '取消';

  // Parent mode.
  static const parentTitle = '家長模式';
  static const levelTitle = '難度';
  static String levelLine(Level l) => '${l.zh}（${l.ages}）';
  static const levelNote = '小火車：聽聽找找兩選一、只問開頭，押韻接龍先玩「哪個是ㄇ開頭」，司機每一步都說；建議走 1～4 站。'
      '大火車：三選一、也問尾巴，兩種押韻題輪流，說明只說一次。寫寫看兩個難度都是看、點、描（自己寫在 0.2 版）。';
  static const playTime = '每次可以玩多久';
  static String minutes(int m) => '$m 分鐘';
  static const playTimeNote = '時間到了火車進站、司機下車休息，APP 說「換你去做了！」。要家長解開，或等一個小時，才能再玩。';
  static const playOn = '讓小朋友再玩一次（重新計時）';
  static const resting = '現在是休息時間。';
  static const stationsTitle = '要哪幾站';
  static const stationsNote = '關掉的站火車會直接開過去；至少留一站。完整版才有第 3～7 站。';
  static const jumpTitle = '直接跳到哪一站';
  static const jumpNote = '前面的站算走過了（已經在幼兒園學過的話可以用）。';
  static const orderTitle = '符號順序';
  static String orderNote(Order o) => o == Order.common
      ? '常用的先：ㄚㄧㄨㄛㄜ → ㄅㄆㄇㄈ → …… → 捲舌音最後，第二站就有爸爸、媽媽。'
      : '課本順序：ㄅㄆㄇㄈ／ㄉㄊㄋㄌ／ㄍㄎㄏㄐㄑㄒ／ㄓㄔㄕㄖㄗㄘㄙ／ㄧㄨㄩㄚㄛㄜㄝ／ㄞㄟㄠㄡ／ㄢㄣㄤㄥㄦ。';
  static const voiceTitle = '語音';
  static const voice = '念出題目、符號和詞';
  static const slow = '念慢一點';
  static const twice = '每個詞念兩次';
  static const tryVoice = '語音試聽';
  static const tryVoiceNote = '手機的國語語音不會念單獨的符號，所以每個符號用一個同音的國字念（ㄅ念「播」），後面接著念詞。請每一個都聽聽看，念得不對或聽不清楚的告訴我們，我們換一個字。';
  static String tryLine(String sym, String h, String word) => '$sym　念「$h」　$word';
  static const progressTitle = '進度（37 節車廂）';
  static const legend = '灰色：還沒；淡色：認過；深色：聽對 3 次；綠點：描過';
  static String today(int minutes, List<Module> modules) => '今天玩了 $minutes 分鐘${modules.isEmpty ? '' : '：${modules.map((m) => m.zh).join('、')}'}';
  static String rhymeScore(int right, int asked) => asked == 0 ? '押韻接龍還沒玩過。' : '押韻接龍第一次就答對：$right／$asked 題（${(right * 100 / asked).round()}%）';
  static const findTitle = '家裡找找';
  static String todayTask(String sym, List<String> hints) => '今天的任務：$sym（${hints.join('、')}）';
  static String stickers(int n) => '找到過 $n 次，貼紙在火車頭上。';
  static const otherTitle = '其他';
  static const leftHanded = '左撇子（寫寫看的箭頭在右邊）';
  static const music = '背景音樂';
  static const effects = '音效';
  static const changeDriver = '換一個司機（下次打開時讓小朋友選）';
  static const fullVersion = '完整版';
  static const fullNote = '免費版有第 1、2 站和認符號、聽聽找找、寫寫看；完整版有全部七站、押韻接龍和家裡找找（之後還有拼拼看）。購買只在這裡。（測試版先全部打開。）';
  static const fullSwitch = '打開完整版（測試用）';
  static const about = '關於';
  static const privacy = '不連網、不定位、沒有廣告、沒有帳號、不要任何權限；進度只存在這支手機裡。';
  static String version(String v) => '版本 $v';
}
