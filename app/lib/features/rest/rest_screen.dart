import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/train.dart';
import '../../app/widgets.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';
import '../parent/parent_gate.dart';

/// The play time is up (docs/design.md 「每次玩多久」): the train is in the
/// station, the driver dozes, night falls, and the child is sent off to look
/// for things at home: 「換你去做了！去找找家裡的ㄅ吧！」 Only a parent
/// (through the gate) or an hour's wait lets play go on.
class RestScreen extends ConsumerStatefulWidget {
  const RestScreen({super.key});

  @override
  ConsumerState<RestScreen> createState() => _RestScreenState();
}

class _RestScreenState extends ConsumerState<RestScreen> {
  late final String _sym = () {
    final b = ref.read(bookProvider);
    return ref.read(gameProvider).taskFor(b, ref.read(clockProvider)()).sym;
  }();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      sfx(ref, 'night');
      speak(ref, '${Strings.restTitle}，${Strings.restLine(_sym).replaceAll('\n', '')}');
    });
  }

  Future<void> _parent() async {
    if (!await showParentGate(context) || !mounted) return;
    ref.read(gameProvider.notifier).change((g) => g.playOn());
    ref.read(sessionStartProvider.notifier).restart();
    context.go('/');
  }

  @override
  Widget build(BuildContext context) {
    final b = ref.watch(bookProvider);
    final g = ref.watch(gameProvider);
    final order = g.settings.order;
    final cars = [for (final s in b.all(order)) if (g.of(s).seen) s].take(2).toList();
    return WithMusic(
      music: Music.rest,
      child: Scaffold(
        body: DecoratedBox(
          decoration: const BoxDecoration(gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [Toy.night1, Toy.night2])),
          child: SafeArea(
            child: LayoutBuilder(builder: (context, box) {
              final w = math.min(box.maxWidth, 600.0);
              return Center(
                child: SizedBox(
                  width: w,
                  child: Stack(children: [
                    for (final (x, y, s) in [(.1, .06, 22.0), (.32, .14, 16.0), (.55, .05, 18.0), (.12, .3, 14.0), (.62, .24, 14.0), (.9, .36, 18.0)])
                      Positioned(left: w * x, top: box.maxHeight * y, width: s, height: s, child: Bob(amount: 2, phase: x, child: const Art('home/star'))),
                    Positioned(right: w * .06, top: 18, width: w * .22, height: w * .22, child: const Art('home/moon')),
                    Positioned(
                      left: 24,
                      right: 24,
                      top: box.maxHeight * .2,
                      child: Container(
                        padding: const EdgeInsets.fromLTRB(20, 16, 20, 16),
                        decoration: toyBox(Toy.paper, radius: 26),
                        child: Column(children: [
                          const Text(Strings.restTitle, style: TextStyle(fontSize: 28, fontWeight: FontWeight.w700, color: Toy.ink)),
                          const SizedBox(height: 8),
                          Text(Strings.restLine(_sym), textAlign: TextAlign.center, style: const TextStyle(fontSize: 22, height: 1.5, color: Toy.ink)),
                        ]),
                      ),
                    ),
                    Positioned(left: w * .1, right: w * .1, bottom: box.maxHeight * .2, height: w * .55, child: const Opacity(opacity: .92, child: Art('train/station'))),
                    Positioned(
                      left: 0,
                      right: 0,
                      bottom: box.maxHeight * .1,
                      child: OnTrack(
                        track: 16,
                        child: Row(mainAxisAlignment: MainAxisAlignment.center, crossAxisAlignment: CrossAxisAlignment.end, children: [
                          for (final s in cars) Carriage(station: b.stationOf(s, order), sym: s, width: w * .2),
                          Stack(clipBehavior: Clip.none, children: [
                            Locomotive(width: w * .32),
                            Positioned(left: w * .02, top: -w * .08, child: Text('Z z z', style: TextStyle(fontSize: w * .05, fontWeight: FontWeight.w700, color: Colors.white.withValues(alpha: .85)))),
                          ]),
                        ]),
                      ),
                    ),
                    Positioned(
                      right: 18,
                      bottom: 16,
                      child: Semantics(
                        container: true,
                        button: true,
                        label: Strings.parent,
                        excludeSemantics: true,
                        onTap: _parent,
                        child: Pressable(
                          onTap: _parent,
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                            decoration: toyBox(Colors.white.withValues(alpha: .9), radius: 22, shadow: false),
                            child: const Row(mainAxisSize: MainAxisSize.min, children: [
                              Icon(Icons.lock_outline_rounded, color: Toy.inkSoft, size: 20),
                              SizedBox(width: 6),
                              Text(Strings.parent, style: TextStyle(fontSize: 16, color: Toy.inkSoft)),
                            ]),
                          ),
                        ),
                      ),
                    ),
                  ]),
                ),
              );
            }),
          ),
        ),
      ),
    );
  }
}
