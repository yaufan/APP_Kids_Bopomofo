import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/map_layout.dart';
import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/train.dart';
import '../../app/widgets.dart';
import '../../core/book.dart';
import '../../core/game.dart';
import '../../core/lines.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';
import '../parent/parent_gate.dart';

/// The station (docs/design.md 「火車站」): the map of Taiwan with the train
/// at its station, the child's own train, and the big buttons.
class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> with SingleTickerProviderStateMixin {
  late final _drive = AnimationController(vsync: this, duration: const Duration(milliseconds: 2600));
  int _from = 0, _to = 0;
  int _toot = 0;

  Bopomofo get _b => ref.read(bookProvider);

  @override
  void initState() {
    super.initState();
    final g = ref.read(gameProvider);
    _from = _to = g.current(_b);
    WidgetsBinding.instance.addPostFrameCallback((_) => _arrive());
  }

  @override
  void dispose() {
    _drive.dispose();
    super.dispose();
  }

  /// The train drives to a new station when one was passed (or a parent jumped).
  void _arrive() {
    if (!mounted) return;
    final g = ref.read(gameProvider);
    final cur = g.current(_b), was = g.arrivedAt();
    final once = ref.read(onceProvider);
    if (cur > was) {
      setState(() {
        _from = was;
        _to = cur;
      });
      sfx(ref, 'whistle');
      sfx(ref, 'clack');
      _drive.forward(from: 0).whenComplete(() {
        if (!mounted) return;
        sfx(ref, 'chime');
        speak(ref, Strings.arrived(_b.stations[cur].name));
      });
      ref.read(gameProvider.notifier).change((g) => g.arrive(cur).copyWith(clearAt: true));
      once.add('hello');
      return;
    }
    if (cur != was) ref.read(gameProvider.notifier).change((g) => g.arrive(cur));
    _drive.value = 1;
    if (once.add('hello')) speak(ref, Strings.hello(_b.stations[g.playing(_b)].name));
  }

  void _open(Module m) {
    final s = ref.read(gameProvider).settings;
    if (!s.open(m)) {
      sfx(ref, 'try');
      speak(ref, Strings.locked);
      return;
    }
    context.go('/${m.name}');
  }

  void _station(int i) {
    final g = ref.read(gameProvider);
    if (!g.settings.unlocked(i)) {
      sfx(ref, 'try');
      speak(ref, Strings.lockedStation);
    } else if (g.reachable(_b, i)) {
      sfx(ref, 'chime');
      ref.read(gameProvider.notifier).change((g) => g.playAt(i));
      speak(ref, Strings.goStation(_b.stations[i].name));
    } else {
      sfx(ref, 'try');
      speak(ref, Strings.notYet);
    }
  }

  void _loco() {
    setState(() => _toot++);
    sfx(ref, 'whistle');
    sfx(ref, 'puff');
    speak(ref, Strings.choo);
  }

  Future<void> _parent() async {
    if (!await showParentGate(context) || !mounted) return;
    context.go('/parent');
  }

