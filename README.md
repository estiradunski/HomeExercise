# Distributed Acoustic Signal Processing System

A Python microservices system that processes audio signals through a REST API pipeline.
Three independent FastAPI services communicate over HTTP to ingest audio, analyse the
signal, and classify it as **speech**, **tone**, or **noise**.

---

## Architecture

```
User
 │
 │  POST /upload-audio  {"file_name": "sound.wav"}
 ▼
┌─────────────────────────────┐  port 8001
│   Audio Ingestion Service   │  Reads / generates audio samples
│                             │  Assigns a signal_id
└────────────┬────────────────┘
             │  POST /process-signal  {signal_id, samples, sample_rate}
             ▼
┌─────────────────────────────┐  port 8002
│  Signal Processing Service  │  Noise filter (moving average)
│                             │  Computes FFT (numpy.fft.rfft + Hanning window)
│                             │  Computes RMS
└────────────┬────────────────┘
             │  POST /analyze  {signal_id, fft, frequencies, sample_rate}
             ▼
┌─────────────────────────────┐  port 8003
│  Acoustic Analysis Service  │  Detects dominant frequency
│                             │  Classifies: speech | tone | noise
└─────────────────────────────┘
             │
             └──► Final result bubbles back through the chain to the user
```

### Ports

| Service                  | Port |
|--------------------------|------|
| Audio Ingestion Service  | 8001 |
| Signal Processing Service| 8002 |
| Acoustic Analysis Service| 8003 |

---

## Project Structure

```
HomeExercise/
├── audio_ingestion/
│   ├── main.py            ← FastAPI app, POST /upload-audio
│   ├── audio_utils.py     ← WAV reader + synthetic signal generator
│   ├── audio_files/       ← Place your WAV files here
│   └── requirements.txt
│
├── signal_processing/
│   ├── main.py            ← FastAPI app, POST /process-signal
│   ├── signal_utils.py    ← FFT, RMS, moving-average filter
│   └── requirements.txt
│
├── acoustic_analysis/
│   ├── main.py            ← FastAPI app, POST /analyze
│   ├── analysis_utils.py  ← dominant frequency, spectral flatness, classification
│   └── requirements.txt
│
├── test_client/
│   ├── generate_test_audio.py  ← Creates speech/tone/noise WAV files
│   └── test_pipeline.py        ← End-to-end test runner
│
└── README.md
```

---

## Prerequisites

- Python 3.10 or higher
- pip

---

## Setup

Each service has its own virtual environment and dependencies.
Open **three separate terminals**, one per service.

### Terminal 1 — Audio Ingestion Service

```bash
cd audio_ingestion
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Terminal 2 — Signal Processing Service

```bash
cd signal_processing
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Terminal 3 — Acoustic Analysis Service

```bash
cd acoustic_analysis
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Generate Test Audio Files (optional but recommended)

From the project root, run:

```bash
# Uses the same numpy/venv as any service that already has numpy installed
cd audio_ingestion
.venv\Scripts\activate          # Windows  (or source .venv/bin/activate on Linux/Mac)
cd ..
python test_client/generate_test_audio.py
```

This creates three WAV files inside `audio_ingestion/audio_files/`:

| File               | Signal type |
|--------------------|-------------|
| speech_sample.wav  | Harmonic stack (150 Hz fundamental + overtones) |
| tone_440hz.wav     | Pure 440 Hz sine wave (concert A) |
| noise_sample.wav   | Normalized white noise |

---

## Running the Services

Start **each service in its own terminal** (with the corresponding venv active).

**Terminal 3 — Acoustic Analysis (start first, no dependencies)**
```bash
cd acoustic_analysis
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

**Terminal 2 — Signal Processing**
```bash
cd signal_processing
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

**Terminal 1 — Audio Ingestion**
```bash
cd audio_ingestion
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

All three services expose a `/health` endpoint so you can verify they are up:

```
GET http://localhost:8001/health
GET http://localhost:8002/health
GET http://localhost:8003/health
```

---

## Running the End-to-End Test

Once all three services are running:

```bash
# From project root, using any Python env that has 'requests' installed
python test_client/test_pipeline.py
```

