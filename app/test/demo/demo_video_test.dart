// Records a demo video of ㄅㄆㄇ小火車 being played: a scripted child (a white
// dot where the finger is) with a caption under the phone screen; the music
// and sounds the app asked for are written down and mixed in afterwards by
// tools/demo_audio.py.
//
//   flutter test test/demo/demo_video_test.dart --dart-define=DEMO=true
//   python3 ../tools/demo_audio.py
//
// Needs ffmpeg; writes build/demo/demo.mp4, chapters.txt and sounds.txt.
// Skipped in normal test runs.
import 'dart:io';
import 'dart:math' as math;
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:bopomofo_train/app/app.dart';
import 'package:bopomofo_train/app/widgets.dart';
import 'package:bopomofo_train/core/book.dart';
import 'package:bopomofo_train/core/game.dart';
import 'package:bopomofo_train/core/providers.dart';
import 'package:bopomofo_train/core/sounds.dart';
import 'package:bopomofo_train/core/store.dart';
import 'package:bopomofo_train/core/voice.dart';
import 'package:bopomofo_train/features/parent/parent_gate.dart';

import '../flow_test.dart' show listenAnswer, pageAt;
import '../helpers.dart' show book, loadFonts;

const _phone = Size(390, 844);
const _captionHeight = 84.0;
const _fps = 10;
const _demo = bool.fromEnvironment('DEMO');

/// The music and the sounds asked for, with the frame they were asked at.
class _Recording implements Sounds {
  _Recording(this.frame);

  final int Function() frame;
  final lines = <String>[];
  final _holders = MusicHolders();
  Music? _playing;

  @override
  set music(bool on) {}

  @override
  set effects(bool on) {}

  @override
  void play(String sfx) => lines.add('${frame()} sfx $sfx');

  @override
  void hold(Object owner, Music? music) {
    _holders.hold(owner, music);
    _changed();
  }

  @override
  void release(Object owner) {
    _holders.release(owner);
    _changed();
  }

  void _changed() {
    final now = _holders.current;
    if (now == _playing) return;
    _playing = now;
    lines.add('${frame()} music ${now?.file ?? '-'}');
  }
}

