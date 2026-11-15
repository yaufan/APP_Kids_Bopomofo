import 'package:flutter/material.dart';

/// The app's colours (docs/art.md 「顏色」: saturated toy colours, deep plum
/// words, never pure black).
abstract final class Toy {
  static const ink = Color(0xFF2E2440);
  static const inkSoft = Color(0xFF7A7090);
  static const cream = Color(0xFFFFF6E6);
  static const paper = Color(0xFFFFFBF3);
  static const red = Color(0xFFF2545B);
  static const pink = Color(0xFFF59BC2);
  static const orange = Color(0xFFFFA35C);
  static const yellow = Color(0xFFFFD44F);
  static const gold = Color(0xFFFFB627);
  static const green = Color(0xFF4DBA6A);
  static const mint = Color(0xFF7FD08A);
  static const teal = Color(0xFF4FD1C5);
  static const sky = Color(0xFF8CCBF2);
  static const blue = Color(0xFF4E9DF0);
  static const navy = Color(0xFF3A4E8C);
  static const purple = Color(0xFFB79AF0);
  static const sea1 = Color(0xFF8ED6F5);
  static const sea2 = Color(0xFF5FBDEB);
  static const night1 = Color(0xFF2E2F66);
  static const night2 = Color(0xFF6C5A9E);
  static const parentBg = Color(0xFFF4F2EE);
  static const line = Color(0xFFE8DCC8);

  /// The darker rim of a toy part in [c].
  static Color rim(Color c) => Color.lerp(c, ink, .45)!;
}

abstract final class ToyTheme {
  /// jf open 粉圓 (OFL): a rounded typeface made in Taiwan, with every 注音 symbol.
  static const font = 'Huninn';

  static ThemeData light() {
    final base = ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: Toy.red, surface: Toy.cream),
      scaffoldBackgroundColor: Toy.cream,
      fontFamily: font,
      materialTapTargetSize: MaterialTapTargetSize.padded,
    );
    return base.copyWith(textTheme: base.textTheme.apply(bodyColor: Toy.ink, displayColor: Toy.ink, fontFamily: font));
  }
}
