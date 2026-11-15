import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/game.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';

/// The first time: the child picks a driver by its look (no name to type).
class DriverScreen extends ConsumerStatefulWidget {
  const DriverScreen({super.key});

  @override
  ConsumerState<DriverScreen> createState() => _DriverScreenState();
}

class _DriverScreenState extends ConsumerState<DriverScreen> {
  Driver? _picked;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) speak(ref, Strings.pickDriver);
    });
  }

  void _pick(Driver d) {
    if (_picked != null) return;
    setState(() => _picked = d);
    sfx(ref, 'whistle');
    speak(ref, Strings.driverPicked(d));
    ref.read(gameProvider.notifier).change((g) => g.copyWith(driver: d));
    Future<void>.delayed(const Duration(milliseconds: 1600), () {
      if (mounted) context.go('/');
    });
  }

  @override
  Widget build(BuildContext context) => WithMusic(
        music: Music.station,
        child: Scaffold(
          body: ToyBg(
            child: SafeArea(
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 560),
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(children: [
                      const SizedBox(height: 10),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 8),
                        decoration: toyBox(Toy.paper, radius: 20),
                        child: const Text(Strings.appName, style: TextStyle(fontSize: 28, fontWeight: FontWeight.w700)),
                      ),
                      const SizedBox(height: 18),
                      const Bubble(text: Strings.pickDriver, size: 20),
                      const SizedBox(height: 18),
                      Expanded(
                        child: GridView.count(
                          crossAxisCount: 2,
                          mainAxisSpacing: 16,
                          crossAxisSpacing: 16,
                          childAspectRatio: .9,
                          physics: const NeverScrollableScrollPhysics(),
                          children: [
                            for (final d in Driver.values)
                              Semantics(
                                key: ValueKey('driver-${d.name}'),
                                container: true,
                                button: true,
                                label: d.zh,
                                excludeSemantics: true,
                                onTap: () => _pick(d),
                                child: Pressable(
                                  onTap: () => _pick(d),
                                  sound: null,
                                  child: AnimatedScale(
                                    duration: const Duration(milliseconds: 300),
                                    scale: _picked == d ? 1.08 : (_picked == null ? 1 : .9),
                                    child: Container(
                                      decoration: toyBox(_picked == d ? Toy.yellow : Toy.paper, radius: 28),
                                      padding: const EdgeInsets.all(10),
                                      child: Column(children: [
                                        Expanded(child: Bob(amount: 3, phase: d.index * .25, child: DriverView(driver: d, size: 150))),
                                        Text(d.zh, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w700)),
                                      ]),
                                    ),
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                    ]),
                  ),
                ),
              ),
            ),
          ),
        ),
      );
}
