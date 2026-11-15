import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../core/book.dart';
import '../core/game.dart';
import '../core/providers.dart';
import '../core/sounds.dart';
import '../core/voice.dart';
import 'strings.dart';
import 'theme.dart';

/// A drawing from assets/art/ (nothing at all if it is missing).
class Art extends StatelessWidget {
  const Art(this.path, {super.key, this.fit = BoxFit.contain, this.alignment = Alignment.center});

  /// Under assets/art/, without ".svg" (train/wheel).
  final String path;
  final BoxFit fit;
  final Alignment alignment;

  @override
  Widget build(BuildContext context) =>
      SvgPicture.asset('assets/art/$path.svg', fit: fit, alignment: alignment, excludeFromSemantics: true, errorBuilder: (_, _, _) => const SizedBox.expand());
}

/// Says [text] out loud (if the parent left the voice on): every symbol in
/// it is read as its character (voice.dart), slower if the parent asked.
void speak(WidgetRef ref, String text) {
  final s = ref.read(gameProvider).settings;
  if (!s.voice) return;
  ref.read(voiceProvider).say(speakable(text), slow: s.slow);
}

void sfx(WidgetRef ref, String name) => ref.read(soundsProvider).play(name);

/// Shrinks a little while pressed and fires when the finger lifts on it
/// (raw pointer events: a touch counts at once, no gesture to wait for).
class Pressable extends ConsumerStatefulWidget {
  const Pressable({super.key, required this.child, this.onTap, this.sound = 'tap'});

  final Widget child;
  final VoidCallback? onTap;
  final String? sound;

  @override
  ConsumerState<Pressable> createState() => _PressableState();
}

class _PressableState extends ConsumerState<Pressable> {
  int? _pointer;

  @override
  Widget build(BuildContext context) {
    final enabled = widget.onTap != null;
    return Listener(
      behavior: HitTestBehavior.opaque,
      onPointerDown: enabled && _pointer == null ? (e) => setState(() => _pointer = e.pointer) : null,
      onPointerCancel: (e) {
        if (e.pointer == _pointer) setState(() => _pointer = null);
      },
      onPointerUp: (e) {
        if (e.pointer != _pointer) return;
        setState(() => _pointer = null);
        final box = context.findRenderObject() as RenderBox?;
        if (!enabled || box == null || !(Offset.zero & box.size).inflate(12).contains(e.localPosition)) return;
        final s = widget.sound;
        if (s != null) ref.read(soundsProvider).play(s);
        widget.onTap!();
      },
      child: AnimatedScale(scale: _pointer != null ? 0.93 : 1, duration: const Duration(milliseconds: 90), child: widget.child),
    );
  }
}

/// A glossy vinyl block: lit from the top, a darker rim, a plain shadow.
BoxDecoration toyBox(Color color, {double radius = 22, bool shadow = true, Color? ring, double rim = 2.5}) => BoxDecoration(
      gradient: LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [Color.lerp(color, Colors.white, .32)!, color, Color.lerp(color, Toy.ink, .12)!],
        stops: const [0, .45, 1],
      ),
      borderRadius: BorderRadius.circular(radius),
      border: Border.all(color: ring ?? (color == Colors.white || color == Toy.paper ? Toy.line : Toy.rim(color)), width: ring == null ? rim : 4),
      boxShadow: shadow ? [BoxShadow(color: Toy.ink.withValues(alpha: .16), offset: const Offset(3, 4))] : null,
    );

/// The two white gleams of a glossy toy, laid over a block.
class Gleam extends StatelessWidget {
  const Gleam({super.key, this.size = 1});

  final double size;

  @override
  Widget build(BuildContext context) => IgnorePointer(
        child: Align(
          alignment: const Alignment(-.72, -.72),
          child: Transform.rotate(
            angle: -.45,
            child: Stack(clipBehavior: Clip.none, children: [
              Container(width: 26 * size, height: 12 * size, decoration: BoxDecoration(color: Colors.white.withValues(alpha: .45), borderRadius: BorderRadius.circular(12 * size))),
              Positioned(left: 4 * size, top: 3 * size, child: Container(width: 7 * size, height: 5 * size, decoration: BoxDecoration(color: Colors.white.withValues(alpha: .95), borderRadius: BorderRadius.circular(4 * size)))),
            ]),
          ),
        ),
      );
}

/// A round button with an icon.
class RoundButton extends StatelessWidget {
  const RoundButton({super.key, required this.label, required this.icon, this.onTap, this.size = 50, this.color = Colors.white, this.sound = 'tap'});

  final String label;
  final IconData icon;
  final VoidCallback? onTap;
  final double size;
  final Color color;
  final String? sound;

