from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from harmonic_filter_pkg.wav_utils import save_wav

__all__ = ["generate_harmonic_signal"]

_DEFAULT_BASE_FREQ: float = 50.0
_DEFAULT_NUM_HARMONICS: int = 10
_DEFAULT_SAMPLE_RATE: int = 44_100
_DEFAULT_DURATION: float = 2.0
_DEFAULT_DECAY: float = 1.0


def generate_harmonic_signal(
    base_freq: float = _DEFAULT_BASE_FREQ,
    num_harmonics: int = _DEFAULT_NUM_HARMONICS,
    sample_rate: int = _DEFAULT_SAMPLE_RATE,
    duration: float = _DEFAULT_DURATION,
    decay: float = _DEFAULT_DECAY,
) -> np.ndarray:
    if base_freq <= 0:
        raise ValueError(f"base_freq must be positive, got {base_freq!r}")
    if num_harmonics < 0:
        raise ValueError(f"num_harmonics must be >= 0, got {num_harmonics!r}")
    if sample_rate <= 0:
        raise ValueError(f"sample_rate must be positive, got {sample_rate!r}")
    if duration <= 0:
        raise ValueError(f"duration must be positive, got {duration!r}")
    if decay <= 0:
        raise ValueError(f"decay must be positive, got {decay!r}")

    n_samples: int = int(sample_rate * duration)
    t: np.ndarray = np.linspace(0.0, duration, n_samples, endpoint=False)

    signal = np.zeros(n_samples, dtype=np.float64)
    nyquist: float = sample_rate / 2.0

    for k in range(1, num_harmonics + 2):
        freq: float = k * base_freq
        if freq >= nyquist:
            break
        amplitude: float = 1.0 / (k ** decay)
        signal += amplitude * np.sin(2.0 * np.pi * freq * t)

    peak: float = float(np.max(np.abs(signal)))
    if peak > 0.0:
        signal /= peak

    return signal


def _print_summary(
    output_path: Path,
    base_freq: float,
    num_harmonics: int,
    sample_rate: int,
    duration: float,
    n_samples: int,
) -> None:
    harmonics_hz = [
        int(base_freq * k) for k in range(2, num_harmonics + 2)
        if k * base_freq < sample_rate / 2
    ]
    print(f"\nGenerated: {output_path.resolve()}")
    print(f"  Fundamental   : {base_freq:.1f} Hz  [will be preserved by filter]")
    print(f"  Harmonics     : {', '.join(map(str, harmonics_hz))} Hz  [to be removed]")
    print(f"  Sample rate   : {sample_rate} Hz")
    print(f"  Duration      : {duration:.2f} s  ({n_samples} samples)")
    print(f"\nTo filter:  python harmonic_filter.py "
          f"-i {output_path} -o out.wav -f {base_freq:.0f} -n {num_harmonics}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="generate_test_signal",
        description="Generate a synthetic harmonic WAV file for filter testing.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--output", default="in.wav", metavar="PATH",
                        help="Output WAV file path")
    parser.add_argument("--base-freq", type=float, default=_DEFAULT_BASE_FREQ,
                        metavar="HZ", help="Fundamental frequency in Hz")
    parser.add_argument("--num-harmonics", type=int, default=_DEFAULT_NUM_HARMONICS,
                        metavar="N", help="Number of harmonics above the fundamental")
    parser.add_argument("--sample-rate", type=int, default=_DEFAULT_SAMPLE_RATE,
                        metavar="HZ", help="Sampling frequency in Hz")
    parser.add_argument("--duration", type=float, default=_DEFAULT_DURATION,
                        metavar="S", help="Signal duration in seconds")
    parser.add_argument("--decay", type=float, default=_DEFAULT_DECAY,
                        metavar="A", help="Amplitude decay exponent 1/k^A")

    args = parser.parse_args(argv)
    output_path = Path(args.output)

    try:
        signal = generate_harmonic_signal(
            base_freq=args.base_freq,
            num_harmonics=args.num_harmonics,
            sample_rate=args.sample_rate,
            duration=args.duration,
            decay=args.decay,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    save_wav(output_path, signal, args.sample_rate)
    _print_summary(
        output_path,
        args.base_freq,
        args.num_harmonics,
        args.sample_rate,
        args.duration,
        len(signal),
    )


if __name__ == "__main__":
    main()
