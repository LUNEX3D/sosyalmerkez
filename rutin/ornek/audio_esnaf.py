"""Esnaf3D videosu ses miksi (Onur Büyü seslendirmesi vo_a.mp3 + kısılan müzik + efektler).
Kullanım: python3 audio_esnaf.py -> mix_esnaf.wav
"""
import json, wave, subprocess
import numpy as np

HERE = "/mnt/project-files/dashtock-esnaf3d/kaynak/"
M = json.loads(subprocess.run(["python3", HERE + "render_esnaf.py", "meta"], capture_output=True, text=True).stdout)
DUR = M["dur"]
SR = 48000; N = int(DUR * SR); rng = np.random.default_rng(21)
BPM = 118; BEAT = 60 / BPM

def note(m): return 440 * 2 ** ((m - 69) / 12)
def env(n, a, d):
    e = np.ones(n); ai = int(a * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    e[ai:] = np.exp(-np.arange(n - ai) / (d * SR)); return e
def filt(x, lo=None, hi=None):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    if hi: X *= 1 / (1 + (f / hi) ** 4)
    if lo: X *= 1 - 1 / (1 + (f / lo) ** 4)
    return np.fft.irfft(X, len(x))
def add(buf, x, at, g=1.0):
    i = int(at * SR)
    if i >= N or i < 0: return
    x = x[:N - i]; buf[i:i + len(x)] += g * x
music = np.zeros(N); sfx = np.zeros(N)
def kick(at, g=0.24):
    n = int(0.3 * SR); t_ = np.arange(n) / SR
    add(music, np.sin(2 * np.pi * np.cumsum(46 + 90 * np.exp(-t_ * 30)) / SR) * env(n, 0.002, 0.12), at, g)
def hat(at, g=0.03):
    n = int(0.05 * SR); add(music, filt(rng.normal(0, 1, n), lo=7000) * env(n, 0.001, 0.012), at, g)
def clap(at, g=0.07):
    n = int(0.2 * SR); add(music, filt(rng.normal(0, 1, n), lo=1200, hi=6000) * env(n, 0.001, 0.05), at, g)
def pluck(at, m, g=0.05, d=0.12):
    n = int(0.3 * SR); t_ = np.arange(n) / SR
    add(music, (np.sin(2 * np.pi * note(m) * t_) + 0.3 * np.sin(4 * np.pi * note(m) * t_)) * env(n, 0.003, d), at, g)
def hit(at, g=0.45, f0=46):
    n = int(1.2 * SR); t_ = np.arange(n) / SR
    add(sfx, np.sin(2 * np.pi * (f0 + 60 * np.exp(-t_ * 25)) * t_) * env(n, 0.002, 0.35) + 0.25 * rng.normal(0, 1, n) * env(n, 0.0005, 0.006), at, g)
def ding(at, g=0.07):                            # bildirim
    n = int(0.6 * SR); t_ = np.arange(n) / SR
    add(sfx, (np.sin(2 * np.pi * note(88) * t_) * env(n, 0.002, 0.15)), at, g)
    add(sfx, (np.sin(2 * np.pi * note(93) * t_) * env(n, 0.002, 0.25)), at + 0.09, g)
def kaching(at, g=0.06):                         # kasa
    n = int(0.5 * SR); t_ = np.arange(n) / SR
    add(sfx, filt(rng.normal(0, 1, n), lo=4000) * env(n, 0.001, 0.03), at, g)
    add(sfx, sum(np.sin(2 * np.pi * f * t_) for f in (2637, 3520, 4186)) * env(n, 0.002, 0.18) * 0.4, at + 0.05, g)
def tick(at, g=0.05):
    n = int(0.04 * SR); t_ = np.arange(n) / SR
    add(sfx, np.sin(2 * np.pi * 2600 * t_) * env(n, 0.0005, 0.01), at, g)
def scratch(at, g=0.12):                         # plak durması
    n = int(0.45 * SR); t_ = np.arange(n) / SR; p = t_ / t_[-1]
    add(sfx, filt(rng.normal(0, 1, n), lo=500, hi=4000) * np.sin(2 * np.pi * (6 - 4 * p) * t_) ** 2 * (1 - p), at, g)
    add(sfx, np.sin(2 * np.pi * np.cumsum(400 * (1 - p) ** 2 + 60) / SR) * (1 - p) * 0.5, at, g)
def fall(at, dur, g=0.05):                       # düşen sayaç
    n = int(dur * SR); t_ = np.arange(n) / SR; p = t_ / t_[-1]
    add(sfx, np.sin(2 * np.pi * np.cumsum(900 * (1 - p) ** 1.5 + 90) / SR) * (0.4 + 0.6 * p), at, g)
    a = at
    while a < at + dur: tick(a, 0.025); a += 0.05 + 0.1 * ((a - at) / dur) ** 2
def whoosh(at, dur=0.4, g=0.05, lo=1200):
    n = int(dur * SR); t_ = np.arange(n) / SR
    add(sfx, filt(rng.normal(0, 1, n) * np.sin(np.pi * t_ / dur) ** 2, lo=lo, hi=5000), at, g)
def bloop(at, m0, m1, g=0.06, dur=0.18):
    n = int(dur * SR); t_ = np.arange(n) / SR; f = note(m0) * (note(m1) / note(m0)) ** (t_ / dur)
    add(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, dur / 3), at, g)
