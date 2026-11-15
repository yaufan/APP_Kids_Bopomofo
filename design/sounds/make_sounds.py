"""ㄅㄆㄇ小火車: every sound in the app, made here from sine waves and noise: nothing recorded,
nothing downloaded, every tune written for this app.

- Music (WAV, 16,000 Hz, seamless loops of 20 to 27 s): a bouncy xylophone and harmonica tune on
  the train's beat for the station, a quiet piano for 寫寫看, a clapping beat for 押韻接龍 (to hear
  the rhythm of the words) and a glockenspiel lullaby for the rest.
- Short sounds (WAV, 22,050 Hz): the toy train (the whistle 「嗚—」, the chimney's 「噗噗」, the
  wheels' dull 「喀噠喀噠」, a carriage coupling 「喀」, the station bell), and the game's (a symbol
  tapped 「叮」, right is a little rising xylophone, try-again is a soft 「咚」, the start dot, a stroke
  traced, a symbol done, a sticker, a whoosh, night).
- Every random choice uses a fixed seed (from the sound's name), so each run writes the same files.
- Soft for 4 to 6 year olds: a toy's sounds, never harsh or sudden.

    python3 design/sounds/make_sounds.py              # writes app/assets/sounds/*.wav
    python3 design/sounds/make_sounds.py tap whistle  # only these
    python3 design/sounds/make_sounds.py preview OUT.m4a   # all of them in a row (needs ffmpeg)
"""
import pathlib
import subprocess
import sys
import tempfile
import wave
import zlib

import numpy as np
from scipy.signal import lfilter

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "app" / "assets" / "sounds"
SR = 22050
LOOP_SR = 16000
LIMIT = 8_000_000       # bytes, the whole folder

NOTE = {f"{n}{o}": 440 * 2 ** ((k - 9) / 12 + o - 4) for o in range(1, 9) for k, n in enumerate("C C# D D# E F F# G G# A A# B".split())}
for _o in range(1, 9):
    for _f, _s in (("Db", "C#"), ("Eb", "D#"), ("Gb", "F#"), ("Ab", "G#"), ("Bb", "A#")):
        NOTE[f"{_f}{_o}"] = NOTE[f"{_s}{_o}"]


# ---------------------------------------------------------------- helpers
def rng(name):
    return np.random.default_rng(zlib.crc32(name.encode()))


def t_of(dur, sr=SR):
    return np.arange(int(dur * sr)) / sr


def env(n, attack=.005, release=.05, sr=SR):
    e = np.ones(n)
    a, r = max(1, min(n, int(attack * sr))), max(1, min(n, int(release * sr)))
    e[:a] = np.linspace(0, 1, a) ** 2
    e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


def adsr(n, a, d, s, r, sr=SR):
    """Attack, decay to sustain level s, release (seconds)."""
    e = np.full(n, s, float)
    ia, idd, ir = int(a * sr), int(d * sr), int(r * sr)
    ia = max(1, min(ia, n))
    e[:ia] = np.linspace(0, 1, ia)
    j = min(n, ia + idd)
    if j > ia:
        e[ia:j] = np.linspace(1, s, j - ia)
    ir = max(1, min(ir, n))
    e[-ir:] *= np.linspace(1, 0, ir) ** 1.5
    return e


def lowpass(x, cutoff, sr=SR):
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(spec, len(x))


def bandpass(x, lo, hi, sr=SR):
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4)
    return np.fft.irfft(spec, len(x))


def partial(freq, t, sr):
    return np.sin(2 * np.pi * freq * t) if freq < .45 * sr else np.zeros_like(t)


