import 'dart:math' as math;

import 'book.dart';

/// 小火車 (4 to 5) or 大火車 (5 to 6): docs/design.md 「4～5 歲和 5～6 歲的差別」.
enum Level {
  small('小火車', '4～5 歲'),
  big('大火車', '5～6 歲');

  const Level(this.zh, this.ages);

  final String zh;
  final String ages;
}

/// The driver the child picked: only a look, no name to type.
enum Driver {
  bear('小熊'),
  rabbit('小兔'),
  cat('小貓'),
  penguin('小企鵝');

  const Driver(this.zh);

  final String zh;
}

/// The four things to do at a station (and 家裡找找, which is not part of it).
enum Module {
  see('認符號'),
  listen('聽聽找找'),
  write('寫寫看'),
  rhyme('押韻接龍'),
  find('家裡找找');

  const Module(this.zh);

  final String zh;
}

/// What a parent set (parent mode).
class Settings {
  const Settings({
    this.level = Level.small,
    this.minutes = 15,
    this.order = Order.common,
    this.stations = const {0, 1, 2, 3, 4, 5, 6},
    this.slow = false,
    this.twice = false,
    this.leftHanded = false,
    this.music = true,
    this.sounds = true,
    this.voice = true,
    this.full = true,
  });

  final Level level;

  /// How long one sitting may be before a rest.
  final int minutes;
  final Order order;

  /// The stations to play (at least one).
  final Set<int> stations;

  /// A slower voice.
  final bool slow;

  /// Every word said twice.
  final bool twice;
  final bool leftHanded;
  final bool music;
  final bool sounds;
  final bool voice;

  /// The full version (everything); on while testing.
  final bool full;

  static const minuteChoices = [5, 10, 15, 20, 30];
  static const stationCount = 7;

  /// The free version has the first two stations.
  static const freeStations = 2;

  /// The modules of the free version.
  static const freeModules = {Module.see, Module.listen, Module.write};

  bool open(Module m) => full || freeModules.contains(m);

  bool unlocked(int station) => full || station < freeStations;

  /// Stations a parent turned off are skipped; at least one that can be
  /// played is always on (in the free version, one of the first two: with
  /// only full-version stations left on, nothing would be on at all and the
  /// train would go back to a station the parent turned off).
  static Set<int> tidy(Set<int> s, {bool full = true}) {
    final out = {for (final i in s) if (i >= 0 && i < stationCount) i};
    if (!out.any((i) => full || i < freeStations)) out.add(0);
    return out;
  }

  Settings copyWith({Level? level, int? minutes, Order? order, Set<int>? stations, bool? slow, bool? twice, bool? leftHanded, bool? music, bool? sounds, bool? voice, bool? full}) => Settings(
        level: level ?? this.level,
        minutes: minutes ?? this.minutes,
        order: order ?? this.order,
        stations: tidy(stations ?? this.stations, full: full ?? this.full),
        slow: slow ?? this.slow,
        twice: twice ?? this.twice,
        leftHanded: leftHanded ?? this.leftHanded,
        music: music ?? this.music,
        sounds: sounds ?? this.sounds,
        voice: voice ?? this.voice,
        full: full ?? this.full,
      );

  Map<String, dynamic> toJson() => {
        'level': level.name,
        'minutes': minutes,
        'order': order.name,
        'stations': (stations.toList()..sort()),
        'slow': slow,
        'twice': twice,
        'leftHanded': leftHanded,
        'music': music,
        'sounds': sounds,
        'voice': voice,
        'full': full,
      };

