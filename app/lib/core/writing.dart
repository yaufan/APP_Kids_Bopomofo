import 'dart:math' as math;
import 'dart:ui';

// The tracing engine of 字母寵物 (its core/writing.dart), for 寫寫看: a
// stroke is a list of points from where the pen starts to where it lifts,
// in a 100 × 100 box. 0.1 has the first three steps (看、點、描); writing
// alone comes in 0.2.

double pathLength(List<Offset> points) {
  var total = 0.0;
  for (var i = 1; i < points.length; i++) {
    total += (points[i] - points[i - 1]).distance;
  }
  return total;
}

/// The first part of [points], [t] (0..1) of the way along.
List<Offset> partOf(List<Offset> points, double t) {
  if (t >= 1) return points;
  if (t <= 0) return [points.first];
  final total = pathLength(points);
  var left = total * t;
  final out = <Offset>[points.first];
  for (var i = 1; i < points.length; i++) {
    final seg = (points[i] - points[i - 1]).distance;
    if (left <= seg) {
      out.add(Offset.lerp(points[i - 1], points[i], seg == 0 ? 0 : left / seg)!);
      return out;
    }
    left -= seg;
    out.add(points[i]);
  }
  return out;
}

/// Tracing one stroke along its road (the third step): how far along the
/// finger has come. The finger has to start at the start dot; if it leaves
/// the road the tracing waits where it was until the finger comes back.
class Tracer {
  Tracer(this.stroke, {this.width = 20}) : _length = pathLength(stroke);

  final List<Offset> stroke;

  /// How far from the line (box units) still counts as on the road: wide,
  /// since 注音 has hooks and bends (docs/design.md 「寫寫看」).
  final double width;
  final double _length;
  double _along = 0;
  bool _active = false;
  bool offRoad = false;

  /// How far along the stroke (0..1).
  double get progress => _length == 0 ? 1 : (_along / _length).clamp(0, 1);

  bool get done => progress >= 0.96;

  /// The finger comes down at [p]: it has to be at the start, or (after it
  /// left the road) back where the tracing stopped.
  bool down(Offset p) {
    final at = pointAt(_along);
    _active = (p - at).distance <= width * 1.5;
    offRoad = !_active;
    return _active;
  }

  /// The finger moved to [p]: the tracing follows it forwards along the
  /// road, never backwards, and never jumps ahead past a gap.
  void move(Offset p) {
    if (!_active || done) return;
    var best = _along, bestD = double.infinity;
    // Look a little way ahead of where the tracing is.
    final ahead = math.min(_length, _along + width * 3);
    for (var s = _along; s <= ahead; s += 1) {
      final d = (pointAt(s) - p).distance;
      if (d < bestD) {
        bestD = d;
        best = s;
      }
    }
    if (bestD > width) {
      offRoad = true;
      return;
    }
    offRoad = false;
    _along = math.max(_along, best);
  }

  void up() => _active = false;

  /// The point [s] along the stroke.
  Offset pointAt(double s) {
    var left = s;
    for (var i = 1; i < stroke.length; i++) {
      final seg = (stroke[i] - stroke[i - 1]).distance;
      if (left <= seg) return Offset.lerp(stroke[i - 1], stroke[i], seg == 0 ? 0 : left / seg)!;
      left -= seg;
    }
    return stroke.last;
  }

  /// The part of the stroke traced so far.
  List<Offset> get traced {
    final out = <Offset>[stroke.first];
    var walked = 0.0;
    for (var i = 1; i < stroke.length; i++) {
      final seg = (stroke[i] - stroke[i - 1]).distance;
      if (walked + seg >= _along) {
        out.add(pointAt(_along));
        return out;
      }
      walked += seg;
      out.add(stroke[i]);
    }
    return out;
  }
}
