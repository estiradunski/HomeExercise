"""
End-to-end test client for the Distributed Acoustic Signal Processing pipeline.

Checks that all three services are healthy, then runs the full pipeline on a
set of sample audio files and prints a formatted results table.

Usage:
    python test_client/test_pipeline.py
"""
import sys
import textwrap

import requests

AUDIO_SERVICE = "http://localhost:8001"
SIGNAL_SERVICE = "http://localhost:8002"
ANALYSIS_SERVICE = "http://localhost:8003"

TEST_FILES = [
    "speech_sample.wav",   # expected: speech
    "tone_440hz.wav",      # expected: tone
    "noise_sample.wav",    # expected: noise
    "mystery.wav",         # triggers synthetic generation (seed-based type)
]


def check_health() -> bool:
    services = {
        "Audio Ingestion   (8001)": f"{AUDIO_SERVICE}/health",
        "Signal Processing (8002)": f"{SIGNAL_SERVICE}/health",
        "Acoustic Analysis (8003)": f"{ANALYSIS_SERVICE}/health",
    }
    print("=" * 55)
    print("  Health checks")
    print("=" * 55)
    all_ok = True
    for name, url in services.items():
        try:
            resp = requests.get(url, timeout=5)
            status = resp.json().get("status", "unknown")
            icon = "OK" if status == "healthy" else "!!"
            print(f"  [{icon}] {name} — {status}")
        except requests.RequestException as exc:
            print(f"  [!!] {name} — UNREACHABLE ({exc})")
            all_ok = False
    print()
    return all_ok


def run_pipeline(file_name: str) -> dict | None:
    try:
        resp = requests.post(
            f"{AUDIO_SERVICE}/upload-audio",
            json={"file_name": file_name},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as exc:
        print(f"  HTTP error: {exc}")
        return None
    except requests.RequestException as exc:
        print(f"  Request error: {exc}")
        return None


def print_result(file_name: str, result: dict) -> None:
    print(f"  File            : {file_name}")
    print(f"  Signal ID       : {result['signal_id']}")
    print(f"  Samples         : {len(result['samples'])} @ {result['sample_rate']} Hz")
    print(f"  RMS             : {result['rms']:.4f}")
    print(f"  Dominant freq   : {result['dominant_frequency']:.1f} Hz")
    print(f"  Classification  : {result['classification'].upper()}")


def main() -> None:
    if not check_health():
        print("One or more services are not running. Start all services first (see README).")
        sys.exit(1)

    print("=" * 55)
    print("  Pipeline tests")
    print("=" * 55)

    for file_name in TEST_FILES:
        print(f"\n>>> {file_name}")
        result = run_pipeline(file_name)
        if result:
            print_result(file_name, result)

    print("\n" + "=" * 55)
    print("  Done.")
    print("=" * 55)


if __name__ == "__main__":
    main()
