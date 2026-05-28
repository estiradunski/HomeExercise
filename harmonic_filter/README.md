# Part I Algo– Harmonic Filter

## Task

Given a WAV file containing a fundamental frequency f₀ and its harmonics (2×f₀, 3×f₀, …, N×f₀), implement a filter that removes all the harmonics while preserving the fundamental frequency.

**Example:**
- Input `in.wav` contains: 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550 Hz
- Filter parameters: `base_freq = 50 Hz`, `num_harmonics = 10`
- Output `out.wav` contains: **50 Hz only**

---

## Installation

Python 3.10+ required.

```bash
pip install numpy scipy
```

---

## File structure

```
harmonic_filter/
├── harmonic_filter_pkg/
│   ├── __init__.py          # Public API exports
│   ├── __main__.py          # Enables: python -m harmonic_filter_pkg
│   ├── models.py            # FilterResult dataclass (printed summary)
│   ├── wav_utils.py         # WAV file read / write / info
│   ├── fft_filter.py        # FFT-based notch filter
│   ├── iir_filter.py        # IIR-based notch filter cascade
│   ├── pipeline.py          # Orchestrates load → filter → save
│   └── cli.py               # Argument parser and main() entry point
├── generate_test_signal.py  # Generates a synthetic in.wav for testing
├── verify_output.py         # Checks that out.wav meets pass/fail thresholds
├── in.wav                   # Test input (50 Hz fundamental + harmonics)
└── out.wav                  # Filtered output (50 Hz only)
```

---

## How to run

### 1 — Generate test input

```bash
python generate_test_signal.py
```

Creates `in.wav` containing 50 Hz + harmonics at 100, 150, …, 550 Hz.

### 2 — Run the filter

```bash
python -m harmonic_filter_pkg -i in.wav -o out.wav -f 50 -n 10 --bandwidth 15
```

| Flag | Description |
|------|-------------|
| `-i` | Input WAV file |
| `-o` | Output WAV file |
| `-f` | Fundamental frequency to **preserve** (Hz) |
| `-n` | Number of harmonics to remove |
| `--bandwidth` | Notch width in Hz — use `15` for 8000 Hz / 1 s files, `2` (default) for 44100 Hz files |
| `--method` | `fft` (default) or `iir` |
| `--quality-factor` | IIR Q factor — higher = narrower notch (default: 30) |

### 3 — Verify the result

```bash
python verify_output.py -i in.wav -o out.wav -f 50 -n 10
```

Prints amplitude at each frequency and a PASS / FAIL verdict.
Pass criteria: fundamental within −1 dB, each harmonic suppressed by at least −40 dB.

---

## Python API

```python
from harmonic_filter_pkg import apply_harmonic_filter

result = apply_harmonic_filter(
    input_path="in.wav",
    output_path="out.wav",
    base_freq=50.0,
    num_harmonics=10,
)
print(result)
```
