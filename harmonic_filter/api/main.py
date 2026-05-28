from __future__ import annotations

import numpy as np
from fastapi import FastAPI, HTTPException

from api.models import FilterRequest, FilterResponse
from harmonic_filter_pkg.fft_filter import filter_harmonics_fft


app = FastAPI(title="Harmonic Filter API")


@app.post("/harmonic_filter", response_model=FilterResponse)
def harmonic_filter(request: FilterRequest) -> FilterResponse:
    samples = np.array(request.samples, dtype=np.float64)

    bin_width = request.sample_rate / len(samples)
    notch_bandwidth_hz = min(request.base_freq * 0.4, max(2.0, 15.0 * bin_width))

    try:
        filtered, _ = filter_harmonics_fft(
            samples,
            request.sample_rate,
            request.base_freq,
            request.num_harmonics,
            notch_bandwidth_hz=notch_bandwidth_hz,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return FilterResponse(filtered_samples=filtered.tolist())