  @override
  Widget build(BuildContext context) => Semantics(
        container: true,
        button: true,
        label: label,
        excludeSemantics: true,
        onTap: onTap,
        child: Pressable(
          onTap: onTap,
          sound: sound,
          child: Container(
            width: size,
            height: size,
            decoration: toyBox(color, radius: size / 2),
            child: Icon(icon, size: size * 0.54, color: color == Colors.white ? Toy.ink : Colors.white),
          ),
        ),
      );
}

/// A wide glossy pill with a word.
class PillButton extends StatelessWidget {
  const PillButton({super.key, required this.label, this.onTap, this.color = Toy.green, this.icon, this.height = 58, this.sound = 'tap', this.expand = false});

  final String label;
  final VoidCallback? onTap;
  final Color color;
  final IconData? icon;
  final double height;
  final String? sound;
  final bool expand;

  @override
  Widget build(BuildContext context) {
    final light = color.computeLuminance() > .6;
    final fg = light ? Toy.ink : Colors.white;
    return Semantics(
      container: true,
      button: true,
      label: label,
      excludeSemantics: true,
      onTap: onTap,
      child: Pressable(
        onTap: onTap,
        sound: sound,
        child: Container(
          height: height,
          padding: EdgeInsets.symmetric(horizontal: height * 0.4),
          decoration: toyBox(color, radius: height / 2),
          child: Row(mainAxisSize: expand ? MainAxisSize.max : MainAxisSize.min, mainAxisAlignment: MainAxisAlignment.center, children: [
            if (icon != null) ...[Icon(icon, size: height * 0.46, color: fg), const SizedBox(width: 8)],
            Flexible(
              child: Text(label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontSize: height * 0.36, fontWeight: FontWeight.w700, color: fg, shadows: light ? null : [Shadow(color: Toy.ink.withValues(alpha: .35), offset: const Offset(0, 1.5))])),
            ),
          ]),
        ),
      ),
    );
  }
}

/// A speech bubble (tap to hear it again).
class Bubble extends StatelessWidget {
  const Bubble({super.key, required this.text, this.onTap, this.size = 18, this.speaker = false, this.tail = true});

  final String text;
  final VoidCallback? onTap;
  final double size;
  final bool speaker;
  final bool tail;

  @override
  Widget build(BuildContext context) => Semantics(
        container: true,
        button: onTap != null,
        label: text,
        excludeSemantics: true,
        onTap: onTap,
        child: Pressable(
          onTap: onTap,
          sound: null,
          child: Container(
            padding: EdgeInsets.fromLTRB(speaker ? 8 : 16, 9, 16, 9),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(22),
              border: Border.all(color: Toy.line, width: 2),
              boxShadow: [BoxShadow(color: Toy.ink.withValues(alpha: .12), offset: const Offset(2, 3))],
            ),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              if (speaker) ...[
                Container(
                  width: size * 1.8,
                  height: size * 1.8,
                  decoration: toyBox(Toy.orange, radius: size, shadow: false, rim: 1.5),
                  child: Icon(Icons.volume_up_rounded, color: Colors.white, size: size * 1.05),
                ),
                const SizedBox(width: 10),
              ],
              Flexible(child: Text(text, style: TextStyle(fontSize: size, fontWeight: FontWeight.w700, color: Toy.ink, height: 1.35))),
            ]),
          ),
        ),
      );
}

/// A station's name in its colour (the top bar and the map).
class StationChip extends StatelessWidget {
  const StationChip({super.key, required this.station});

  final Station station;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
        decoration: toyBox(station.color, radius: 16, shadow: false, rim: 2),
        child: Text('${station.name}站', style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: Toy.ink)),
      );
}

/// The bar at the top of a screen: home, the title on a sign, the station, a speaker.
class TopBar extends StatelessWidget {
  const TopBar({super.key, required this.title, this.onHome, this.onSpeak, this.station, this.leading});

  final String title;
  final VoidCallback? onHome;
  final VoidCallback? onSpeak;
  final Station? station;
  final Widget? leading;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.fromLTRB(12, 6, 12, 4),
        child: Row(children: [
          leading ?? (onHome == null ? const SizedBox(width: 48) : RoundButton(label: Strings.home, icon: Icons.home_rounded, onTap: onHome, size: 48, color: Toy.red)),
          const SizedBox(width: 8),
          Expanded(
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 6),
                decoration: toyBox(Toy.paper, radius: 18, shadow: true),
                child: Text(title, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 21, fontWeight: FontWeight.w700, color: Toy.ink)),
              ),
            ),
          ),
          const SizedBox(width: 8),
          if (station != null) StationChip(station: station!),
          if (onSpeak != null) ...[
            const SizedBox(width: 6),
            RoundButton(label: Strings.again, icon: Icons.volume_up_rounded, onTap: onSpeak, size: 46, color: Toy.orange, sound: null),
          ],
          if (station == null && onSpeak == null) const SizedBox(width: 48),
        ]),
      );
}

