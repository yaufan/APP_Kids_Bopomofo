import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../app/strings.dart';
import '../app/theme.dart';
import '../app/widgets.dart';
import '../core/game.dart';
import '../core/providers.dart';

/// The buttons at the end of a round: again, the next thing to do, home,
/// and today's 家裡找找 card when it has not been looked at yet (docs/design.md:
/// 每天第一次玩完一個模組，司機會給一張任務卡).
List<Widget> doneActions(BuildContext context, WidgetRef ref, {required VoidCallback again, Module? next}) {
  final g = ref.read(gameProvider);
  final now = ref.read(clockProvider)();
  final task = g.settings.full && !g.taskGiven(now);
  return [
    if (task) PillButton(label: Strings.taskCard, color: Toy.gold, icon: Icons.star_rounded, expand: true, onTap: () => context.go('/find')),
    if (next != null && g.settings.open(next)) PillButton(label: next.zh, color: Toy.blue, expand: true, onTap: () => context.go('/${next.name}')),
    PillButton(label: Strings.playAgain, color: Toy.orange, icon: Icons.replay_rounded, expand: true, onTap: again),
    PillButton(label: Strings.home, color: Toy.red, icon: Icons.home_rounded, expand: true, onTap: () => context.go('/')),
  ];
}

/// The symbols of the station being played, as small carriages on a track
/// (認符號 and 寫寫看 pick one with them).
class StationRow extends StatelessWidget {
  const StationRow({super.key, required this.syms, required this.station, required this.picked, required this.onPick, required this.done, this.width = 64});

  final List<String> syms;
  final int station;
  final String picked;
  final void Function(String sym) onPick;
  final bool Function(String sym) done;
  final double width;

  @override
  Widget build(BuildContext context) => SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 10),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          for (final s in syms)
            Padding(
              padding: const EdgeInsets.fromLTRB(3, 10, 3, 4),
              child: Semantics(
                key: ValueKey('pick-$s'),
                container: true,
                button: true,
                selected: s == picked,
                label: s,
                excludeSemantics: true,
                onTap: () => onPick(s),
                child: Pressable(
                  onTap: () => onPick(s),
                  sound: null,
                  child: Stack(clipBehavior: Clip.none, children: [
                    AnimatedScale(
                      duration: const Duration(milliseconds: 200),
                      scale: s == picked ? 1.1 : 1,
                      child: CarriageThumb(sym: s, station: station, width: width, ring: s == picked ? Toy.yellow : null),
                    ),
                    if (done(s)) const Positioned(right: -6, top: -8, width: 24, height: 24, child: Art('icons/check')),
                  ]),
                ),
              ),
            ),
        ]),
      );
}

/// A carriage without wheels turning (a thumbnail).
class CarriageThumb extends StatelessWidget {
  const CarriageThumb({super.key, required this.sym, required this.station, this.width = 64, this.ring});

  final String sym;
  final int station;
  final double width;
  final Color? ring;

  @override
  Widget build(BuildContext context) => _Thumb(sym: sym, station: station, width: width, ring: ring);
}

class _Thumb extends StatelessWidget {
  const _Thumb({required this.sym, required this.station, required this.width, this.ring});

  final String sym;
  final int station;
  final double width;
  final Color? ring;

  @override
  Widget build(BuildContext context) {
    final h = width / 1.2;
    return SizedBox(
      width: width,
      height: h,
      child: Stack(clipBehavior: Clip.none, children: [
        if (ring != null)
          Positioned.fill(
            child: DecoratedBox(decoration: BoxDecoration(borderRadius: BorderRadius.circular(width * .2), boxShadow: [BoxShadow(color: ring!.withValues(alpha: .85), blurRadius: 4, spreadRadius: 4)])),
          ),
        Positioned.fill(child: Art('train/carriage_$station')),
        for (final cx in [32.0, 88.0])
          Positioned(left: cx / 120 * width - width * .11, top: h * .86 - width * .11, width: width * .22, height: width * .22, child: const Art('train/wheel')),
        Positioned(
          left: width * 22 / 120,
          top: h * .18,
          width: width * 76 / 120,
          height: h * .52,
          child: Center(child: Text(sym, textScaler: TextScaler.noScaling, style: TextStyle(fontSize: h * .44, height: 1.05, fontWeight: FontWeight.w700, color: Toy.ink))),
        ),
      ]),
    );
  }
}
