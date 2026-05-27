from __future__ import annotations

import argparse
import logging
import sys

from .pipeline import apply_harmonic_filter


__all__ = ["main"]

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="harmonic_filter",
        description=(
            "Remove harmonics (2xf0, 3xf0, ...) from a WAV file "
            "while preserving the fundamental frequency f0."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python -m harmonic_filter_pkg -i in.wav -o out.wav -f 50 -n 10\n"
            "  python -m harmonic_filter_pkg -i in.wav -o out_iir.wav "
            "-f 50 -n 10 --method iir --quality-factor 35\n"
        ),
    )

    io = parser.add_argument_group("I/O")
    io.add_argument("-i", "--input",  required=True, metavar="PATH", help="Input WAV file")
    io.add_argument("-o", "--output", required=True, metavar="PATH", help="Output WAV file")

    filt = parser.add_argument_group("filter parameters")
    filt.add_argument("-f", "--base-freq",     type=float, required=True, metavar="HZ",
                      help="Base (fundamental) frequency to preserve (Hz)")
    filt.add_argument("-n", "--num-harmonics", type=int,   required=True, metavar="N",
                      help="Number of harmonics to remove (starting from 2x base)")
    filt.add_argument("--method", choices=["fft", "iir"], default="fft",
                      help="Filter method: fft (default) or iir")

    fft_grp = parser.add_argument_group("FFT options")
    fft_grp.add_argument("--bandwidth", type=float, default=2.0, metavar="HZ",
                         help="Notch full-width in Hz (default: 2.0)")
    fft_grp.add_argument("--no-taper", action="store_true",
                         help="Use a hard rectangular notch instead of Gaussian taper")

    iir_grp = parser.add_argument_group("IIR options")
    iir_grp.add_argument("--quality-factor", type=float, default=30.0, metavar="Q",
                         help="Notch Q factor - higher = narrower (default: 30.0)")

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable DEBUG-level logging")
    return parser


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s - %(message)s",
    )
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        result = apply_harmonic_filter(
            input_path=args.input,
            output_path=args.output,
            base_freq=args.base_freq,
            num_harmonics=args.num_harmonics,
            method=args.method,
            notch_bandwidth_hz=args.bandwidth,
            taper=not args.no_taper,
            quality_factor=args.quality_factor,
        )
        print(result)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