void main() {
  testWidgets('demo video', skip: !_demo, (tester) async {
    await tester.runAsync(loadFonts);
    tester.view.physicalSize = Size(_phone.width * 3, (_phone.height + _captionHeight) * 3);
    tester.view.devicePixelRatio = 3;
    addTearDown(tester.view.reset);

    var frameCount = 0;
    var now = DateTime(2026, 11, 15, 10);
    final track = _Recording(() => frameCount);
    final finger = ValueNotifier<Offset?>(null);
    final caption = ValueNotifier<String>('');
    final key = GlobalKey();
    final store = MemoryStore();
    await tester.pumpWidget(RepaintBoundary(
      key: key,
      child: Directionality(
        textDirection: TextDirection.ltr,
        child: Column(children: [
          SizedBox.fromSize(
            size: _phone,
            child: MediaQuery(
              data: const MediaQueryData(size: _phone, devicePixelRatio: 3, padding: EdgeInsets.only(top: 24)),
              child: Stack(children: [
                ProviderScope(
                  overrides: [
                    bookProvider.overrideWithValue(book),
                    storeProvider.overrideWithValue(store),
                    savedGameProvider.overrideWithValue(const Game()),
                    soundsProvider.overrideWithValue(track),
                    voiceProvider.overrideWithValue(const SilentVoice()),
                    randomProvider.overrideWithValue(math.Random(3)),
                    clockProvider.overrideWithValue(() => now),
                  ],
                  child: const TrainApp(),
                ),
                IgnorePointer(child: ValueListenableBuilder(valueListenable: finger, builder: (_, at, _) => _Finger(at))),
              ]),
            ),
          ),
          SizedBox(
            width: _phone.width,
            height: _captionHeight,
            child: ColoredBox(
              color: const Color(0xFFE2545B),
              child: Center(
                child: ValueListenableBuilder(
                  valueListenable: caption,
                  builder: (_, text, _) => Text(text, textAlign: TextAlign.center, style: const TextStyle(fontFamily: 'Huninn', color: Colors.white, fontSize: 17, height: 1.35)),
                ),
              ),
            ),
          ),
        ]),
      ),
    ));

    final rec = (await tester.runAsync(() => _Recorder.start(key)))!;
    final marks = <String>[];
    void mark(String name) => marks.add('$name $frameCount');
    Future<void> frames(int n) async {
      for (var i = 0; i < n; i++) {
        frameCount++;
        await tester.runAsync(() async {
          await rec.capture();
          await Future<void>.delayed(const Duration(milliseconds: 15));
        });
        await tester.pump(const Duration(milliseconds: 1000 ~/ _fps));
      }
    }

    Future<void> seconds(double s) => frames((s * _fps).round());
    Future<void> touch(Offset at) async {
      finger.value = at;
      await frames(2);
      await tester.tapAt(at);
      await frames(2);
      finger.value = null;
    }

    Offset at(String l) => tester.getCenter(find.bySemanticsLabel(l).last);
    Future<void> label(String l) async {
      final f = find.bySemanticsLabel(l);
      if (f.evaluate().isEmpty || !tester.getRect(f.last).overlaps(Offset.zero & _phone)) {
        await tester.scrollUntilVisible(f, 120, scrollable: find.byType(Scrollable).first);
        await frames(3);
      }
      await touch(at(l));
    }
    Future<void> tapKey(String id) => touch(tester.getCenter(find.byKey(ValueKey(id)).last));
    ProviderContainer container() => ProviderScope.containerOf(tester.element(find.byType(TrainApp)));
    void change(Game Function(Game) f) => container().read(gameProvider.notifier).change(f);


    Future<void> traceStroke(List<Offset> stroke) async {
      final pts = [for (final p in stroke) pageAt(tester, p)];
      finger.value = pts.first;
      final g = await tester.startGesture(pts.first);
      await frames(2);
      for (var k = 1; k < pts.length; k++) {
        finger.value = pts[k];
        await g.moveTo(pts[k]);
        if (k % 3 == 0) await frames(1);
      }
      await g.up();
      finger.value = null;
      await frames(3);
    }

    final row1 = book.rows(Order.common)[0];
    final now0 = now;

    // Picking a driver, then the station.
    mark('home');
    caption.value = 'ㄅㄆㄇ小火車：4～6 歲學注音符號\n每個符號是一節車廂，學會就掛上火車';
    await seconds(3);
    caption.value = '第一次打開：選一個小司機（只選外表，不用取名字）';
    await label('小熊');
    await seconds(3);
    caption.value = '火車站：上面是台灣地圖，火車從台北一站一站開到高雄\n中間是自己的火車，下面是玩法';
    await seconds(4.5);
    caption.value = '點火車頭：嘟嘟—冒煙；灰灰的車廂還沒學';
    await tapKey('locomotive');
    await seconds(2);

    // 認符號.
    mark('see');
    caption.value = '認符號：點車廂，念「ㄚ（啊），阿嬤」\n手機語音不會念符號，所以用同音的國字念';
    await label('認符號');
    await seconds(4);
    for (final s in row1.skip(1)) {
      caption.value = '下面是這一站的符號，點一個換一個';
      await tapKey('pick-$s');
      await seconds(2.2);
    }
    caption.value = '這一站全部認識了：車廂掛上火車，喀！嘟嘟—';
    await seconds(4);
    await label('回火車站');
    await seconds(2.5);

    // 聽聽找找.
    mark('listen');
    caption.value = '聽聽找找：APP 念一個詞，找出它開頭的車廂\n小火車兩個選一個';
    await label('聽聽找找');
    await seconds(3.5);
    var (word, answer) = listenAnswer(tester);
    final wrong = book.symbols.keys.firstWhere((s) => s != answer && find.byKey(ValueKey('option-$s')).evaluate().isNotEmpty);
    caption.value = '點錯了不扣分：車廂晃一下\n念「這是$wrong，${book.wordOf(wrong).zh}的$wrong」';
    await tapKey('option-$wrong');
    await seconds(3.5);
    for (var i = 0; i < 3; i++) {
      (word, answer) = listenAnswer(tester);
      caption.value = '點對了：車廂載著$word開走\n「對！$word，$answer開頭！」';
      await tapKey('option-$answer');
      await seconds(3);
    }
    await label('回火車站');
    await seconds(1.5);

    // 寫寫看.
    mark('write');
    caption.value = '寫寫看：先看筆順（照教育部的手冊）';
    await label('寫寫看');
    final strokes = book.symbols[row1.first]!.strokes;
    await seconds(.9 * strokes.length + 1.6);
    caption.value = '再點點看：每一筆從哪裡開始？';
    for (final s in strokes) {
      await touch(pageAt(tester, s.first));
      await seconds(.6);
    }
    await seconds(1);
    caption.value = '最後沿著寬寬的小路描，手指一碰就畫\n（小火車描完就好，自己寫在 0.2 版）';
    for (final s in strokes) {
      await traceStroke(s);
      await seconds(.4);
    }
    await seconds(3);
    await label('回火車站');
    await seconds(1.5);

    // 押韻接龍.
    mark('rhyme');
    caption.value = '押韻接龍（練耳朵）：哪個是ㄜ開頭？\n小火車先玩開頭，再玩押韻';
    await label('押韻接龍');
    await seconds(4);
    for (var i = 0; i < 4; i++) {
      final cards = tester.widgetList<WordCard>(find.byType(WordCard)).map((c) => c.word).toList();
      final ask = (find.byType(Bubble).evaluate().first.widget as Bubble).text;
      if (ask.startsWith('哪個是')) {
        final sym = ask[3];
        final right = cards.firstWhere((w) => w.head == sym);
        caption.value = '哪個是$sym開頭？點對了說出為什麼：\n「${right.zh}，$sym開頭！」火車多一節';
        await label(right.zh);
        await seconds(3.2);
      } else {
        final pair = [for (final w in cards) if (cards.where((x) => x.rhyme == w.rhyme).length == 2) w];
        caption.value = '哪兩個押韻？點兩張圖：\n「${pair.first.zh}和${pair.last.zh}，尾巴都是${pair.first.rhyme}！」';
        await label(pair.first.zh);
        await seconds(1);
        await label(pair.last.zh);
        await seconds(3.2);
      }
    }
    await label('回火車站');
    await seconds(1);

    // The station done: the train drives on.
    mark('arrive');
    change((g) {
      var x = g;
      for (final s in row1) {
        x = x.saw(s).heard(s).traced(s);
      }
      return x.rhymeRound(0);
    });
    caption.value = '一站的認、聽、寫、押韻都玩過了\n火車鳴笛，開到下一站：桃園！';
    await label('認符號');
    await seconds(.5);
    await label('回火車站');
    await seconds(5);

    // 家裡找找.
    mark('find');
    caption.value = '家裡找找（離開螢幕）：今天的任務卡\n和爸爸媽媽一起找家裡的東西';
    await label('家裡找找');
    await seconds(5);
    caption.value = '找到了回來按，選一張貼紙貼在火車頭上';
    await label('找到了！');
    await seconds(2);
    final t = container().read(gameProvider).task!;
    await tapKey('word-${book.symbols[t.sym]!.hints.first}');
    await seconds(4);

    // 大火車.
    mark('big');
    change((g) => g.withSettings(g.settings.copyWith(level: Level.big)));
    caption.value = '大火車（5～6 歲）：三選一、也問尾巴\n認符號多一個「小故事」幫忙記形狀';
    await seconds(3);
    await label('認符號');
    await seconds(2.5);
    await touch(tester.getCenter(find.textContaining('的小故事')));
    await seconds(4);
    await label('回火車站');
    await seconds(1.5);

    // Parent mode.
    mark('parent');
    caption.value = '家長答對題目，才能進家長模式';
    const digits = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9};
    Future<void> gate() async {
      final parts = (find.textContaining('加').evaluate().first.widget as Text).data!.split(' ');
      for (final d in '${digits[parts[0]]! + digits[parts[2]]!}'.split('')) {
        await touch(tester.getCenter(find.byKey(ValueKey('gate-key-$d'))));
        await frames(3);
      }
    }

    await label('家長');
    await seconds(1.2);
    await gate();
    await seconds(1.5);
    caption.value = '家長模式：難度、玩多久、37 節車廂的進度\n（淡色認過、深色聽對 3 次、綠點描過）';
    await seconds(4);
    await tester.drag(find.byType(ListView), const Offset(0, -560));
    await seconds(2);
    caption.value = '語音試聽：每個符號念的同音字，先在手機上聽過';
    await tester.ensureVisible(find.byKey(const ValueKey('try-voice')));
    await frames(3);
    await touch(tester.getCenter(find.text('語音試聽')));
    await seconds(1.5);
    await tester.drag(find.byType(ListView), const Offset(0, -260));
    await seconds(3.5);
    caption.value = '還有：要哪幾站、直接跳站、課本順序、慢一點念、左撇子';
    await tester.drag(find.byType(ListView), const Offset(0, -1700));
    await seconds(3.5);
    await touch(tester.getCenter(find.byIcon(Icons.close_rounded)));
    await seconds(1.5);

    // Rest.
    mark('rest');
    now = now0.add(const Duration(minutes: 15, seconds: 1));
    caption.value = '家長設定的時間到了（預設 15 分鐘）\n「火車休息囉，換你去做了！去找找家裡的${t.sym}吧！」';
    await seconds(6);
    caption.value = '';
    mark('end');
    await seconds(0.5);
    expect(ParentPass.take(), isFalse);
    await tester.runAsync(() async {
      await rec.finish();
      File('build/demo/chapters.txt').writeAsStringSync('${marks.join('\n')}\n');
      File('build/demo/sounds.txt').writeAsStringSync('fps $_fps\nframes $frameCount\n${track.lines.join('\n')}\n');
    });
    await tester.pumpWidget(const SizedBox());
    await tester.pump(const Duration(milliseconds: 100));
  }, timeout: const Timeout(Duration(minutes: 40)));
}

