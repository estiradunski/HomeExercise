from __future__ import annotations

import wave
from pathlib import Path

import numpy as np


__all__ = ["load_wav", "save_wav", "wav_info"]


def load_wav(path: str | Path) -> tuple[np.ndarray, int]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"WAV file not found: {path}")

    with wave.open(str(path), "r") as wf:
        n_channels: int = wf.getnchannels()
        sample_width: int = wf.getsampwidth()
        sample_rate: int = wf.getframerate()
        n_frames: int = wf.getnframes()
        raw: bytes = wf.readframes(n_frames)

    _dtype_map: dict[int, type] = {1: np.int8, 2: np.int16, 4: np.int32}
    dtype = _dtype_map.get(sample_width)
    if dtype is None:
        raise ValueError(
            f"Unsupported sample width {sample_width} bytes. "
            "Only 8-bit, 16-bit, and 32-bit PCM WAV files are supported."
        )

    samples = np.frombuffer(raw, dtype=dtype).astype(np.float64)

    if n_channels > 1:
        samples = samples.reshape(-1, n_channels).mean(axis=1)

    peak = float(2 ** (8 * sample_width - 1))
    samples /= peak

    return samples, sample_rate


def save_wav(
    path: str | Path,
    samples: np.ndarray,
    sample_rate: int,
    bit_depth: int = 16,
) -> None:
    path = Path(path)

    _int_scale: dict[int, tuple[type, int]] = {
        16: (np.int16, 32_767),
        32: (np.int32, 2_147_483_647),
    }
    if bit_depth not in _int_scale:
        raise ValueError(f"bit_depth must be 16 or 32, got {bit_depth}.")

    int_type, scale = _int_scale[bit_depth]
    quantised = (np.clip(samples, -1.0, 1.0) * scale).astype(int_type)

    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(bit_depth // 8)
        wf.setframerate(sample_rate)
        wf.writeframes(quantised.tobytes())


def wav_info(path: str | Path) -> dict[str, int | float]:
    path = Path(path)
    with wave.open(str(path), "r") as wf:
        info: dict[str, int | float] = {
            "channels": wf.getnchannels(),
            "sample_width_bytes": wf.getsampwidth(),
            "sample_rate": wf.getframerate(),
            "num_frames": wf.getnframes(),
        }
    info["duration_s"] = round(info["num_frames"] / info["sample_rate"], 6)
    return info
