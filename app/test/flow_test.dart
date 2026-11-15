import 'package:bopomofo_train/app/widgets.dart';
import 'package:bopomofo_train/core/book.dart';
import 'package:bopomofo_train/core/game.dart';
import 'package:bopomofo_train/core/voice.dart';
import 'package:bopomofo_train/features/parent/parent_gate.dart';
import 'package:bopomofo_train/features/write/write_painter.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'helpers.dart';

/// A visit as a child (and a parent) would play it, through every screen,
/// on a phone and a tablet, with screenshots in `build/screenshots/<device>/`.
void main() {
  setUpAll(loadFonts);

  for (final MapEntry(key: device, value: (size, ratio)) in {'phone': (const Size(1080, 2340), 2.75), 'tablet': (const Size(1620, 2160), 2.0)}.entries) {
    testWidgets('a trip on the train ($device)', (tester) async {
      final app = await TestApp.start(tester, game: const Game(), size: size, ratio: ratio, seed: 3);
      Future<void> shot(String name) => shoot(tester, device, name);
      final row1 = book.rows(Order.common)[0];

      // The first time: pick a driver.
      expect(app.location, '/driver');
      await app.settle(600);
      expect(app.voice.said.last, speakable('選一個小司機，和你一起開火車！'));
      await shot('01_driver');
      await app.tapLabel('小熊', ms: 2200);
      expect(app.game.driver, Driver.bear);
      expect(app.location, '/');
      expect(app.sounds.played, contains('whistle'));
      await app.settle(800);
      await shot('02_home');
      expect(app.voice.said.last, '嘟嘟！我們在台北站。今天想玩哪個？');

      // A grey carriage: see it first. The locomotive toots.
      await tester.tap(find.byKey(const ValueKey('car-ㄚ')));
      await app.settle();
      expect(app.voice.said.last, '先去認符號吧！');
      await tester.tap(find.byKey(const ValueKey('locomotive')));
      await app.settle();
      expect(app.sounds.played.last, 'puff');

      // 認符號: every carriage of 台北 站, heard as its character and its word.
      await app.tapLabel('認符號', ms: 900);
      expect(app.location, '/see');
      expect(app.voice.said.last, '啊，阿嬤。');
      await shot('03_see');
      for (final s in row1.skip(1)) {
        await tester.tap(find.byKey(ValueKey('pick-$s')));
        await app.settle(500);
      }
      expect(app.voice.said, contains('婀，鵝。'));
      expect(row1.every((s) => app.game.of(s).seen), isTrue);
      await app.settle(2200);
      expect(app.voice.said.last, '這一站的車廂都認識了！掛上火車囉！');
      expect(app.sounds.played, containsAll(['couple', 'whistle']));
      await shot('04_see_done');
      await app.tapLabel('回火車站', ms: 900);
      await shot('05_home_train');
      await tester.tap(find.byKey(const ValueKey('car-ㄧ')));
      await app.settle();
      expect(app.voice.said.last, '衣，衣服。');

      // 聽聽找找: a wrong carriage first (nothing lost), then right ten times.
      await app.tapLabel('聽聽找找', ms: 900);
      expect(app.location, '/listen');
      await shot('06_listen');
      var (word, answer) = listenAnswer(tester);
      final wrong = book.symbols.keys.firstWhere((s) => s != answer && find.byKey(ValueKey('option-$s')).evaluate().isNotEmpty);
      await tester.tap(find.byKey(ValueKey('option-$wrong')));
      await app.settle();
      expect(app.sounds.played.last, 'try');
      expect(app.voice.said.last, startsWith(speakable('這是$wrong，')));
      for (var i = 0; i < 10; i++) {
        (word, answer) = listenAnswer(tester);
        await tester.tap(find.byKey(ValueKey('option-$answer')));
        await app.settle(900);
        if (i == 0) {
          expect(app.voice.said.last, speakable('對！$word，$answer開頭！'));
          await shot('07_listen_right');
        }
        await app.settle(1600);
      }
      expect(row1.every((s) => app.game.of(s).heard > 0), isTrue);
      expect(app.voice.said.last, '這一站聽完了！你的耳朵好厲害！');
      await shot('08_listen_done');

      // 寫寫看: watch, tap the starts, trace along the roads; every symbol of the station.
      await app.tapLabel('寫寫看', ms: 900);
      expect(app.location, '/write');
      await app.settle(700);
      await shot('09_write_watch');
      for (var k = 0; k < row1.length; k++) {
        final sym = row1.firstWhere((s) => !app.game.of(s).traced);
        final strokes = book.symbols[sym]!.strokes;
        await app.settle(900 * strokes.length + 1400);
        for (var i = 0; i < strokes.length; i++) {
          await tester.tapAt(pageAt(tester, strokes[i].first));
          await app.settle(200);
        }
        await app.settle(900);
        for (var i = 0; i < strokes.length; i++) {
          final pts = [for (final p in strokes[i]) pageAt(tester, p)];
          final g = await tester.startGesture(pts.first);
          for (final p in pts.skip(1)) {
            await g.moveTo(p);
            await tester.pump(const Duration(milliseconds: 8));
          }
          if (k == 1 && i == strokes.length - 1) await shot('10_write_trace');
          await g.up();
          await app.settle(150);
        }
        expect(app.game.of(sym).traced, isTrue, reason: sym);
        await app.settle(2800);
      }
      expect(app.voice.said.last, '這一站的符號都描好了！');
      await shot('11_write_done');

      // 押韻接龍: a wrong picture, then right; six questions.
      await app.tapLabel('押韻接龍', ms: 900);
      expect(app.location, '/rhyme');
      await shot('12_rhyme');
      for (var i = 0; i < 6; i++) {
        final cards = tester.widgetList<WordCard>(find.byType(WordCard)).map((c) => c.word).toList();
        final ask = (find.byType(Bubble).evaluate().first.widget as Bubble).text;
        if (ask.startsWith('哪個是')) {
          final sym = ask[3];
          if (i == 0) {
            await app.tapLabel(cards.firstWhere((w) => w.head != sym).zh);
            expect(app.sounds.played.last, 'try');
          }
          await app.tapLabel(cards.firstWhere((w) => w.head == sym).zh, ms: 900);
        } else {
          final pair = [for (final w in cards) if (cards.where((x) => x.rhyme == w.rhyme).length == 2) w];
          if (i == 3) {
            final odd = cards.firstWhere((w) => !pair.contains(w));
            await app.tapLabel(pair.first.zh);
            await app.tapLabel(odd.zh);
            expect(app.voice.said.last, speakable('${pair.first.zh}、${odd.zh}，尾巴不一樣喔。再聽聽看。'));
          }
          await app.tapLabel(pair.first.zh);
          await app.tapLabel(pair.last.zh, ms: 900);
          expect(app.voice.said.last, speakable('對！${pair.first.zh}和${pair.last.zh}，尾巴都是${pair.first.rhyme}！'));
          if (i == 3) await shot('13_rhyme_pair');
        }
        await app.settle(2000);
      }
      expect(app.game.rhymeAsked, 6);
      expect(app.game.rhymeRight, 4, reason: 'two were wrong first');
      await shot('14_rhyme_done');
      expect(app.game.passed(book, 0), isTrue);

      // 家裡找找 from the round's end: today's card, found it, a sticker.
      await app.tapLabel('任務卡', ms: 900);
      expect(app.location, '/find');
      await app.settle(600);
      final task = app.game.task!;
      expect(row1, contains(task.sym));
      await shot('15_find');
      await app.tapLabel('找到了！', ms: 700);
      await shot('16_find_sticker');
      final sticker = book.words[book.symbols[task.sym]!.hints.first]!;
      await tester.tap(find.byKey(ValueKey('word-${sticker.id}')).last);
      await app.settle(900);
      expect(app.game.stickers, [sticker.id]);
      expect(app.voice.said.last, '貼紙貼在火車頭上囉！');
      await app.settle(2600);

      // Home again: the train drives on to 桃園.
      expect(app.location, '/');
      await app.settle(1300);
      await shot('17_home_driving');
      await app.settle(2400);
      expect(app.voice.said.last, '嘟嘟—到桃園站囉！');
      expect(app.game.arrivedAt(), 1);
      await shot('18_home_taoyuan');

      // 大火車: 拼拼看 waits for 0.2; 認符號 has the shape story; 聽聽找找 three cards.
      app.change((g) => g.withSettings(g.settings.copyWith(level: Level.big)));
      await app.settle();
      await app.tapLabel('拼拼看');
      expect(app.voice.said.last, '拼拼看 0.2 版才有喔！');
      await shot('19_home_big');
      await app.tapLabel('認符號', ms: 900);
      expect(app.voice.said.last, '播，爸爸。');
      await app.tapLabel('ㄅ的小故事', ms: 600);
      expect(app.voice.said.last, speakable('ㄅ像爸爸彎彎的手臂，抱抱你。'));
      await shot('20_see_big');
      await app.tapLabel('回火車站', ms: 900);
      await app.tapLabel('聽聽找找', ms: 900);
      expect(find.byWidgetPredicate((w) => w.key is ValueKey<String> && (w.key! as ValueKey<String>).value.startsWith('option-')).evaluate().length, 3);
      await shot('21_listen_big');
      await app.tapLabel('回火車站', ms: 900);

      // Parent mode: progress, the voice list, jumping to a station.
      ParentPass.grant();
      app.go('/parent');
      await app.settle(800);
      expect(find.byKey(const ValueKey('grid-ㄚ')), findsOneWidget);
      await shot('22_parent');
      await tester.scrollUntilVisible(find.byKey(const ValueKey('try-voice')), 200, scrollable: find.byType(Scrollable).first);
      await tester.ensureVisible(find.byKey(const ValueKey('try-voice')));
      await app.settle(300);
      await tester.tap(find.text('語音試聽'));
      await app.settle(600);
      await tester.ensureVisible(find.byKey(const ValueKey('try-ㄅ')));
      await app.settle(300);
      await shot('23_parent_voice');
      await tester.tap(find.descendant(of: find.byKey(const ValueKey('try-ㄅ')), matching: find.byType(IconButton)));
      await app.settle();
      expect(app.voice.said.last, '播，爸爸。');
      await tester.scrollUntilVisible(find.byKey(const ValueKey('jump-4')), 200, scrollable: find.byType(Scrollable).first);
      await tester.ensureVisible(find.byKey(const ValueKey('jump-4')));
      await app.settle(300);
      await tester.tap(find.byKey(const ValueKey('jump-4')));
      await app.settle(600);
      expect(app.game.current(book), 4);
      app.go('/');
      await app.settle(4200);
      expect(app.voice.said.last, '嘟嘟—到嘉義站囉！');
      await shot('24_home_chiayi');

      // The play time runs out: the train rests.
      app.now = app.now.add(const Duration(minutes: 16));
      await app.settle(2600);
      expect(app.location, '/rest');
      expect(app.voice.said.last, speakable('火車休息囉，換你去做了！去找找家裡的${task.sym}吧！'));
      await shot('25_rest');
      expect(app.game.log(app.now).seconds, greaterThan(0));

      // Never a symbol for the voice.
      expect(app.voice.said.where(hasZhuyin), isEmpty);
      await app.end();
    }, timeout: const Timeout(Duration(minutes: 15)));
  }
}

/// The word asked in 聽聽找找 and the carriage that answers it.
(String, String) listenAnswer(WidgetTester tester) {
  final text = tester.widgetList<Text>(find.byType(Text)).map((t) => t.data ?? '').firstWhere((t) => t.endsWith('是哪一節車廂？'));
  final tail = text.contains('的尾巴是');
  final zh = text.substring(0, text.indexOf(tail ? '的尾巴是' : '的開頭是'));
  final w = book.words.values.firstWhere((w) => w.zh == zh);
  return (zh, tail ? w.tail! : w.head);
}

/// Where a point of the 100 × 100 symbol box is on the writing page.
Offset pageAt(WidgetTester tester, Offset p) {
  final page = tester.getRect(find.byKey(const ValueKey('page')));
  return page.topLeft + BoxFit100(page.size).toScreen(p);
}
