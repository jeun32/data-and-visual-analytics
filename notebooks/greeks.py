"""
============================================================================
 greeks.py  --  OptionLib
============================================================================
Sensitivity ("Greeks") estimation.

  fd_greeks               : central finite-difference MC Greeks for a
                            European option using COMMON RANDOM NUMBERS
                            (the same shock vector Z is reused across all
                            bumped prices). CRN is essential: without it the
                            differencing noise swamps the signal
                            (see report Section 4.5).
  delta_crn / delta_no_crn: helper estimators used to quantify the variance
                            reduction from CRN.

Analytical Greeks are in analytics.bsm_greeks (used as ground truth).

Project : ISyE 6644 (Simulation), Georgia Tech -- Summer 2026, Topic 27
Team    : Taeho Kim, Seungjun Lee, Jong Wook Eun
============================================================================
"""
import numpy as np


def _mc_price_crn(S0, K, r, sigma, T, n, call, Z):
    """Discounted-payoff sample mean using a supplied shock vector Z."""
    ST = S0 * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
    payoff = np.maximum(ST - K, 0) if call else np.maximum(K - ST, 0)
    return np.exp(-r * T) * payoff


def fd_greeks(S0, K, r, sigma, T, n, call=True, rng=None,
              hS=0.5, hsig=0.005, hr=0.001, hT=1/365):
    """Central finite-difference Greeks with common random numbers."""
    if rng is None:
        rng = np.random.default_rng()
    Z = rng.standard_normal(n)                 # shared across all bumps

    def price(S0_, r_, sig_, T_):
        return _mc_price_crn(S0_, K, r_, sig_, T_, n, call, Z).mean()

    p = price(S0, r, sigma, T)
    delta = (price(S0 + hS, r, sigma, T) - price(S0 - hS, r, sigma, T)) / (2 * hS)
    gamma = (price(S0 + hS, r, sigma, T) - 2 * p + price(S0 - hS, r, sigma, T)) / hS ** 2
    vega = (price(S0, r, sigma + hsig, T) - price(S0, r, sigma - hsig, T)) / (2 * hsig)
    rho = (price(S0, r + hr, sigma, T) - price(S0, r - hr, sigma, T)) / (2 * hr)
    theta = -(price(S0, r, sigma, T) - price(S0, r, sigma, T - hT)) / hT
    return dict(delta=delta, gamma=gamma, vega=vega, theta=theta, rho=rho)


def delta_crn(S0, K, r, sigma, T, n, rng, hS=0.5):
    """FD Delta reusing the SAME shocks for up/down bumps (low variance)."""
    Z = rng.standard_normal(n)
    up = _mc_price_crn(S0 + hS, K, r, sigma, T, n, True, Z).mean()
    dn = _mc_price_crn(S0 - hS, K, r, sigma, T, n, True, Z).mean()
    return (up - dn) / (2 * hS)


def delta_no_crn(S0, K, r, sigma, T, n, rng, hS=0.5):
    """FD Delta with INDEPENDENT shocks for up/down bumps (high variance)."""
    Zp = rng.standard_normal(n)
    Zm = rng.standard_normal(n)
    up = _mc_price_crn(S0 + hS, K, r, sigma, T, n, True, Zp).mean()
    dn = _mc_price_crn(S0 - hS, K, r, sigma, T, n, True, Zm).mean()
    return (up - dn) / (2 * hS)
