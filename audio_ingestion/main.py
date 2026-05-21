import logging
import os
import uuid

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s - %(message)s",
)
logger = logging.getLogger("audio_ingestion")

app = FastAPI(title="Audio Ingestion Service", version="1.0.0")

SIGNAL_PROCESSING_URL = os.getenv("SIGNAL_PROCESSING_URL", "http://localhost:8002")


class AudioUploadRequest(BaseModel):
    file_name: str


class AudioUploadResponse(BaseModel):
    signal_id: str
    samples: list[float]
    sample_rate: int
    rms: float
    dominant_frequency: float
    classification: str


@app.post("/upload-audio", response_model=AudioUploadResponse)
async def upload_audio(request: AudioUploadRequest):
    logger.info(f"Upload request received for: '{request.file_name}'")

    signal_id = str(uuid.uuid4())[:8]
    logger.info(f"Assigned signal_id: {signal_id}")

    from audio_utils import load_audio

    samples, sample_rate = load_audio(request.file_name)
    logger.info(f"Audio loaded: {len(samples)} samples @ {sample_rate} Hz")

    # Forward samples to Signal Processing Service (which chains to Acoustic Analysis)
    payload = {
        "signal_id": signal_id,
        "samples": samples,
        "sample_rate": sample_rate,
    }
    try:
        logger.info(f"Forwarding signal_id={signal_id} to Signal Processing Service at {SIGNAL_PROCESSING_URL}")
        sp_resp = requests.post(
            f"{SIGNAL_PROCESSING_URL}/process-signal",
            json=payload,
            timeout=30,
        )
        sp_resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error(f"Signal Processing Service error: {exc}")
        raise HTTPException(
            status_code=503,
            detail=f"Signal Processing Service unavailable: {exc}",
        )

    result = sp_resp.json()
    logger.info(
        f"Pipeline complete — signal_id={signal_id} | "
        f"RMS={result['rms']:.4f} | "
        f"dominant_freq={result['dominant_frequency']:.1f} Hz | "
        f"classification={result['classification']}"
    )

    return AudioUploadResponse(
        signal_id=signal_id,
        samples=samples,
        sample_rate=sample_rate,
        rms=result["rms"],
        dominant_frequency=result["dominant_frequency"],
        classification=result["classification"],
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "audio_ingestion", "port": 8001}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
