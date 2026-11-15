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
import '../../core/quiz.dart';
import '../../core/sounds.dart';
import '../common.dart';

/// 聽聽找找 (docs/design.md): the app says a word; which carriage does it
/// start with (or, at 大火車 now and then, end with)? Right: the carriage
/// drives off with the word on board. Wrong: it shakes and the app says
/// which one that was; nothing is lost.
class ListenScreen extends ConsumerStatefulWidget {
  const ListenScreen({super.key});

  @override
  ConsumerState<ListenScreen> createState() => _ListenScreenState();
}

class _ListenScreenState extends ConsumerState<ListenScreen> {
  late final Bopomofo _b = ref.read(bookProvider);
  late final int _station;
  late List<ListenQuestion> _qs;
  int _i = 0;
  final _shake = <String, int>{};
  String? _gone;
  bool _done = false;
  int _hop = 0, _party = 0;
  Timer? _next;

  @override
  void initState() {
    super.initState();
    final g = ref.read(gameProvider);
    _station = g.playing(_b);
    _qs = listenRound(_b, g, _station, ref.read(randomProvider));
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) _ask();
    });
  }

  @override
  void dispose() {
    _next?.cancel();
    super.dispose();
  }

  ListenQuestion get _q => _qs[_i];

  bool get _small => ref.read(gameProvider).settings.level == Level.small;

  String _prompt(ListenQuestion q) => q.tail ? Strings.listenTail(q.word.zh, spell(q.word.keySyllable.$2)) : Strings.listenHead(q.word.zh);

  /// 小火車: the whole question every time; 大火車: once, then only the word.
  void _ask() {
    final first = ref.read(onceProvider).add('listen-howto');
    final q = _q;
    if (_small || first) {
      speak(ref, _prompt(q));
    } else {
      speak(ref, q.tail ? '${q.word.zh}，${spell(q.word.keySyllable.$2)}。' : '${q.word.zh}。');
    }
  }

  void _tap(String sym) {
    if (_gone != null || _done) return;
    final q = _q;
    if (sym == q.answer) {
      setState(() {
        _gone = sym;
        _hop++;
      });
      sfx(ref, 'right');
      sfx(ref, 'clack');
      speak(ref, q.tail ? Strings.listenRightTail(q.word.zh, sym) : Strings.listenRightHead(q.word.zh, sym));
      ref.read(gameProvider.notifier).change((g) => g.heard(sym));
      _next = Timer(const Duration(milliseconds: 2200), _advance);
    } else {
      setState(() => _shake[sym] = (_shake[sym] ?? 0) + 1);
      sfx(ref, 'try');
      speak(ref, '${thisIs(_b, sym)}${_prompt(q)}');
    }
  }

  void _advance() {
    if (!mounted) return;
    if (_i + 1 >= _qs.length) {
      ref.read(gameProvider.notifier).change((g) => g.did(ref.read(clockProvider)(), Module.listen));
      setState(() {
        _done = true;
        _party++;
      });
      sfx(ref, 'done');
      speak(ref, Strings.listenDone);
      return;
    }
    setState(() {
      _i++;
      _gone = null;
      _shake.clear();
    });
    _ask();
  }

  void _restart() {
    setState(() {
      _qs = listenRound(_b, ref.read(gameProvider), _station, ref.read(randomProvider));
      _i = 0;
      _gone = null;
      _done = false;
      _shake.clear();
    });
    _ask();
  }

  @override
  Widget build(BuildContext context) {
    final st = _b.stations[_station];
    final q = _q;
    final order = ref.watch(gameProvider.select((g) => g.settings.order));
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
                    TopBar(title: Module.listen.zh, onHome: () => context.go('/'), station: st, onSpeak: () => speak(ref, _prompt(q))),
                    Expanded(
                      flex: 5,
                      child: Padding(
                        padding: const EdgeInsets.fromLTRB(14, 8, 14, 6),
                        child: Container(
                          decoration: toyBox(Toy.paper, radius: 30),
                          padding: const EdgeInsets.all(14),
                          child: LayoutBuilder(builder: (context, box) {
                            final pic = math.min(box.maxHeight * .72, box.maxWidth * .48);
                            return Row(children: [
                              Expanded(
                                child: Semantics(
                                  container: true,
                                  button: true,
                                  label: Strings.again,
                                  excludeSemantics: true,
                                  onTap: () => speak(ref, _prompt(q)),
                                  child: Pressable(
                                    onTap: () => speak(ref, _prompt(q)),
                                    sound: null,
                                    child: Bob(amount: 3, period: 1600, child: SizedBox(height: pic * .7, child: const Art('icons/speaker'))),
                                  ),
                                ),
                              ),
                              Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                                Bubble(text: q.tail ? '${q.word.zh}（${spell(q.word.keySyllable.$2)}）' : q.word.zh, size: 22),
                                const SizedBox(height: 6),
                                Hop(trigger: _hop, height: 30, child: WordPicture(q.word, size: pic * .82)),
                              ]),
                            ]);
                          }),
                        ),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Text(q.tail ? '${q.word.zh}的尾巴是哪一節車廂？' : '${q.word.zh}的開頭是哪一節車廂？',
                          textAlign: TextAlign.center, style: const TextStyle(fontSize: 21, fontWeight: FontWeight.w700, color: Toy.ink)),
                    ),
                    Expanded(
                      flex: 4,
                      child: LayoutBuilder(builder: (context, box) {
                        final n = q.options.length;
                        final cw = math.min((box.maxWidth - 40) / n - 8, 150.0);
                        return TrainClock(
                          period: 1400,
                          builder: (context, t) => Align(
                            alignment: Alignment.center,
                            child: OnTrack(
                              track: 18,
                              child: Row(key: ValueKey('q$_i'), mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [
                                for (final s in q.options)
                                  AnimatedSlide(
                                    duration: const Duration(milliseconds: 1500),
                                    curve: Curves.easeIn,
                                    offset: Offset(_gone == s ? 4 : 0, 0),
                                    child: Semantics(
                                      key: ValueKey('option-$s'),
                                      container: true,
                                      button: true,
                                      label: s,
                                      excludeSemantics: true,
                                      onTap: () => _tap(s),
                                      child: Pressable(
                                        onTap: () => _tap(s),
                                        sound: null,
                                        child: Wiggle(
                                          trigger: _shake[s] ?? 0,
                                          amount: .14,
                                          child: Stack(clipBehavior: Clip.none, children: [
                                            Carriage(station: _b.stationOf(s, order), sym: s, width: cw, spin: _gone == s ? t * 3 : 0),
                                            if (_gone == s) Positioned(left: cw * .3, top: -cw * .45, width: cw * .4, height: cw * .4, child: WordPicture(q.word, size: cw * .4)),
                                          ]),
                                        ),
                                      ),
                                    ),
                                  ),
                              ]),
                            ),
                          ),
                        );
                      }),
                    ),
                    Padding(
                      padding: const EdgeInsets.only(bottom: 6),
                      child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                        for (var k = 0; k < _qs.length; k++)
                          Container(
                            width: 16,
                            height: 16,
                            margin: const EdgeInsets.all(3),
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: k < _i || (k == _i && _gone != null) ? Toy.green : (k == _i ? Toy.yellow : Colors.white),
                              border: Border.all(color: Toy.line, width: 2),
                            ),
                          ),
                      ]),
                    ),
                    Padding(padding: const EdgeInsets.only(bottom: 8), child: Text(Strings.questionNo(_i + 1, _qs.length), style: const TextStyle(fontSize: 14, color: Toy.inkSoft))),
                  ]),
                ),
              ),
              Positioned.fill(child: Confetti(trigger: _party)),
              if (_done) Positioned.fill(child: DonePanel(title: Strings.listenDone, actions: doneActions(context, ref, next: Module.write, again: _restart))),
            ]),
          ),
        ),
      ),
    );
  }
}
