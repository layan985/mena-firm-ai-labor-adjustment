from math import isclose, log1p
from mena_ai_labor.labor_outcomes import clean_nonnegative, log_change, share


def test_missing_codes():
    assert clean_nonnegative(-9) is None
    assert clean_nonnegative(10) == 10


def test_log_change():
    assert isclose(log_change(20, 10), log1p(20) - log1p(10))


def test_share():
    assert share(5, 20) == 0.25
    assert share(1, 0) is None
