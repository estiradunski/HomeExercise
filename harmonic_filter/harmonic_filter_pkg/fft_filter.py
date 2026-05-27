from __future__ import annotations

import logging

import numpy as np


__all__ = ["filter_harmonics_fft"]

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def filter_harmonics_fft(
    samples: np.ndarray,
    sample_rate: int,
    base_freq: float,
    num_harmonics: int,
    notch_bandwidth_hz: float = 2.0,
    taper: bool = True,
) -> tuple[np.ndarray, list[float]]:
    if base_freq <= 0:
        raise ValueError(f"base_freq must be positive, got {base_freq!r}")
    if num_harmonics < 1:
        raise ValueError(f"num_harmonics must be >= 1, got {num_harmonics!r}")

    n: int = len(samples)
    nyquist: float = sample_rate / 2.0

    spectrum = np.fft.rfft(samples)
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)

    mask = np.ones(len(spectrum), dtype=np.float64)
    removed_frequencies: list[float] = []

    for k in range(2, num_harmonics + 2):
        harmonic_freq: float = k * base_freq
        if harmonic_freq >= nyquist:
            logger.debug(
                "Harmonic %d*%.1f Hz = %.1f Hz >= Nyquist (%.1f Hz); stopping.",
                k, base_freq, harmonic_freq, nyquist,
            )
            break

        if taper:
            sigma: float = notch_bandwidth_hz / 2.3548
            gaussian_bump = np.exp(-0.5 * ((freqs - harmonic_freq) / sigma) ** 2)
            mask *= 1.0 - gaussian_bump
        else:
            half_bw: float = notch_bandwidth_hz / 2.0
            mask[np.abs(freqs - harmonic_freq) <= half_bw] = 0.0

        removed_frequencies.append(harmonic_freq)
        logger.debug("  Notched %.1f Hz  (k=%d)", harmonic_freq, k)

    logger.info(
        "FFT filter: removed %d harmonic(s) - %s Hz",
        len(removed_frequencies),
        ", ".join(f"{f:.1f}" for f in removed_frequencies),
    )

    filtered = np.fft.irfft(spectrum * mask, n=n)
    return filtered, removed_frequencies