  @override
  Widget build(BuildContext context) {
    final g = ref.watch(gameProvider);
    final b = ref.watch(bookProvider);
    final now = ref.read(clockProvider)();
    final playing = g.playing(b);
    final station = b.stations[playing];
    final small = g.settings.level == Level.small;
    final taskReady = g.settings.full && !g.taskGiven(now) && g.log(now).modules.isNotEmpty;
    return WithMusic(
      music: Music.station,
      child: Scaffold(
        body: ToyBg(
          hills: false,
          child: SafeArea(
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 620),
                child: LayoutBuilder(builder: (context, box) {
                  final mapH = (box.maxHeight * .36).clamp(220.0, 420.0);
                  final btn = math.min((box.maxWidth - 32 - 24) / 3, 150.0);
                  return Column(children: [
                    _bar(),
                    Padding(padding: const EdgeInsets.symmetric(horizontal: 14), child: SizedBox(height: mapH, child: _map(g, b, playing, station, mapH))),
                    const SizedBox(height: 8),
                    SizedBox(height: 112, child: _train(g, b, playing)),
                    const Spacer(),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Wrap(alignment: WrapAlignment.center, spacing: 12, runSpacing: 12, children: [
                        _button(g, b, playing, Module.see, Toy.blue, 'see', btn),
                        _button(g, b, playing, Module.listen, Toy.orange, 'listen', btn),
                        if (!small) _spell(btn),
                        _button(g, b, playing, Module.write, Toy.green, 'write', btn),
                        _button(g, b, playing, Module.rhyme, Toy.pink, 'rhyme', btn),
                        _button(g, b, playing, Module.find, Toy.yellow, 'find', btn, glow: taskReady),
                      ]),
                    ),
                    const Spacer(),
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 0, 12, 10),
                      child: Align(
                        alignment: Alignment.centerRight,
                        child: DriverSays(
                          text: taskReady ? Strings.taskReady : Strings.whatToPlay,
                          size: 74,
                          onTap: () => taskReady ? context.go('/find') : speak(ref, Strings.hello(station.name)),
                        ),
                      ),
                    ),
                  ]);
                }),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _bar() => Padding(
        padding: const EdgeInsets.fromLTRB(12, 6, 12, 6),
        child: Row(children: [
          Semantics(
            container: true,
            button: true,
            label: Strings.parent,
            excludeSemantics: true,
            onTap: _parent,
            child: Pressable(
              onTap: _parent,
              child: Container(width: 46, height: 46, padding: const EdgeInsets.all(7), decoration: toyBox(Toy.paper, radius: 23), child: const Art('icons/lock')),
            ),
          ),
          Expanded(
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 6),
                decoration: toyBox(Toy.paper, radius: 18),
                child: const Text(Strings.appName, style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700, color: Toy.ink)),
              ),
            ),
          ),
          const SizedBox(width: 46),
        ]),
      );

  Widget _map(Game g, Bopomofo b, int playing, Station station, double h) {
    final mapW = (h - 12) * mapAspect;
    final row = g.row(b, playing);
    final seen = b.all(g.settings.order).where((s) => g.of(s).seen).length;
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [Toy.sea1, Toy.sea2]),
        borderRadius: BorderRadius.circular(26),
        border: Border.all(color: Toy.rim(Toy.sea2), width: 2.5),
        boxShadow: [BoxShadow(color: Toy.ink.withValues(alpha: .16), offset: const Offset(3, 4))],
      ),
      child: Row(children: [
        Expanded(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 14, 4, 12),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(Strings.stationNo(playing), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Colors.white)),
              const SizedBox(height: 2),
              FittedBox(
                child: Text(station.name,
                    style: TextStyle(fontSize: 40, fontWeight: FontWeight.w700, color: Colors.white, shadows: [Shadow(color: Toy.ink.withValues(alpha: .45), offset: const Offset(0, 2.5))])),
              ),
              const SizedBox(height: 8),
              Wrap(spacing: 4, runSpacing: 4, children: [
                for (final s in row)
                  Container(
                    width: 30,
                    height: 30,
                    alignment: Alignment.center,
                    decoration: toyBox(g.of(s).seen ? station.color : Colors.white, radius: 9, shadow: false, rim: 1.5),
                    child: Text(s, textScaler: TextScaler.noScaling, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Toy.ink)),
                  ),
              ]),
              const Spacer(),
              Text(Strings.myTrain(seen), style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Colors.white)),
            ]),
          ),
        ),
        SizedBox(
          width: mapW,
          height: h - 12,
          child: AnimatedBuilder(
            animation: _drive,
            builder: (context, _) => Stack(clipBehavior: Clip.none, children: [
              const Positioned.fill(child: Art('map/taiwan')),
              for (var i = 0; i < mapStations.length; i++) _stationDot(g, b, i, mapW, h - 12, playing),
              _trainMarker(mapW, h - 12),
            ]),
          ),
        ),
        const SizedBox(width: 8),
      ]),
    );
  }

  Widget _stationDot(Game g, Bopomofo b, int i, double w, double h, int playing) {
    final (fx, fy) = mapStations[i];
    final st = b.stations[i];
    final on = g.enabled(i);
    final passed = g.passed(b, i);
    final locked = !g.settings.unlocked(i);
    const r = 13.0;
    return Positioned(
      left: fx * w - r,
      top: fy * h - r,
      width: r * 2,
      height: r * 2,
      child: Semantics(
        key: ValueKey('station-$i'),
        container: true,
        button: true,
        label: '${st.name}站',
        excludeSemantics: true,
        onTap: () => _station(i),
        child: Pressable(
          onTap: () => _station(i),
          sound: null,
          child: Stack(clipBehavior: Clip.none, children: [
            Container(
              decoration: BoxDecoration(
                color: on ? st.color : const Color(0xFFD6D2DD),
                shape: BoxShape.circle,
                border: Border.all(color: i == playing ? Colors.white : Toy.rim(on ? st.color : const Color(0xFFD6D2DD)), width: i == playing ? 3.5 : 2),
                boxShadow: [BoxShadow(color: Toy.ink.withValues(alpha: .25), offset: const Offset(1.5, 2))],
              ),
              alignment: Alignment.center,
              child: locked ? const Icon(Icons.lock_rounded, size: 13, color: Toy.inkSoft) : Text('${i + 1}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Toy.ink)),
            ),
            if (passed) const Positioned(left: 12, top: -24, width: 22, height: 28, child: Art('train/flag')),
          ]),
        ),
      ),
    );
  }

  /// The little train on the map: at its station, or driving along the line.
  Widget _trainMarker(double w, double h) {
    final t = Curves.easeInOut.transform(_drive.value);
    final path = [for (var i = _from; i <= _to; i++) mapStations[i]];
    (double, double) at;
    if (path.length < 2) {
      at = mapStations[_to];
    } else {
      final f = t * (path.length - 1);
      final k = math.min(f.floor(), path.length - 2);
      final u = f - k;
      at = (path[k].$1 + (path[k + 1].$1 - path[k].$1) * u, path[k].$2 + (path[k + 1].$2 - path[k].$2) * u);
    }
    const tw = 46.0;
    return Positioned(
      left: at.$1 * w - tw * .55,
      top: at.$2 * h - tw * .95,
      width: tw,
      height: tw / Locomotive.aspect,
      child: IgnorePointer(child: TrainClock(period: 900, builder: (_, c) => Locomotive(width: tw, t: _drive.isAnimating ? c : 0))),
    );
  }

  Widget _train(Game g, Bopomofo b, int playing) {
    final order = g.settings.order;
    final row = g.row(b, playing);
    final others = [for (final s in b.all(order)) if (g.of(s).seen && !row.contains(s)) s];
    final cars = [for (final s in row) (s, !g.of(s).seen), for (final s in others) (s, false)];
    const cw = 92.0;
    return TrainClock(
      period: 2600,
      builder: (context, t) => OnTrack(
        track: 16,
        child: ListView(
          scrollDirection: Axis.horizontal,
          reverse: true,
          padding: const EdgeInsets.symmetric(horizontal: 12),
          children: [
            Semantics(
              key: const ValueKey('locomotive'),
              container: true,
              button: true,
              label: '火車頭',
              excludeSemantics: true,
              onTap: _loco,
              child: Pressable(
                onTap: _loco,
                sound: null,
                child: Hop(trigger: _toot, height: 10, child: Locomotive(width: 140, t: t, stickers: g.stickers)),
              ),
            ),
            for (final (s, ghost) in cars)
              Padding(
                padding: const EdgeInsets.only(right: 2, top: 22),
                child: Semantics(
                  key: ValueKey('car-$s'),
                  container: true,
                  button: true,
                  label: ghost ? '還沒掛上的車廂' : s,
                  excludeSemantics: true,
                  onTap: () => _car(s, ghost),
                  child: Pressable(onTap: () => _car(s, ghost), sound: null, child: Carriage(station: b.stationOf(s, order), sym: s, width: cw, spin: t * 1.6, ghost: ghost)),
                ),
              ),
          ],
        ),
      ),
    );
  }

  void _car(String s, bool ghost) {
    if (ghost) {
      sfx(ref, 'try');
      speak(ref, Strings.seeFirst);
      return;
    }
    sfx(ref, 'ding');
    final settings = ref.read(gameProvider).settings;
    speak(ref, symbolLine(_b, s, twice: settings.twice));
  }

  Widget _button(Game g, Bopomofo b, int playing, Module m, Color color, String icon, double size, {bool glow = false}) {
    final open = g.settings.open(m);
    final done = g.moduleDone(b, playing, m);
    return Semantics(
      key: ValueKey('module-${m.name}'),
      container: true,
      button: true,
      label: m.zh,
      excludeSemantics: true,
      onTap: () => _open(m),
      child: Pressable(
        onTap: () => _open(m),
        child: SizedBox(
          width: size,
          height: size * .96,
          child: Stack(clipBehavior: Clip.none, children: [
            Positioned.fill(
              child: Container(
                decoration: toyBox(open ? color : const Color(0xFFCFCAD8), radius: 24, ring: glow ? Toy.yellow : null),
                padding: const EdgeInsets.fromLTRB(6, 6, 6, 4),
                child: Column(children: [
                  Expanded(child: Opacity(opacity: open ? 1 : .5, child: Art('icons/$icon'))),
                  Text(m.zh,
                      maxLines: 1,
                      style: TextStyle(fontSize: math.min(19, size * .15), fontWeight: FontWeight.w700, color: Colors.white, shadows: [Shadow(color: Toy.ink.withValues(alpha: .5), offset: const Offset(0, 1.5))])),
                ]),
              ),
            ),
            const Positioned.fill(child: Gleam(size: .9)),
            if (done) const Positioned(right: -6, top: -6, width: 30, height: 30, child: Art('icons/check')),
            if (!open) const Positioned(right: -4, top: -6, width: 30, height: 30, child: Art('icons/lock')),
          ]),
        ),
      ),
    );
  }

  Widget _spell(double size) => Semantics(
        key: const ValueKey('module-spell'),
        container: true,
        button: true,
        label: Strings.spell,
        excludeSemantics: true,
        onTap: () => speak(ref, Strings.spellSoon),
        child: Pressable(
          onTap: () => speak(ref, Strings.spellSoon),
          child: SizedBox(
            width: size,
            height: size * .96,
            child: Stack(clipBehavior: Clip.none, children: [
              Positioned.fill(
                child: Container(
                  decoration: toyBox(Toy.teal, radius: 24),
                  padding: const EdgeInsets.fromLTRB(6, 6, 6, 4),
                  child: Column(children: [
                    const Expanded(child: Opacity(opacity: .55, child: Art('icons/spell'))),
                    Text(Strings.spell,
                        style: TextStyle(fontSize: math.min(19, size * .15), fontWeight: FontWeight.w700, color: Colors.white, shadows: [Shadow(color: Toy.ink.withValues(alpha: .5), offset: const Offset(0, 1.5))])),
                  ]),
                ),
              ),
              Positioned(
                right: -4,
                top: -8,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                  decoration: toyBox(Colors.white, radius: 10, shadow: false, rim: 1.5),
                  child: const Text(Strings.soon, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Toy.inkSoft)),
                ),
              ),
            ]),
          ),
        ),
      );
}
