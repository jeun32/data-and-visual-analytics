==============================================================================
 OptionLib -- A Modular Python Library for Pricing Stock Options via
              Monte Carlo Simulation
 ISyE 6644 (Simulation), Georgia Tech -- Summer 2026
 Project Topic 27: Stock Option Pricing
 Team: Taeho Kim, Seungjun Lee, Jong Wook Eun
==============================================================================

WHAT THIS ZIP CONTAINS

This zip is the CODE submission that accompanies our final report
(OptionLib_Final_Report.docx / .pdf, submitted separately). It contains the
complete OptionLib source, a driver that regenerates every table and figure
in the report, and this README. 

 FILE-BY-FILE DESCRIPTION

  README.txt          This file. Explains every file and how to run the code.

  requirements.txt    Exact Python package versions needed to run the code.

  analytics.py        Closed-form BENCHMARKS (ground truth):
                        - bsm_price ............ Black-Scholes-Merton European price
                        - bsm_greeks ........... analytical Delta/Gamma/Vega/Theta/Rho
                        - geometric_asian_closed  Kemna-Vorst geometric-Asian price
                                                  (used as a control variate)

  gbm.py              Risk-neutral GBM SIMULATORS:
                        - gbm_terminal ......... n terminal prices S_T (single step)
                        - gbm_paths ............ n full paths, shape (n, steps+1)
                      Both accept an explicit numpy Generator so streams can be
                      shared (CRN / control variate) or independent (coverage).

  mc_european.py      Monte Carlo pricer for European calls/puts with optional
                      antithetic + control-variate variance reduction; returns
                      (estimate, standard_error).  --> report Sections 4.1, 4.2

  mc_asian.py         MC pricer for the ARITHMETIC-average Asian option with an
                      optional geometric-average control variate (~1300x
                      variance reduction).                    --> Section 4.2

  american.py         American-option pricing:
                        - binomial_american ...  CRR lattice (exact benchmark)
                        - lsm_american ........  Longstaff-Schwartz least-squares
                                                 Monte Carlo (lower-bound estimator)
                                                                --> Section 4.3

  greeks.py           Sensitivity estimation:
                        - fd_greeks ...........  central finite-difference MC Greeks
                                                 using COMMON RANDOM NUMBERS
                        - delta_crn / delta_no_crn  helpers quantifying the CRN
                                                 variance reduction   --> 4.4, 4.5

  varred.py           Thin convenience wrappers that drive the pricers above
                      under matched replication budgets and report the
                      variance-reduction ratio (naive var / method var).

  reproduce.py        DRIVER. Regenerates every table (3-9) and figure (1-6)
                      in the report from FIXED SEEDS. See Section 3 to run.