/// The cream background with soft hills along the bottom.
class ToyBg extends StatelessWidget {
  const ToyBg({super.key, required this.child, this.hills = true, this.top = const Color(0xFFDDF1FB), this.bottom = Toy.cream});

  final Widget child;
  final bool hills;
  final Color top, bottom;

  @override
  Widget build(BuildContext context) => DecoratedBox(
        decoration: BoxDecoration(gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [top, bottom], stops: const [0, .45])),
        child: Stack(fit: StackFit.expand, children: [
          if (hills) const Positioned(left: 0, right: 0, bottom: 0, height: 80, child: Opacity(opacity: .7, child: Art('home/hills', fit: BoxFit.fill))),
          child,
        ]),
      );
}

/// Plays [music] while this is on screen.
class WithMusic extends ConsumerStatefulWidget {
  const WithMusic({super.key, required this.music, required this.child});

  final Music music;
  final Widget child;

  @override
  ConsumerState<WithMusic> createState() => _WithMusicState();
}

class _WithMusicState extends ConsumerState<WithMusic> {
  late final Sounds _sounds = ref.read(soundsProvider);

  @override
  void initState() {
    super.initState();
    _sounds.hold(this, widget.music);
  }

  @override
  void dispose() {
    _sounds.release(this);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => widget.child;
}

/// Shakes its child side to side once each time [trigger] changes.
class Wiggle extends StatefulWidget {
  const Wiggle({super.key, required this.trigger, required this.child, this.amount = 0.1});

  final int trigger;
  final Widget child;
  final double amount;

  @override
  State<Wiggle> createState() => _WiggleState();
}

class _WiggleState extends State<Wiggle> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 600));

  @override
  void didUpdateWidget(Wiggle old) {
    super.didUpdateWidget(old);
    if (old.trigger != widget.trigger) _c.forward(from: 0);
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
        animation: _c,
        builder: (_, child) {
          final t = _c.value;
          return Transform.rotate(angle: math.sin(t * math.pi * 4) * (1 - t) * widget.amount, child: child);
        },
        child: widget.child,
      );
}

/// Jumps up once each time [trigger] changes.
class Hop extends StatefulWidget {
  const Hop({super.key, required this.trigger, required this.child, this.height = 24});

  final int trigger;
  final Widget child;
  final double height;

  @override
  State<Hop> createState() => _HopState();
}

class _HopState extends State<Hop> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 520));

  @override
  void didUpdateWidget(Hop old) {
    super.didUpdateWidget(old);
    if (old.trigger != widget.trigger) _c.forward(from: 0);
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
        animation: _c,
        builder: (_, child) {
          final t = _c.value;
          final up = math.sin(t * math.pi) * widget.height;
          final squash = 1 + .06 * math.sin(t * math.pi * 2);
          return Transform.translate(offset: Offset(0, -up), child: Transform.scale(scaleX: squash, scaleY: 2 - squash, child: child));
        },
        child: widget.child,
      );
}

/// A gentle bob up and down.
class Bob extends StatefulWidget {
  const Bob({super.key, required this.child, this.phase = 0, this.amount = 4, this.period = 2400});

  final Widget child;
  final double phase;
  final double amount;
  final int period;

  @override
  State<Bob> createState() => _BobState();
}

class _BobState extends State<Bob> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: Duration(milliseconds: widget.period))..repeat();

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
        animation: _c,
        builder: (_, child) => Transform.translate(offset: Offset(0, math.sin((_c.value + widget.phase) * 2 * math.pi) * widget.amount), child: child),
        child: widget.child,
      );
}

/// A word's picture.
class WordPicture extends StatelessWidget {
  const WordPicture(this.word, {super.key, this.size = 100});

  final Word word;
  final double size;

  @override
  Widget build(BuildContext context) => SizedBox(width: size, height: size, child: Art('words/${word.id}'));
}

/// A white card with a word's picture and its name (押韻接龍, 家裡找找).
class WordCard extends StatelessWidget {
  const WordCard({super.key, required this.word, this.onTap, this.size = 110, this.ring, this.faded = false, this.label});

  final Word word;
  final VoidCallback? onTap;
  final double size;
  final Color? ring;
  final bool faded;
  final String? label;

