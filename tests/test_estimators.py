import numpy as np
from mena_ai_labor.estimators import ols, did_2x2, within_transform


def test_ols_line():
    x = np.array([0, 1, 2, 3], dtype=float)
    y = 2 + 3 * x
    beta, resid = ols(y, x)
    assert np.allclose(beta, [2, 3])
    assert np.allclose(resid, 0)


def test_did():
    assert did_2x2([10], [15], [8], [10]) == 3


def test_within_transform_group_means_zero():
    x = np.array([1., 3., 10., 14.])
    g = np.array([1, 1, 2, 2])
    z = within_transform(x, g)
    assert np.allclose([z[g == 1].mean(), z[g == 2].mean()], 0)
