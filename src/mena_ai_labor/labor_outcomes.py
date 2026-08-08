from __future__ import annotations

import math
from typing import Any

MISSING_CODES = {-9, -8, -7, -6, -5}


def clean_nonnegative(value: Any) -> float | None:
    if value is None:
        return None
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(x) or x in MISSING_CODES or x < 0:
        return None
    return x


def log_change(current: Any, baseline: Any) -> float | None:
    current = clean_nonnegative(current)
    baseline = clean_nonnegative(baseline)
    if current is None or baseline is None:
        return None
    return math.log1p(current) - math.log1p(baseline)


def share(numerator: Any, denominator: Any) -> float | None:
    num = clean_nonnegative(numerator)
    den = clean_nonnegative(denominator)
    if num is None or den is None or den == 0:
        return None
    return num / den