  factory Settings.fromJson(Map<String, dynamic> j) {
    final m = j['minutes'], st = j['stations'];
    bool flag(String k, bool d) => j[k] is bool ? j[k] as bool : d;
    final full = flag('full', true);
    return Settings(
      level: Level.values.asNameMap()[j['level']] ?? Level.small,
      minutes: m is int && minuteChoices.contains(m) ? m : 15,
      order: Order.values.asNameMap()[j['order']] ?? Order.common,
      stations: st is List ? tidy({for (final i in st) if (i is int) i}, full: full) : const {0, 1, 2, 3, 4, 5, 6},
      slow: flag('slow', false),
      twice: flag('twice', false),
      leftHanded: flag('leftHanded', false),
      music: flag('music', true),
      sounds: flag('sounds', true),
      voice: flag('voice', true),
      full: full,
    );
  }
}

/// How far a symbol has come: 認過 (its carriage is on the train), how many
/// times it was found right in 聽聽找找, 描過.
class Progress {
  const Progress({this.seen = false, this.heard = 0, this.traced = false});

  final bool seen;
  final int heard;
  final bool traced;

  /// 「聽對 3 次」 in parent mode.
  static const heardWell = 3;

  Progress copyWith({bool? seen, int? heard, bool? traced}) => Progress(seen: seen ?? this.seen, heard: heard ?? this.heard, traced: traced ?? this.traced);

  Map<String, dynamic> toJson() => {'seen': seen, 'heard': heard, 'traced': traced};

  static Progress fromJson(dynamic j) {
    if (j is! Map) return const Progress();
    final h = j['heard'];
    return Progress(seen: j['seen'] == true, heard: h is int && h > 0 ? math.min(h, 9999) : 0, traced: j['traced'] == true);
  }
}

/// Today's 家裡找找 card.
class HomeTask {
  const HomeTask(this.day, this.sym, {this.found});

  final String day;
  final String sym;

  /// The sticker picked when it was found (a word id).
  final String? found;

  Map<String, dynamic> toJson() => {'day': day, 'sym': sym, if (found != null) 'found': found};

  static HomeTask? fromJson(dynamic j, Bopomofo book) {
    if (j is! Map || j['day'] is! String || Days.parse(j['day'] as String) == null) return null;
    final sym = j['sym'], found = j['found'];
    if (sym is! String || !book.symbols.containsKey(sym)) return null;
    return HomeTask(j['day'] as String, sym, found: found is String && book.words.containsKey(found) ? found : null);
  }
}

/// What was played today (parent mode): minutes, modules, right answers.
class DayLog {
  const DayLog(this.day, {this.seconds = 0, this.modules = const {}});

  final String day;
  final int seconds;
  final Set<Module> modules;

  Map<String, dynamic> toJson() => {'day': day, 'seconds': seconds, 'modules': [for (final m in modules) m.name]};

  static DayLog? fromJson(dynamic j) {
    if (j is! Map || j['day'] is! String || Days.parse(j['day'] as String) == null) return null;
    final s = j['seconds'], m = j['modules'];
    return DayLog(j['day'] as String, seconds: s is int && s > 0 ? s : 0, modules: {
      if (m is List)
        for (final n in m) ?Module.values.asNameMap()[n],
    });
  }
}

abstract final class Days {
  static String key(DateTime d) => '${d.year.toString().padLeft(4, '0')}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

  static DateTime? parse(String k) {
    final m = RegExp(r'^(\d{4})-(\d{2})-(\d{2})$').firstMatch(k);
    if (m == null) return null;
    final d = DateTime(int.parse(m[1]!), int.parse(m[2]!), int.parse(m[3]!));
    return key(d) == k ? d : null;
  }

  /// Days since 1 January 2000 (the 家裡找找 card changes every day).
  static int number(DateTime d) => DateTime.utc(d.year, d.month, d.day).difference(DateTime.utc(2000)).inDays;
}

/// Everything kept on the phone. One small file (store.dart).
class Game {
  const Game({
    this.settings = const Settings(),
    this.driver,
    this.progress = const {},
    this.rhymed = const {},
    this.skipped = const {},
    this.arrived = const {},
    this.at,
    this.stickers = const [],
    this.task,
    this.today,
    this.rhymeAsked = 0,
    this.rhymeRight = 0,
    this.restSince,
  });

  final Settings settings;
  final Driver? driver;

