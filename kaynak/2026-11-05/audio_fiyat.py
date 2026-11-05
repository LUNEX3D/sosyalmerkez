"""Hakediş videosu miks (anlatım Sosyal Merkez'de eklenir): ritim + her bildirimde 'ding', soru anında gerilim, cevap vuruşu, tıklama sesleri, slogan vuruşları."""
import json, wave, subprocess, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
M = json.loads(subprocess.run(["python3", HERE + "render_fiyat.py", "meta"], capture_output=True, text=True).stdout)
DUR = M["dur"]; SR = 48000; N = int(DUR * SR); rng = np.random.default_rng(7)
BPM = 120; BEAT = 60 / BPM
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
music = np.zeros(N); sfx = np.zeros(N)
def add(buf, x, at, g=1.0):
    i = int(at * SR)
    if i >= N or i < 0: return
    x = x[:N - i]; buf[i:i + len(x)] += g * x
def kick(at, g=0.22):
    n = int(0.3 * SR); t_ = np.arange(n) / SR
    add(music, np.sin(2 * np.pi * np.cumsum(46 + 90 * np.exp(-t_ * 30)) / SR) * env(n, 0.002, 0.12), at, g)
def hat(at, g=0.03):
    n = int(0.05 * SR); add(music, filt(rng.normal(0, 1, n), lo=7000) * env(n, 0.001, 0.012), at, g)
def clap(at, g=0.06):
    n = int(0.2 * SR); add(music, filt(rng.normal(0, 1, n), lo=1200, hi=6000) * env(n, 0.001, 0.05), at, g)
def pluck(at, m, g=0.04, d=0.12):
    n = int(0.3 * SR); t_ = np.arange(n) / SR
    add(music, (np.sin(2 * np.pi * note(m) * t_) + 0.3 * np.sin(4 * np.pi * note(m) * t_)) * env(n, 0.003, d), at, g)
def hit(at, g=0.45, f0=46):
    n = int(1.2 * SR); t_ = np.arange(n) / SR
    add(sfx, np.sin(2 * np.pi * (f0 + 60 * np.exp(-t_ * 25)) * t_) * env(n, 0.002, 0.35) + 0.25 * rng.normal(0, 1, n) * env(n, 0.0005, 0.006), at, g)
def ding(at, m=88, g=0.07):
    n = int(0.6 * SR); t_ = np.arange(n) / SR
    add(sfx, np.sin(2 * np.pi * note(m) * t_) * env(n, 0.002, 0.15), at, g)
    add(sfx, np.sin(2 * np.pi * note(m + 5) * t_) * env(n, 0.002, 0.22), at + 0.08, g)
def tick(at, g=0.05):
    n = int(0.04 * SR); t_ = np.arange(n) / SR
    add(sfx, np.sin(2 * np.pi * 2600 * t_) * env(n, 0.0005, 0.01), at, g)
def click(at, g=0.12):
    n = int(0.03 * SR); add(sfx, filt(rng.normal(0, 1, n), lo=2000) * env(n, 0.0005, 0.005), at, g)
def whoosh(at, dur=0.35, g=0.05):
    n = int(dur * SR); t_ = np.arange(n) / SR
    add(sfx, filt(rng.normal(0, 1, n) * np.sin(np.pi * t_ / dur) ** 2, lo=1200, hi=5000), at, g)
def swoosh_ok(at, g=0.06):
    n = int(0.25 * SR); t_ = np.arange(n) / SR; f = note(79) * (note(91) / note(79)) ** (t_ / 0.25)
    add(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.08), at, g)
def drone(t0, t1, g=0.14):
    tt = np.arange(int((t1 - t0) * SR)) / SR
    dr = (np.sin(2 * np.pi * note(38) * tt) + 0.5 * np.sin(2 * np.pi * note(45) * 1.004 * tt)) * np.minimum(1, tt / 0.3) * np.minimum(1, (tt[-1] - tt) / 0.3)
    add(music, filt(dr, hi=700), t0, g)
prog = [69, 72, 76, 72, 67, 71, 74, 71]; prog2 = [72, 76, 79, 76, 74, 77, 81, 77]
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

hit(0.0, 0.35, 48); ding(0.3, 84, 0.05)
bed(0.4, M["q"], prog, 0.8, clapon=False)
for k, d_ in enumerate(M["drops"]):
    hit(d_, 0.28 if k % 2 == 0 else 0.22, 52 - k * 1.2); whoosh(d_ - 0.08, 0.15, 0.03)
whoosh(M["q"] - 0.15)
drone(M["q"], M["ans"], 0.14)
seg = (M["ans"] - M["cd"]) / 3
for k in range(3): tick(M["cd"] + k * seg, 0.12)
hit(M["ans"], 0.45, 44); hit(M["ans"] + 0.6, 0.55, 40); ding(M["ans"] + 0.9, 76, 0.05)
drone(M["ans"], M["pan"], 0.1)
whoosh(M["pan"] - 0.15)
bed(M["pan"], M["s"], prog2, 0.9)
ding(M["tab"], 80, 0.05); hit(M["riv"], 0.3, 50); hit(M["warn"], 0.4, 44)
swoosh_ok(M["rec"], 0.06)
click(M["clk"], 0.15); swoosh_ok(M["clk"] + 0.05, 0.07)
hit(M["s"] + 0.2, 0.5, 44); hit(M["s2"], 0.55, 40); drone(M["s"], M["end"], 0.12)
whoosh(M["end"] - 0.2); hit(M["end"], 0.4, 46); ding(M["end"] + 0.35, 88, 0.06)
bed(M["end"] + 0.2, DUR, prog2, 0.85)
music = music / np.max(np.abs(music)) * 0.8
fade = np.ones(N); fs = int((DUR - 0.3) * SR); fade[fs:] = np.linspace(1, 0, N - fs)
mix = (music * 0.6 + sfx * 0.6) * fade
mix = mix / np.max(np.abs(mix)) * 0.9
s = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
w = wave.open(HERE + "mix.wav", "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(s.tobytes()); w.close()
print("ok", DUR)
