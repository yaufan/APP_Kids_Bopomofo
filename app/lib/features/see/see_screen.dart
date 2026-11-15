import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/train.dart';
import '../../app/widgets.dart';
import '../../core/book.dart';
import '../../core/game.dart';
import '../../core/lines.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';
import '../common.dart';

/// 認符號 (docs/design.md): a big carriage with the symbol and its word's
/// picture; tap to hear 「ㄅ，爸爸」. The station's symbols are below; once
/// every one was seen, its carriages go on the train.
class SeeScreen extends ConsumerStatefulWidget {
  const SeeScreen({super.key});

  @override
  ConsumerState<SeeScreen> createState() => _SeeScreenState();
}

class _SeeScreenState extends ConsumerState<SeeScreen> {
  late final Bopomofo _b = ref.read(bookProvider);
  late final int _station;
  late final List<String> _row;
  late String _sym;
  int _hop = 0, _wiggle = 0, _party = 0;
  bool _done = false;
  Timer? _panel;

  @override
  void initState() {
    super.initState();
    final g = ref.read(gameProvider);
    _station = g.playing(_b);
    _row = g.row(_b, _station);
    _sym = _row.firstWhere((s) => !g.of(s).seen, orElse: () => _row.first);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) _pick(_sym, first: true);
    });
  }

  @override
  void dispose() {
    _panel?.cancel();
    super.dispose();
  }

  String get _line => symbolLine(_b, _sym, twice: ref.read(gameProvider).settings.twice);

  void _pick(String s, {bool first = false}) {
    final before = ref.read(gameProvider).seenAll(_b, _station);
    setState(() {
      _sym = s;
      _hop++;
    });
    if (!first) sfx(ref, 'ding');
    speak(ref, _line);
    final game = ref.read(gameProvider.notifier);
    game.change((g) => g.saw(s));
    if (!before && ref.read(gameProvider).seenAll(_b, _station)) _allSeen();
  }

  void _again() {
    setState(() => _hop++);
    sfx(ref, 'ding');
    speak(ref, _line);
  }

  void _story() {
    setState(() => _wiggle++);
    sfx(ref, 'pop');
    speak(ref, _b.symbols[_sym]!.story);
  }

  /// Every carriage of the station was seen: they go on the train.
  void _allSeen() {
    ref.read(gameProvider.notifier).change((g) => g.did(ref.read(clockProvider)(), Module.see));
    _panel = Timer(const Duration(milliseconds: 1800), () {
      if (!mounted) return;
      setState(() {
        _done = true;
        _party++;
      });
      sfx(ref, 'couple');
      sfx(ref, 'whistle');
      speak(ref, Strings.seeAll);
    });
  }

  @override
  Widget build(BuildContext context) {
    final g = ref.watch(gameProvider);
    final st = _b.stations[_station];
    final z = _b.symbols[_sym]!;
    final word = _b.words[z.wordId]!;
    final big = g.settings.level == Level.big;
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
                    TopBar(title: Module.see.zh, onHome: () => context.go('/'), station: st, onSpeak: _again),
                    Expanded(
                      child: Padding(
                        padding: const EdgeInsets.fromLTRB(14, 8, 14, 6),
                        child: Container(
                          decoration: toyBox(Toy.paper, radius: 30),
                          child: LayoutBuilder(builder: (context, box) {
                            final cw = math.min(box.maxWidth * .58, box.maxHeight * .5);
                            return Stack(children: [
                              Positioned(
                                left: 16,
                                right: 16,
                                top: 14,
                                child: Align(alignment: Alignment.topLeft, child: Bubble(text: _line.replaceAll('。', '！'), onTap: _again, speaker: true, size: 20)),
                              ),
                              Positioned(
                                left: 10,
                                bottom: cw * .55,
                                width: math.min(box.maxWidth * .46, 230),
                                height: math.min(box.maxWidth * .46, 230),
                                child: Semantics(
                                  container: true,
                                  button: true,
                                  label: word.zh,
                                  excludeSemantics: true,
                                  onTap: _again,
                                  child: Pressable(onTap: _again, sound: null, child: Hop(trigger: _hop, height: 18, child: Wiggle(trigger: _hop, child: Art('words/${word.id}')))),
                                ),
                              ),
                              Positioned(
                                left: 0,
                                right: 0,
                                bottom: 10,
                                child: OnTrack(
                                  track: 18,
                                  child: Align(
                                    alignment: Alignment.bottomRight,
                                    child: Padding(
                                      padding: const EdgeInsets.only(right: 18),
                                      child: Semantics(
                                        key: const ValueKey('big-carriage'),
                                        container: true,
                                        button: true,
                                        label: '$_sym車廂',
                                        excludeSemantics: true,
                                        onTap: _again,
                                        child: Pressable(
                                          onTap: _again,
                                          sound: null,
                                          child: Wiggle(trigger: _wiggle, amount: .18, child: Hop(trigger: _hop, child: Carriage(station: _station, sym: _sym, width: cw))),
                                        ),
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                              if (big)
                                Positioned(
                                  right: 16,
                                  top: 80,
                                  child: PillButton(label: Strings.storyOf(_sym), color: Toy.purple, icon: Icons.auto_stories_rounded, height: 50, onTap: _story),
                                ),
                            ]);
                          }),
                        ),
                      ),
                    ),
                    Text('${st.name}站的車廂', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Toy.inkSoft)),
                    StationRow(syms: _row, station: _station, picked: _sym, onPick: _pick, done: (s) => g.of(s).seen, width: 70),
                    const Padding(padding: EdgeInsets.only(bottom: 8), child: Text(Strings.seeTap, style: TextStyle(fontSize: 14, color: Toy.inkSoft))),
                  ]),
                ),
              ),
              Positioned.fill(child: Confetti(trigger: _party)),
              if (_done)
                Positioned.fill(
                  child: DonePanel(
                    title: Strings.seeAll,
                    actions: doneActions(context, ref, next: Module.listen, again: () => setState(() => _done = false)),
                  ),
                ),
            ]),
          ),
        ),
      ),
    );
  }
}