class _Finger extends StatelessWidget {
  const _Finger(this.at);

  final Offset? at;

  @override
  Widget build(BuildContext context) {
    final p = at;
    if (p == null) return const SizedBox.expand();
    return Stack(children: [
      Positioned(
        left: p.dx - 22,
        top: p.dy - 22,
        child: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.white.withValues(alpha: 0.55),
            border: Border.all(color: const Color(0xFF4A3B32).withValues(alpha: 0.5), width: 3),
          ),
        ),
      ),
    ]);
  }
}

/// Streams frames of [key]'s boundary into ffmpeg.
class _Recorder {
  _Recorder(this._key, this._ffmpeg);

  final GlobalKey _key;
  final Process _ffmpeg;

  static Future<_Recorder> start(GlobalKey key) async {
    Directory('build/demo').createSync(recursive: true);
    final size = Size(_phone.width * 2, (_phone.height + _captionHeight) * 2);
    final ffmpeg = await Process.start('ffmpeg', [
      '-y', '-loglevel', 'error',
      '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '${size.width.toInt()}x${size.height.toInt()}', '-r', '$_fps', '-i', '-',
      '-vf', 'fps=30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '24', '-movflags', '+faststart', 'build/demo/demo_silent.mp4',
    ]);
    ffmpeg.stderr.listen(stderr.add);
    return _Recorder(key, ffmpeg);
  }

  Future<void> capture() async {
    final boundary = _key.currentContext!.findRenderObject()! as RenderRepaintBoundary;
    final image = await boundary.toImage(pixelRatio: 2);
    final bytes = await image.toByteData(format: ui.ImageByteFormat.rawRgba);
    image.dispose();
    _ffmpeg.stdin.add(bytes!.buffer.asUint8List());
    await _ffmpeg.stdin.flush();
  }

  Future<void> finish() async {
    await _ffmpeg.stdin.flush();
    await _ffmpeg.stdin.close();
    final code = await _ffmpeg.exitCode;
    if (code != 0) throw StateError('ffmpeg failed ($code)');
  }
}