  /// Symbol → how far it has come.
  final Map<String, Progress> progress;

  /// Stations whose 押韻接龍 round was played ('common:4').
  final Set<String> rhymed;

  /// Stations a parent jumped past ('textbook:2').
  final Set<String> skipped;

  /// The furthest station the train has been seen arriving at, per order.
  final Map<Order, int> arrived;

  /// The station the child tapped on the map to play (null: the current one).
  final int? at;

  /// Stickers on the locomotive from 家裡找找 (word ids, oldest first).
  final List<String> stickers;
  final HomeTask? task;
  final DayLog? today;

  /// 押韻接龍 questions asked, and answered right the first time.
  final int rhymeAsked;
  final int rhymeRight;

  /// When the play time ran out (null: playing).
  final DateTime? restSince;

  static const restLength = Duration(hours: 1);
  static const maxStickers = 60;

  Progress of(String sym) => progress[sym] ?? const Progress();

  static String key(Order o, int station) => '${o.name}:$station';

  /// Resting for an hour after the time ran out. A clock moved back (now
  /// before the rest began) does not lock the app: it counts as rested.
  bool resting(DateTime now) {
    final since = restSince;
    if (since == null) return false;
    final d = now.difference(since);
    return !d.isNegative && d < restLength;
  }

  // ---- stations

  bool enabled(int i) => settings.stations.contains(i) && settings.unlocked(i);

  List<String> row(Bopomofo b, int i) => b.rows(settings.order)[i];

  bool seenAll(Bopomofo b, int i) => row(b, i).every((s) => of(s).seen);
  bool heardAll(Bopomofo b, int i) => row(b, i).every((s) => of(s).heard > 0);
  bool tracedAll(Bopomofo b, int i) => row(b, i).every((s) => of(s).traced);
  bool rhymedAt(int i) => rhymed.contains(key(settings.order, i));

  /// Whether [m] is done at station [i] (the little checks on the buttons).
  bool moduleDone(Bopomofo b, int i, Module m) => switch (m) {
        Module.see => seenAll(b, i),
        Module.listen => heardAll(b, i),
        Module.write => tracedAll(b, i),
        Module.rhyme => rhymedAt(i),
        Module.find => false,
      };

  /// A station is passed when its symbols were seen, found by ear and
  /// traced, and (in the full version) its 押韻接龍 played, or a parent
  /// jumped past it.
  bool passed(Bopomofo b, int i) =>
      skipped.contains(key(settings.order, i)) || (seenAll(b, i) && heardAll(b, i) && tracedAll(b, i) && (!settings.full || rhymedAt(i)));

  /// The station the train is at: the first one turned on and not passed
  /// (all passed: the last one turned on).
  int current(Bopomofo b) {
    final on = [for (var i = 0; i < Settings.stationCount; i++) if (enabled(i)) i];
    if (on.isEmpty) return 0;
    return on.firstWhere((i) => !passed(b, i), orElse: () => on.last);
  }

  /// Whether the child may play station [i] (tapping it on the map): one
  /// turned on, up to the train.
  bool reachable(Bopomofo b, int i) => enabled(i) && (i <= current(b) || passed(b, i));

  /// The station being played.
  int playing(Bopomofo b) {
    final a = at;
    return a != null && reachable(b, a) ? a : current(b);
  }

  /// Whether every turned-on station is passed (環島完成).
  bool finished(Bopomofo b) => [for (var i = 0; i < Settings.stationCount; i++) if (enabled(i)) i].every((i) => passed(b, i));

  /// The symbols of the stations up to [station], for mixing into questions;
  /// stations a parent turned off are left out.
  List<String> pool(Bopomofo b, int station) => [
        for (var i = 0; i <= station; i++)
          if (i == station || enabled(i)) ...row(b, i),
      ];

  // ---- changes