def bell(freq, dur=.8, sr=SR, bright=.6):
    """A soft glockenspiel / music-box note."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * .35))
         + .3 * bright * partial(freq * 2.76, t, sr) * np.exp(-t / (dur * .12))
         + .12 * bright * partial(freq * 5.4, t, sr) * np.exp(-t / (dur * .06)))
    return x * env(len(t), .002, .04, sr)


def kalimba(freq, dur=.9, sr=SR):
    t = t_of(dur, sr)
    x = partial(freq, t, sr) * np.exp(-t / (dur * .3)) + .25 * partial(freq * 3.0, t, sr) * np.exp(-t / .04) + .1 * partial(freq * 5.2, t, sr) * np.exp(-t / .02)
    return x * env(len(t), .003, .05, sr)


def pad(freqs, dur, sr=SR, swell=.6):
    """A soft, slowly swelling chord (a few detuned sines)."""
    t = t_of(dur, sr)
    x = np.zeros_like(t)
    for f in freqs:
        for det in (-.15, .15):
            x += np.sin(2 * np.pi * (f + det) * t) + .25 * partial(2 * f + det, t, sr)
    return x / len(freqs) * adsr(len(t), dur * swell * .5, .1, .9, dur * .45, sr)


def place(total, parts, sr=SR):
    out = np.zeros(int(total * sr))
    for start, sig in parts:
        i = int(start * sr)
        j = min(len(out), i + len(sig))
        if j > i:
            out[i:j] += sig[: j - i]
    return out


def place_loop(total, parts, sr):
    """Like place, but what runs past the end comes back in at the start (a seamless loop)."""
    n = int(total * sr)
    out = np.zeros(n)
    for start, sig in parts:
        i = int(start * sr) % n
        k = 0
        while k < len(sig):
            j = min(n, i + len(sig) - k)
            out[i:j] += sig[k: k + j - i]
            k += j - i
            i = 0
    return out


def resonator(x, freq, bw, sr=SR):
    r = np.exp(-np.pi * bw / sr)
    th = 2 * np.pi * freq / sr
    return lfilter([1 - r], [1, -2 * r * np.cos(th), r * r], x)


def voice(f0, formants, dur, sr=SR, breath=.15, seed="v"):
    """A soft little hum: a buzz whose pitch follows f0 (an array or a number) through formants."""
    n = int(dur * sr)
    f = np.full(n, f0, float) if np.isscalar(f0) else np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(f0)), f0)
    ph = np.cumsum(f) / sr
    buzz = sum(np.sin(2 * np.pi * k * ph) / k ** 1.2 for k in range(1, 14) if True)
    buzz = buzz + breath * rng(seed).standard_normal(n)
    y = sum(g * resonator(buzz, fr, bw, sr) for fr, bw, g in formants)
    return y / max(1e-9, np.abs(y).max())


VOWEL_M = [(300, 90, 1.0), (900, 160, .25), (2300, 220, .08)]      # a closed-mouth "mmm"
VOWEL_U = [(330, 90, 1.0), (850, 140, .3), (2250, 200, .1)]        # "uu"
VOWEL_A = [(750, 110, 1.0), (1200, 130, .6), (2500, 200, .2)]      # "aa"
VOWEL_E = [(450, 100, 1.0), (1900, 160, .4), (2600, 220, .15)]     # "eh"


def noise(n, name):
    return rng(name).standard_normal(n)


def norm(x, peak=.7):
    return x / max(1e-9, np.abs(x).max()) * peak


def fade_edges(x, sr=SR, ms=6):
    k = max(1, int(sr * ms / 1000))
    x = x.copy()
    x[:k] *= np.linspace(0, 1, k)
    x[-k:] *= np.linspace(1, 0, k)
    return x


# ---------------------------------------------------------------- instruments
def xylo(freq, dur=.5, sr=SR):
    """A wooden xylophone / marimba bar: a quick, woody decay."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / .16) + .35 * partial(freq * 3.93, t, sr) * np.exp(-t / .035)
         + .1 * partial(freq * 9.2, t, sr) * np.exp(-t / .012))
    return x * env(len(t), .002, .03, sr)


