import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/book.dart';
import '../../core/game.dart';
import '../../core/lines.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';
import '../../core/writing.dart';
import '../common.dart';
import 'write_painter.dart';

/// 寫寫看 (docs/design.md): write a symbol on a carriage in three steps,
/// as 字母寵物 does: watch it written (in order, numbered), tap where each
/// stroke starts, then trace along wide roads from the green dot. The
/// finger draws the moment it touches (raw pointer events).
class WriteScreen extends ConsumerStatefulWidget {
  const WriteScreen({super.key, this.sym});

  final String? sym;

  @override
  ConsumerState<WriteScreen> createState() => _WriteScreenState();
}

class _WriteScreenState extends ConsumerState<WriteScreen> with SingleTickerProviderStateMixin {
  late final Bopomofo _b = ref.read(bookProvider);
  late final Ticker _ticker;
  final _clock = ValueNotifier<double>(0);
  double get _t => _clock.value;

  late final int _station;
  late final List<String> _row;
  late String _sym;
  var _step = WriteStep.watch;
  double _watchStart = 0;
  int _tapped = 0;
  List<Tracer> _tracers = [];
  int _current = 0;
  bool _finished = false, _done = false;
  int _party = 0;
  String? _say;
  double _lastNudge = -10;
  Size _page = Size.zero;
  int? _pointer;
  Timer? _next;
  late final Sounds _sounds = ref.read(soundsProvider);

  @override
  void initState() {
    super.initState();
    final g = ref.read(gameProvider);
    _station = g.playing(_b);
    _row = g.row(_b, _station);
    final asked = widget.sym;
    _sym = asked != null && _b.symbols.containsKey(asked) ? asked : _row.firstWhere((s) => !g.of(s).traced, orElse: () => _row.first);
    _ticker = createTicker((e) {
      _clock.value = e.inMicroseconds / 1e6;
      if (_step == WriteStep.watch && !_finished && _watched >= _strokes.length + .3 && _next == null) {
        _next = Timer(const Duration(milliseconds: 700), () => _go(WriteStep.tap));
      }
    })
      ..start();
    WidgetsBinding.instance.addPostFrameCallback((_) => _go(WriteStep.watch, first: true));
  }

  @override
  void dispose() {
    _ticker.dispose();
    _clock.dispose();
    _next?.cancel();
    super.dispose();
  }

  List<List<Offset>> get _strokes => _b.symbols[_sym]!.strokes;

  double get _watched => (_t - _watchStart) / .9;

  void _go(WriteStep step, {bool first = false}) {
    if (!mounted) return;
    _next?.cancel();
    _next = null;
    setState(() {
      _step = step;
      _finished = false;
      _current = 0;
      switch (step) {
        case WriteStep.watch:
          _watchStart = _t;
        case WriteStep.tap:
          _tapped = 0;
        case WriteStep.trace:
          _tracers = [for (final s in _strokes) Tracer(s)];
      }
    });
    final line = switch (step) {
      WriteStep.watch => '${first ? symbolLine(_b, _sym) : ''}${Strings.watch(_sym)}',
      WriteStep.tap => Strings.tapStars,
      WriteStep.trace => Strings.traceRoad,
    };
    _bubble(step == WriteStep.watch ? Strings.watch(_sym) : line);
    speak(ref, line);
  }

  void _bubble(String s) => setState(() => _say = s);

  void _pick(String s) {
    if (s == _sym) return;
    sfx(ref, 'ding');
    setState(() => _sym = s);
    _go(WriteStep.watch, first: true);
  }

  // --- The finger on the page ---------------------------------------------

  BoxFit100 get _fit => BoxFit100(_page);

  void _down(PointerDownEvent e) {
    if (_pointer != null || _finished) return; // one finger; no palms
    _pointer = e.pointer;
    final p = _fit.toBox(e.localPosition);
    switch (_step) {
      case WriteStep.watch:
        break;
      case WriteStep.tap:
        if ((p - _strokes[_tapped].first).distance < 22) {
          _sounds.play('star');
          setState(() => _tapped++);
          if (_tapped == _strokes.length) _next = Timer(const Duration(milliseconds: 600), () => _go(WriteStep.trace));
        } else {
          _nudge(Strings.startAtStar);
        }
      case WriteStep.trace:
        if (_current >= _tracers.length) return;
        if (!_tracers[_current].down(p)) _nudge(_tracers[_current].progress == 0 ? Strings.startAtDot : Strings.backOnRoad);
        setState(() {});
    }
  }

  void _move(PointerMoveEvent e) {
    if (e.pointer != _pointer || _step != WriteStep.trace || _current >= _tracers.length || _finished) return;
    final tr = _tracers[_current];
    tr.move(_fit.toBox(e.localPosition));
    if (tr.offRoad) _nudge(Strings.backOnRoad);
    if (tr.done) _strokeTraced();
    setState(() {});
  }

  void _up(PointerEvent e) {
    if (e.pointer != _pointer) return;
    _pointer = null;
    if (_step == WriteStep.trace && _current < _tracers.length) _tracers[_current].up();
  }

  void _nudge(String s) {
    if (_t - _lastNudge < 2.5) return;
    _lastNudge = _t;
    _sounds.play('try');
    _bubble(s);
    speak(ref, s);
  }

