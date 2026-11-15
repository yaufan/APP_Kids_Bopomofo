import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/book.dart';
import '../../core/game.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';

/// 家裡找找 (docs/design.md, away from the screen): today's card asks for
/// things at home with a sound; on purpose nothing here can be tapped but a
/// big 「找到了！」, then a sticker for the locomotive.
class FindScreen extends ConsumerStatefulWidget {
  const FindScreen({super.key});

  @override
  ConsumerState<FindScreen> createState() => _FindScreenState();
}

class _FindScreenState extends ConsumerState<FindScreen> {
  late final Bopomofo _b = ref.read(bookProvider);
  bool _choosing = false;
  int _party = 0;
  Timer? _home;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      final now = ref.read(clockProvider)();
      ref.read(gameProvider.notifier).change((g) => g.giveTask(_b, now).did(now, Module.find));
      final t = ref.read(gameProvider).taskFor(_b, ref.read(clockProvider)());
      speak(ref, t.found != null ? Strings.foundToday : '${Strings.findHello}${_line(t.sym)}');
    });
  }

  @override
  void dispose() {
    _home?.cancel();
    super.dispose();
  }

  String _line(String sym) => Strings.findSay(sym, Bopomofo.isInitial(sym));

  void _found() {
    sfx(ref, 'right');
    setState(() => _choosing = true);
    speak(ref, Strings.pickSticker);
  }

  void _sticker(Word w) {
    final now = ref.read(clockProvider)();
    ref.read(gameProvider.notifier).change((g) => g.found(_b, now, w.id));
    sfx(ref, 'sticker');
    sfx(ref, 'whistle');
    speak(ref, Strings.stickerOn);
    setState(() {
      _choosing = false;
      _party++;
    });
    _home = Timer(const Duration(milliseconds: 2600), () {
      if (mounted) context.go('/');
    });
  }

  @override
  Widget build(BuildContext context) {
    final g = ref.watch(gameProvider);
    final now = ref.read(clockProvider)();
    final t = g.taskFor(_b, now);
    final z = _b.symbols[t.sym]!;
    final hints = [for (final h in z.hints.take(3)) _b.words[h]!];
    final st = _b.stations[_b.stationOf(t.sym, g.settings.order)];
    final initial = Bopomofo.isInitial(t.sym);
    return WithMusic(
      music: Music.station,
      child: Scaffold(
        body: ToyBg(
          child: SafeArea(
            child: Stack(children: [
              Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 620),
                  child: Column(children: [
                    TopBar(title: Module.find.zh, onHome: () => context.go('/'), station: st, onSpeak: () => speak(ref, _line(t.sym))),
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 6, 16, 0),
                      child: DriverSays(text: t.found != null ? Strings.foundToday : Strings.findHello, size: 84, right: false, onTap: () => speak(ref, _line(t.sym))),
                    ),
                    Expanded(
                      child: Padding(
                        padding: const EdgeInsets.fromLTRB(18, 14, 18, 10),
                        child: Stack(clipBehavior: Clip.none, children: [
                          Positioned.fill(
                            child: Container(
                              decoration: toyBox(Toy.paper, radius: 30),
                              padding: const EdgeInsets.fromLTRB(18, 26, 18, 18),
                              child: LayoutBuilder(builder: (context, box) {
                                final pic = (box.maxWidth - 40) / 3;
                                return Column(children: [
                                  const Text(Strings.findLook, style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700, color: Toy.ink)),
                                  const SizedBox(height: 4),
                                  Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                                    if (!initial) const Text(Strings.findSoundBefore, style: TextStyle(fontSize: 26, fontWeight: FontWeight.w700, color: Toy.red)),
                                    Container(
                                      width: 56,
                                      height: 56,
                                      margin: const EdgeInsets.symmetric(horizontal: 6),
                                      alignment: Alignment.center,
                                      decoration: toyBox(st.color, radius: 16),
                                      child: Text(t.sym, textScaler: TextScaler.noScaling, style: const TextStyle(fontSize: 36, fontWeight: FontWeight.w700, color: Toy.ink)),
                                    ),
                                    Flexible(
                                      child: Text(initial ? Strings.findStartAfter : Strings.findSoundAfter, style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w700, color: Toy.red)),
                                    ),
                                  ]),
                                  const Spacer(),
                                  Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [
                                    for (final w in hints)
                                      Column(children: [
                                        WordPicture(w, size: pic * 1.0),
                                        Text(w.zh, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: Toy.ink)),
                                      ]),
                                  ]),
                                  const Spacer(),
                                  const Text(Strings.findTogether, textAlign: TextAlign.center, style: TextStyle(fontSize: 15, color: Toy.inkSoft, height: 1.45)),
                                  const SizedBox(height: 12),
                                  if (t.found == null)
                                    PillButton(label: Strings.found, color: Toy.green, icon: Icons.check_rounded, height: 66, expand: true, sound: null, onTap: _found)
                                  else
                                    Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                                      const SizedBox(width: 36, height: 36, child: Art('icons/star')),
                                      const SizedBox(width: 8),
                                      WordPicture(_b.words[t.found]!, size: 56),
                                    ]),
                                ]);
                              }),
                            ),
                          ),
                          // The pin holding the card up.
                          Positioned(top: -10, left: 0, right: 0, child: Center(child: Container(width: 22, height: 22, decoration: toyBox(Toy.red, radius: 11)))),
                        ]),
                      ),
                    ),
                  ]),
                ),
              ),
              if (_choosing)
                Positioned.fill(
                  child: Container(
                    color: Toy.ink.withValues(alpha: .35),
                    alignment: Alignment.center,
                    padding: const EdgeInsets.all(20),
                    child: Container(
                      constraints: const BoxConstraints(maxWidth: 480),
                      padding: const EdgeInsets.all(18),
                      decoration: toyBox(Toy.paper, radius: 30),
                      child: Column(mainAxisSize: MainAxisSize.min, children: [
                        const Text(Strings.pickSticker, textAlign: TextAlign.center, style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700)),
                        const SizedBox(height: 14),
                        Wrap(alignment: WrapAlignment.center, spacing: 12, runSpacing: 12, children: [
                          for (final h in z.hints) WordCard(word: _b.words[h]!, size: 104, onTap: () => _sticker(_b.words[h]!)),
                        ]),
                      ]),
                    ),
                  ),
                ),
              Positioned.fill(child: Confetti(trigger: _party)),
            ]),
          ),
        ),
      ),
    );
  }
}