  @override
  Widget build(BuildContext context) => Semantics(
        key: ValueKey('word-${word.id}'),
        container: true,
        button: onTap != null,
        label: label ?? word.zh,
        excludeSemantics: true,
        onTap: onTap,
        child: Pressable(
          onTap: onTap,
          sound: null,
          child: AnimatedOpacity(
            duration: const Duration(milliseconds: 250),
            opacity: faded ? .45 : 1,
            child: Container(
              width: size,
              padding: EdgeInsets.fromLTRB(size * .06, size * .06, size * .06, size * .04),
              decoration: toyBox(Toy.paper, radius: size * .2, ring: ring),
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                WordPicture(word, size: size * .78),
                Text(word.zh, style: TextStyle(fontSize: size * .17, fontWeight: FontWeight.w700, color: Toy.ink)),
              ]),
            ),
          ),
        ),
      );
}

/// The driver the child picked (head and shoulders in the cap).
class DriverView extends ConsumerWidget {
  const DriverView({super.key, this.size = 80, this.driver});

  final double size;
  final Driver? driver;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final d = driver ?? ref.watch(gameProvider.select((g) => g.driver)) ?? Driver.bear;
    return SizedBox(width: size, height: size, child: Art('train/driver_${d.name}'));
  }
}

/// The driver with something to say beside it.
class DriverSays extends StatelessWidget {
  const DriverSays({super.key, required this.text, this.onTap, this.size = 76, this.right = true});

  final String text;
  final VoidCallback? onTap;
  final double size;
  final bool right;

  @override
  Widget build(BuildContext context) {
    final driver = Semantics(
      container: true,
      button: onTap != null,
      label: '司機',
      excludeSemantics: true,
      onTap: onTap,
      child: Pressable(onTap: onTap, sound: null, child: Bob(amount: 3, child: DriverView(size: size))),
    );
    final bubble = Flexible(child: Bubble(text: text, onTap: onTap, size: 17));
    return Row(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.center, children: right ? [bubble, const SizedBox(width: 6), driver] : [driver, const SizedBox(width: 6), bubble]);
  }
}

/// Little bits of paper flying up when something went right.
class Confetti extends StatefulWidget {
  const Confetti({super.key, required this.trigger});

  final int trigger;

  @override
  State<Confetti> createState() => _ConfettiState();
}

class _ConfettiState extends State<Confetti> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 1400));

  @override
  void didUpdateWidget(Confetti old) {
    super.didUpdateWidget(old);
    if (old.trigger != widget.trigger) _c.forward(from: 0);
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => IgnorePointer(
        child: AnimatedBuilder(
          animation: _c,
          builder: (_, _) => _c.isAnimating ? CustomPaint(painter: _ConfettiPainter(_c.value, widget.trigger), size: Size.infinite) : const SizedBox.expand(),
        ),
      );
}

class _ConfettiPainter extends CustomPainter {
  _ConfettiPainter(this.t, this.seed);

  final double t;
  final int seed;

  static const colors = [Toy.red, Toy.yellow, Toy.blue, Toy.mint, Toy.pink, Toy.purple, Toy.orange];

  @override
  void paint(Canvas canvas, Size size) {
    final r = math.Random(seed);
    for (var i = 0; i < 36; i++) {
      final x0 = size.width * (.2 + .6 * r.nextDouble());
      final vx = (r.nextDouble() - .5) * size.width * .9;
      final vy = -size.height * (.6 + .5 * r.nextDouble());
      final x = x0 + vx * t;
      final y = size.height * .62 + vy * t + size.height * 1.3 * t * t;
      final p = Paint()..color = colors[i % colors.length].withValues(alpha: (1 - t).clamp(0, 1));
      canvas.save();
      canvas.translate(x, y);
      canvas.rotate(t * 8 + i);
      canvas.drawRRect(RRect.fromRectAndRadius(const Rect.fromLTWH(-5, -3, 10, 6), const Radius.circular(2)), p);
      canvas.restore();
    }
  }

  @override
  bool shouldRepaint(_ConfettiPainter old) => old.t != t;
}

/// The end of a round: a big card with what happened and where to go next.
class DonePanel extends StatelessWidget {
  const DonePanel({super.key, required this.title, required this.actions});

  final String title;
  final List<Widget> actions;

  @override
  Widget build(BuildContext context) => Container(
        color: Toy.ink.withValues(alpha: .35),
        alignment: Alignment.center,
        padding: const EdgeInsets.all(22),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 440),
          child: Container(
            padding: const EdgeInsets.fromLTRB(20, 18, 20, 20),
            decoration: toyBox(Toy.paper, radius: 30),
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              const Bob(amount: 3, child: DriverView(size: 110)),
              const SizedBox(height: 8),
              Text(title, textAlign: TextAlign.center, style: const TextStyle(fontSize: 23, fontWeight: FontWeight.w700, color: Toy.ink, height: 1.35)),
              const SizedBox(height: 16),
              for (final a in actions) Padding(padding: const EdgeInsets.only(top: 10), child: a),
            ]),
          ),
        ),
      );
}