  void _strokeTraced() {
    _tracers[_current].up();
    _current++;
    if (_current < _tracers.length) {
      _sounds.play('stroke');
      return;
    }
    _finished = true;
    _sounds.play('done');
    final sym = _sym;
    final game = ref.read(gameProvider.notifier);
    game.change((g) => g.traced(sym));
    final line = Strings.traced(symbolLine(_b, sym));
    _bubble(Strings.traced(''));
    speak(ref, line);
    setState(() => _party++);
    final g = ref.read(gameProvider);
    if (g.tracedAll(_b, _station)) {
      game.change((g) => g.did(ref.read(clockProvider)(), Module.write));
      _next = Timer(const Duration(milliseconds: 2400), () {
        if (!mounted) return;
        setState(() => _done = true);
        speak(ref, Strings.writeDone);
      });
      return;
    }
    final nextSym = _row.firstWhere((s) => !g.of(s).traced, orElse: () => _row.first);
    _next = Timer(const Duration(milliseconds: 2600), () {
      if (!mounted) return;
      setState(() => _sym = nextSym);
      _go(WriteStep.watch, first: true);
    });
  }

  @override
  Widget build(BuildContext context) {
    final g = ref.watch(gameProvider);
    final st = _b.stations[_station];
    final left = g.settings.leftHanded;
    return WithMusic(
      music: Music.write,
      child: Scaffold(
        body: ToyBg(
          child: SafeArea(
            child: Stack(children: [
              Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 620),
                  child: Column(children: [
                    TopBar(title: Module.write.zh, onHome: () => context.go('/'), station: st, onSpeak: () => speak(ref, symbolLine(_b, _sym))),
                    Padding(
                      padding: const EdgeInsets.only(top: 6, bottom: 4),
                      child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                        for (final s in WriteStep.values) _StepChip(step: s, on: s == _step, onTap: () => _go(s)),
                      ]),
                    ),
                    Expanded(
                      child: Padding(
                        padding: const EdgeInsets.fromLTRB(22, 6, 22, 6),
                        child: Center(
                          child: AspectRatio(
                            aspectRatio: .92,
                            child: Container(
                              decoration: toyBox(st.color, radius: 34),
                              padding: const EdgeInsets.fromLTRB(16, 16, 16, 22),
                              child: Container(
                                decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(24), border: Border.all(color: Toy.rim(st.color).withValues(alpha: .6), width: 2.5)),
                                child: LayoutBuilder(builder: (context, box) {
                                  _page = box.biggest;
                                  return Listener(
                                    behavior: HitTestBehavior.opaque,
                                    onPointerDown: _down,
                                    onPointerMove: _move,
                                    onPointerUp: _up,
                                    onPointerCancel: _up,
                                    child: ValueListenableBuilder<double>(
                                      valueListenable: _clock,
                                      builder: (context, t, _) => CustomPaint(
                                        key: const ValueKey('page'),
                                        size: box.biggest,
                                        painter: WritePainter(
                                          strokes: _strokes,
                                          step: _step,
                                          t: t,
                                          watched: _watched,
                                          tapped: _tapped,
                                          tracers: _tracers,
                                          current: _current,
                                          leftHanded: left,
                                        ),
                                      ),
                                    ),
                                  );
                                }),
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 14),
                      child: Row(children: [
                        Expanded(child: DriverSays(text: _say ?? Strings.watch(_sym), size: 62, right: false, onTap: () => speak(ref, _say ?? Strings.watch(_sym)))),
                        if (_step == WriteStep.watch) RoundButton(label: Strings.watchAgain, icon: Icons.replay_rounded, color: Toy.blue, onTap: () => _go(WriteStep.watch)),
                      ]),
                    ),
                    Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Text(Strings.strokeNo(_step == WriteStep.trace ? (_current + 1).clamp(1, _strokes.length) : _strokes.length, _strokes.length),
                          style: const TextStyle(fontSize: 14, color: Toy.inkSoft)),
                    ),
                    StationRow(syms: _row, station: _station, picked: _sym, onPick: _pick, done: (s) => g.of(s).traced, width: 58),
                    const SizedBox(height: 6),
                  ]),
                ),
              ),
              Positioned.fill(child: Confetti(trigger: _party)),
              if (_done)
                Positioned.fill(
                  child: DonePanel(
                    title: Strings.writeDone,
                    actions: doneActions(context, ref, next: Module.rhyme, again: () {
                      setState(() => _done = false);
                      _go(WriteStep.watch, first: true);
                    }),
                  ),
                ),
            ]),
          ),
        ),
      ),
    );
  }
}

class _StepChip extends StatelessWidget {
  const _StepChip({required this.step, required this.on, required this.onTap});

  final WriteStep step;
  final bool on;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final label = switch (step) {
      WriteStep.watch => Strings.stepWatch,
      WriteStep.tap => Strings.stepTap,
      WriteStep.trace => Strings.stepTrace,
    };
    final color = switch (step) {
      WriteStep.watch => Toy.mint,
      WriteStep.tap => Toy.sky,
      WriteStep.trace => Toy.yellow,
    };
    return Semantics(
      key: ValueKey('step-${step.name}'),
      container: true,
      button: true,
      selected: on,
      label: label,
      excludeSemantics: true,
      child: Pressable(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          width: on ? 72 : 58,
          height: on ? 48 : 40,
          margin: const EdgeInsets.symmetric(horizontal: 6),
          alignment: Alignment.center,
          decoration: toyBox(on ? color : Colors.white, radius: 24, shadow: on),
          child: Text(label, style: TextStyle(fontSize: on ? 24 : 19, fontWeight: FontWeight.w700, color: on ? Toy.ink : Toy.inkSoft)),
        ),
      ),
    );
  }
}
