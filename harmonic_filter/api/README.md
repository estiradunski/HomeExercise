# Harmonic Filter – REST API (Part II)

A REST API wrapper for the harmonic filter built in Part I.  
Accepts audio samples as JSON, removes harmonic frequencies, and returns the filtered samples.

---

## Installation

Python 3.10+ required.

```bash
pip install fastapi "uvicorn[standard]" numpy scipy pydantic
```

---

## How to run

Run from the `harmonic_filter/` directory:

```bash
uvicorn api.main:app --reload --port 8001
```

The API is available at `http://localhost:8001`.  
Interactive docs (Swagger UI) at `http://localhost:8001/docs`.

---

## Endpoint

### `POST /harmonic_filter`

Removes harmonic frequencies from an audio signal while preserving the fundamental frequency.

**Request body (JSON):**

| Field | Type | Description |
|-------|------|-------------|
| `sample_rate` | int | Sampling rate in Hz (e.g. 8000, 44100, 48000) |
| `base_freq` | float | Fundamental frequency to preserve, in Hz |
| `num_harmonics` | int | Number of harmonics to remove (≥ 1) |
| `samples` | list[float] | Audio samples normalized between -1.0 and 1.0 |

**Response body (JSON):**

| Field | Type | Description |
|-------|------|-------------|
| `filtered_samples` | list[float] | Filtered audio samples normalized between -1.0 and 1.0 |

---

## Example

**Request:**
```json
{
  "sample_rate": 8000,
  "base_freq": 50.0,
  "num_harmonics": 10,
  "samples": [0.0, 0.0801, 0.1597, 0.2382, ...]
}
```

**Response:**
```json
{
  "filtered_samples": [0.0, 0.0799, 0.1594, 0.2379, ...]
}
```

---

## Test the API

With the server running, execute from the `harmonic_filter/` directory:

```bash
python api/test_api.py
```

This generates a 50 Hz + harmonics test signal, sends it to the API, and prints a frequency-by-frequency PASS/FAIL table confirming the harmonics are removed and the fundamental is preserved.