def harmonica(freq, dur=.5, sr=SR):
    """A soft reed: odd and even harmonics, a little vibrato, breathy."""
    t = t_of(dur, sr)
    vib = 1 + .006 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t / .15, 0, 1)
    ph = np.cumsum(freq * vib) / sr
    x = sum((.9 ** k) / k * np.sin(2 * np.pi * k * ph) for k in range(1, 8) if k * freq < .45 * sr)
    x = lowpass(x + .04 * rng(f"harm{freq:.0f}").standard_normal(len(t)), 2600, sr)
    return x * adsr(len(t), .03, .08, .75, min(.12, dur * .4), sr)


def piano(freq, dur=1.2, sr=SR):
    """A soft piano-like note."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / .7) + .4 * partial(freq * 2.001, t, sr) * np.exp(-t / .35)
         + .15 * partial(freq * 3.003, t, sr) * np.exp(-t / .18) + .06 * partial(freq * 4.01, t, sr) * np.exp(-t / .1))
    return x * env(len(t), .004, .08, sr)


def knock(dur, f, name, sr=SR, decay=.02, cut=1400):
    """A dull wooden knock (a toy's click)."""
    t = t_of(dur, sr)
    x = lowpass(noise(len(t), name), cut, sr) * np.exp(-t / decay) * .7 + np.sin(2 * np.pi * f * t) * np.exp(-t / (decay * 1.4))
    return x


# ---------------------------------------------------------------- the short sounds
def s_tap():
    n = int(.13 * SR)
    x = lowpass(noise(n, "tap"), 900) * np.exp(-t_of(.13) / .025) * .6 + np.sin(2 * np.pi * 180 * t_of(.13)) * np.exp(-t_of(.13) / .03)
    return norm(x, .5)


def s_pop():
    t = t_of(.16)
    f = np.linspace(500, 1100, len(t))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .04)
    return norm(x, .55)


def s_ding():
    return norm(bell(NOTE["A6"], .9, bright=.7), .5)


def s_right():
    """A little rising xylophone run: right!"""
    return norm(place(.9, [(0, xylo(NOTE["C6"])), (.09, xylo(NOTE["E6"])), (.18, xylo(NOTE["G6"])), (.27, xylo(NOTE["C7"], .6))]), .55)


def s_try():
    """A soft low 「咚」: not this one, nothing lost."""
    return norm(lowpass(xylo(NOTE["G4"], .45) + .5 * xylo(NOTE["D4"], .45), 1500), .45)


def s_whistle():
    """The toy train's 「嗚—」: three soft pipes together, a breath of steam, the pitch sagging at the end."""
    d = 1.3
    t = t_of(d)
    sag = 1 - .03 * np.clip((t - .95) / .35, 0, 1)
    x = np.zeros_like(t)
    for f in (NOTE["F5"], NOTE["A5"], NOTE["C6"]):
        ph = np.cumsum(f * sag * (1 + .003 * np.sin(2 * np.pi * 6 * t))) / SR
        x += np.sin(2 * np.pi * ph) + .18 * np.sin(4 * np.pi * ph)
    x = x / 3 + .12 * bandpass(noise(len(t), "whistle"), 600, 3000)
    return norm(x * adsr(len(t), .08, .1, .85, .3), .55)


def s_puff():
    """The chimney's 「噗噗」: two soft puffs of steam."""
    one = lambda k: lowpass(noise(int(.16 * SR), f"puff{k}"), 700) * np.sin(np.pi * t_of(.16) / .16) ** 2
    return norm(place(.42, [(0, one(0)), (.2, .8 * one(1))]), .4)


def s_clack():
    """The wheels on the track, 「喀噠喀噠」: dull toy clicks in pairs."""
    parts = []
    for i, at in enumerate((0, .14, .5, .64)):
        parts.append((at, knock(.12, 220 if i % 2 == 0 else 180, f"clack{i}", decay=.018, cut=1100)))
    return norm(place(.85, parts), .45)


def s_couple():
    """A carriage hooked on: 「喀」, a metal-ish click and a knock."""
    t = t_of(.25)
    click = bandpass(noise(len(t), "couple"), 1800, 4200) * np.exp(-t / .008) * .5
    return norm(place(.3, [(0, click + knock(.25, 160, "couple2", decay=.03)), (.07, .6 * knock(.2, 240, "couple3", decay=.02))]), .55)


