from __future__ import annotations

from pydantic import BaseModel, field_validator, model_validator


class FilterRequest(BaseModel):
    sample_rate: int
    base_freq: float
    num_harmonics: int
    samples: list[float]

    @field_validator("sample_rate")
    @classmethod
    def sample_rate_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("must be positive")
        return v

    @field_validator("base_freq")
    @classmethod
    def base_freq_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("must be positive")
        return v

    @field_validator("num_harmonics")
    @classmethod
    def num_harmonics_valid(cls, v: int) -> int:
        if v < 1:
            raise ValueError("must be >= 1")
        return v

    @field_validator("samples")
    @classmethod
    def samples_not_empty(cls, v: list[float]) -> list[float]:
        if not v:
            raise ValueError("must not be empty")
        return v

    @model_validator(mode="after")
    def base_freq_below_nyquist(self) -> FilterRequest:
        if self.base_freq >= self.sample_rate / 2:
            raise ValueError("base_freq must be below Nyquist frequency (sample_rate / 2)")
        return self


class FilterResponse(BaseModel):
    filtered_samples: list[float]
