import 'dart:convert';

import 'package:flutter/services.dart';

/// Which way the seven stations share out the symbols (docs/design.md 「符號的順序」):
/// the common ones first (the default) or the schoolbook's ㄅㄆㄇㄈ.
enum Order {
  common('常用的先'),
  textbook('課本順序');

  const Order(this.zh);

  final String zh;
}

/// One of the 37 symbols, as in assets/bopomofo.json (design/bopomofo.py).
class Zhuyin {
  const Zhuyin({required this.sym, required this.id, required this.initial, required this.wordId, required this.atEnd, required this.story, required this.hints, required this.strokes});

  /// The symbol itself (ㄅ); shown with the font, never sent to the voice.
  final String sym;

  /// A short ASCII name (b, zh, ang).
  final String id;

  /// 聲母 (21) or 韻母 (16).
  final bool initial;

  /// Its example word (爸爸), a picture in assets/art/words/.
  final String wordId;

  /// Whether the word has the symbol at its end (貓 for ㄠ) rather than its start.
  final bool atEnd;

  /// The shape story for 大火車 (「ㄅ像爸爸彎彎的手臂」).
  final String story;

  /// 家裡找找: things at home with the sound.
  final List<String> hints;

  /// The strokes in writing order, in a 100 × 100 box.
  final List<List<Offset>> strokes;

  static const box = 100.0;

  factory Zhuyin.fromJson(Map<String, dynamic> j) => Zhuyin(
        sym: j['sym'] as String,
        id: j['id'] as String,
        initial: j['kind'] == 'initial',
        wordId: j['word'] as String,
        atEnd: j['at'] == 'end',
        story: j['story'] as String,
        hints: [for (final h in j['hints'] as List) h as String],
        strokes: [
          for (final s in j['strokes'] as List)
            [for (final p in s as List) Offset(((p as List)[0] as num).toDouble(), (p[1] as num).toDouble())],
        ],
      );
}

/// A word with a picture (`assets/art/words/<id>.svg`).
class Word {
  const Word({required this.id, required this.zh, required this.zy, this.key, this.home = false});

  final String id;

  /// The word (媽媽).
  final String zh;

  /// Its zhuyin, one string per syllable, without tones (ㄇㄚ, ㄇㄚ).
  final List<String> zy;

  /// The syllable that teaches a final at the end (杯 in 杯子); null: the last one.
  final int? key;

  /// Something found at home (家裡找找 hints).
  final bool home;

  /// The symbol the word starts with (ㄇ for 媽媽, ㄧ for 衣服).
  String get head => zy.first[0];

  /// The final the key syllable ends with (ㄠ for 貓), or null (子 has none).
  String? get tail => _final(zy[key ?? zy.length - 1]);

  /// The final its last syllable ends with: words with the same rhyme 押韻.
  String? get rhyme => _final(zy.last);

  /// The key syllable and its character (貓, ㄇㄠ).
  (String, String) get keySyllable {
    final i = key ?? zy.length - 1;
    return (zh[i], zy[i]);
  }

  /// Whether [sym] is heard in the word: an initial at its start, a final anywhere.
  bool hasSound(String sym) => Bopomofo.isInitial(sym) ? head == sym : zy.any((s) => s.contains(sym));

  /// Every symbol in the word (all of them, like the words, are one UTF-16 unit each).
  Set<String> get symbols => {for (final s in zy) ...s.split('')};

  static String? _final(String syllable) {
    final last = syllable[syllable.length - 1];
    return Bopomofo.isInitial(last) ? null : last;
  }

  factory Word.fromJson(Map<String, dynamic> j) => Word(
        id: j['id'] as String,
        zh: j['zh'] as String,
        zy: [for (final s in j['zy'] as List) s as String],
        key: j['key'] as int?,
        home: j['home'] == true,
      );
}

/// A station on the line round Taiwan (台北 to 高雄), with its colour.
class Station {
  const Station(this.index, this.name, this.color);

  final int index;
  final String name;
  final Color color;
}

/// Everything about the symbols: stations, both orders, the symbols, the words.
class Bopomofo {
  Bopomofo({required this.stations, required this.orders, required List<Zhuyin> symbols, required List<Word> words})
      : symbols = {for (final s in symbols) s.sym: s},
        words = {for (final w in words) w.id: w};

  final List<Station> stations;
  final Map<Order, List<List<String>>> orders;
  final Map<String, Zhuyin> symbols;
  final Map<String, Word> words;

  static const initials = 'ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙ';
  static const finals = 'ㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦㄧㄨㄩ';

  static bool isInitial(String s) => initials.contains(s);

  static bool isZhuyin(String s) => s.length == 1 && (initials.contains(s) || finals.contains(s));

  /// Pairs that sound alike to a 4 or 5 year old: never the only two cards
  /// at 小火車, and never the odd one out next to each other in 押韻接龍.
  static const confusable = [
    ('ㄓ', 'ㄗ'), ('ㄔ', 'ㄘ'), ('ㄕ', 'ㄙ'), ('ㄖ', 'ㄌ'), ('ㄋ', 'ㄌ'), ('ㄈ', 'ㄏ'),
    ('ㄣ', 'ㄥ'), ('ㄢ', 'ㄤ'), ('ㄛ', 'ㄜ'), ('ㄝ', 'ㄟ'), ('ㄧ', 'ㄩ'),
  ];

  static bool alike(String a, String b) => a == b || confusable.any((p) => (p.$1 == a && p.$2 == b) || (p.$1 == b && p.$2 == a));

  /// The symbols of every station, in this order.
  List<List<String>> rows(Order o) => orders[o]!;

  /// The station [sym] is in.
  int stationOf(String sym, Order o) => rows(o).indexWhere((r) => r.contains(sym));

  /// Every symbol in learning order.
  List<String> all(Order o) => [for (final r in rows(o)) ...r];

  Word wordOf(String sym) => words[symbols[sym]!.wordId]!;

  factory Bopomofo.fromJson(Map<String, dynamic> j) => Bopomofo(
        stations: [
          for (final (i, s) in (j['stations'] as List).indexed)
            Station(i, (s as Map)['name'] as String, Color(int.parse((s['color'] as String).substring(1), radix: 16) | 0xFF000000)),
        ],
        orders: {
          for (final o in Order.values)
            o: [
              for (final r in (j['orders'] as Map)[o.name] as List) [for (final s in r as List) s as String],
            ],
        },
        symbols: [for (final s in j['symbols'] as List) Zhuyin.fromJson(s as Map<String, dynamic>)],
        words: [for (final w in j['words'] as List) Word.fromJson(w as Map<String, dynamic>)],
      );

  static Bopomofo parse(String json) => Bopomofo.fromJson(jsonDecode(json) as Map<String, dynamic>);

  static Future<Bopomofo> load([AssetBundle? bundle]) async => parse(await (bundle ?? rootBundle).loadString('assets/bopomofo.json'));
}
