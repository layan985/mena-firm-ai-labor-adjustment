from __future__ import annotations

import numpy as np


def ols(y, X, add_intercept: bool = True):
    """Educational OLS implementation using the Moore-Penrose inverse."""
    y = np.asarray(y, dtype=float).reshape(-1, 1)
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    if add_intercept:
        X = np.column_stack([np.ones(X.shape[0]), X])
    beta = np.linalg.pinv(X.T @ X) @ X.T @ y
    resid = y - X @ beta
    return beta.ravel(), resid.ravel()


def did_2x2(y_pre_treated, y_post_treated, y_pre_control, y_post_control):
    """Canonical 2x2 difference-in-differences estimand."""
    treated_change = float(np.mean(y_post_treated) - np.mean(y_pre_treated))
    control_change = float(np.mean(y_post_control) - np.mean(y_pre_control))
    return treated_change - control_change


def within_transform(values, groups):
    """One-way demeaning used to explain fixed-effects estimation from scratch."""
    values = np.asarray(values, dtype=float)
    groups = np.asarray(groups)
    out = np.empty_like(values, dtype=float)
    for g in np.unique(groups):
        mask = groups == g
        out[mask] = values[mask] - values[mask].mean(axis=0)
    return out
