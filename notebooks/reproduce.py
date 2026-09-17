"""
============================================================================
 reproduce.py  --  OptionLib
============================================================================
DRIVER -- regenerates every numerical table and figure in the OptionLib
final report from fixed seeds.

  Reproduce everything:
      python reproduce.py --experiment all

  Or one experiment at a time:
      python reproduce.py --experiment validate    # Table 3
      python reproduce.py --experiment coverage    # Table 4
      python reproduce.py --experiment varred      # Tables 5-6, Figure 3
      python reproduce.py --experiment american    # Table 7, Figure 4
      python reproduce.py --experiment greeks      # Table 8, Figure 5
      python reproduce.py --experiment crn         # Table 9, Figure 6

Dependencies : numpy, scipy, pandas, matplotlib.
Figures are written to the current directory as PNG files.

Project : ISyE 6644 (Simulation), Georgia Tech -- Summer 2026, Topic 27
Team    : Taeho Kim, Seungjun Lee, Jong Wook Eun
============================================================================
"""
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analytics import bsm_price, bsm_greeks
from gbm import gbm_paths
from mc_european import mc_european
from mc_asian import mc_asian
from american import binomial_american, lsm_american
from greeks import fd_greeks, delta_crn, delta_no_crn
from varred import european_vr_table, asian_vr_table

BASE = dict(S0=100, r=0.05, sigma=0.20, T=1.0)


