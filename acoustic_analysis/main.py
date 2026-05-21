import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s - %(message)s",
)
logger = logging.getLogger("acoustic_analysis")

app = FastAPI(title="Acoustic Analysis Service", version="1.0.0")


class AnalyzeRequest(BaseModel):
    signal_id: str
    fft: list[float]
    frequencies: list[float] | None = None
    sample_rate: int = 44100


class AnalyzeResponse(BaseModel):
    signal_id: str
    dominant_frequency: float
    classification: str


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    logger.info(
        f"Analyzing signal_id={request.signal_id} | "
        f"fft_bins={len(request.fft)} | sample_rate={request.sample_rate} Hz"
    )

    if not request.fft:
        raise HTTPException(status_code=422, detail="fft array must not be empty")

    from analysis_utils import classify_signal, detect_dominant_frequency

    dominant_freq = detect_dominant_frequency(
        request.fft,
        request.frequencies,
        request.sample_rate,
    )
    classification = classify_signal(request.fft, dominant_freq)

    logger.info(
        f"signal_id={request.signal_id} — "
        f"dominant_frequency={dominant_freq:.2f} Hz | "
        f"classification={classification}"
    )

    return AnalyzeResponse(
        signal_id=request.signal_id,
        dominant_frequency=dominant_freq,
        classification=classification,
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "acoustic_analysis", "port": 8003}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
