import 'book.dart';

/// What the app says about a symbol. Lines keep the symbols in them (they
/// are also shown on screen); the voice gets them through speakable()
/// (voice.dart), so 「ㄅ，爸爸。」 is heard as 「播，爸爸。」.

/// A syllable spelled out: 「ㄇ、ㄠ」.
String spell(String syllable) => syllable.split('').join('、');

/// The symbol and its word, always together (docs/design.md 「語音」):
/// 「ㄅ，爸爸。」; a final taught at the end of its word is spelled too:
/// 「ㄠ，貓，ㄇ、ㄠ，貓。」. [twice]: the word once more.
String symbolLine(Bopomofo b, String sym, {bool twice = false}) {
  final z = b.symbols[sym]!;
  final w = b.words[z.wordId]!;
  final again = twice ? '${w.zh}。' : '';
  if (!z.atEnd) return '$sym，${w.zh}。$again';
  final (char, syllable) = w.keySyllable;
  return '$sym，${w.zh}，${spell(syllable)}，$char。$again';
}

/// After a wrong card: 「這是ㄅ，爸爸的ㄅ。」
String thisIs(Bopomofo b, String sym) => '這是$sym，${b.wordOf(sym).zh}的$sym。';