# ---------- Table 3: MC vs BSM validation ----------
def exp_validate():
    strikes = [80, 90, 100, 110, 120]
    rows = []
    for K in strikes:
        for typ, call in [("Call", True), ("Put", False)]:
            ana = bsm_price(BASE["S0"], K, BASE["r"], BASE["sigma"], BASE["T"], call=call)
            rng = np.random.default_rng(1000 + K + (0 if call else 500))
            est, se = mc_european(BASE["S0"], K, BASE["r"], BASE["sigma"],
                                  BASE["T"], n=100000, call=call, rng=rng)
            lo, hi = est - 1.96 * se, est + 1.96 * se
            rows.append([K, typ, ana, est, se, lo, hi, "Yes" if lo <= ana <= hi else "No"])
    df = pd.DataFrame(rows, columns=["K", "Type", "BSM", "MC", "SE", "CIlo", "CIhi", "Covers"])
    print("\n=== Table 3: MC vs BSM validation ===")
    print(df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    return df


# ---------- Table 4: CI coverage study ----------
def exp_coverage():
    rng = np.random.default_rng(2024)
    macro, n = 1000, 5000
    rows = []
    for K in [90, 100, 110]:
        true = bsm_price(100, K, 0.05, 0.2, 1.0, call=True)
        covered, halfs, ests = 0, [], []
        for _ in range(macro):
            est, se = mc_european(100, K, 0.05, 0.2, 1.0, n, call=True, rng=rng)
            lo, hi = est - 1.96 * se, est + 1.96 * se
            covered += (lo <= true <= hi)
            halfs.append(1.96 * se); ests.append(est)
        ests = np.array(ests)
        rows.append([K, true, ests.mean(), covered / macro,
                     np.mean(halfs) / 1.96, ests.std(ddof=1)])
    df = pd.DataFrame(rows, columns=["K", "True", "AvgMC", "Coverage",
                                     "AvgSE", "EmpSE"])
    print("\n=== Table 4: CI coverage (nominal 0.95) ===")
    print(df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    return df


# ---------- Tables 5-6 + Figure 3: variance reduction ----------
def exp_varred():
    eur = european_vr_table(100, 90, 0.05, 0.2, 1.0, 100000, call=True)
    asn = asian_vr_table(100, 100, 0.05, 0.2, 1.0, 50, 100000, call=True)
    print("\n=== Table 5: European call (K=90) variance reduction ===")
    for name, est, se, vr in eur:
        print(f"{name:22s} est={est:.4f} SE={se:.4f} VR={vr:6.1f}x")
    print("\n=== Table 6: Arithmetic-Asian call variance reduction ===")
    for name, est, se, vr in asn:
        print(f"{name:22s} est={est:.4f} SE={se:.4f} VR={vr:8.1f}x")

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
    names = [m[0] for m in eur]; ses = [m[2] for m in eur]
    axes[0].bar(range(len(names)), ses)
    axes[0].set_xticks(range(len(names))); axes[0].set_xticklabels(names, rotation=20, ha="right", fontsize=8)
    axes[0].set_ylabel("Standard error"); axes[0].set_title("European call (K=90)")
    names2 = [m[0] for m in asn]; ses2 = [m[2] for m in asn]
    axes[1].bar(range(len(names2)), ses2); axes[1].set_yscale("log")
    axes[1].set_xticks(range(len(names2))); axes[1].set_xticklabels(names2, rotation=20, ha="right", fontsize=8)
    axes[1].set_ylabel("Standard error"); axes[1].set_title("Arithmetic-Asian call")
    plt.tight_layout(); plt.savefig("fig3_varreduction.png", dpi=130); plt.close()
    print("saved fig3_varreduction.png")


# ---------- Table 7 + Figure 4: American options ----------
def exp_american():
    rows = []
    for K in [90, 95, 100, 105, 110]:
        bin_ = binomial_american(100, K, 0.05, 0.2, 1.0, 2000, call=False)
        eur = bsm_price(100, K, 0.05, 0.2, 1.0, call=False)
        rng = np.random.default_rng(3000 + K)
        lsm, se = lsm_american(100, K, 0.05, 0.2, 1.0, 50, 200000,
                               call=False, rng=rng, antithetic=True)
        rows.append([K, eur, bin_, lsm, se, bin_ - eur, abs(lsm - bin_)])
    df = pd.DataFrame(rows, columns=["K", "Eur", "Binomial", "LSM", "SE",
                                     "EarlyExPrem", "|LSM-bin|"])
    print("\n=== Table 7: American put LSM vs binomial ===")
    print(df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    ns = [2000, 5000, 10000, 20000, 50000, 100000, 200000, 400000]
    ref = binomial_american(100, 100, 0.05, 0.2, 1.0, 3000, call=False)
    means, halfs = [], []
    for nn in ns:
        rng = np.random.default_rng(500 + nn)
        est, se = lsm_american(100, 100, 0.05, 0.2, 1.0, 50, nn,
                               call=False, rng=rng, antithetic=True)
        means.append(est); halfs.append(1.96 * se)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.errorbar(ns, means, yerr=halfs, fmt="o-", capsize=3, ms=4, label="LSM +/- 95% CI")
    ax.axhline(ref, ls="--", color="crimson", label=f"Binomial = {ref:.3f}")
    ax.set_xscale("log"); ax.set_xlabel("paths n"); ax.set_ylabel("American put price")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig("fig4_lsm_conv.png", dpi=130); plt.close()
    print("saved fig4_lsm_conv.png")
    return df


# ---------- Table 8 + Figure 5: Greeks ----------
def exp_greeks():
    ana = bsm_greeks(100, 100, 0.05, 0.2, 1.0, call=True)
    rng = np.random.default_rng(808)
    fd = fd_greeks(100, 100, 0.05, 0.2, 1.0, 1000000, call=True, rng=rng)
    print("\n=== Table 8: ATM call Greeks (analytical vs FD-MC/CRN) ===")
    for g in ["delta", "gamma", "vega", "theta", "rho"]:
        print(f"{g:6s} analytical={ana[g]:+.5f}  FD-MC={fd[g]:+.5f}  diff={fd[g]-ana[g]:+.5f}")

    spots = np.linspace(70, 130, 25)
    da = [bsm_greeks(s, 100, 0.05, 0.2, 1.0, call=True)["delta"] for s in spots]
    ga = [bsm_greeks(s, 100, 0.05, 0.2, 1.0, call=True)["gamma"] for s in spots]
    smc = np.linspace(75, 125, 11); dmc, gmc = [], []
    for s in smc:
        r_ = np.random.default_rng(int(s * 10))
        g = fd_greeks(s, 100, 0.05, 0.2, 1.0, 500000, call=True, rng=r_)
        dmc.append(g["delta"]); gmc.append(g["gamma"])
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    ax[0].plot(spots, da, "-", label="Analytical"); ax[0].plot(smc, dmc, "o", label="FD-MC")
    ax[0].set_title("Delta vs spot"); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)
    ax[1].plot(spots, ga, "-", label="Analytical"); ax[1].plot(smc, gmc, "o", label="FD-MC")
    ax[1].set_title("Gamma vs spot"); ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
    plt.tight_layout(); plt.savefig("fig6_greeks.png", dpi=130); plt.close()
    print("saved fig6_greeks.png")


# ---------- Table 9 + Figure 6: CRN effect ----------
def exp_crn():
    reps, n = 200, 20000
    no, yes = [], []
    rng = np.random.default_rng(1)
    for _ in range(reps):
        no.append(delta_no_crn(100, 100, 0.05, 0.2, 1.0, n, rng))
        yes.append(delta_crn(100, 100, 0.05, 0.2, 1.0, n, rng))
    no, yes = np.array(no), np.array(yes)
    td = bsm_greeks(100, 100, 0.05, 0.2, 1.0, call=True)["delta"]
    print("\n=== Table 9: CRN effect on FD Delta ===")
    print(f"true Delta            = {td:.5f}")
    print(f"independent RNs  std  = {no.std(ddof=1):.5f}")
    print(f"common RNs (CRN) std  = {yes.std(ddof=1):.5f}")
    print(f"variance reduction    = {(no.std(ddof=1)/yes.std(ddof=1))**2:.0f}x")

    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.hist(no, bins=30, alpha=0.6, label=f"Independent (sd={no.std(ddof=1):.4f})")
    ax.hist(yes, bins=30, alpha=0.6, label=f"CRN (sd={yes.std(ddof=1):.4f})")
    ax.axvline(td, ls="--", color="k", label=f"true Delta={td:.4f}")
    ax.set_xlabel("FD Delta estimate"); ax.set_ylabel("frequency")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig("fig5_crn.png", dpi=130); plt.close()
    print("saved fig5_crn.png")


EXPERIMENTS = dict(validate=exp_validate, coverage=exp_coverage,
                   varred=exp_varred, american=exp_american,
                   greeks=exp_greeks, crn=exp_crn)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment", default="all",
                    choices=list(EXPERIMENTS) + ["all"])
    args = ap.parse_args()
    if args.experiment == "all":
        for fn in EXPERIMENTS.values():
            fn()
    else:
        EXPERIMENTS[args.experiment]()
