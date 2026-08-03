from __future__ import annotations

from collections.abc import Sequence


def compute(values: Sequence[float]) -> float:
    """Return a deterministic arithmetic mean for offline conformance."""
    if not values:
        raise ValueError("values must not be empty")
    return sum(values) / len(values)
