"""
============================================================================
 mc_asian.py  --  OptionLib
============================================================================
Monte Carlo pricer for the ARITHMETIC-average Asian option.

Optional GEOMETRIC-average control variate whose price is known in closed
form via analytics.geometric_asian_closed. The geometric payoff is almost
perfectly correlated with the arithmetic payoff, giving ~1000x variance
reduction.

Project : ISyE 6644 (Simulation), Georgia Tech -- Summer 2026, Topic 27
Team    : Taeho Kim, Seungjun Lee, Jong Wook Eun
============================================================================
"""
import numpy as np
from gbm import gbm_paths
from analytics import geometric_asian_closed


def mc_asian(S0, K, r, sigma, T, steps, n, call=True,
             antithetic=False, control_geo=False, rng=None):
    """Returns (estimate, standard_error) for the arithmetic-Asian option."""
    if rng is None:
        rng = np.random.default_rng()
    S = gbm_paths(S0, r, sigma, T, steps, n, antithetic=antithetic, rng=rng)

    A_arith = S[:, 1:].mean(axis=1)
    payoff = np.maximum(A_arith - K, 0) if call else np.maximum(K - A_arith, 0)
    disc = np.exp(-r * T) * payoff

    if control_geo:
        A_geo = np.exp(np.log(S[:, 1:]).mean(axis=1))
        payoff_geo = np.maximum(A_geo - K, 0) if call else np.maximum(K - A_geo, 0)
        disc_geo = np.exp(-r * T) * payoff_geo
        geo_true = geometric_asian_closed(S0, K, r, sigma, T, steps, call)
        cov = np.cov(disc, disc_geo, ddof=1)
        b = cov[0, 1] / cov[1, 1]
        disc = disc - b * (disc_geo - geo_true)

    est = disc.mean()
    se = disc.std(ddof=1) / np.sqrt(len(disc))
    return est, se
