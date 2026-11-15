import 'dart:io';
import 'dart:math' as math;

import 'package:bopomofo_train/core/book.dart';
import 'package:bopomofo_train/core/game.dart';
import 'package:bopomofo_train/core/lines.dart';
import 'package:bopomofo_train/core/quiz.dart';
import 'package:bopomofo_train/core/store.dart';
import 'package:bopomofo_train/core/voice.dart';
import 'package:flutter_test/flutter_test.dart';

Bopomofo loadBook() => Bopomofo.parse(File('assets/bopomofo.json').readAsStringSync());

/// The rules of docs/design.md, without the screens.
void main() {
  final b = loadBook();

  group('the symbols', () {
    test('37 symbols, 21 initials and 16 finals', () {
      expect(b.symbols.length, 37);
      expect(b.symbols.values.where((z) => z.initial).length, 21);
      expect(Bopomofo.initials.length + Bopomofo.finals.length, 37);
    });

    test('every symbol is in exactly one of the seven stations, in each order', () {
      for (final o in Order.values) {
        final rows = b.rows(o);
        expect(rows.length, 7, reason: o.name);
        for (final sym in b.symbols.keys) {
          expect(rows.where((r) => r.contains(sym)).length, 1, reason: '$sym in ${o.name}');
        }
        expect(rows.expand((r) => r).length, 37, reason: o.name);
      }
      // docs/design.md: the common order starts ㄚㄧㄨㄛㄜ and ends with the 捲舌音; the book's starts ㄅㄆㄇㄈ.
      expect(b.rows(Order.common).first, ['ㄚ', 'ㄧ', 'ㄨ', 'ㄛ', 'ㄜ']);
      expect(b.rows(Order.common)[1], ['ㄅ', 'ㄆ', 'ㄇ', 'ㄈ']);
      expect(b.rows(Order.common).last.take(7).join(), 'ㄓㄔㄕㄖㄗㄘㄙ');
      expect(b.rows(Order.textbook).first, ['ㄅ', 'ㄆ', 'ㄇ', 'ㄈ']);
      expect(b.stations.map((s) => s.name).toList(), ['台北', '桃園', '新竹', '台中', '嘉義', '台南', '高雄']);
    });

    test('every symbol has its character for the voice and an example word with the sound', () {
      expect(homophones.keys.toSet(), b.symbols.keys.toSet());
      expect(homophones['ㄅ'], '播');
      expect(homophones['ㄇ'], '摸');
      for (final z in b.symbols.values) {
        final h = homophones[z.sym]!;
        expect(h.length, 1, reason: z.sym);
        expect(hasZhuyin(h), isFalse);
        final w = b.words[z.wordId];
        expect(w, isNotNull, reason: '${z.sym}: ${z.wordId}');
        expect(z.atEnd ? w!.tail : w!.head, z.sym, reason: '${z.sym} ${w.zh}');
        expect(z.story, startsWith(z.sym));
      }
    });

    test('every word has as many characters as syllables, and toneless zhuyin', () {
      for (final w in b.words.values) {
        expect(w.zh.length, w.zy.length, reason: w.id);
        for (final s in w.zy) {
          expect(s.split('').every(Bopomofo.isZhuyin), isTrue, reason: '${w.id}: $s');
          expect(s.length, inInclusiveRange(1, 3), reason: w.id);
        }
      }
    });

    test('the voice never gets a symbol', () {
      for (final sym in b.symbols.keys) {
        for (final twice in [false, true]) {
          final line = symbolLine(b, sym, twice: twice);
          expect(line, contains(b.wordOf(sym).zh));
          expect(hasZhuyin(speakable(line)), isFalse, reason: line);
        }
        expect(hasZhuyin(speakable(thisIs(b, sym))), isFalse);
      }
      expect(speakable(symbolLine(b, 'ㄅ')), '播，爸爸。');
      expect(speakable(symbolLine(b, 'ㄠ')), '凹，貓，摸、凹，貓。');
      expect(speakable(symbolLine(b, 'ㄟ')), '欸，杯子，播、欸，杯。');
      expect(speakable('ㄅㄚˋ'), '播啊');
    });

    test('家裡找找 has three to five things at home for every symbol, all with the sound', () {
      for (final z in b.symbols.values) {
        expect(z.hints.length, inInclusiveRange(3, 5), reason: z.sym);
        for (final h in z.hints) {
          final w = b.words[h]!;
          expect(w.home, isTrue, reason: '${z.sym}: ${w.zh}');
          expect(w.hasSound(z.sym), isTrue, reason: '${z.sym}: ${w.zh}');
        }
      }
    });
  });

  group('questions', () {
    // docs/design.md: two cards at 小火車 never sound alike (ㄣ/ㄥ, ㄓ/ㄗ…).
    test('the confusable pairs', () {
      expect(Bopomofo.alike('ㄣ', 'ㄥ'), isTrue);
      expect(Bopomofo.alike('ㄗ', 'ㄓ'), isTrue);
      expect(Bopomofo.alike('ㄢ', 'ㄤ'), isTrue);
      expect(Bopomofo.alike('ㄅ', 'ㄇ'), isFalse);
      for (final (a, c) in Bopomofo.confusable) {
        expect(b.symbols.containsKey(a) && b.symbols.containsKey(c), isTrue);
      }
    });

    for (final level in Level.values) {
      for (final order in Order.values) {
        test('聽聽找找 at ${level.zh}, ${order.zh}: the right card once, never two alike at 小火車', () {
          for (var seed = 0; seed < 30; seed++) {
            final r = math.Random(seed);
            final g = Game(settings: Settings(level: level, order: order));
            for (var st = 0; st < 7; st++) {
              final qs = listenRound(b, g, st, r);
              expect(qs.length, listenCount);
              expect(qs.map((q) => q.answer).toSet(), g.row(b, st).toSet(), reason: 'every symbol of the station is asked');
              for (final q in qs) {
                expect(q.options.length, level == Level.small ? 2 : 3);
                expect(q.options.toSet().length, q.options.length, reason: 'no card twice');
                expect(q.options.where((o) => o == q.answer).length, 1);
                expect(q.tail ? q.word.tail : q.word.head, q.answer, reason: q.word.zh);
                for (final o in q.options.where((o) => o != q.answer)) {
                  expect(q.word.symbols.contains(o), isFalse, reason: 'a card heard in ${q.word.zh}');
                  if (level == Level.small) expect(Bopomofo.alike(o, q.answer), isFalse, reason: '$o / ${q.answer}');
                }
                if (level == Level.small && q.tail) expect(q.word, b.wordOf(q.answer), reason: '小火車 asks a word\'s end only for the final it teaches');
              }
              for (var i = 1; i < qs.length; i++) {
                if (qs[i].answer == qs[i - 1].answer && qs[i].word == qs[i - 1].word && headWords(b, qs[i].answer).length > 1) fail('the same word twice in a row');
              }
            }
          }
        });
      }

      test('押韻接龍 at ${level.zh}: one picture starts with the sound, two rhyme', () {
        for (var seed = 0; seed < 30; seed++) {
          final r = math.Random(seed);
          final g = Game(settings: Settings(level: level));
          for (var st = 0; st < 7; st++) {
            final qs = rhymeRound(b, g, st, r);
            expect(qs.length, rhymeCount);
            if (level == Level.small) {
              expect(qs.take(3).every((q) => q is HeadQuestion), isTrue, reason: '小火車 starts with 「哪個是ㄇ開頭？」');
              expect(qs.skip(3).every((q) => q is PairQuestion), isTrue);
            }
            for (final q in qs) {
              expect(q.options.length, 3);
              expect(q.options.toSet().length, 3);
              switch (q) {
                case HeadQuestion(:final sym, :final right):
                  expect(right.head, sym);
                  expect(q.options.where((w) => w.head == sym).length, 1);
                  for (final w in q.options.where((w) => w != right)) {
                    expect(Bopomofo.alike(w.head, sym), isFalse, reason: '${w.zh} / $sym');
                  }
                case PairQuestion(:final rhyme, :final right):
                  expect(right.length, 2);
                  expect(right.every((w) => w.rhyme == rhyme), isTrue);
                  final odd = q.options.firstWhere((w) => !right.contains(w));
                  expect(odd.rhyme, isNotNull);
                  expect(Bopomofo.alike(odd.rhyme!, rhyme), isFalse, reason: '${odd.zh} / $rhyme');
              }
            }
          }
        }
      });
    }
  });

  group('stations and progress', () {
    Game learn(Game g, String sym) => g.saw(sym).heard(sym).traced(sym);

    test('a station is passed when seen, heard, traced and (full version) rhymed', () {
      var g = const Game();
      expect(g.current(b), 0);
      for (final s in g.row(b, 0)) {
        g = learn(g, s);
      }
      expect(g.passed(b, 0), isFalse, reason: '押韻接龍 still to play');
      g = g.rhymeRound(0);
      expect(g.passed(b, 0), isTrue);
      expect(g.current(b), 1);
      expect(g.reachable(b, 0), isTrue);
      expect(g.reachable(b, 2), isFalse);
      expect(g.playAt(0).playing(b), 0);
      expect(g.playAt(3).playing(b), 1, reason: 'not there yet');
    });

    test('the free version: two stations, three modules', () {
      var g = const Game(settings: Settings(full: false));
      expect(g.settings.open(Module.see) && g.settings.open(Module.listen) && g.settings.open(Module.write), isTrue);
      expect(g.settings.open(Module.rhyme), isFalse);
      expect(g.settings.open(Module.find), isFalse);
      expect([for (var i = 0; i < 7; i++) if (g.enabled(i)) i], [0, 1]);
      for (final s in g.pool(b, 1)) {
        g = learn(g, s);
      }
      expect(g.passed(b, 0), isTrue, reason: 'no 押韻接龍 in the free version');
      expect(g.current(b), 1, reason: 'station 3 is in the full version');
      expect(g.finished(b), isTrue);
      expect(g.reachable(b, 2), isFalse);
    });

    test('stations turned off are skipped; at least one stays on', () {
      final g = const Game().withSettings(const Settings().copyWith(stations: {2, 3}));
      expect(g.current(b), 2);
      expect(const Settings().copyWith(stations: {}).stations, {0});
    });

    test('jumping to a station and switching the order', () {
      var g = const Game().jump(3);
      expect(g.current(b), 3);
      expect(g.passed(b, 1), isTrue);
      g = g.withSettings(g.settings.copyWith(order: Order.textbook));
      expect(g.current(b), 0, reason: 'the book order has its own stations');
    });

    test('today\'s 家裡找找 card changes with the day and keeps the sticker', () {
      final day1 = DateTime(2026, 11, 15, 9), day2 = DateTime(2026, 11, 16, 9);
      var g = const Game().saw('ㄚ').saw('ㄧ').saw('ㄨ');
      final t1 = g.taskFor(b, day1);
      expect(['ㄚ', 'ㄧ', 'ㄨ'], contains(t1.sym));
      g = g.giveTask(b, day1);
      expect(g.taskGiven(day1), isTrue);
      expect(g.taskFor(b, day1.add(const Duration(hours: 5))).sym, t1.sym);
      g = g.found(b, day1, b.symbols[t1.sym]!.hints.first);
      expect(g.stickers, [b.symbols[t1.sym]!.hints.first]);
      expect(g.taskFor(b, day1).found, isNotNull);
      expect(g.taskFor(b, day2).found, isNull);
      expect(g.taskGiven(day2), isFalse);
    });
  });

  group('saving', () {
    test('a game comes back the same after saving', () {
      final now = DateTime(2026, 11, 15, 10);
      final g = const Game(settings: Settings(level: Level.big, minutes: 20, order: Order.textbook, stations: {0, 1, 4}, slow: true, twice: true, leftHanded: true, music: false, full: false), driver: Driver.penguin)
          .saw('ㄅ')
          .heard('ㄅ')
          .heard('ㄅ')
          .traced('ㄆ')
          .rhymeRound(0)
          .jump(1)
          .arrive(1)
          .playAt(0)
          .giveTask(b, now)
          .found(b, now, 'cup')
          .played(now, 125)
          .did(now, Module.listen)
          .rhymeAnswer(true)
          .rhymeAnswer(false)
          .rest(now);
      final back = Game.fromJson(MemoryStore().roundTrip(g.toJson()), b);
      expect(back.toJson(), g.toJson());
      expect(back.of('ㄅ').heard, 2);
      expect(back.settings.stations, {0, 1, 4});
      expect(back.driver, Driver.penguin);
      expect(back.log(now).seconds, 125);
      expect(back.rhymeRight, 1);
    });

    test('a broken or strange file gives a fresh game, never a crash', () {
      expect(Game.fromJson(null, b).toJson(), const Game().toJson());
      final odd = Game.fromJson({
        'settings': {'level': 'huge', 'minutes': 999, 'order': 7, 'stations': ['x', 9, -1], 'music': 'yes'},
        'driver': 'dragon',
        'progress': {'ㄅ': {'seen': true, 'heard': -4}, 'X': {'seen': true}, 'ㄆ': 'no'},
        'rhymed': ['common:9', 'common:2', 5],
        'skipped': 'all',
        'arrived': {'common': 12, 'textbook': 2},
        'at': 40,
        'stickers': ['cup', 'unicorn', 3],
        'task': {'day': '2026-13-45', 'sym': 'ㄅ'},
        'today': {'day': '2026-11-15', 'seconds': 'many', 'modules': ['see', 'fly']},
        'rhymeAsked': 3,
        'rhymeRight': 10,
        'restSince': 'yesterday',
      }, b);
      expect(odd.settings.level, Level.small);
      expect(odd.settings.minutes, 15);
      expect(odd.settings.order, Order.common);
      expect(odd.settings.stations, {0});
      expect(odd.settings.music, isTrue);
      expect(odd.driver, isNull);
      expect(odd.progress.keys, ['ㄅ', 'ㄆ']);
      expect(odd.of('ㄅ').heard, 0);
      expect(odd.of('ㄆ').seen, isFalse);
      expect(odd.rhymed, {'common:2'});
      expect(odd.skipped, isEmpty);
      expect(odd.arrived, {Order.textbook: 2});
      expect(odd.at, isNull);
      expect(odd.stickers, ['cup']);
      expect(odd.task, isNull);
      expect(odd.today!.seconds, 0);
      expect(odd.today!.modules, {Module.see});
      expect(odd.rhymeRight, 3);
      expect(odd.restSince, isNull);
    });

    test('the file store keeps the last good save when a file is broken', () async {
      final dir = Directory.systemTemp.createTempSync('bopomofo_store');
      addTearDown(() => dir.deleteSync(recursive: true));
      final store = FileStore(dir);
      store.write(const Game(driver: Driver.cat).toJson());
      await store.flush();
      store.write(const Game(driver: Driver.bear).toJson());
      await store.flush();
      File('${dir.path}/bopomofo_train.json').writeAsStringSync('{broken');
      expect(Game.fromJson(await store.read(), b).driver, Driver.cat, reason: 'the copy from the save before');
      File('${dir.path}/bopomofo_train.json.bak').writeAsStringSync('');
      expect(await store.read(), isNull);
    });
  });

  group('resting', () {
    test('an hour of rest; a clock moved back does not lock the app', () {
      final now = DateTime(2026, 11, 15, 10);
      final g = const Game().rest(now);
      expect(g.resting(now.add(const Duration(minutes: 30))), isTrue);
      expect(g.resting(now.add(const Duration(minutes: 61))), isFalse);
      expect(g.resting(now.subtract(const Duration(minutes: 5))), isFalse, reason: 'the clock was moved back');
      expect(g.playOn().resting(now), isFalse);
    });

    test('the play time choices', () {
      expect(Settings.minuteChoices, [5, 10, 15, 20, 30]);
      expect(const Settings().minutes, 15);
    });
  });
}

extension on MemoryStore {
  Map<String, dynamic> roundTrip(Map<String, dynamic> json) {
    write(json);
    return saved!;
  }
}
