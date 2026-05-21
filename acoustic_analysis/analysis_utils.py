import logging

import numpy as np

logger = logging.getLogger("acoustic_analysis.utils")


def detect_dominant_frequency(
    fft_magnitudes: list[float],
    frequencies: list[float] | None,
    sample_rate: int = 44100,
) -> float:
    """Return the frequency (Hz) of the highest-magnitude FFT bin."""
    magnitudes = np.asarray(fft_magnitudes, dtype=np.float64)

    if frequencies is not None:
        freqs = np.asarray(frequencies, dtype=np.float64)
    else:
        # Reconstruct rfft frequency bins from bin count
        n_bins = len(magnitudes)
        freqs = np.fft.rfftfreq(2 * (n_bins - 1), d=1.0 / sample_rate)

    dominant_idx = int(np.argmax(magnitudes))
    dominant_freq = float(freqs[dominant_idx])
    logger.debug(f"Dominant bin: index={dominant_idx}, frequency={dominant_freq:.2f} Hz")
    return dominant_freq


def _spectral_flatness(magnitudes: np.ndarray) -> float:
    """
    Wiener entropy — ratio of geometric to arithmetic mean of the spectrum.
    Approaches 1.0 for white noise; approaches 0.0 for a pure sinusoid.
    """
    eps = 1e-10
    mag = magnitudes + eps
    geo_mean = float(np.exp(np.mean(np.log(mag))))
    ari_mean = float(np.mean(mag))
    return geo_mean / (ari_mean + eps)


def _second_peak_ratio(magnitudes: np.ndarray, dominant_idx: int) -> float:
    """
    Ratio of the strongest bin *outside* a narrow sidelobe exclusion zone
    around the dominant peak, to the dominant peak itself.

    Near 0.0  → single-peak signal (tone).
    Near 1.0  → multiple peaks of comparable strength (speech / noise).

    The guard of 12 bins (~65 Hz at 44100/8192 Hz/bin) is wide enough to
    cover Hanning window sidelobes but narrow enough that harmonics at 2x
    the dominant frequency remain visible as a second peak.
    """
    max_mag = magnitudes[dominant_idx]
    if max_mag < 1e-10:
        return 0.0

    guard = 12  # bins (~65 Hz at 44100 Hz / 8192 samples)
    lo = max(0, dominant_idx - guard)
    hi = min(len(magnitudes), dominant_idx + guard + 1)

    outside = np.concatenate([magnitudes[:lo], magnitudes[hi:]])
    if outside.size == 0:
        return 0.0

    return float(np.max(outside)) / (max_mag + 1e-10)


def classify_signal(fft_magnitudes: list[float], dominant_frequency: float) -> str:
    """
    Classify the signal as one of: 'speech', 'tone', 'noise'.

    Decision logic:
    1. noise  — spectral flatness > 0.65 (energy spread broadly across spectrum)
    2. tone   — single dominant peak:
                  peak-to-mean ratio > 10
                  AND dominant freq in [50, 4000] Hz
                  AND second-peak-ratio < 0.15  (no significant harmonics)
    3. speech — everything else (multiple harmonic peaks, moderate flatness)
    """
    magnitudes = np.asarray(fft_magnitudes, dtype=np.float64)
    dominant_idx = int(np.argmax(magnitudes))

    flatness = _spectral_flatness(magnitudes)
    logger.debug(f"Spectral flatness={flatness:.4f}")

    if flatness > 0.65:
        logger.info(f"Classification: NOISE (flatness={flatness:.3f})")
        return "noise"

    peak_to_mean = float(np.max(magnitudes)) / (float(np.mean(magnitudes)) + 1e-10)
    spr = _second_peak_ratio(magnitudes, dominant_idx)
    logger.debug(
        f"peak_to_mean={peak_to_mean:.2f}, second_peak_ratio={spr:.3f}, "
        f"dominant_freq={dominant_frequency:.2f} Hz"
    )

    if peak_to_mean > 10 and 50.0 <= dominant_frequency <= 4000.0 and spr < 0.15:
        logger.info(
            f"Classification: TONE "
            f"(peak_to_mean={peak_to_mean:.1f}, spr={spr:.3f}, freq={dominant_frequency:.1f} Hz)"
        )
        return "tone"

    logger.info(
        f"Classification: SPEECH "
        f"(peak_to_mean={peak_to_mean:.1f}, spr={spr:.3f}, flatness={flatness:.3f})"
    )
    return "speech"
