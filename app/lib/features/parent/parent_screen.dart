import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/version.dart';
import '../../app/widgets.dart';
import '../../core/book.dart';
import '../../core/game.dart';
import '../../core/lines.dart';
import '../../core/providers.dart';
import '../../core/voice.dart';

/// Parent mode (after the gate, docs/design.md 「家長模式」): the level and
/// the play time, the stations and the order, the voice (and 語音試聽 of all
/// 37 symbols), progress as 37 carriages, today's 家裡找找, the rest.
class ParentScreen extends ConsumerWidget {
  const ParentScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final g = ref.watch(gameProvider);
    final b = ref.watch(bookProvider);
    final s = g.settings;
    final game = ref.read(gameProvider.notifier);
    final now = ref.read(clockProvider)();

    Widget section(String title, List<Widget> children, {Key? key}) => Padding(
          key: key,
          padding: const EdgeInsets.only(bottom: 16),
          child: Material(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(18, 14, 18, 12),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(title, style: const TextStyle(fontSize: 15, color: Toy.inkSoft, fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                ...children,
              ]),
            ),
          ),
        );

    Widget toggle(String label, bool value, void Function(bool)? set, {Key? key, String? note}) => SwitchListTile(
          key: key,
          contentPadding: EdgeInsets.zero,
          title: Text(label, style: const TextStyle(fontSize: 17)),
          subtitle: note == null ? null : Text(note, style: const TextStyle(fontSize: 13, color: Toy.inkSoft)),
          value: value,
          onChanged: set,
        );

    Widget chips<T>(List<T> values, T selected, String Function(T) label, void Function(T) pick, String keyOf) => Wrap(spacing: 8, runSpacing: 8, children: [
          for (final v in values)
            ChoiceChip(
              key: ValueKey('$keyOf-${v is Enum ? v.name : v}'),
              label: Text(label(v), style: const TextStyle(fontSize: 16)),
              selected: v == selected,
              onSelected: (_) => pick(v),
              selectedColor: const Color(0xFFFFE3B8),
              showCheckmark: false,
            ),
        ]);

    const note = TextStyle(fontSize: 14, height: 1.5, color: Toy.inkSoft);
    final log = g.log(now);
    final task = g.taskFor(b, now);
    final current = g.current(b);

    return Scaffold(
      backgroundColor: Toy.parentBg,
      appBar: AppBar(
        backgroundColor: Toy.parentBg,
        title: const Text(Strings.parentTitle),
        leading: IconButton(icon: const Icon(Icons.close_rounded), tooltip: Strings.back, onPressed: () => context.go('/')),
      ),
      body: ListView(padding: const EdgeInsets.fromLTRB(16, 8, 16, 32), children: [
        section(Strings.levelTitle, [
          chips(Level.values, s.level, Strings.levelLine, (v) => game.settings((x) => x.copyWith(level: v)), 'level'),
          const SizedBox(height: 10),
          const Text(Strings.levelNote, style: note),
        ]),
        section(Strings.playTime, [
          chips(Settings.minuteChoices, s.minutes, Strings.minutes, (v) => game.settings((x) => x.copyWith(minutes: v)), 'minutes'),
          const SizedBox(height: 10),
          const Text(Strings.playTimeNote, style: note),
          if (g.resting(now)) ...[
            const SizedBox(height: 10),
            const Text(Strings.resting, style: TextStyle(fontSize: 16)),
            const SizedBox(height: 6),
            FilledButton(
              key: const ValueKey('play-on'),
              onPressed: () {
                game.change((g) => g.playOn());
                ref.read(sessionStartProvider.notifier).restart();
                context.go('/');
              },
              child: const Text(Strings.playOn),
            ),
          ],
        ]),
        section(Strings.progressTitle, [
          _Grid(game: g, book: b),
          const SizedBox(height: 8),
          const Text(Strings.legend, style: note),
          const SizedBox(height: 8),
          Text(Strings.today(log.seconds ~/ 60, [for (final m in Module.values) if (log.modules.contains(m)) m]), style: const TextStyle(fontSize: 16)),
          const SizedBox(height: 4),
          Text(Strings.rhymeScore(g.rhymeRight, g.rhymeAsked), style: const TextStyle(fontSize: 16)),
        ]),
        section(Strings.voiceTitle, [
          toggle(Strings.voice, s.voice, (v) => game.settings((x) => x.copyWith(voice: v)), key: const ValueKey('voice')),
          toggle(Strings.slow, s.slow, (v) => game.settings((x) => x.copyWith(slow: v)), key: const ValueKey('slow')),
          toggle(Strings.twice, s.twice, (v) => game.settings((x) => x.copyWith(twice: v)), key: const ValueKey('twice')),
          const SizedBox(height: 4),
          ExpansionTile(
            key: const ValueKey('try-voice'),
            tilePadding: EdgeInsets.zero,
            title: const Text(Strings.tryVoice, style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
            subtitle: const Text(Strings.tryVoiceNote, style: TextStyle(fontSize: 13, color: Toy.inkSoft, height: 1.45)),
            children: [
              for (final sym in b.all(s.order))
                ListTile(
                  key: ValueKey('try-$sym'),
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                  title: Text(Strings.tryLine(sym, homophones[sym]!, b.wordOf(sym).zh), style: const TextStyle(fontSize: 17)),
                  trailing: IconButton(
                    tooltip: '試聽 $sym',
                    icon: const Icon(Icons.volume_up_rounded, color: Toy.orange),
                    onPressed: () => ref.read(voiceProvider).say(speakable(symbolLine(b, sym, twice: s.twice)), slow: s.slow),
                  ),
                ),
            ],
          ),
        ]),
        section(Strings.stationsTitle, [
          const Text(Strings.stationsNote, style: note),
          const SizedBox(height: 6),
          Wrap(spacing: 8, runSpacing: 4, children: [
            for (var i = 0; i < Settings.stationCount; i++)
              FilterChip(
                key: ValueKey('station-on-$i'),
                avatar: s.unlocked(i) ? null : const Icon(Icons.lock_rounded, size: 16),
                label: Text('${i + 1} ${b.stations[i].name}　${g.row(b, i).join()}', style: const TextStyle(fontSize: 15)),
                selected: s.stations.contains(i),
                onSelected: (on) => game.settings((x) => x.copyWith(stations: on ? {...x.stations, i} : ({...x.stations}..remove(i)))),
                selectedColor: b.stations[i].color.withValues(alpha: .45),
              ),
          ]),
          const SizedBox(height: 12),
          const Text(Strings.jumpTitle, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
          const Text(Strings.jumpNote, style: note),
          const SizedBox(height: 6),
          Wrap(spacing: 8, runSpacing: 8, children: [
            for (var i = 0; i < Settings.stationCount; i++)
              ChoiceChip(
                key: ValueKey('jump-$i'),
                label: Text(b.stations[i].name, style: const TextStyle(fontSize: 15)),
                selected: i == current,
                onSelected: g.enabled(i)
                    ? (_) => game.change((g) => g.jump(i))
                    : null,
                showCheckmark: false,
                selectedColor: b.stations[i].color.withValues(alpha: .55),
              ),
          ]),
          const SizedBox(height: 12),
          const Text(Strings.orderTitle, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          chips(Order.values, s.order, (o) => o.zh, (v) => game.settings((x) => x.copyWith(order: v)), 'order'),
          const SizedBox(height: 6),
          Text(Strings.orderNote(s.order), style: note),
        ]),
        if (s.full)
          section(Strings.findTitle, [
            Text(Strings.todayTask(task.sym, [for (final h in b.symbols[task.sym]!.hints) b.words[h]!.zh]), style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 4),
            Text(Strings.stickers(g.stickers.length), style: note),
            if (g.stickers.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 6),
                child: Wrap(spacing: 6, children: [for (final w in g.stickers.reversed.take(12)) SizedBox(width: 36, height: 36, child: Art('words/$w'))]),
              ),
          ]),
        section(Strings.otherTitle, [
          toggle(Strings.leftHanded, s.leftHanded, (v) => game.settings((x) => x.copyWith(leftHanded: v)), key: const ValueKey('left')),
          toggle(Strings.music, s.music, (v) => game.settings((x) => x.copyWith(music: v)), key: const ValueKey('music')),
          toggle(Strings.effects, s.sounds, (v) => game.settings((x) => x.copyWith(sounds: v)), key: const ValueKey('effects')),
          const SizedBox(height: 4),
          OutlinedButton.icon(
            key: const ValueKey('change-driver'),
            onPressed: () {
              game.change((g) => g.copyWith(clearDriver: true));
              context.go('/driver');
            },
            icon: const Icon(Icons.face_rounded),
            label: const Text(Strings.changeDriver),
          ),
        ]),
        section(Strings.fullVersion, [
          const Text(Strings.fullNote, style: note),
          toggle(Strings.fullSwitch, s.full, (v) => game.settings((x) => x.copyWith(full: v)), key: const ValueKey('full')),
        ]),
        section(Strings.about, [
          const Text(Strings.privacy, style: TextStyle(fontSize: 15, height: 1.5)),
          const SizedBox(height: 6),
          Text(Strings.version(appVersion), style: note),
        ]),
      ]),
    );
  }
}

