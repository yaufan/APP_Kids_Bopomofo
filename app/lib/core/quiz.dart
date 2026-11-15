import 'dart:math' as math;

import 'book.dart';
import 'game.dart';

/// 聽聽找找: the app says [word]; which carriage is its start (or, [tail],
/// its end)? Two cards at 小火車, three at 大火車.
class ListenQuestion {
  const ListenQuestion(this.word, this.answer, this.options, {this.tail = false});

  final Word word;
  final String answer;
  final List<String> options;
  final bool tail;
}

/// A 押韻接龍 question.
sealed class RhymeQuestion {
  const RhymeQuestion(this.options);

  /// Three pictures.
  final List<Word> options;
}

/// 「哪個是ㄇ開頭？」: one picture starts with [sym].
class HeadQuestion extends RhymeQuestion {
  const HeadQuestion(this.sym, this.right, super.options);

  final String sym;
  final Word right;
}

/// 「哪兩個押韻？」: two pictures end with [rhyme].
class PairQuestion extends RhymeQuestion {
  const PairQuestion(this.rhyme, this.right, super.options);

  final String rhyme;
  final Set<Word> right;
}

/// Questions per round.
const listenCount = 10;
const rhymeCount = 6;

/// Words that start with [sym].
List<Word> headWords(Bopomofo b, String sym) => [for (final w in b.words.values) if (w.head == sym) w];

/// Words whose key syllable ends with [sym].
List<Word> tailWords(Bopomofo b, String sym) => [for (final w in b.words.values) if (w.tail == sym) w];

/// Cards to go with [answer]: from [pool] first (the stations so far), then
/// any symbol; never the answer twice, never a symbol heard in [word], and at
/// 小火車 never one that sounds like the answer.
List<String> _cards(Bopomofo b, String answer, Word word, List<String> pool, int n, bool small, math.Random r) {
  bool ok(String s, List<String> taken) => s != answer && !taken.contains(s) && !word.symbols.contains(s) && !(small && Bopomofo.alike(s, answer));
  final out = <String>[answer];
  for (final from in [[...pool]..shuffle(r), [...b.all(Order.common)]..shuffle(r)]) {
    for (final s in from) {
      if (out.length >= n) break;
      if (ok(s, out)) out.add(s);
    }
  }
  return out..shuffle(r);
}

/// A round of 聽聽找找 at [station]: every symbol of the station at least
/// once (in a shuffled order), the cards from it and the stations before.
/// 小火車 asks for the start (a final only taught at the end of its word,
/// like ㄠ in 貓, is asked at the end); 大火車 asks for either.
List<ListenQuestion> listenRound(Bopomofo b, Game g, int station, math.Random r, {int count = listenCount}) {
  final s = g.settings;
  final small = s.level == Level.small;
  final row = [...g.row(b, station)]..shuffle(r);
  final pool = g.pool(b, station);
  final out = <ListenQuestion>[];
  Word? last;
  for (var i = 0; i < count; i++) {
    final sym = row[i % row.length];
    final heads = headWords(b, sym), tails = tailWords(b, sym);
    final tail = heads.isEmpty || (!small && tails.isNotEmpty && r.nextInt(3) == 0);
    var words = tail ? (small ? [b.wordOf(sym)] : tails) : heads;
    if (words.length > 1) words = [for (final w in words) if (w != last) w];
    final word = words[r.nextInt(words.length)];
    last = word;
    out.add(ListenQuestion(word, sym, _cards(b, sym, word, pool, small ? 2 : 3, small, r), tail: tail));
  }
  return out;
}

/// A round of 押韻接龍 at [station]: 小火車 first 「哪個是ㄇ開頭？」 then
/// 「哪兩個押韻？」, 大火車 the two taking turns.
List<RhymeQuestion> rhymeRound(Bopomofo b, Game g, int station, math.Random r, {int count = rhymeCount}) {
  final small = g.settings.level == Level.small;
  final used = <Word>{};
  final heads = [for (final s in g.row(b, station)) if (headWords(b, s).isNotEmpty) s]..shuffle(r);
  final morePool = [for (final s in g.pool(b, station)) if (headWords(b, s).isNotEmpty && !heads.contains(s)) s]..shuffle(r);
  final headSyms = [...heads, ...morePool];
  final groups = <String, List<Word>>{};
  for (final w in b.words.values) {
    final rh = w.rhyme;
    if (rh != null) (groups[rh] ??= []).add(w);
  }
  final rhymes = [for (final e in groups.entries) if (e.value.length >= 2) e.key]..shuffle(r);
  final out = <RhymeQuestion>[];
  var h = 0, p = 0;
  for (var i = 0; i < count; i++) {
    final head = small ? i < count ~/ 2 : i.isEven;
    if (head && headSyms.isNotEmpty) {
      out.add(_head(b, headSyms[h++ % headSyms.length], used, r));
    } else {
      out.add(_pair(b, rhymes[p++ % rhymes.length], groups, used, r));
    }
  }
  return out;
}

Word _pick(List<Word> from, Set<Word> used, math.Random r) {
  final fresh = [for (final w in from) if (!used.contains(w)) w];
  final list = fresh.isEmpty ? from : fresh;
  final w = list[r.nextInt(list.length)];
  used.add(w);
  return w;
}

HeadQuestion _head(Bopomofo b, String sym, Set<Word> used, math.Random r) {
  final right = _pick(headWords(b, sym), used, r);
  final others = <Word>[];
  final taken = {sym};
  for (final w in [...b.words.values]..shuffle(r)) {
    if (others.length >= 2) break;
    if (used.contains(w) || taken.any((t) => Bopomofo.alike(t, w.head))) continue;
    others.add(w);
    taken.add(w.head);
  }
  used.addAll(others);
  return HeadQuestion(sym, right, [right, ...others]..shuffle(r));
}

PairQuestion _pair(Bopomofo b, String rhyme, Map<String, List<Word>> groups, Set<Word> used, math.Random r) {
  final group = [...groups[rhyme]!];
  final a = _pick(group, used, r);
  final b2 = _pick([for (final w in group) if (w != a) w], used, r);
  final odd = _pick([
    for (final w in b.words.values)
      if (w.rhyme != null && !Bopomofo.alike(w.rhyme!, rhyme)) w,
  ], used, r);
  return PairQuestion(rhyme, {a, b2}, [a, b2, odd]..shuffle(r));
}
