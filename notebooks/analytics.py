"""
============================================================================
 analytics.py  --  OptionLib
============================================================================
Closed-form (analytical) BENCHMARKS.

  bsm_price              : Black-Scholes-Merton European call/put price.
  bsm_greeks             : analytical Greeks (Delta, Gamma, Vega, Theta, Rho).
  geometric_asian_closed : Kemna-Vorst (1990) closed form for the DISCRETE
                           geometric-average Asian option
                           (control variate used in mc_asian.py).

References : Black & Scholes (1973); Merton (1973); Kemna & Vorst (1990).

Project : ISyE 6644 (Simulation), Georgia Tech -- Summer 2026, Topic 27
Team    : Taeho Kim, Seungjun Lee, Jong Wook Eun
============================================================================
"""
import numpy as np
from scipy.stats import norm


def bsm_price(S0, K, r, sigma, T, q=0.0, call=True):
    """Black-Scholes-Merton price of a European option."""
    if T <= 0:
        payoff = max(S0 - K, 0.0) if call else max(K - S0, 0.0)
        return payoff
    d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if call:
        return S0 * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S0 * np.exp(-q * T) * norm.cdf(-d1)


def bsm_greeks(S0, K, r, sigma, T, q=0.0, call=True):
    """Analytical Greeks for a European option. Returns a dict."""
    d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    pdf = norm.pdf(d1)
    if call:
        delta = np.exp(-q * T) * norm.cdf(d1)
        theta = (-S0 * pdf * sigma * np.exp(-q * T) / (2 * np.sqrt(T))
                 - r * K * np.exp(-r * T) * norm.cdf(d2)
                 + q * S0 * np.exp(-q * T) * norm.cdf(d1))
        rho = K * T * np.exp(-r * T) * norm.cdf(d2)
    else:
        delta = -np.exp(-q * T) * norm.cdf(-d1)
        theta = (-S0 * pdf * sigma * np.exp(-q * T) / (2 * np.sqrt(T))
                 + r * K * np.exp(-r * T) * norm.cdf(-d2)
                 - q * S0 * np.exp(-q * T) * norm.cdf(-d1))
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
    gamma = np.exp(-q * T) * pdf / (S0 * sigma * np.sqrt(T))
    vega = S0 * np.exp(-q * T) * pdf * np.sqrt(T)
    return dict(delta=delta, gamma=gamma, vega=vega, theta=theta, rho=rho)


def geometric_asian_closed(S0, K, r, sigma, T, steps, call=True):
    """
    Closed-form price of a DISCRETE geometric-average Asian option
    (Kemna-Vorst). Used as the control variate for the arithmetic-average
    Asian option, whose price has no closed form.
    """
    n = steps
    sig_g = sigma * np.sqrt((2 * n + 1) / (6 * (n + 1)))
    mu_g = (r - 0.5 * sigma ** 2) * (T * (n + 1) / (2 * n)) + 0.5 * sig_g ** 2
    d1 = (np.log(S0 / K) + (mu_g + 0.5 * sig_g ** 2) * T) / (sig_g * np.sqrt(T))
    d2 = d1 - sig_g * np.sqrt(T)
    if call:
        return np.exp(-r * T) * (S0 * np.exp(mu_g * T) * norm.cdf(d1) - K * norm.cdf(d2))
    return np.exp(-r * T) * (K * norm.cdf(-d2) - S0 * np.exp(mu_g * T) * norm.cdf(-d1))