/// The 37 carriages in learning order, coloured by how far each has come.
class _Grid extends StatelessWidget {
  const _Grid({required this.game, required this.book});

  final Game game;
  final Bopomofo book;

  @override
  Widget build(BuildContext context) {
    final order = game.settings.order;
    return Wrap(spacing: 5, runSpacing: 7, children: [
      for (final sym in book.all(order))
        () {
          final p = game.of(sym);
          final col = book.stations[book.stationOf(sym, order)].color;
          final fill = !p.seen ? const Color(0xFFE6E2EA) : (p.heard >= Progress.heardWell ? col : Color.lerp(col, Colors.white, .62)!);
          return Stack(clipBehavior: Clip.none, children: [
            Container(
              key: ValueKey('grid-$sym'),
              width: 38,
              height: 32,
              alignment: Alignment.center,
              decoration: BoxDecoration(color: fill, borderRadius: BorderRadius.circular(9), border: Border.all(color: p.seen ? Toy.rim(col) : const Color(0xFFCFCAD8), width: 1.5)),
              child: Text(sym, textScaler: TextScaler.noScaling, style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: p.seen ? Toy.ink : Toy.inkSoft)),
            ),
            if (p.traced)
              Positioned(
                right: -3,
                top: -4,
                child: Container(width: 12, height: 12, decoration: BoxDecoration(color: Toy.green, shape: BoxShape.circle, border: Border.all(color: Colors.white, width: 1.5))),
              ),
          ]);
        }(),
    ]);
  }
}
