import json
import sys
import urllib.request
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))


def peak_amplitude(samples: np.ndarray, sample_rate: int, target_hz: float) -> float:
    n = len(samples)
    magnitudes = (2.0 / n) * np.abs(np.fft.rfft(samples))
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    mask = np.abs(freqs - target_hz) <= 5.0
    return float(np.max(magnitudes[mask])) if mask.any() else 0.0


def db(ratio: float) -> str:
    if ratio <= 0:
        return "-inf dB"
    return f"{20.0 * np.log10(ratio):+.1f} dB"


SAMPLE_RATE = 8000
BASE_FREQ = 50.0
NUM_HARMONICS = 10
DURATION = 1.0

t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
signal = sum(
    (1.0 / k) * np.sin(2 * np.pi * k * BASE_FREQ * t)
    for k in range(1, NUM_HARMONICS + 2)
)
signal /= np.max(np.abs(signal))

payload = json.dumps({
    "sample_rate": SAMPLE_RATE,
    "base_freq": BASE_FREQ,
    "num_harmonics": NUM_HARMONICS,
    "samples": signal.tolist(),
}).encode()

req = urllib.request.Request(
    "http://localhost:8001/harmonic_filter",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())

filtered = np.array(data["filtered_samples"])
frequencies = [BASE_FREQ * k for k in range(1, NUM_HARMONICS + 2)]

col_w = 10
print(f"\n  {'Freq':>6}   {'input':>{col_w}}   {'filtered':>{col_w}}   {'Change':>10}   Result")
print("  " + "-" * 62)

all_passed = True
for freq in frequencies:
    p_in = peak_amplitude(signal, SAMPLE_RATE, freq)
    p_out = peak_amplitude(filtered, SAMPLE_RATE, freq)
    ratio = p_out / p_in if p_in > 1e-12 else 0.0
    change = db(ratio)
    is_base = freq == BASE_FREQ

    if is_base:
        passed = ratio >= 10 ** (-1.0 / 20)
        tag = "PRESERVED" if passed else "FAIL - too much loss"
    else:
        passed = ratio <= 10 ** (-40.0 / 20)
        tag = "REMOVED" if passed else f"FAIL - only {change}"

    if not passed:
        all_passed = False

    label = "[base]    " if is_base else "[harmonic]"
    print(f"  {freq:>5.0f} Hz   {p_in:>{col_w}.5f}   {p_out:>{col_w}.5f}   {change:>10}   {tag}  {label}")

print("  " + "-" * 62)
verdict = "PASS" if all_passed else "FAIL"
print(f"\n  Verdict: {verdict}\n")
