from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


__all__ = ["FilterResult"]


@dataclass
class FilterResult:
    input_path: Path
    output_path: Path
    base_freq: float
    num_harmonics: int
    method: str
    sample_rate: int
    num_samples: int
    removed_frequencies: list[float] = field(default_factory=list)
    input_rms: float = 0.0
    output_rms: float = 0.0

    def __str__(self) -> str:
        duration = self.num_samples / self.sample_rate
        removed_str = (
            ", ".join(f"{f:.1f}" for f in self.removed_frequencies)
            if self.removed_frequencies
            else "none"
        )
        rms_reduction_pct = (
            100.0 * (1.0 - self.output_rms / self.input_rms)
            if self.input_rms > 0
            else 0.0
        )
        sep = "-" * 52
        return (
            f"\n{sep}\n"
            f"  Harmonic Filter Result\n"
            f"{sep}\n"
            f"  Input file   : {self.input_path}\n"
            f"  Output file  : {self.output_path}\n"
            f"  Method       : {self.method.upper()}\n"
            f"  Duration     : {duration:.3f} s  "
            f"({self.num_samples} samples @ {self.sample_rate} Hz)\n"
            f"  Base freq    : {self.base_freq:.1f} Hz  [preserved]\n"
            f"  Harmonics    : {removed_str} Hz  [removed]\n"
            f"  RMS before   : {self.input_rms:.6f}\n"
            f"  RMS after    : {self.output_rms:.6f}  "
            f"({rms_reduction_pct:.1f}% reduction)\n"
            f"{sep}"
        )
