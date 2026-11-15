import 'dart:async';

import 'package:bopomofo_train/app/strings.dart';
import 'package:bopomofo_train/app/widgets.dart';
import 'package:bopomofo_train/core/providers.dart';
import 'package:bopomofo_train/features/parent/parent_gate.dart';
import 'package:bopomofo_train/features/write/write_painter.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'helpers.dart';

/// Things found in the review of 0.1.0: the play time, the voice between
/// screens, and quick taps in 寫寫看.
void main() {
  testWidgets('time in parent mode is not the child\'s play time', (tester) async {
    final app = await TestApp.start(tester);
    app.now = app.now.add(const Duration(minutes: 10));
    await app.settle(2600);
    ParentPass.grant();
    app.go('/parent');
    await app.settle(2600);
    app.now = app.now.add(const Duration(minutes: 20));
    await app.settle(2600);
    expect(app.location, '/parent');
    app.go('/');
    await app.settle(2600);
    expect(app.location, '/', reason: 'the child has played 10 of the 15 minutes');
    app.now = app.now.add(const Duration(minutes: 6));
    await app.settle(2600);
    expect(app.location, '/rest');
    await app.end();
  });

  testWidgets('today\'s minutes do not count while the app is in the background', (tester) async {
    final app = await TestApp.start(tester);
    await app.settle(2600);
    for (final s in [AppLifecycleState.inactive, AppLifecycleState.hidden, AppLifecycleState.paused]) {
      tester.binding.handleAppLifecycleStateChanged(s);
    }
    for (var i = 0; i < 4; i++) {
      await app.settle(30000);
    }
    for (final s in [AppLifecycleState.hidden, AppLifecycleState.inactive, AppLifecycleState.resumed]) {
      tester.binding.handleAppLifecycleStateChanged(s);
    }
    await app.settle(400);
    expect(app.game.log(app.now).seconds, lessThan(10), reason: 'two minutes away are not two minutes played');
    await app.end();
  });

  testWidgets('leaving a screen stops its voice, but never the next screen\'s first line', (tester) async {
    final app = await TestApp.start(tester);
    app.go('/listen');
    await app.settle(1200);
    final stops = app.voice.stops;
    expect(stops, 0, reason: 'the listen screen spoke before the station went away');
    await app.tapLabel(Strings.home, ms: 1200);
    expect(app.location, '/');
    expect(app.voice.stops, 1, reason: 'the question does not go on over the station');
    app.go('/see');
    await app.settle(1200);
    expect(app.voice.stops, 1);
    await app.end();
  });

  testWidgets('寫寫看: a quick extra tap after the last star is fine', (tester) async {
    final app = await TestApp.start(tester);
    app.go('/write');
    await app.settle(800);
    await app.tapLabel(Strings.stepTap, ms: 300);
    final sym = app.game.row(book, 0).first;
    final strokes = book.symbols[sym]!.strokes;
    Offset at(Offset p) {
      final page = tester.getRect(find.byKey(const ValueKey('page')));
      return page.topLeft + BoxFit100(page.size).toScreen(p);
    }

    for (final s in strokes) {
      await tester.tapAt(at(s.first));
      await tester.pump(const Duration(milliseconds: 50));
    }
    await tester.tapAt(at(strokes.last.first));
    await tester.pump(const Duration(milliseconds: 50));
    expect(tester.takeException(), isNull);
    await app.settle(1200);
    expect(app.voice.said.last, Strings.traceRoad);
    await app.end();
  });

  testWidgets('家裡找找: found after midnight marks the card on screen; the new day gets its own', (tester) async {
    final app = await TestApp.start(tester);
    app.now = DateTime(2026, 11, 15, 23, 58);
    app.container.read(sessionStartProvider.notifier).restart();
    app.change((g) => g.saw('ㄚ').saw('ㄧ').saw('ㄨ').saw('ㄛ').saw('ㄜ'));
    app.go('/find');
    await app.settle(800);
    final shown = app.game.task!;
    app.now = DateTime(2026, 11, 16, 0, 2);
    await app.settle(2600);
    await app.tapLabel(Strings.found, ms: 600);
    final hint = book.words[book.symbols[shown.sym]!.hints.first]!;
    await app.tapLabel(hint.zh, ms: 600);
    expect(app.game.task!.day, shown.day);
    expect(app.game.task!.sym, shown.sym);
    expect(app.game.task!.found, hint.id);
    expect(app.game.taskGiven(app.now), isFalse, reason: 'today\'s card is still to come');
    await app.settle(3000);
    await app.end();
  });

  testWidgets('the next step waits until a slow line has been said, but not for ever', (tester) async {
    final line = Completer<void>();
    var ran = 0;
    Later(const Duration(milliseconds: 500), () => ran++, after: line.future);
    await tester.pump(const Duration(seconds: 2));
    expect(ran, 0, reason: 'still speaking');
    line.complete();
    await tester.pump();
    expect(ran, 1);

    Later(const Duration(milliseconds: 500), () => ran++, after: Completer<void>().future, atMost: const Duration(seconds: 3));
    await tester.pump(const Duration(seconds: 2));
    expect(ran, 1);
    await tester.pump(const Duration(seconds: 2));
    expect(ran, 2, reason: 'a voice that never says it is done does not hold the game up');

    Later(const Duration(milliseconds: 500), () => ran++).cancel();
    await tester.pump(const Duration(seconds: 1));
    expect(ran, 2);
  });
}