def s_chime():
    """The station bell: ding-dong."""
    return norm(place(1.4, [(0, bell(NOTE["E6"], 1.0, bright=.4)), (.32, bell(NOTE["C6"], 1.1, bright=.4))]), .5)


def s_star():
    """The start dot tapped: a tiny sparkle."""
    return norm(place(.5, [(0, bell(NOTE["E7"], .35, bright=.3)), (.06, bell(NOTE["B7"], .3, bright=.2))]), .4)


def s_stroke():
    """A stroke traced to its end."""
    return norm(place(.7, [(0, xylo(NOTE["G5"])), (.1, xylo(NOTE["D6"], .55))]), .5)


def s_done():
    """A symbol done: a little fanfare."""
    return norm(place(1.3, [(0, xylo(NOTE["C6"])), (.12, xylo(NOTE["E6"])), (.24, xylo(NOTE["G6"])), (.4, bell(NOTE["C7"], .8, bright=.5)),
                            (.4, .6 * xylo(NOTE["E6"], .7))]), .55)


def s_sticker():
    t = t_of(.3)
    f = np.linspace(400, 900, len(t))
    pop = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .05)
    return norm(place(.8, [(0, pop), (.12, .5 * bell(NOTE["G6"], .6)), (.2, .4 * bell(NOTE["D7"], .5))]), .5)


