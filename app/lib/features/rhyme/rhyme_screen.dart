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
import '../../core/providers.dart';
import '../../core/quiz.dart';
import '../../core/sounds.dart';
import '../common.dart';

/// 押韻接龍 (docs/design.md, training the ear): 「哪個是ㄇ開頭？」 and
/// 「哪兩個押韻？」 with three pictures; nothing to read. A right answer says
/// why and hooks a carriage on; a wrong one says both words again.
class RhymeScreen extends ConsumerStatefulWidget {
  const RhymeScreen({super.key});

  @override
  ConsumerState<RhymeScreen> createState() => _RhymeScreenState();
}

class _RhymeScreenState extends ConsumerState<RhymeScreen> with HushOnLeave {
  late final Bopomofo _b = ref.read(bookProvider);
  late final int _station;
  late List<RhymeQuestion> _qs;
  int _i = 0;
  final _picked = <Word>{};
  final _shake = <String, int>{};
  bool _solved = false, _firstTry = true, _done = false;
  final _won = <Word>[];
  int _party = 0;
  String _said = '';
  Later? _next;

  @override
  void initState() {
    super.initState();
    final g = ref.read(gameProvider);
    _station = g.playing(_b);
    _qs = rhymeRound(_b, g, _station, ref.read(randomProvider));
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) _ask();
    });
  }

  @override
  void dispose() {
    _next?.cancel();
    super.dispose();
  }

  RhymeQuestion get _q => _qs[_i];

  String get _question => switch (_q) {
        HeadQuestion(:final sym) => Strings.whichStarts(sym),
        PairQuestion() => Strings.whichRhyme,
      };

  void _ask() {
    final words = _q.options.map((w) => w.zh).join('、');
    setState(() => _said = _question);
    speak(ref, '$_question$words。');
  }

  void _tap(Word w) {
    if (_solved || _done) return;
    switch (_q) {
      case HeadQuestion(:final sym, :final right):
        if (w == right) {
          _right({w}, Strings.headRight(w.zh, sym));
        } else {
          _wrong([w], Strings.headWrong(w.zh, w.head, sym));
        }
      case PairQuestion(:final rhyme, :final right):
        if (_picked.contains(w)) {
          setState(() => _picked.remove(w));
          return;
        }
        if (_picked.isEmpty) {
          sfx(ref, 'pop');
          setState(() => _picked.add(w));
          speak(ref, w.zh);
          return;
        }
        final a = _picked.first;
        final pair = {a, w};
        if (right.containsAll(pair)) {
          _right(pair, Strings.pairRight(a.zh, w.zh, rhyme));
        } else {
          setState(() => _picked.clear());
          _wrong([a, w], Strings.pairWrong(a.zh, w.zh));
        }
    }
  }

  void _right(Set<Word> words, String line) {
    ref.read(gameProvider.notifier).change((g) => g.rhymeAnswer(_firstTry));
    setState(() {
      _solved = true;
      _picked
        ..clear()
        ..addAll(words);
      _won.addAll(words.take(1));
      _said = line;
    });
    sfx(ref, 'right');
    sfx(ref, 'couple');
    final said = speak(ref, line);
    _next = Later(const Duration(milliseconds: 2600), _advance, after: said);
  }

  void _wrong(List<Word> words, String line) {
    _firstTry = false;
    setState(() {
      for (final w in words) {
        _shake[w.id] = (_shake[w.id] ?? 0) + 1;
      }
      _said = line;
    });
    sfx(ref, 'try');
    speak(ref, line);
  }

  void _advance() {
    if (!mounted) return;
    if (_i + 1 >= _qs.length) {
      final now = ref.read(clockProvider)();
      ref.read(gameProvider.notifier).change((g) => g.rhymeRound(_station).did(now, Module.rhyme));
      setState(() {
        _done = true;
        _party++;
      });
      sfx(ref, 'whistle');
      speak(ref, Strings.rhymeDone);
      return;
    }
    setState(() {
      _i++;
      _solved = false;
      _firstTry = true;
      _picked.clear();
      _shake.clear();
    });
    _ask();
  }

  void _restart() {
    setState(() {
      _qs = rhymeRound(_b, ref.read(gameProvider), _station, ref.read(randomProvider));
      _i = 0;
      _solved = false;
      _firstTry = true;
      _done = false;
      _picked.clear();
      _shake.clear();
      _won.clear();
    });
    _ask();
  }

  @override
  Widget build(BuildContext context) {
    final st = _b.stations[_station];
    final q = _q;
    return WithMusic(
      music: Music.rhyme,
      child: Scaffold(
        body: ToyBg(
          child: SafeArea(
            child: Stack(children: [
              Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 620),
                  child: Column(children: [
                    TopBar(title: Module.rhyme.zh, onHome: () => context.go('/'), station: st, onSpeak: _ask),
                    const SizedBox(height: 8),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: SizedBox(width: double.infinity, child: Bubble(text: _question, onTap: _ask, speaker: true, size: 22)),
                    ),
                    Expanded(
                      flex: 5,
                      child: LayoutBuilder(builder: (context, box) {
                        final size = math.min((box.maxWidth - 56) / 3, box.maxHeight * .8);
                        return Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [
                          for (final w in q.options)
                            Wiggle(
                              trigger: _shake[w.id] ?? 0,
                              amount: .12,
                              child: AnimatedScale(
                                duration: const Duration(milliseconds: 250),
                                scale: _picked.contains(w) ? 1.07 : 1,
                                child: WordCard(
                                  word: w,
                                  size: size,
                                  ring: _picked.contains(w) ? (_solved ? Toy.green : Toy.yellow) : null,
                                  faded: _solved && !_picked.contains(w),
                                  onTap: () => _tap(w),
                                ),
                              ),
                            ),
                        ]);
                      }),
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: AnimatedSwitcher(
                        duration: const Duration(milliseconds: 250),
                        child: Container(
                          key: ValueKey(_said),
                          width: double.infinity,
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                          decoration: toyBox(_solved ? const Color(0xFFE5F7DF) : Toy.paper, radius: 20, shadow: false),
                          child: Text(_said, textAlign: TextAlign.center, style: const TextStyle(fontSize: 19, fontWeight: FontWeight.w700, color: Toy.ink, height: 1.35)),
                        ),
                      ),
                    ),
                    Expanded(flex: 3, child: _train()),
                    Padding(padding: const EdgeInsets.only(bottom: 8), child: Text(Strings.questionNo(_i + 1, _qs.length), style: const TextStyle(fontSize: 14, color: Toy.inkSoft))),
                  ]),
                ),
              ),
              Positioned.fill(child: Confetti(trigger: _party)),
              if (_done) Positioned.fill(child: DonePanel(title: Strings.rhymeDone, actions: doneActions(context, ref, next: Module.find, again: _restart))),
            ]),
          ),
        ),
      ),
    );
  }

  /// The train grows a carriage for every right answer, the word riding on it.
  Widget _train() => LayoutBuilder(builder: (context, box) {
        final cw = math.min(78.0, box.maxHeight * .8);
        return TrainClock(
          period: 1600,
          builder: (context, t) => Align(
            alignment: Alignment.bottomCenter,
            child: OnTrack(
              track: 16,
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                reverse: true,
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: Row(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.end, children: [
                  for (final w in _won)
                    Padding(
                      padding: const EdgeInsets.only(right: 2),
                      child: Stack(clipBehavior: Clip.none, children: [
                        Carriage(station: 4, width: cw, spin: t),
                        Positioned(left: cw * .25, top: cw * .08, width: cw * .5, height: cw * .5, child: WordPicture(w, size: cw * .5)),
                      ]),
                    ),
                  Locomotive(width: cw * 1.45, t: t),
                ]),
              ),
            ),
          ),
        );
      });
}
