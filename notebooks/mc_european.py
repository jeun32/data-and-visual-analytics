"""
============================================================================
 mc_european.py  --  OptionLib
============================================================================
Monte Carlo pricer for European calls/puts.

Optional variance reduction (antithetic variates and a discounted-
terminal-price control variate) plus a 95% confidence interval.

  Control variate : X = e^{-rT} S_T, with known mean E_Q[X] = S0.

Project : ISyE 6644 (Simulation), Georgia Tech -- Summer 2026, Topic 27
Team    : Taeho Kim, Seungjun Lee, Jong Wook Eun
============================================================================
"""
import numpy as np


def mc_european(S0, K, r, sigma, T, n, call=True,
                antithetic=False, control=False, rng=None):
    """
    Returns (estimate, standard_error). 95% CI = estimate +/- 1.96*SE.
    """
    if rng is None:
        rng = np.random.default_rng()
    if antithetic:
        m = n // 2
        Z = rng.standard_normal(m)
        Z = np.concatenate([Z, -Z])
    else:
        Z = rng.standard_normal(n)

    ST = S0 * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
    payoff = np.maximum(ST - K, 0) if call else np.maximum(K - ST, 0)
    disc = np.exp(-r * T) * payoff

    if control:
        cv = np.exp(-r * T) * ST          # control variate
        cv_mean = S0                      # known mean under Q
        cov = np.cov(disc, cv, ddof=1)
        b = cov[0, 1] / cov[1, 1]
        disc = disc - b * (cv - cv_mean)

    est = disc.mean()
    se = disc.std(ddof=1) / np.sqrt(len(disc))
    return est, se
