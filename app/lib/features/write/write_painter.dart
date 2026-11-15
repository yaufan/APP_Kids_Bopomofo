import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../app/theme.dart';
import '../../core/book.dart';
import '../../core/writing.dart';

/// Where the 100 × 100 symbol box sits on the page.
class BoxFit100 {
  BoxFit100(Size page, {double fill = .82})
      : scale = math.min(page.width, page.height) * fill / Zhuyin.box,
        origin = Offset((page.width - math.min(page.width, page.height) * fill) / 2, (page.height - math.min(page.width, page.height) * fill) / 2);

  final double scale;
  final Offset origin;

  Offset toScreen(Offset p) => origin + p * scale;
  Offset toBox(Offset p) => (p - origin) / scale;
}

Path strokePath(List<Offset> points, Offset Function(Offset) map) {
  final p = Path();
  if (points.isEmpty) return p;
  final first = map(points.first);
  p.moveTo(first.dx, first.dy);
  for (final q in points.skip(1)) {
    final s = map(q);
    p.lineTo(s.dx, s.dy);
  }
  return p;
}

/// The three steps of 0.1 (docs/design.md 「寫寫看」: 看、點、描; 寫 is 0.2).
enum WriteStep { watch, tap, trace }

/// The writing page: the faint box lines, the roads, the strokes being
/// shown, the start stars, the traced ink, the green dot and its arrow.
class WritePainter extends CustomPainter {
  WritePainter({
    required this.strokes,
    required this.step,
    required this.t,
    this.watched = 0,
    this.tapped = 0,
    this.tracers = const [],
    this.current = 0,
    this.leftHanded = false,
    this.ink = Toy.red,
  });

  final List<List<Offset>> strokes;
  final WriteStep step;

  /// Seconds (the bouncing dot and star).
  final double t;

  /// Strokes shown so far in 看 (1.5: half of the second).
  final double watched;

  /// Start stars tapped (點).
  final int tapped;
  final List<Tracer> tracers;

  /// The stroke being traced.
  final int current;
  final bool leftHanded;
  final Color ink;

  static const roadWidth = 22.0, inkWidth = 10.0;
  static const road = Color(0xFFEDE6F3), roadLine = Color(0xFFD5CBE0), go = Color(0xFF4DBA6A), goLine = Color(0xFF2E8B4E);

  @override
  void paint(Canvas canvas, Size size) {
    final fit = BoxFit100(size);
    Paint line(Color c, double w) => Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = w * fit.scale
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..color = c;

    // The faint cross of a writing square (田字格 without the frame).
    final dash = Paint()
      ..color = roadLine.withValues(alpha: .7)
      ..strokeWidth = 1.5;
    final a = fit.toScreen(Offset.zero), b = fit.toScreen(const Offset(100, 100));
    final mid = (a + b) / 2;
    for (var x = a.dx; x < b.dx; x += 14) {
      canvas.drawLine(Offset(x, mid.dy), Offset(math.min(x + 7, b.dx), mid.dy), dash);
    }
    for (var y = a.dy; y < b.dy; y += 14) {
      canvas.drawLine(Offset(mid.dx, y), Offset(mid.dx, math.min(y + 7, b.dy)), dash);
    }

    switch (step) {
      case WriteStep.watch:
        for (final s in strokes) {
          canvas.drawPath(strokePath(s, fit.toScreen), line(road, roadWidth * .75));
        }
        for (var i = 0; i < strokes.length; i++) {
          final p = (watched - i).clamp(0.0, 1.0);
          if (p <= 0) break;
          final part = partOf(strokes[i], p);
          canvas.drawPath(strokePath(part, fit.toScreen), line(ink, inkWidth));
          if (p < 1) _pencil(canvas, fit.toScreen(part.last), fit.scale);
          if (p > 0) _number(canvas, fit.toScreen(strokes[i].first), fit.scale, i + 1, ink);
        }
      case WriteStep.tap:
        for (var i = 0; i < strokes.length; i++) {
          canvas.drawPath(strokePath(strokes[i], fit.toScreen), line(i < tapped ? ink : road, i < tapped ? inkWidth : roadWidth * .75));
        }
        if (tapped < strokes.length) _star(canvas, fit.toScreen(strokes[tapped].first), fit.scale, tapped + 1);
      case WriteStep.trace:
        for (var i = 0; i < strokes.length; i++) {
          final path = strokePath(strokes[i], fit.toScreen);
          canvas.drawPath(path, line(roadLine, roadWidth + 2.5));
          canvas.drawPath(path, line(road, roadWidth));
        }
        for (var i = 0; i < tracers.length && i <= current; i++) {
          canvas.drawPath(strokePath(i < current ? strokes[i] : tracers[i].traced, fit.toScreen), line(ink, inkWidth * 1.25));
        }
        if (current < strokes.length && current < tracers.length) {
          final tr = tracers[current];
          final at = tr.pointAt(tr.progress * pathLength(strokes[current]));
          _arrow(canvas, fit, strokes[current], tr.progress);
          _dot(canvas, fit.toScreen(at), fit.scale);
        }
    }
  }

