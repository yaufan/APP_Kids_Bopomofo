import 'package:flutter_tts/flutter_tts.dart';

/// The phone's Mandarin voice cannot read a symbol on its own (Android reads
/// 「ㄅ」 badly or not at all), so every symbol is read as the character a
/// teacher says it with (docs/design.md 「語音」): ㄅ is 播. The voice is
/// never sent a symbol: [speakable] swaps them all before anything is said.
/// ㄥ has no common character of its own; 鞥 is the first one to try on a
/// real phone (parent mode's 語音試聽 plays every one of these).
const homophones = {
  'ㄅ': '播', 'ㄆ': '坡', 'ㄇ': '摸', 'ㄈ': '佛', 'ㄉ': '得', 'ㄊ': '特', 'ㄋ': '訥', 'ㄌ': '勒', 'ㄍ': '哥', 'ㄎ': '科', 'ㄏ': '喝',
  'ㄐ': '基', 'ㄑ': '欺', 'ㄒ': '希', 'ㄓ': '知', 'ㄔ': '吃', 'ㄕ': '詩', 'ㄖ': '日', 'ㄗ': '資', 'ㄘ': '雌', 'ㄙ': '思',
  'ㄚ': '啊', 'ㄛ': '喔', 'ㄜ': '婀', 'ㄝ': '耶', 'ㄞ': '哀', 'ㄟ': '欸', 'ㄠ': '凹', 'ㄡ': '歐', 'ㄢ': '安', 'ㄣ': '恩', 'ㄤ': '骯',
  'ㄥ': '鞥', 'ㄦ': '兒', 'ㄧ': '衣', 'ㄨ': '烏', 'ㄩ': '迂',
};

/// [text] as the voice should get it: every symbol replaced by its
/// character, tone marks dropped.
String speakable(String text) {
  final out = StringBuffer();
  for (final c in text.split('')) {
    if ('ˊˇˋ˙'.contains(c)) continue;
    out.write(homophones[c] ?? c);
  }
  return out.toString();
}

/// Whether [text] still has a symbol in it (the voice must never get one).
bool hasZhuyin(String text) => text.split('').any((c) => homophones.containsKey(c) || 'ˊˇˋ˙'.contains(c));

/// Reads things out for children who cannot read yet, in Taiwanese Mandarin.
abstract interface class Voice {
  /// Says [zh] (already [speakable]); [slow] for a slower voice.
  Future<void> say(String zh, {bool slow = false});
  Future<void> stop();
}

class SystemVoice implements Voice {
  FlutterTts? _tts;
  double? _rate;

  Future<FlutterTts> _engine() async {
    final existing = _tts;
    if (existing != null) return existing;
    final tts = _tts = FlutterTts();
    await tts.awaitSpeakCompletion(true);
    await tts.setLanguage('zh-TW');
    await tts.setPitch(1.15);
    return tts;
  }

  @override
  Future<void> say(String zh, {bool slow = false}) async {
    try {
      final tts = await _engine();
      await tts.stop();
      final rate = slow ? 0.32 : 0.45;
      if (rate != _rate) {
        _rate = rate;
        await tts.setSpeechRate(rate);
      }
      if (zh.isNotEmpty) await tts.speak(speakable(zh));
    } catch (_) {
      // No speech engine (tests, or a phone without one): the pictures and
      // the words on screen are enough.
    }
  }

  @override
  Future<void> stop() async {
    try {
      await _tts?.stop();
    } catch (_) {}
  }
}

class SilentVoice implements Voice {
  const SilentVoice();

  @override
  Future<void> say(String zh, {bool slow = false}) async {}

  @override
  Future<void> stop() async {}
}

/// Remembers what was said (tests).
class RecordingVoice implements Voice {
  final said = <String>[];

  @override
  Future<void> say(String zh, {bool slow = false}) async => said.add(zh);

  @override
  Future<void> stop() async {}
}
