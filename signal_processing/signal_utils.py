import logging

import numpy as np

logger = logging.getLogger("signal_processing.utils")


def compute_rms(samples: list[float]) -> float:
    """Root Mean Square amplitude of the signal."""
    arr = np.asarray(samples, dtype=np.float64)
    return float(np.sqrt(np.mean(arr ** 2)))


def apply_moving_average(samples: list[float], window: int = 5) -> list[float]:
    """
    Moving-average low-pass filter using symmetric convolution.
    Attenuates high-frequency noise while preserving the signal envelope.
    """
    arr = np.asarray(samples, dtype=np.float64)
    kernel = np.ones(window) / window
    filtered = np.convolve(arr, kernel, mode="same")
    return filtered.tolist()


def compute_fft(samples: list[float], sample_rate: int = 44100) -> tuple[list[float], list[float]]:
    """
    One-sided FFT magnitude spectrum with a Hanning window to reduce spectral leakage.
    Returns (magnitudes, frequency_bins_hz).
    Uses numpy.fft.rfft so only positive frequencies are returned.
    """
    arr = np.asarray(samples, dtype=np.float64)
    n = len(arr)

    window = np.hanning(n)
    windowed = arr * window

    fft_complex = np.fft.rfft(windowed)
    # Scale so that magnitude reflects true peak amplitude
    magnitudes = (2.0 / n) * np.abs(fft_complex)
    frequencies = np.fft.rfftfreq(n, d=1.0 / sample_rate)

    logger.debug(f"FFT: n={n}, bins={len(magnitudes)}, peak_bin={int(np.argmax(magnitudes))}")
    return magnitudes.tolist(), frequencies.tolist()