  void _dot(Canvas canvas, Offset at, double scale) {
    final r = (9.5 + 1.6 * math.sin(t * 6)) * scale;
    canvas.drawCircle(at, r + 3.5 * scale, Paint()..color = go.withValues(alpha: .25));
    canvas.drawCircle(at, r, Paint()..color = go);
    canvas.drawCircle(
        at,
        r,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2
          ..color = goLine);
    canvas.drawCircle(at + Offset(-r * .3, -r * .3), r * .25, Paint()..color = Colors.white.withValues(alpha: .85));
  }

  void _star(Canvas canvas, Offset at, double scale, int n) {
    final r = (13 + 1.5 * math.sin(t * 6)) * scale;
    canvas.drawCircle(at, r * 1.3, Paint()..color = Toy.yellow.withValues(alpha: .35));
    final path = Path();
    for (var i = 0; i < 10; i++) {
      final a = -math.pi / 2 + i * math.pi / 5;
      final rr = i.isEven ? r : r * .5;
      final p = at + Offset(math.cos(a), math.sin(a)) * rr;
      if (i == 0) {
        path.moveTo(p.dx, p.dy);
      } else {
        path.lineTo(p.dx, p.dy);
      }
    }
    path.close();
    canvas.drawPath(path, Paint()..color = Toy.yellow);
    canvas.drawPath(
        path,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2
          ..strokeJoin = StrokeJoin.round
          ..color = Toy.rim(Toy.yellow));
    _label(canvas, at, '$n', r * .9, Toy.ink);
  }

  void _number(Canvas canvas, Offset at, double scale, int n, Color c) {
    final r = 6.5 * scale;
    canvas.drawCircle(at, r, Paint()..color = Colors.white);
    canvas.drawCircle(
        at,
        r,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2
          ..color = c);
    _label(canvas, at, '$n', r * 1.2, c);
  }

  void _label(Canvas canvas, Offset at, String s, double size, Color c) {
    final tp = TextPainter(
      text: TextSpan(text: s, style: TextStyle(fontSize: size, fontWeight: FontWeight.w700, color: c, fontFamily: 'Huninn')),
      textDirection: TextDirection.ltr,
    )..layout();
    tp.paint(canvas, at - Offset(tp.width / 2, tp.height / 2));
  }

  void _pencil(Canvas canvas, Offset at, double scale) {
    canvas.drawCircle(at, 7.5 * scale, Paint()..color = Toy.rim(ink));
    canvas.drawCircle(at, 4 * scale, Paint()..color = Colors.white.withValues(alpha: .75));
  }

  /// Which way to go: a soft arrow beside the road, on the side the hand
  /// does not cover.
  void _arrow(Canvas canvas, BoxFit100 fit, List<Offset> stroke, double from) {
    final len = pathLength(stroke);
    if (len < 8) return;
    final s0 = from * len;
    final tr = Tracer(stroke);
    final a = tr.pointAt(s0 + 4), b = tr.pointAt(math.min(len, s0 + 24));
    final d = b - a;
    if (d.distance < 1) return;
    final dir = d / d.distance;
    var normal = Offset(-dir.dy, dir.dx);
    if ((normal.dx > 0) != leftHanded) normal = -normal;
    final off = normal * 21;
    final p0 = fit.toScreen(a + off), p1 = fit.toScreen(b + off);
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4.5 * fit.scale
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..color = goLine.withValues(alpha: .8);
    canvas.drawLine(p0, p1, paint);
    final back = -dir * 7 * fit.scale;
    final side = Offset(-dir.dy, dir.dx) * 6 * fit.scale;
    canvas.drawPath(
        Path()
          ..moveTo(p1.dx + back.dx + side.dx, p1.dy + back.dy + side.dy)
          ..lineTo(p1.dx, p1.dy)
          ..lineTo(p1.dx + back.dx - side.dx, p1.dy + back.dy - side.dy),
        paint);
  }

  @override
  bool shouldRepaint(WritePainter old) => true;
}
