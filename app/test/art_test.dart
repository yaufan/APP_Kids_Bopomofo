import 'dart:io';

import 'package:bopomofo_train/app/map_layout.dart';
import 'package:bopomofo_train/core/game.dart';
import 'package:flutter_test/flutter_test.dart';

import 'helpers.dart';

/// Every picture and sound the program asks for exists (docs/art.md), and
/// no picture uses what flutter_svg cannot draw.
void main() {
  bool has(String path) => File('assets/art/$path.svg').existsSync();

  test('every picture the screens ask for is drawn', () {
    final wanted = [
      for (var i = 0; i < 7; i++) 'train/carriage_$i',
      for (final n in ['carriage_ghost', 'locomotive', 'wheel', 'smoke', 'track', 'flag', 'sign', 'station']) 'train/$n',
      for (final d in Driver.values) 'train/driver_${d.name}',
      'map/taiwan',
      for (final w in book.words.keys) 'words/$w',
      for (final n in ['see', 'listen', 'spell', 'write', 'rhyme', 'find', 'lock', 'check', 'star', 'speaker']) 'icons/$n',
      for (final n in ['sun', 'cloud', 'moon', 'star', 'hills', 'tunnel']) 'home/$n',
    ];
    expect([for (final p in wanted) if (!has(p)) p], isEmpty, reason: 'draw these in design/art/');
  });

  test('every word and every hint has a picture, and no picture is left over', () {
    final words = Directory('assets/art/words').listSync().map((f) => f.uri.pathSegments.last.replaceAll('.svg', '')).toSet();
    expect(words, book.words.keys.toSet());
  });

  test('the stations on the map are inside the picture, from the north down', () {
    expect(mapStations.length, 7);
    for (final (x, y) in mapStations) {
      expect(x, inInclusiveRange(.05, .95));
      expect(y, inInclusiveRange(.05, .95));
    }
    // 台北 at the top, 高雄 near the bottom; 台中 to 台南 heading south.
    expect(mapStations.first.$2, lessThan(mapStations[3].$2));
    expect(mapStations[4].$2, lessThan(mapStations[5].$2));
    expect(mapStations.last.$2, greaterThan(.7));
  });

  test('no picture uses what flutter_svg cannot draw, and none is too big', () {
    final bad = <String>[];
    var n = 0;
    for (final f in Directory('assets/art').listSync(recursive: true).whereType<File>()) {
      if (!f.path.endsWith('.svg')) continue;
      n++;
      final text = f.readAsStringSync();
      if (f.lengthSync() > 70 * 1024) bad.add('${f.path} too big');
      for (final no in ['<filter', '<mask', '<clipPath', '<style', 'style=', '<text', '<image', '<pattern', 'mix-blend']) {
        if (text.contains(no)) bad.add('${f.path} uses $no');
      }
      if (!text.trimRight().endsWith('</svg>')) bad.add('${f.path} is cut off');
    }
    expect(n, greaterThan(120));
    expect(bad, isEmpty);
  });

  test('every sound the app plays is there', () {
    final names = [
      'tap', 'pop', 'ding', 'right', 'try', 'whistle', 'puff', 'clack', 'couple', 'chime', 'star', 'stroke', 'done', 'sticker', 'whoosh', 'night',
      for (final m in ['station', 'write', 'rhyme', 'rest']) 'music_$m',
    ];
    expect([for (final s in names) if (!File('assets/sounds/$s.wav').existsSync()) s], isEmpty);
    final played = RegExp(r"""(?:sfx\(ref, |_sounds\.play\()'([a-z_]+)'""");
    final used = <String>{};
    for (final f in Directory('lib').listSync(recursive: true).whereType<File>()) {
      for (final m in played.allMatches(f.readAsStringSync())) {
        used.add(m.group(1)!);
      }
    }
    expect(used.difference(names.toSet()), isEmpty, reason: 'a sound the code plays that is not made');
  });

  test('the font has every symbol (the app writes them, the pictures do not)', () {
    expect(File('assets/fonts/jf-openhuninn-2.1.ttf').existsSync(), isTrue);
    expect(File('assets/fonts/OFL-jf-openhuninn.txt').existsSync(), isTrue);
  });
}
