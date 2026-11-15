import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/providers.dart';
import 'theme.dart';
import 'widgets.dart';

/// Turns the wheels and puffs the smoke of whatever train is under it.
class TrainClock extends StatefulWidget {
  const TrainClock({super.key, required this.builder, this.period = 1800});

  /// [t] goes round 0..1 every [period] milliseconds.
  final Widget Function(BuildContext context, double t) builder;
  final int period;

  @override
  State<TrainClock> createState() => _TrainClockState();
}

class _TrainClockState extends State<TrainClock> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: Duration(milliseconds: widget.period))..repeat();

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(animation: _c, builder: (context, _) => widget.builder(context, _c.value));
}

/// One carriage (docs/art.md: 120 × 100, the symbol on its panel, two wheels).
class Carriage extends StatelessWidget {
  const Carriage({super.key, required this.station, this.sym, this.width = 100, this.spin = 0, this.ghost = false, this.ring});

  final int station;

  /// The symbol written on its panel (none: an empty carriage).
  final String? sym;
  final double width;

  /// The wheels' turn (0..1).
  final double spin;

  /// Still to come: grey and see-through.
  final bool ghost;

  /// A coloured glow round it (picked).
  final Color? ring;

  static const aspect = 120 / 100;

  @override
  Widget build(BuildContext context) {
    final w = width, h = width / aspect;
    double x(double u) => u / 120 * w;
    double y(double u) => u / 100 * h;
    final wheel = x(26);
    return SizedBox(
      width: w,
      height: h,
      child: Stack(clipBehavior: Clip.none, children: [
        if (ring != null)
          Positioned(
            left: x(2),
            top: y(2),
            width: x(116),
            height: y(84),
            child: DecoratedBox(decoration: BoxDecoration(borderRadius: BorderRadius.circular(x(22)), boxShadow: [BoxShadow(color: ring!.withValues(alpha: .8), blurRadius: 4, spreadRadius: x(6))])),
          ),
        Positioned.fill(child: Art(ghost ? 'train/carriage_ghost' : 'train/carriage_$station')),
        for (final cx in [32.0, 88.0])
          Positioned(
            left: x(cx) - wheel / 2,
            top: y(86) - wheel / 2,
            width: wheel,
            height: wheel,
            child: Opacity(opacity: ghost ? .35 : 1, child: Transform.rotate(angle: spin * 2 * math.pi, child: const Art('train/wheel'))),
          ),
        if (sym != null)
          Positioned(
            left: x(22),
            top: y(18),
            width: x(76),
            height: y(52),
            child: Center(
              child: Text(
                sym!,
                textScaler: TextScaler.noScaling,
                style: TextStyle(fontSize: y(46), height: 1.05, fontWeight: FontWeight.w700, color: ghost ? Toy.inkSoft.withValues(alpha: .55) : Toy.ink),
              ),
            ),
          ),
      ]),
    );
  }
}

/// The locomotive with the driver in its cab, turning wheels and smoke
/// (docs/art.md: 200 × 140).
class Locomotive extends ConsumerWidget {
  const Locomotive({super.key, this.width = 160, this.t = 0, this.stickers = const []});

  final double width;

  /// The train clock (0..1): the wheels and the smoke.
  final double t;

  /// 家裡找找 stickers (word ids) to show on the boiler, newest last.
  final List<String> stickers;

  static const aspect = 200 / 140;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final w = width, h = width / aspect;
    double x(double u) => u / 200 * w;
    double y(double u) => u / 140 * h;
    Widget wheel(double cx, double r) => Positioned(
          left: x(cx - r),
          top: y(116) - x(r),
          width: x(r * 2),
          height: x(r * 2),
          child: Transform.rotate(angle: t * 2 * math.pi * (21 / r), child: const Art('train/wheel')),
        );
    final shown = stickers.length > 3 ? stickers.sublist(stickers.length - 3) : stickers;
    return SizedBox(
      width: w,
      height: h,
      child: Stack(clipBehavior: Clip.none, children: [
        for (var k = 0; k < 3; k++) _puff(x, y, (t + k / 3) % 1),
        Positioned.fill(child: const Art('train/locomotive')),
        Positioned(
          left: x(20),
          top: y(30),
          width: x(46),
          height: y(40),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(x(8)),
            child: OverflowBox(
              alignment: Alignment.topCenter,
              maxHeight: x(52),
              maxWidth: x(52),
              child: Padding(padding: EdgeInsets.only(top: y(1)), child: DriverView(size: x(48))),
            ),
          ),
        ),
        for (final (i, s) in shown.indexed)
          Positioned(
            left: x(98 + i * 24.0),
            top: y(62),
            width: x(26),
            height: x(26),
            child: Container(
              decoration: BoxDecoration(color: Colors.white, shape: BoxShape.circle, border: Border.all(color: Toy.gold, width: 1.5)),
              padding: EdgeInsets.all(x(2)),
              child: Art('words/$s'),
            ),
          ),
        wheel(42, 21),
        wheel(108, 17),
        wheel(152, 17),
      ]),
    );
  }

  Widget _puff(double Function(double) x, double Function(double) y, double p) {
    final size = x(22 + 26 * p);
    return Positioned(
      left: x(151) - size / 2 - x(30) * p,
      top: y(22) - size * .7 - y(60) * p,
      width: size,
      height: size * 32 / 44,
      child: Opacity(opacity: (1 - p) * .9, child: const Art('train/smoke')),
    );
  }
}

/// A row of track under a train.
class Track extends StatelessWidget {
  const Track({super.key, this.height = 14});

  final double height;

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final piece = height * 120 / 22;
        final n = (box.maxWidth / piece).ceil() + 1;
        return ClipRect(
          child: SizedBox(
            height: height,
            child: OverflowBox(
              alignment: Alignment.centerLeft,
              maxWidth: n * piece,
              child: Row(children: [for (var i = 0; i < n; i++) SizedBox(width: piece, height: height, child: const Art('train/track', fit: BoxFit.fill))]),
            ),
          ),
        );
      });
}

/// Puts [child] on the train's track (the clock turns the wheels).
class OnTrack extends StatelessWidget {
  const OnTrack({super.key, required this.child, this.track = 14});

  final Widget child;
  final double track;

  @override
  Widget build(BuildContext context) => Stack(clipBehavior: Clip.none, children: [
        Positioned(left: 0, right: 0, bottom: 0, child: Track(height: track)),
        Padding(padding: EdgeInsets.only(bottom: track * .45), child: child),
      ]);
}

/// The ref for a game's stickers (the locomotive shows them).
List<String> stickersOf(WidgetRef ref) => ref.watch(gameProvider.select((g) => g.stickers));
