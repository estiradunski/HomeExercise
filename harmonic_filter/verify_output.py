from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from harmonic_filter_pkg.wav_utils import load_wav


def peak_amplitude(
    samples: np.ndarray,
    sample_rate: int,
    target_hz: float,
    search_band_hz: float = 5.0,
) -> float:
    n = len(samples)
    magnitudes = (2.0 / n) * np.abs(np.fft.rfft(samples))
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    mask = np.abs(freqs - target_hz) <= search_band_hz
    return float(np.max(magnitudes[mask])) if mask.any() else 0.0


def db(ratio: float) -> str:
    if ratio <= 0:
        return "-inf dB"
    return f"{20.0 * np.log10(ratio):+.1f} dB"


def verify(
    input_path: str | Path,
    output_path: str | Path,
    base_freq: float,
    num_harmonics: int,
) -> bool:
    input_path = Path(input_path)
    output_path = Path(output_path)

    s_in,  sr_in  = load_wav(input_path)
    s_out, sr_out = load_wav(output_path)

    if sr_in != sr_out:
        print(f"WARNING: sample rates differ ({sr_in} vs {sr_out})")

    sr = sr_in
    nyquist = sr / 2.0

    frequencies = [base_freq * k for k in range(1, num_harmonics + 2)
                   if base_freq * k < nyquist]

    col_w = 10
    header = (
        f"  {'Freq':>6}   "
        f"{input_path.name:>{col_w}}   "
        f"{output_path.name:>{col_w}}   "
        f"{'Change':>10}   "
        f"{'Result'}"
    )
    sep = "  " + "-" * (len(header) - 2)

    print(f"\n  Input   : {input_path}  ({len(s_in)} samples @ {sr} Hz)")
    print(f"  Output  : {output_path}  ({len(s_out)} samples @ {sr_out} Hz)")
    print(f"  Base    : {base_freq:.0f} Hz  |  Harmonics to remove: {num_harmonics}\n")
    print(header)
    print(sep)

    all_passed = True

    for freq in frequencies:
        p_in  = peak_amplitude(s_in,  sr, freq)
        p_out = peak_amplitude(s_out, sr, freq)

        ratio = p_out / p_in if p_in > 1e-12 else 0.0
        change = db(ratio)
        is_base = (freq == base_freq)

        if is_base:
            passed = ratio >= 10 ** (-1.0 / 20)
            tag = "PRESERVED" if passed else "FAIL - too much loss"
        else:
            passed = ratio <= 10 ** (-40.0 / 20)
            tag = "REMOVED" if passed else f"FAIL - only {change}"

        if not passed:
            all_passed = False

        label = "[base]    " if is_base else "[harmonic]"
        print(
            f"  {freq:>5.0f} Hz   "
            f"{p_in:>{col_w}.5f}   "
            f"{p_out:>{col_w}.5f}   "
            f"{change:>10}   "
            f"{tag}  {label}"
        )

    print(sep)
    verdict = "PASS - filter output is correct." if all_passed else "FAIL - check rows marked FAIL above."
    print(f"\n  Verdict: {verdict}\n")
    return all_passed


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Verify harmonic filter output against input WAV."
    )
    parser.add_argument("-i", "--input",  default="in.wav",  metavar="PATH")
    parser.add_argument("-o", "--output", default="out.wav", metavar="PATH")
    parser.add_argument("-f", "--base-freq",     type=float, default=50.0,  metavar="HZ")
    parser.add_argument("-n", "--num-harmonics", type=int,   default=10,    metavar="N")
    args = parser.parse_args(argv)

    passed = verify(args.input, args.output, args.base_freq, args.num_harmonics)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