  Game copyWith({
    Settings? settings,
    Driver? driver,
    bool clearDriver = false,
    Map<String, Progress>? progress,
    Set<String>? rhymed,
    Set<String>? skipped,
    Map<Order, int>? arrived,
    int? at,
    bool clearAt = false,
    List<String>? stickers,
    HomeTask? task,
    DayLog? today,
    int? rhymeAsked,
    int? rhymeRight,
    DateTime? restSince,
    bool clearRest = false,
  }) =>
      Game(
        settings: settings ?? this.settings,
        driver: clearDriver ? null : (driver ?? this.driver),
        progress: progress ?? this.progress,
        rhymed: rhymed ?? this.rhymed,
        skipped: skipped ?? this.skipped,
        arrived: arrived ?? this.arrived,
        at: clearAt ? null : (at ?? this.at),
        stickers: stickers ?? this.stickers,
        task: task ?? this.task,
        today: today ?? this.today,
        rhymeAsked: rhymeAsked ?? this.rhymeAsked,
        rhymeRight: rhymeRight ?? this.rhymeRight,
        restSince: clearRest ? null : (restSince ?? this.restSince),
      );

  Game _symbol(String sym, Progress Function(Progress p) f) => copyWith(progress: {...progress, sym: f(of(sym))});

  /// 認符號: the symbol's carriage goes on the train.
  Game saw(String sym) => of(sym).seen ? this : _symbol(sym, (p) => p.copyWith(seen: true));

  /// 聽聽找找: found right.
  Game heard(String sym) => _symbol(sym, (p) => p.copyWith(heard: p.heard + 1));

  /// 寫寫看: traced along its roads.
  Game traced(String sym) => of(sym).traced ? this : _symbol(sym, (p) => p.copyWith(traced: true));

  /// A round of 押韻接龍 played at [station].
  Game rhymeRound(int station) => copyWith(rhymed: {...rhymed, key(settings.order, station)});

  /// One 押韻接龍 question answered ([firstTry]: right the first time).
  Game rhymeAnswer(bool firstTry) => copyWith(rhymeAsked: rhymeAsked + 1, rhymeRight: rhymeRight + (firstTry ? 1 : 0));

  /// Parent mode's 「直接跳到這一站」: the stations before it count as passed,
  /// and the ones from it on no longer do (unless really played), so a jump
  /// back after jumping too far does not leave the stations between skipped.
  /// The train plays there, even when the station was already played.
  Game jump(int station) => copyWith(
        skipped: {
          for (final k in skipped)
            if (!k.startsWith('${settings.order.name}:')) k,
          for (var i = 0; i < station; i++) key(settings.order, i),
        },
        at: station,
      );

  /// The child tapped a station on the map.
  Game playAt(int station) => copyWith(at: station);

  /// The train has been shown arriving at [station].
  Game arrive(int station) => copyWith(arrived: {...arrived, settings.order: station});

  /// The furthest station the train was seen at (in this order).
  int arrivedAt() => arrived[settings.order] ?? 0;

  Game withSettings(Settings s) {
    final orderChanged = s.order != settings.order;
    return copyWith(settings: s, clearAt: orderChanged);
  }

  // ---- 家裡找找

  /// Today's card: the one already given, or a new one from the symbols
  /// seen so far (the playing station's first, if none), a different one
  /// each day.
  HomeTask taskFor(Bopomofo b, DateTime now) {
    final day = Days.key(now);
    final t = task;
    if (t != null && t.day == day) return t;
    final upTo = playing(b);
    final seen = [for (final s in pool(b, upTo)) if (of(s).seen) s];
    final from = seen.isEmpty ? row(b, upTo) : seen;
    return HomeTask(day, from[Days.number(now) % from.length]);
  }

  /// Whether today's card was looked at yet.
  bool taskGiven(DateTime now) => task?.day == Days.key(now);

  Game giveTask(Bopomofo b, DateTime now) => taskGiven(now) ? this : copyWith(task: taskFor(b, now));

