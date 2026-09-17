"""
============================================================================
 varred.py  --  OptionLib
============================================================================
Convenience wrappers and diagnostics for variance-reduction studies.

These simply drive the pricers in mc_european.py / mc_asian.py under
matched replication budgets and report the variance-reduction ratio
(naive_variance / method_variance).

Project : ISyE 6644 (Simulation), Georgia Tech -- Summer 2026, Topic 27
Team    : Taeho Kim, Seungjun Lee, Jong Wook Eun
============================================================================
"""
import numpy as np
from mc_european import mc_european
from mc_asian import mc_asian


def european_vr_table(S0, K, r, sigma, T, n, call=True, seed=4242):
    """Compare naive / antithetic / control / both for a European option."""
    methods = [("Naive", False, False),
               ("Antithetic", True, False),
               ("Control variate", False, True),
               ("Antithetic + Control", True, True)]
    rows, base_se = [], None
    for name, anti, ctrl in methods:
        rng = np.random.default_rng(seed)
        est, se = mc_european(S0, K, r, sigma, T, n, call=call,
                              antithetic=anti, control=ctrl, rng=rng)
        if base_se is None:
            base_se = se
        rows.append((name, est, se, (base_se / se) ** 2))
    return rows


def asian_vr_table(S0, K, r, sigma, T, steps, n, call=True, seed=77):
    """Compare naive / antithetic / geometric-control for an Asian option."""
    out = []
    rng = np.random.default_rng(seed); n1, s1 = mc_asian(S0, K, r, sigma, T, steps, n, call=call, rng=rng)
    rng = np.random.default_rng(seed); n2, s2 = mc_asian(S0, K, r, sigma, T, steps, n, call=call, antithetic=True, rng=rng)
    rng = np.random.default_rng(seed); n3, s3 = mc_asian(S0, K, r, sigma, T, steps, n, call=call, control_geo=True, rng=rng)
    for nm, e, s in [("Naive", n1, s1), ("Antithetic", n2, s2), ("Geometric control", n3, s3)]:
        out.append((nm, e, s, (s1 / s) ** 2))
    return out
