from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

import numpy as np

from .fft_filter import filter_harmonics_fft
from .iir_filter import filter_harmonics_iir
from .models import FilterResult
from .wav_utils import load_wav, save_wav


__all__ = ["apply_harmonic_filter"]

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def apply_harmonic_filter(
    input_path: str | Path,
    output_path: str | Path,
    base_freq: float,
    num_harmonics: int,
    method: Literal["fft", "iir"] = "fft",
    *,
    notch_bandwidth_hz: float = 2.0,
    quality_factor: float = 30.0,
) -> FilterResult:
    input_path = Path(input_path)
    output_path = Path(output_path)

    logger.info("Loading '%s'", input_path)
    samples, sample_rate = load_wav(input_path)
    input_rms: float = float(np.sqrt(np.mean(samples ** 2)))

    logger.info(
        "  %d samples | %d Hz | %.3f s | RMS=%.6f",
        len(samples), sample_rate, len(samples) / sample_rate, input_rms,
    )

    if method == "fft":
        filtered, removed = filter_harmonics_fft(
            samples, sample_rate, base_freq, num_harmonics,
            notch_bandwidth_hz=notch_bandwidth_hz,
        )
    elif method == "iir":
        filtered, removed = filter_harmonics_iir(
            samples, sample_rate, base_freq, num_harmonics,
            quality_factor=quality_factor,
        )
    else:
        raise ValueError(f"Unknown method '{method}'. Valid choices are 'fft' and 'iir'.")

    output_rms: float = float(np.sqrt(np.mean(filtered ** 2)))
    save_wav(output_path, filtered, sample_rate)

    return FilterResult(
        input_path=input_path,
        output_path=output_path,
        base_freq=base_freq,
        num_harmonics=num_harmonics,
        method=method,
        sample_rate=sample_rate,
        num_samples=len(samples),
        removed_frequencies=removed,
        input_rms=input_rms,
        output_rms=output_rms,
    )