  /// Found it: the sticker goes on the locomotive.
  Game found(Bopomofo b, DateTime now, String wordId) => foundFor(taskFor(b, now), wordId);

  /// Found the things of card [shown] (the one on screen, even if midnight
  /// has passed since it was given: tomorrow's card stays new).
  Game foundFor(HomeTask shown, String wordId) {
    final list = [...stickers, wordId];
    return copyWith(task: HomeTask(shown.day, shown.sym, found: wordId), stickers: list.skip(math.max(0, list.length - maxStickers)).toList());
  }

  // ---- today (parent mode)

  DayLog log(DateTime now) {
    final d = today;
    return d != null && d.day == Days.key(now) ? d : DayLog(Days.key(now));
  }

  Game played(DateTime now, int seconds) {
    final d = log(now);
    return copyWith(today: DayLog(d.day, seconds: d.seconds + seconds, modules: d.modules));
  }

  Game did(DateTime now, Module m) {
    final d = log(now);
    return d.modules.contains(m) ? this : copyWith(today: DayLog(d.day, seconds: d.seconds, modules: {...d.modules, m}));
  }

  Game rest(DateTime now) => copyWith(restSince: now);

  Game playOn() => copyWith(clearRest: true);

  Map<String, dynamic> toJson() => {
        'version': 1,
        'settings': settings.toJson(),
        if (driver != null) 'driver': driver!.name,
        'progress': {for (final e in progress.entries) e.key: e.value.toJson()},
        'rhymed': rhymed.toList(),
        'skipped': skipped.toList(),
        'arrived': {for (final e in arrived.entries) e.key.name: e.value},
        if (at != null) 'at': at,
        'stickers': stickers,
        if (task != null) 'task': task!.toJson(),
        if (today != null) 'today': today!.toJson(),
        'rhymeAsked': rhymeAsked,
        'rhymeRight': rhymeRight,
        if (restSince != null) 'restSince': restSince!.toIso8601String(),
      };

  /// Reads a saved game; anything broken or unknown is left out.
  factory Game.fromJson(Map<String, dynamic>? j, Bopomofo book) {
    if (j == null) return const Game();
    final p = j['progress'], rh = j['rhymed'], sk = j['skipped'], ar = j['arrived'], st = j['stickers'], rest = j['restSince'];
    final at = j['at'], asked = j['rhymeAsked'], right = j['rhymeRight'];
    bool stationKey(dynamic k) {
      if (k is! String) return false;
      final m = RegExp(r'^(common|textbook):([0-6])$').firstMatch(k);
      return m != null;
    }

    final askedN = asked is int && asked > 0 ? asked : 0;
    return Game(
      settings: Settings.fromJson(j['settings'] is Map ? (j['settings'] as Map).cast<String, dynamic>() : const {}),
      driver: Driver.values.asNameMap()[j['driver']],
      progress: {
        if (p is Map)
          for (final e in p.entries)
            if (e.key is String && book.symbols.containsKey(e.key)) e.key as String: Progress.fromJson(e.value),
      },
      rhymed: {
        if (rh is List)
          for (final k in rh)
            if (stationKey(k)) k as String,
      },
      skipped: {
        if (sk is List)
          for (final k in sk)
            if (stationKey(k)) k as String,
      },
      arrived: {
        if (ar is Map)
          for (final o in Order.values)
            if (ar[o.name] is int && (ar[o.name] as int) >= 0 && (ar[o.name] as int) < Settings.stationCount) o: ar[o.name] as int,
      },
      at: at is int && at >= 0 && at < Settings.stationCount ? at : null,
      stickers: [
        if (st is List)
          for (final s in st)
            if (s is String && book.words.containsKey(s)) s,
      ],
      task: HomeTask.fromJson(j['task'], book),
      today: DayLog.fromJson(j['today']),
      rhymeAsked: askedN,
      rhymeRight: right is int && right > 0 ? math.min(right, askedN) : 0,
      restSince: rest is String ? DateTime.tryParse(rest) : null,
    );
  }
}
