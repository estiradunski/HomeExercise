import logging
import os
import struct
import wave

import numpy as np

logger = logging.getLogger("audio_ingestion.utils")

SAMPLE_RATE = 44100
MAX_SAMPLES = 8192
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio_files")


def load_audio(file_name: str) -> tuple[list[float], int]:
    """Load audio from a WAV file, or fall back to a synthetic signal."""
    file_path = os.path.join(AUDIO_DIR, file_name)

    if os.path.isfile(file_path) and file_name.lower().endswith(".wav"):
        try:
            logger.info(f"Reading WAV file: {file_path}")
            return read_wav(file_path)
        except Exception as exc:
            logger.warning(f"Failed to read WAV ({exc}); falling back to synthetic signal")

    logger.info(f"'{file_name}' not found or unsupported — generating synthetic signal")
    return generate_synthetic(file_name)


def read_wav(file_path: str) -> tuple[list[float], int]:
    """Return (normalized_float_samples, sample_rate) from a mono/stereo WAV file."""
    with wave.open(file_path, "r") as wf:
        sample_rate = wf.getframerate()
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    dtype_map = {1: np.int8, 2: np.int16, 4: np.int32}
    dtype = dtype_map.get(sample_width)
    if dtype is None:
        raise ValueError(f"Unsupported sample width: {sample_width} bytes")

    samples = np.frombuffer(raw, dtype=dtype).astype(np.float32)

    if n_channels > 1:
        samples = samples.reshape(-1, n_channels).mean(axis=1)

    samples /= float(2 ** (8 * sample_width - 1))
    return samples[:MAX_SAMPLES].tolist(), sample_rate


def generate_synthetic(file_name: str) -> tuple[list[float], int]:
    """Generate a deterministic synthetic signal whose type depends on the file name."""
    t = np.linspace(0, MAX_SAMPLES / SAMPLE_RATE, MAX_SAMPLES, endpoint=False)
    seed = sum(ord(c) for c in file_name) % 3
    rng = np.random.default_rng(seed)

    if seed == 0:
        # Speech-like: harmonic stack with mild noise
        signal = (
            0.40 * np.sin(2 * np.pi * 150 * t)
            + 0.30 * np.sin(2 * np.pi * 300 * t)
            + 0.20 * np.sin(2 * np.pi * 600 * t)
            + 0.15 * np.sin(2 * np.pi * 1200 * t)
            + 0.02 * rng.standard_normal(MAX_SAMPLES)
        )
    elif seed == 1:
        # Pure 440 Hz tone
        signal = np.sin(2 * np.pi * 440 * t)
    else:
        # White noise
        signal = rng.standard_normal(MAX_SAMPLES) * 0.5

    peak = np.max(np.abs(signal))
    if peak > 0:
        signal /= peak

    signal_type = ["speech-like", "440 Hz tone", "white noise"][seed]
    logger.info(f"Synthetic signal: type={signal_type}, samples={len(signal)}")
    return signal.tolist(), SAMPLE_RATE
