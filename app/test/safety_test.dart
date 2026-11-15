import 'dart:io';

import 'package:bopomofo_train/core/game.dart';
import 'package:bopomofo_train/features/parent/parent_gate.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'helpers.dart';

/// Privacy, the parent gate and the free version (docs/design.md: no
/// network, nothing leaves the phone, parent mode only through the gate).
void main() {
  test('the app asks for no permissions and takes no links from other apps', () {
    final manifest = File('android/app/src/main/AndroidManifest.xml').readAsStringSync();
    expect(manifest, isNot(contains('uses-permission')), reason: 'no internet, camera, microphone, location…');
    expect(manifest, contains('android:name="flutter_deeplinking_enabled" android:value="false"'));
    expect(manifest, contains('android:label="ㄅㄆㄇ小火車"'));
    final plist = File('ios/Runner/Info.plist').readAsStringSync();
    expect(plist, contains('<key>FlutterDeepLinkingEnabled</key>\n\t<false/>'));
    expect(plist, contains('<string>ㄅㄆㄇ小火車</string>'));
    expect(plist, isNot(contains('UsageDescription')), reason: 'no camera, microphone… prompts');
    expect(File('pubspec.yaml').readAsStringSync(), isNot(contains('source: system')));
    final gradle = File('android/app/build.gradle.kts').readAsStringSync();
    expect(gradle, contains('applicationId = "com.yaufan.bopomofotrain"'));
    expect(gradle, contains('System.getenv("BOPOMOFO_TRAIN_KEYSTORE")'));
    expect(gradle, contains('keyAlias = "kidspaint"'));
  });

  testWidgets('parent mode and unknown pages cannot be opened without the gate', (tester) async {
    final app = await TestApp.start(tester);
    app.go('/parent');
    await app.settle();
    expect(app.location, '/', reason: 'no pass from the gate');
    ParentPass.grant();
    app.go('/parent');
    await app.settle();
    expect(app.location, '/parent', reason: 'right after the gate');
    app.go('/');
    await app.settle();
    app.go('/parent');
    await app.settle();
    expect(app.location, '/', reason: 'the pass is used up');
    app.go('/write?sym=X');
    await app.settle(900);
    expect(app.location, '/write');
    await app.end();
  });

  testWidgets('the parent gate asks a sum written in characters and locks after three misses', (tester) async {
    final app = await TestApp.start(tester);
    await app.tapLabel('家長', ms: 600);
    expect(find.textContaining('加'), findsOneWidget);
    for (var i = 0; i < 3; i++) {
      await tester.tap(find.byKey(const ValueKey('gate-key-1')));
      await app.settle(100);
      await tester.tap(find.byKey(const ValueKey('gate-key-0')));
      await app.settle(100);
    }
    expect(find.textContaining('請等'), findsOneWidget);
    expect(app.location, '/');
    await app.end();
  });

  testWidgets('without a driver the child picks one first', (tester) async {
    final app = await TestApp.start(tester, game: const Game());
    expect(app.location, '/driver');
    app.go('/listen');
    await app.settle();
    expect(app.location, '/driver');
    await app.end();
  });

  testWidgets('the free version: 押韻接龍, 家裡找找 and stations 3 to 7 stay closed', (tester) async {
    final app = await TestApp.start(tester, game: const Game(driver: Driver.cat, settings: Settings(full: false)));
    app.go('/rhyme');
    await app.settle();
    expect(app.location, '/');
    app.go('/find');
    await app.settle();
    expect(app.location, '/');
    await app.tapLabel('押韻接龍');
    expect(app.location, '/');
    expect(app.voice.said.last, '完整版才有喔，請爸爸媽媽看看。');
    await tester.tap(find.byKey(const ValueKey('station-4')));
    await app.settle();
    expect(app.voice.said.last, '這一站在完整版裡，請爸爸媽媽看看。');
    await app.tapLabel('聽聽找找', ms: 700);
    expect(app.location, '/listen');
    await app.end();
  });

  testWidgets('the rest ends after an hour, and a clock moved back does not lock the app', (tester) async {
    final app = await TestApp.start(tester);
    app.change((g) => g.rest(app.now));
    await app.settle(2600);
    expect(app.location, '/rest');
    app.now = app.now.subtract(const Duration(hours: 3));
    await app.settle(2600);
    expect(app.location, '/', reason: 'the clock went back: counts as rested');
    expect(app.game.restSince, isNull);
    await app.end();
  });
}
