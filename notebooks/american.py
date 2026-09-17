"""
============================================================================
 american.py  --  OptionLib
============================================================================
American-option pricing.

  binomial_american : Cox-Ross-Rubinstein lattice (backward induction).
                      Used as the (essentially exact) benchmark with a
                      fine step count (2000-3000).
  lsm_american      : Longstaff-Schwartz least-squares Monte Carlo.
                      Regresses realized continuation values on a quadratic
                      basis {1, S, S^2} of the in-the-money paths to
                      approximate the optimal exercise policy.
                      LSM is a LOW-biased estimator (lower bound).

References : Cox, Ross & Rubinstein (1979); Longstaff & Schwartz (2001).

Project : ISyE 6644 (Simulation), Georgia Tech -- Summer 2026, Topic 27
Team    : Taeho Kim, Seungjun Lee, Jong Wook Eun
============================================================================
"""
import numpy as np
from gbm import gbm_paths


def binomial_american(S0, K, r, sigma, T, steps, call=True):
    """CRR binomial American price via backward induction."""
    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1.0 / u
    p = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)
    j = np.arange(steps + 1)
    ST = S0 * (u ** (steps - j)) * (d ** j)
    V = np.maximum(ST - K, 0) if call else np.maximum(K - ST, 0)
    for i in range(steps - 1, -1, -1):
        j = np.arange(i + 1)
        S = S0 * (u ** (i - j)) * (d ** j)
        cont = disc * (p * V[:i + 1] + (1 - p) * V[1:i + 2])
        ex = np.maximum(S - K, 0) if call else np.maximum(K - S, 0)
        V = np.maximum(cont, ex)
    return V[0]


def lsm_american(S0, K, r, sigma, T, steps, n, call=False,
                 rng=None, antithetic=False):
    """
    Longstaff-Schwartz LSM American price.
    Returns (price, standard_error).
    """
    if rng is None:
        rng = np.random.default_rng()
    S = gbm_paths(S0, r, sigma, T, steps, n, antithetic=antithetic, rng=rng)
    dt = T / steps
    disc = np.exp(-r * dt)
    payoff = (lambda x: np.maximum(x - K, 0)) if call else (lambda x: np.maximum(K - x, 0))

    cf = payoff(S[:, -1])                      # cashflow at maturity
    for t in range(steps - 1, 0, -1):
        St = S[:, t]
        ex = payoff(St)
        itm = ex > 0
        cf = cf * disc                         # discount running cashflow one step
        if itm.sum() > 0:
            X = St[itm]
            Y = cf[itm]
            A = np.vstack([np.ones_like(X), X, X ** 2]).T
            coef, *_ = np.linalg.lstsq(A, Y, rcond=None)
            cont = A @ coef                    # fitted continuation value
            exercise = ex[itm] > cont
            idx = np.where(itm)[0][exercise]
            cf[idx] = ex[itm][exercise]        # exercise where optimal
    price = (cf * disc).mean()
    se = (cf * disc).std(ddof=1) / np.sqrt(n)
    return price, se