def alarm(at, dur=0.8, g=0.04):
    n = int(dur * SR); t_ = np.arange(n) / SR
    add(sfx, np.sign(np.sin(2 * np.pi * (700 + 200 * np.sign(np.sin(2 * np.pi * 6 * t_))) * t_)) * 0.3 * np.minimum(1, (dur - t_) / 0.1), at, g)
def rewind(at, dur=0.8, g=0.06):
    n = int(dur * SR); t_ = np.arange(n) / SR; p = t_ / dur
    add(sfx, filt(rng.normal(0, 1, n), lo=800, hi=6000) * (0.5 + 0.5 * np.sin(2 * np.pi * (20 + 40 * p) * t_)) * np.sin(np.pi * p), at, g)
    add(sfx, np.sin(2 * np.pi * np.cumsum(200 + 1400 * p) / SR) * np.sin(np.pi * p) * 0.4, at, g)
prog = [69, 72, 76, 72, 67, 71, 74, 71]
prog2 = [72, 76, 79, 76, 74, 77, 81, 77]
def bed(t0, t1, pr, g=1.0, clapon=True):
    k = 0
    while t0 + k * BEAT / 2 < t1:
        a = t0 + k * BEAT / 2
        if k % 2 == 0: kick(a, 0.2 * g)
        hat(a, 0.02 if k % 2 == 0 else 0.03)
        if clapon and k % 4 == 2: clap(a, 0.06 * g)
        pluck(a, pr[k % 8], 0.035 * g)
        if k % 4 == 0: pluck(a, pr[k % 8] - 24, 0.06 * g, 0.2)
        k += 1
def drone(t0, t1, g=0.16):
    tt = np.arange(int((t1 - t0) * SR)) / SR
    dr = (np.sin(2 * np.pi * note(38) * tt) + 0.5 * np.sin(2 * np.pi * note(45) * 1.004 * tt)) * np.minimum(1, tt / 0.3) * np.minimum(1, (tt[-1] - tt) / 0.3)
    add(music, filt(dr, hi=700), t0, g)
hit(0.0, 0.3, 50); whoosh(0.0, 0.4, 0.04)
bed(0.0, M["a"] - 0.1, prog, 0.6, False)
for k in ("a", "b", "c"): bloop(M[k], 72, 84, 0.06, 0.12)
drone(M["a"], M["zero"], 0.1)
for k in range(5): tick(M["a"] + 0.5 + k * 0.6, 0.05)
hit(M["zero"], 0.55, 42); ding(M["zero"] + 0.2, 0.07)
whoosh(M["ed"] - 0.15, 0.3, 0.05)
bed(M["ed"], M["panel"], prog2, 0.9)
whoosh(M["drag"] + 0.1, 0.6, 0.035, 2000); hit(M["drop"], 0.35, 60); bloop(M["drop"], 60, 76, 0.06)
for x in M["th"]: tick(x, 0.08); bloop(x, 79, 86, 0.04, 0.1)
whoosh(M["up"] + 0.1, 0.5, 0.05); bloop(M["file"] + 0.35, 64, 79, 0.06, 0.2)
fall(M["file"] + 0.35, 0.55, 0.025)
fall(M["price"], 0.6, 0.03); ding(M["price"] + 0.62, 0.06)
kaching(M["pay"] + 0.15, 0.09); hit(M["pay"] + 0.15, 0.3, 56)
ding(M["panel"] + 0.1, 0.08)
for x in M["rows"]: bloop(x, 76, 88, 0.06, 0.14); tick(x + 0.2, 0.06)
hit(M["ready"], 0.45, 46)
bed(M["panel"], M["s1"], prog2, 0.9)
hit(M["s1"], 0.5, 42); scratch(M["s1"] + 0.25, 0.08)
drone(M["s1"], M["end"], 0.12)
whoosh(M["s2"], 0.4, 0.06); hit(M["s2"] + 0.3, 0.45, 44)
whoosh(M["end"] - 0.2, 0.35, 0.05); hit(M["end"], 0.4, 46); ding(M["end"] + 0.35, 0.06)
bed(M["end"] + 0.2, DUR, prog2, 0.85)
music = music / np.max(np.abs(music)) * 0.8
# seslendirme + müzik kısma
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", HERE + "vo_a.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
vo = np.zeros(N); v = np.frombuffer(raw, dtype=np.float32).astype(float); i0 = int(M["vo_off"] * SR); v = v[:N - i0]; vo[i0:i0 + len(v)] = v
vo = vo / np.max(np.abs(vo)) * 0.9
e = np.convolve(np.abs(vo), np.ones(int(0.05 * SR)) / int(0.05 * SR), "same")
e = np.convolve((e > 0.02).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
duck = 1 - 0.6 * np.clip(e, 0, 1)
music = music * duck; sfx = sfx * (1 - 0.35 * np.clip(e, 0, 1))
fade = np.ones(N); fs = int((DUR - 0.25) * SR); fade[fs:] = np.linspace(1, 0, N - fs)
mix = (music * 0.55 + sfx * 0.5 + vo * 1.0) * fade
mix = mix / np.max(np.abs(mix)) * 0.93
s = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
w = wave.open(HERE + "mix_esnaf.wav", "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(s.tobytes()); w.close()
print("ok", DUR)
