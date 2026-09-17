"""
============================================================================
 gbm.py  --  OptionLib
============================================================================
Risk-neutral geometric Brownian motion (GBM) simulators.

  Under Q:  dS = r S dt + sigma S dW,  with exact lognormal transition
            S_{t+dt} = S_t * exp[(r - 0.5 sigma^2) dt + sigma sqrt(dt) Z].

Every routine accepts an explicit numpy Generator (rng) so random streams
can be shared (common random numbers / control variates) or kept
independent (coverage study), under caller control.

Project : ISyE 6644 (Simulation), Georgia Tech -- Summer 2026, Topic 27
Team    : Taeho Kim, Seungjun Lee, Jong Wook Eun
============================================================================
"""
import numpy as np


def gbm_terminal(S0, r, sigma, T, n, antithetic=False, rng=None):
    """Simulate n terminal prices S_T (single step). Returns array (n,)."""
    if rng is None:
        rng = np.random.default_rng()
    if antithetic:
        m = n // 2
        Z = rng.standard_normal(m)
        Z = np.concatenate([Z, -Z])
    else:
        Z = rng.standard_normal(n)
    return S0 * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)


def gbm_paths(S0, r, sigma, T, steps, n, antithetic=False, rng=None):
    """
    Simulate n full GBM paths on a grid of `steps` intervals.
    Returns array of shape (n, steps+1) including the initial S0 column.
    """
    if rng is None:
        rng = np.random.default_rng()
    dt = T / steps
    if antithetic:
        m = n // 2
        Z = rng.standard_normal((m, steps))
        Z = np.concatenate([Z, -Z], axis=0)
    else:
        Z = rng.standard_normal((n, steps))
    logincr = (r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z
    logpaths = np.cumsum(logincr, axis=1)
    S = S0 * np.exp(logpaths)
    S = np.hstack([np.full((S.shape[0], 1), S0), S])
    return S
