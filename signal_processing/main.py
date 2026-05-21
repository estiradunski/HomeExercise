import logging
import os

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s - %(message)s",
)
logger = logging.getLogger("signal_processing")

app = FastAPI(title="Signal Processing Service", version="1.0.0")

ACOUSTIC_ANALYSIS_URL = os.getenv("ACOUSTIC_ANALYSIS_URL", "http://localhost:8003")


class ProcessSignalRequest(BaseModel):
    signal_id: str
    samples: list[float]
    sample_rate: int = 44100


class ProcessSignalResponse(BaseModel):
    signal_id: str
    fft: list[float]
    frequencies: list[float]
    rms: float
    dominant_frequency: float
    classification: str


@app.post("/process-signal", response_model=ProcessSignalResponse)
async def process_signal(request: ProcessSignalRequest):
    logger.info(
        f"Processing signal_id={request.signal_id} | "
        f"samples={len(request.samples)} | sample_rate={request.sample_rate} Hz"
    )

    from signal_utils import apply_moving_average, compute_fft, compute_rms

    # Step 1 — noise filter
    filtered = apply_moving_average(request.samples, window=5)
    logger.info(f"Moving-average filter applied (window=5)")

    # Step 2 — RMS on filtered signal
    rms = compute_rms(filtered)
    logger.info(f"RMS={rms:.4f}")

    # Step 3 — FFT magnitude spectrum
    fft_magnitudes, frequencies = compute_fft(filtered, request.sample_rate)
    logger.info(f"FFT computed: {len(fft_magnitudes)} bins")

    # Step 4 — forward FFT to Acoustic Analysis Service
    payload = {
        "signal_id": request.signal_id,
        "fft": fft_magnitudes,
        "frequencies": frequencies,
        "sample_rate": request.sample_rate,
    }
    try:
        logger.info(f"Forwarding FFT for signal_id={request.signal_id} to Acoustic Analysis Service at {ACOUSTIC_ANALYSIS_URL}")
        aa_resp = requests.post(
            f"{ACOUSTIC_ANALYSIS_URL}/analyze",
            json=payload,
            timeout=30,
        )
        aa_resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error(f"Acoustic Analysis Service error: {exc}")
        raise HTTPException(
            status_code=503,
            detail=f"Acoustic Analysis Service unavailable: {exc}",
        )

    analysis = aa_resp.json()
    logger.info(
        f"signal_id={request.signal_id} — "
        f"dominant_frequency={analysis['dominant_frequency']:.1f} Hz | "
        f"classification={analysis['classification']}"
    )

    return ProcessSignalResponse(
        signal_id=request.signal_id,
        fft=fft_magnitudes,
        frequencies=frequencies,
        rms=rms,
        dominant_frequency=analysis["dominant_frequency"],
        classification=analysis["classification"],
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "signal_processing", "port": 8002}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
