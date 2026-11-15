import 'dart:convert';
import 'dart:io';

import 'package:bopomofo_train/core/book.dart';
import 'package:bopomofo_train/core/writing.dart';
import 'package:flutter_test/flutter_test.dart';

/// The strokes of 寫寫看 (design/bopomofo.py, docs/bopomofo.md).
void main() {
  final json = jsonDecode(File('assets/bopomofo.json').readAsStringSync()) as Map<String, dynamic>;
  final b = Bopomofo.fromJson(json);
  final sure = (json['sure'] as Map).cast<String, int>();

  test('every symbol has strokes, at most four, each long enough to trace', () {
    for (final z in b.symbols.values) {
      expect(z.strokes, isNotEmpty, reason: z.sym);
      expect(z.strokes.length, lessThanOrEqualTo(4), reason: z.sym);
      for (final s in z.strokes) {
        expect(s.length, greaterThan(3), reason: z.sym);
        expect(pathLength(s), greaterThan(12), reason: '${z.sym}: a stroke too short for a finger');
        for (var i = 1; i < s.length; i++) {
          expect((s[i] - s[i - 1]).distance, lessThan(4), reason: '${z.sym}: points about 2.5 apart');
        }
      }
    }
  });

  test('every stroke stays inside the box', () {
    for (final z in b.symbols.values) {
      for (final s in z.strokes) {
        for (final p in s) {
          expect(p.dx, inInclusiveRange(0, Zhuyin.box), reason: z.sym);
          expect(p.dy, inInclusiveRange(0, Zhuyin.box), reason: z.sym);
        }
      }
      // The symbol fills its carriage: it spans most of the box one way or the other.
      final xs = [for (final s in z.strokes) for (final p in s) p.dx], ys = [for (final s in z.strokes) for (final p in s) p.dy];
      final w = xs.reduce((a, c) => a > c ? a : c) - xs.reduce((a, c) => a < c ? a : c);
      final h = ys.reduce((a, c) => a > c ? a : c) - ys.reduce((a, c) => a < c ? a : c);
      expect(w > 60 || h > 60, isTrue, reason: z.sym);
    }
  });

  test('the stroke counts checked against the 教育部 manual', () {
    // docs/bopomofo.md lists these and the ones not checked yet.
    expect(sure.length, greaterThanOrEqualTo(20));
    for (final e in sure.entries) {
      expect(b.symbols[e.key]!.strokes.length, e.value, reason: e.key);
    }
    expect(b.symbols['ㄖ']!.strokes.length, 4);
    expect(b.symbols['ㄑ']!.strokes.length, 1);
    expect(b.symbols['ㄧ']!.strokes.length, 1);
  });

  test('strokes go the way they are written: top to bottom, left to right', () {
    for (final z in b.symbols.values) {
      for (final s in z.strokes) {
        final a = s.first, e = s.last;
        // A stroke never starts at its bottom and goes up as its main way (no 提 among the 37).
        expect(e.dy - a.dy > -5 || (e.dx - a.dx) > 0, isTrue, reason: '${z.sym}: a stroke written backwards');
      }
      // The first stroke starts in the top half.
      expect(z.strokes.first.first.dy, lessThan(55), reason: z.sym);
    }
    expect(b.symbols['ㄧ']!.strokes.single.first, const Offset(5, 50));
  });

  test('a finger tracing along a stroke finishes it; one off the road does not', () {
    for (final z in b.symbols.values) {
      for (final s in z.strokes) {
        final t = Tracer(s);
        expect(t.down(s.first + const Offset(3, -2)), isTrue, reason: z.sym);
        for (final p in s) {
          t.move(p + const Offset(4, 3));
        }
        t.move(s.last);
        expect(t.done, isTrue, reason: z.sym);
        // (A short stroke's far end is close enough to its start to count.)
        if ((s.last - s.first).distance > 35) expect(Tracer(s).down(s.last), isFalse, reason: '${z.sym}: starting at the far end');
      }
    }
  });
}
