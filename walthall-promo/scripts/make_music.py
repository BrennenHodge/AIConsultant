"""Synthesize the 30s music bed (80 BPM, warm pad + plucked arpeggio + bass).

Writes assets/music_raw.wav; scripts/master_audio.sh then uses FFmpeg to add
room reverb, EQ, fades and loudness-normalize it into assets/music.wav.
Scene cuts in index.html land on beats of this grid (beat = 0.75s).
"""
import sys
import wave

import numpy as np

SR = 44100
BPM = 80
BEAT = 60 / BPM          # 0.75s
BAR = BEAT * 4           # 3.0s
DUR = 30.0
N = int(SR * DUR)
t_all = np.arange(N) / SR


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


# D major, warm and corporate-but-classy: Dmaj9 Bm7 Gmaj7 A6sus ... resolve on D.
CHORDS = [
    [50, 57, 61, 64, 66],  # Dmaj9  (D A C# E F#)
    [47, 54, 57, 62, 66],  # Bm7
    [43, 55, 59, 62, 66],  # Gmaj7
    [45, 57, 62, 64, 66],  # A6sus
    [50, 57, 61, 64, 66],
    [47, 54, 57, 62, 66],
    [43, 55, 59, 62, 66],
    [45, 57, 61, 64, 67],  # A7
    [50, 57, 62, 66, 69],  # D (resolution, rings out)
    [50, 57, 62, 66, 69],
]

out = np.zeros(N)


def add(sig, start):
    i = int(start * SR)
    j = min(N, i + len(sig))
    if i < N:
        out[i:j] += sig[: j - i]


def pad_note(f, dur, amp):
    n = int(dur * SR)
    t = np.arange(n) / SR
    # two slightly detuned voices with soft harmonics
    s = sum(
        a * (np.sin(2 * np.pi * f * k * (1 + d) * t))
        for k, a in ((1, 1.0), (2, 0.28), (3, 0.12))
        for d in (-0.0018, 0.0018)
    )
    att, rel = 0.9, 1.2
    env = np.minimum(1, t / att) * np.minimum(1, (dur - t) / rel).clip(0)
    return amp * s * env


def pluck(f, amp, dur=1.4):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t)
    env = (1 - np.exp(-t * 300)) * np.exp(-t * 3.2)
    return amp * s * env


def bass(f, dur, amp):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * 2 * f * t)
    env = np.minimum(1, t / 0.05) * np.exp(-t * 0.5) * np.minimum(1, (dur - t) / 0.3).clip(0)
    return amp * s * env


for b, chord in enumerate(CHORDS):
    start = b * BAR
    last = b >= 8
    pad_len = BAR + 1.3 if not last else (DUR - start)
    for m in chord[1:]:
        add(pad_note(hz(m), pad_len, 0.045), start)
    add(bass(hz(chord[0] - 12), BAR if not last else DUR - start, 0.20), start)
    if b == 0 or last and b == 9:
        continue  # first bar: pad swells in alone; final bar: let it ring
    # eighth-note arpeggio pattern over the upper chord tones (+1 octave)
    pattern = [0, 2, 1, 3, 2, 4, 3, 2]
    for k, idx in enumerate(pattern):
        note = chord[1:][idx % 4] + 12
        accent = 1.0 if k % 2 == 0 else 0.7
        add(pluck(hz(note), 0.07 * accent), start + k * BEAT / 2)

# Chime accents on the title reveal (4.5s) and the call-to-action (25.5s)
for at, notes in ((4.5, [74, 78, 81]), (25.5, [74, 78, 81, 86])):
    for i, m in enumerate(notes):
        add(pluck(hz(m), 0.09, dur=2.5), at + i * 0.06)

# Soft swell at the start
out *= np.minimum(1, t_all / 1.2)
out /= np.max(np.abs(out)) * 1.12

stereo = np.stack([out, np.roll(out, 220)], axis=1)  # tiny Haas widening
pcm = (stereo * 32767).astype(np.int16)
path = sys.argv[1] if len(sys.argv) > 1 else "assets/music_raw.wav"
with wave.open(path, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", path)
