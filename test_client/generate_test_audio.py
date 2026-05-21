"""
Generate three synthetic WAV files for testing the audio pipeline:
  - speech_sample.wav   harmonic stack simulating a vowel-like speech signal
  - tone_440hz.wav      pure 440 Hz sine (concert A)
  - noise_sample.wav    band-limited white noise

Files are written to audio_ingestion/audio_files/ so the Audio Ingestion
Service can read them directly.

Usage:
    python test_client/generate_test_audio.py
"""
import os
import struct
import wave

import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "audio_ingestion", "audio_files")
SAMPLE_RATE = 44100
DURATION = 1.0
N = int(SAMPLE_RATE * DURATION)


def write_wav(path: str, samples: np.ndarray) -> None:
    int16 = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(struct.pack(f"<{len(int16)}h", *int16))
    print(f"  Written: {os.path.abspath(path)}")


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t = np.linspace(0, DURATION, N, endpoint=False)
    rng = np.random.default_rng(42)

    # 1. Speech-like: harmonic stack (fundamental 150 Hz + overtones) with mild noise
    speech = (
        0.40 * np.sin(2 * np.pi * 150 * t)
        + 0.30 * np.sin(2 * np.pi * 300 * t)
        + 0.20 * np.sin(2 * np.pi * 600 * t)
        + 0.15 * np.sin(2 * np.pi * 1200 * t)
        + 0.02 * rng.standard_normal(N)
    )
    speech /= np.max(np.abs(speech))
    write_wav(os.path.join(OUTPUT_DIR, "speech_sample.wav"), speech)

    # 2. Pure 440 Hz tone
    tone = np.sin(2 * np.pi * 440 * t)
    write_wav(os.path.join(OUTPUT_DIR, "tone_440hz.wav"), tone)

    # 3. White noise (normalized)
    noise = rng.standard_normal(N) * 0.5
    noise /= np.max(np.abs(noise))
    write_wav(os.path.join(OUTPUT_DIR, "noise_sample.wav"), noise)

    print("\nAll test audio files generated successfully.")


if __name__ == "__main__":
    main()