def s_whoosh():
    n = int(.5 * SR)
    t = t_of(.5)
    x = np.zeros(n)
    nz = noise(n, "whoosh")
    for i, c in enumerate(np.linspace(600, 2400, 8)):
        seg = slice(i * n // 8, (i + 1) * n // 8)
        x[seg] = bandpass(nz, c * .7, c * 1.3)[seg]
    return norm(lowpass(x, 3000) * np.sin(np.pi * t / .5) ** 2, .4)


def s_night():
    return norm(place(1.5, [(0, bell(NOTE["G5"], .9, bright=.3)), (.3, bell(NOTE["E5"], .9, bright=.3)), (.6, bell(NOTE["C5"], .9, bright=.3))]), .45)


# ---------------------------------------------------------------- the music
def loop(total, parts, sr=LOOP_SR, peak=.42):
    x = place_loop(total, parts, sr)
    return x / max(1e-9, np.abs(x).max()) * peak


def m_station():
    """Bouncy: xylophone and harmonica in C, the train's 「噗噗」 on the off-beats, 112 bpm, 48 beats."""
    bpm, beats = 112, 48
    b = 60 / bpm
    sr = LOOP_SR
    mel = [(0, "E5", 1), (1, "G5", 1), (2, "C6", 1.5), (3.5, "B5", .5), (4, "A5", 1), (5, "G5", 1), (6, "E5", 2),
           (8, "F5", 1), (9, "A5", 1), (10, "D6", 1.5), (11.5, "C6", .5), (12, "B5", 1), (13, "A5", 1), (14, "G5", 2),
           (16, "E5", 1), (17, "G5", 1), (18, "C6", 1), (19, "E6", 1), (20, "D6", 1), (21, "C6", 1), (22, "A5", 2),
           (24, "G5", 1), (25, "A5", .5), (25.5, "B5", .5), (26, "C6", 1), (27, "D6", 1), (28, "E6", 2), (30, "C6", 2),
           (32, "A5", 1), (33, "C6", 1), (34, "F6", 1.5), (35.5, "E6", .5), (36, "D6", 1), (37, "C6", 1), (38, "A5", 2),
           (40, "G5", 1), (41, "E5", 1), (42, "F5", 1), (43, "D5", 1), (44, "C5", 2), (46, "G5", 2)]
    chords = [(0, "C3"), (4, "A2"), (8, "F2"), (12, "G2"), (16, "C3"), (20, "A2"), (24, "F2"), (28, "G2"), (32, "F2"), (36, "D3"), (40, "G2"), (44, "C3")]
    parts = []
    for i, (beat, nt, ln) in enumerate(mel):
        inst = harmonica(NOTE[nt], ln * b * .95, sr) * .55 if 16 <= beat < 32 else xylo(NOTE[nt], max(.35, ln * b), sr)
        parts.append((beat * b, inst))
    for beat, root in chords:
        for k in range(4):
            parts.append(((beat + k) * b, .55 * xylo(NOTE[root] * (1 if k % 2 == 0 else 1.5), .4, sr)))
    for k in range(beats * 2):
        if k % 2 == 1:
            t = t_of(.11, sr)
            puff = lowpass(noise(len(t), f"chug{k % 4}"), 900, sr) * np.sin(np.pi * t / .11) ** 2
            parts.append((k * b / 2, .18 * puff))
    return loop(beats * b, parts)


def m_write():
    """Quiet: a slow piano in F, 72 bpm, 28 beats."""
    bpm, beats = 72, 28
    b = 60 / bpm
    sr = LOOP_SR
    mel = [(0, "A5", 2), (2, "C6", 1), (3, "A5", 1), (4, "G5", 3), (8, "F5", 2), (10, "A5", 1), (11, "C6", 1), (12, "D6", 3),
           (16, "C6", 2), (18, "A5", 1), (19, "G5", 1), (20, "F5", 2), (22, "G5", 2), (24, "F5", 4)]
    chords = [(0, ["F3", "C4", "A4"]), (4, ["C3", "G3", "E4"]), (8, ["D3", "A3", "F4"]), (12, ["A2", "E3", "C4"]),
              (16, ["Bb2", "F3", "D4"]), (20, ["F2", "C3", "A3"]), (24, ["C3", "G3", "E4"])]
    parts = [(beat * b, .9 * piano(NOTE[nt], max(1.2, ln * b * 1.4), sr)) for beat, nt, ln in mel]
    for beat, notes in chords:
        for k, nt in enumerate(notes):
            parts.append(((beat + k * .5) * b, .45 * piano(NOTE[nt], 2.6, sr)))
    return loop(beats * b, parts, peak=.36)


def m_rhyme():
    """A clapping beat (kick and clap) under a marimba tune in G, 100 bpm, 40 beats."""
    bpm, beats = 100, 40
    b = 60 / bpm
    sr = LOOP_SR
    parts = []
    for k in range(beats):
        t = t_of(.2, sr)
        if k % 2 == 0:
            kick = np.sin(2 * np.pi * np.cumsum(np.linspace(120, 50, len(t))) / sr) * np.exp(-t / .09)
            parts.append((k * b, .7 * kick))
        else:
            clap = sum(bandpass(noise(len(t), f"clap{k % 3}{j}"), 900, 3500, sr) * np.exp(-np.maximum(t - j * .012, 0) / .03) * (t >= j * .012)
                       for j in range(3))
            parts.append((k * b, .32 * clap))
    mel = [(0, "G5"), (1, "B5"), (2, "D6"), (3, "B5"), (4, "C6"), (5, "A5"), (6, "G5"), (8, "E5"), (9, "G5"), (10, "A5"), (11, "G5"),
           (12, "D5"), (14, "G5"), (16, "G5"), (17, "B5"), (18, "D6"), (19, "E6"), (20, "D6"), (21, "B5"), (22, "A5"), (24, "C6"),
           (25, "B5"), (26, "A5"), (27, "G5"), (28, "F#5"), (30, "A5"), (32, "B5"), (33, "A5"), (34, "G5"), (35, "E5"), (36, "D5"),
           (37, "F#5"), (38, "G5")]
    for beat, nt in mel:
        parts.append((beat * b, .8 * xylo(NOTE[nt], .5, sr)))
    for k, root in enumerate(["G2", "E2", "C3", "D3", "G2", "E2", "C3", "D3", "G2", "D3"]):
        parts.append((k * 4 * b, .6 * xylo(NOTE[root], 1.0, sr)))
        parts.append(((k * 4 + 2) * b, .5 * xylo(NOTE[root] * 1.5, .8, sr)))
    return loop(beats * b, parts, peak=.4)


def m_rest():
    """A glockenspiel lullaby, 56 bpm, 24 beats."""
    bpm, beats = 56, 24
    b = 60 / bpm
    sr = LOOP_SR
    mel = [(0, "E5", 2), (2, "D5", 1), (3, "C5", 1), (4, "D5", 2), (6, "G4", 2), (8, "E5", 2), (10, "G5", 1), (11, "E5", 1),
           (12, "D5", 4), (16, "C5", 2), (18, "D5", 1), (19, "E5", 1), (20, "C5", 4)]
    ch = [(0, ["C4", "E4", "G4"]), (4, ["G3", "B3", "D4"]), (8, ["A3", "C4", "E4"]), (12, ["G3", "B3", "D4"]), (16, ["F3", "A3", "C4"]),
          (20, ["C4", "E4", "G4"])]
    parts = [(beat * b, .7 * bell(NOTE[nt], max(.6, ln * b * 1.6), sr, .25)) for beat, nt, ln in mel]
    for beat, notes in ch:
        parts.append((beat * b, .45 * pad([NOTE[x] for x in notes], 4 * b * 1.15, sr)))
    return loop(beats * b, parts, peak=.38)


SOUNDS = {
    "tap": s_tap, "pop": s_pop, "ding": s_ding, "right": s_right, "try": s_try, "whistle": s_whistle, "puff": s_puff,
    "clack": s_clack, "couple": s_couple, "chime": s_chime, "star": s_star, "stroke": s_stroke, "done": s_done,
    "sticker": s_sticker, "whoosh": s_whoosh, "night": s_night,
}
MUSIC = {"music_station": m_station, "music_write": m_write, "music_rhyme": m_rhyme, "music_rest": m_rest}
LONG = {}


def write(path, x, sr):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def make(names=None):
    OUT.mkdir(parents=True, exist_ok=True)
    wanted = set(names or [*SOUNDS, *MUSIC])
    for name, f in SOUNDS.items():
        if name not in wanted:
            continue
        x = fade_edges(np.asarray(f(), float))
        d = len(x) / SR
        if d > LONG.get(name, 1.5):
            raise SystemExit(f"{name}: {d:.2f} s is too long")
        if np.abs(x).max() > .75:
            raise SystemExit(f"{name}: too loud")
        write(OUT / f"{name}.wav", x, SR)
        print(f"  {name:20s} {d:5.2f} s  peak {np.abs(x).max():.2f}")
    for name, f in MUSIC.items():
        if name not in wanted:
            continue
        x = np.asarray(f(), float)
        d = len(x) / LOOP_SR
        jump = abs(x[0] - x[-1])
        if not 18 <= d <= 30 or jump > .05:
            raise SystemExit(f"{name}: {d:.1f} s, seam jump {jump:.3f}")
        write(OUT / f"{name}.wav", x, LOOP_SR)
        print(f"  {name:20s} {d:5.2f} s  loop seam {jump:.3f}")
    known = {f"{n}.wav" for n in [*SOUNDS, *MUSIC]}
    extra = [p.name for p in OUT.glob("*.wav") if p.name not in known]
    if extra:
        raise SystemExit(f"files nobody makes: {extra}")
    size = sum(p.stat().st_size for p in OUT.glob("*.wav"))
    if size > LIMIT:
        raise SystemExit(f"{size} bytes: over {LIMIT}")
    print(f"{len(known)} sounds, {size:,} bytes")


def preview(out):
    with tempfile.TemporaryDirectory(dir="/dev/shm") as tmp:
        parts = []
        for name in [*MUSIC, *SOUNDS]:
            parts.append(str(OUT / f"{name}.wav"))
        lst = pathlib.Path(tmp) / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-ar", "22050", "-c:a", "aac", "-b:a", "96k", out], check=True)
    print(out)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["preview"]:
        preview(args[1])
    else:
        make(args or None)
