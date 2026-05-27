from __future__ import annotations

import logging

import numpy as np
from scipy.signal import iirnotch, sosfiltfilt, tf2sos


__all__ = ["filter_harmonics_iir"]

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def filter_harmonics_iir(
    samples: np.ndarray,
    sample_rate: int,
    base_freq: float,
    num_harmonics: int,
    quality_factor: float = 30.0,
) -> tuple[np.ndarray, list[float]]:
    if base_freq <= 0:
        raise ValueError(f"base_freq must be positive, got {base_freq!r}")
    if num_harmonics < 1:
        raise ValueError(f"num_harmonics must be >= 1, got {num_harmonics!r}")
    if quality_factor <= 0:
        raise ValueError(f"quality_factor must be positive, got {quality_factor!r}")

    nyquist: float = sample_rate / 2.0
    filtered: np.ndarray = samples.copy()
    removed_frequencies: list[float] = []

    for k in range(2, num_harmonics + 2):
        harmonic_freq: float = k * base_freq
        if harmonic_freq >= nyquist:
            logger.debug(
                "Harmonic %d*%.1f Hz = %.1f Hz >= Nyquist (%.1f Hz); stopping.",
                k, base_freq, harmonic_freq, nyquist,
            )
            break

        b, a = iirnotch(w0=harmonic_freq, Q=quality_factor, fs=sample_rate)
        sos = tf2sos(b, a)
        filtered = sosfiltfilt(sos, filtered)

        removed_frequencies.append(harmonic_freq)
        logger.debug("  IIR notch at %.1f Hz  (k=%d, Q=%.1f)", harmonic_freq, k, quality_factor)

    logger.info(
        "IIR filter (Q=%.1f): removed %d harmonic(s) - %s Hz",
        quality_factor,
        len(removed_frequencies),
        ", ".join(f"{f:.1f}" for f in removed_frequencies),
    )

    return filtered, removed_frequencies