Expected output:

```
=======================================================
  Health checks
=======================================================
  [OK] Audio Ingestion   (8001) — healthy
  [OK] Signal Processing (8002) — healthy
  [OK] Acoustic Analysis (8003) — healthy

=======================================================
  Pipeline tests
=======================================================

>>> speech_sample.wav
  File            : speech_sample.wav
  Signal ID       : a1b2c3d4
  Samples         : 8192 @ 44100 Hz
  RMS             : 0.4821
  Dominant freq   : 150.0 Hz
  Classification  : SPEECH

>>> tone_440hz.wav
  File            : tone_440hz.wav
  Signal ID       : e5f6g7h8
  Samples         : 8192 @ 44100 Hz
  RMS             : 0.7071
  Dominant freq   : 440.3 Hz
  Classification  : TONE

>>> noise_sample.wav
  File            : noise_sample.wav
  Signal ID       : i9j0k1l2
  Samples         : 8192 @ 44100 Hz
  RMS             : 0.3104
  Dominant freq   : 21533.2 Hz
  Classification  : NOISE
```

---

## API Reference

### Audio Ingestion Service — `POST /upload-audio`

**Request**
```json
{ "file_name": "sound.wav" }
```

**Response**
```json
{
  "signal_id": "abc123",
  "samples": [ 0.01, -0.02, ... ],
  "sample_rate": 44100,
  "rms": 0.4821,
  "dominant_frequency": 440.3,
  "classification": "tone"
}
```

If the file is not found in `audio_ingestion/audio_files/`, a synthetic signal is
generated deterministically from the file name (type cycles through speech → tone → noise
based on a character-sum hash).

---

### Signal Processing Service — `POST /process-signal`

**Request**
```json
{
  "signal_id": "abc123",
  "samples": [ 0.01, -0.02, ... ],
  "sample_rate": 44100
}
```

**Response**
```json
{
  "signal_id": "abc123",
  "fft": [ 0.001, 0.45, ... ],
  "frequencies": [ 0.0, 5.38, ... ],
  "rms": 0.4821,
  "dominant_frequency": 440.3,
  "classification": "tone"
}
```

Processing steps applied in order:
1. Moving-average low-pass filter (window = 5 samples)
2. RMS calculation on the filtered signal
3. One-sided FFT via `numpy.fft.rfft` with a Hanning window (reduces spectral leakage)
4. Forwards FFT + frequency bins to Acoustic Analysis Service

---

### Acoustic Analysis Service — `POST /analyze`

**Request**
```json
{
  "signal_id": "abc123",
  "fft": [ 0.001, 0.45, ... ],
  "frequencies": [ 0.0, 5.38, ... ],
  "sample_rate": 44100
}
```

**Response**
```json
{
  "signal_id": "abc123",
  "dominant_frequency": 440.3,
  "classification": "tone"
}
```

Classification algorithm:
| Condition | Label |
|-----------|-------|
| Spectral flatness > 0.25 | `noise` |
| Peak-to-mean magnitude ratio > 10 AND dominant freq in [50, 4000] Hz | `tone` |
| Otherwise | `speech` |

---

## Environment Variables

Override default service URLs using environment variables:

| Variable                 | Default                    | Used by                    |
|--------------------------|----------------------------|----------------------------|
| `SIGNAL_PROCESSING_URL`  | `http://localhost:8002`    | Audio Ingestion Service    |
| `ACOUSTIC_ANALYSIS_URL`  | `http://localhost:8003`    | Signal Processing Service  |

Example (Windows PowerShell):
```powershell
$env:SIGNAL_PROCESSING_URL = "http://192.168.1.10:8002"
uvicorn main:app --port 8001
```

---

## Using Your Own Audio Files

Place any `.wav` file in `audio_ingestion/audio_files/` and reference it by name:

```bash
curl -X POST http://localhost:8001/upload-audio \
     -H "Content-Type: application/json" \
     -d '{"file_name": "my_recording.wav"}'
```

Supported: mono or stereo WAV, 8-bit, 16-bit, or 32-bit PCM.
The first 8192 samples are used; stereo is mixed down to mono automatically.
