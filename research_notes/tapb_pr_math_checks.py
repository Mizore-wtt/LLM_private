"""Reproducible mathematical sanity checks, NOT an LLM/privacy benchmark.

Run: python research_notes/tapb_pr_math_checks.py
Dependencies: numpy, scipy. Writes a JSON report alongside this file.
The fixed seed is exclusively for reproducible toy experiments, never deployment.
"""
from pathlib import Path
import json
import math

import numpy as np
from scipy.optimize import brentq
from scipy.special import log_ndtr


def gaussian_delta(epsilon, sigma, sensitivity=2.0):
    """Exact Gaussian privacy profile at the stated mean separation."""
    t = sensitivity / (2 * sigma)
    u = epsilon * sigma / sensitivity
    log_a = log_ndtr(t - u)
    log_b = epsilon + log_ndtr(-t - u)
    return float(math.exp(log_a) * (-math.expm1(log_b - log_a)))


def project(x, radius=1.0):
    return x * min(1.0, radius / max(float(np.linalg.norm(x)), 1e-300))


def main():
    rng = np.random.default_rng(20261106)
    target_delta = 1e-6
    calibration = []
    for epsilon in [1.0, 2.0, 4.0, 8.0]:
        log_delta = math.log(1 / target_delta)
        kappa = (math.sqrt(log_delta + epsilon) - math.sqrt(log_delta)) ** 2
        sigma_rdp = math.sqrt(2 / kappa)
        sigma_analytic = brentq(
            lambda sigma: gaussian_delta(epsilon, sigma) - target_delta,
            0.01, 1000.0, xtol=1e-12,
        )
        assert abs(kappa + 2 * math.sqrt(kappa * log_delta) - epsilon) < 1e-12
        assert gaussian_delta(epsilon, sigma_rdp) <= target_delta
        assert abs(gaussian_delta(epsilon, sigma_analytic) - target_delta) < 1e-12
        calibration.append({
            "epsilon": epsilon, "delta": target_delta,
            "sigma_over_C_RDP": sigma_rdp,
            "MI_upper_bits_RDP": 1 / (2 * sigma_rdp**2 * math.log(2)),
            "sigma_over_C_analytic": sigma_analytic,
            "MI_upper_bits_analytic": 1 / (2 * sigma_analytic**2 * math.log(2)),
            "two_equal_prior_candidates_success_upper_analytic":
                0.5 * (1 + math.erf(1 / (math.sqrt(2) * sigma_analytic))),
        })

    # Public rank-3 linear response: local residual correction is exact.
    m, p, rank = 12, 9, 3
    A, B = rng.normal(size=(p, rank)), rng.normal(size=(m, rank))
    W = A @ B.T
    offset = rng.normal(size=p)
    affine_errors = []
    for _ in range(200):
        u = project(rng.normal(size=m))
        anchor = project(u + rng.normal(size=m))
        corrected = W @ anchor + offset + A @ (B.T @ (u - anchor))
        affine_errors.append(float(np.linalg.norm(corrected - (W @ u + offset))))
    assert max(affine_errors) < 1e-12

    # F(z) = W z + 0.5 beta ||z||^2 v, with ||v|| = 1.
    # Its Jacobian is globally beta-Lipschitz in operator norm.
    beta = 0.3
    v = rng.normal(size=p)
    v /= np.linalg.norm(v)
    def F(z):
        return W @ z + 0.5 * beta * float(z @ z) * v
    nonlinear = []
    for _ in range(500):
        u = project(rng.normal(size=m))
        noise = rng.normal(size=m)
        anchor = project(u + noise)
        residual = u - anchor
        residual_norm = float(np.linalg.norm(residual))
        assert residual_norm <= min(2.0, np.linalg.norm(noise)) + 1e-12
        jacobian = W + beta * np.outer(v, anchor)
        left, singular, right = np.linalg.svd(jacobian, full_matrices=False)
        approx = (left[:, :rank] * singular[:rank]) @ right[:rank]
        eta_at_anchor = float(np.linalg.norm(jacobian - approx, ord=2))
        correction = F(anchor) + approx @ residual
        error = float(np.linalg.norm(correction - F(u)))
        bound = eta_at_anchor * residual_norm + 0.5 * beta * residual_norm**2
        assert error <= bound + 1e-10
        nonlinear.append({"error": error, "bound": bound,
                          "uncorrected_error": float(np.linalg.norm(F(anchor) - F(u)))})

    # Check sharp uniform-M guessing bound using a constructive DP channel.
    # Hockey-stick divergence over all events = sum of positive differences.
    guess_checks = []
    for candidates in [2, 8, 100]:
        epsilon = 2.0
        delta = 1e-4
        den = math.exp(epsilon) + candidates - 1
        success = (math.exp(epsilon) + (candidates - 1) * delta) / den
        channel = np.full((candidates, candidates), (1 - delta) / den)
        np.fill_diagonal(channel, success)
        assert np.max(np.abs(channel.sum(axis=1) - 1)) < 1e-12
        worst_delta = max(float(np.maximum(channel[i] - math.exp(epsilon) * channel[j], 0).sum())
                          for i in range(candidates) for j in range(candidates))
        assert abs(worst_delta - delta) < 1e-12
        guess_checks.append({"M": candidates, "epsilon": epsilon, "delta": delta,
                             "optimal_uniform_guess_success": success,
                             "checked_hockey_stick_delta": worst_delta})

    # Affine scaling alone does not improve the signal/noise information cap.
    C, sigma, scale = 1.0, 3.0, 0.125
    assert C**2 / (2 * sigma**2) == (scale*C)**2 / (2 * (scale*sigma)**2)

    # Weighted response rank: minimize ||(J-T) S^(1/2)||_F^2, rank(T)<=r.
    # S is a second-moment matrix, NOT necessarily a centered covariance.
    jacobian = rng.normal(size=(p, m))
    q, _ = np.linalg.qr(rng.normal(size=(m, m)))
    eigenvalues = np.geomspace(0.01, 3.0, m)
    sqrt_S = (q * np.sqrt(eigenvalues)) @ q.T
    inv_sqrt_S = (q * (1 / np.sqrt(eigenvalues))) @ q.T
    left, singular, right = np.linalg.svd(jacobian @ sqrt_S, full_matrices=False)
    weighted_T = ((left[:, :rank] * singular[:rank]) @ right[:rank]) @ inv_sqrt_S
    weighted_error = float(np.linalg.norm((jacobian-weighted_T) @ sqrt_S, ord='fro')**2)
    tail_energy = float(np.sum(singular[rank:]**2))
    assert abs(weighted_error-tail_energy) < 1e-9
    l0, s0, r0 = np.linalg.svd(jacobian, full_matrices=False)
    ordinary_T = (l0[:, :rank] * s0[:rank]) @ r0[:rank]
    ordinary_weighted_error = float(np.linalg.norm((jacobian-ordinary_T) @ sqrt_S, ord='fro')**2)
    assert weighted_error <= ordinary_weighted_error + 1e-9
    report = {
        "scope": "Analytic calibration and toy-map checks only; no trained LLM, attack benchmark, or latency measurement.",
        "calibration_assumptions": "Whole-prompt replacement; ||f(x)||<=C; sensitivity bound 2C; isotropic Gaussian; C=1.",
        "calibration": calibration,
        "affine": {"trials": len(affine_errors), "max_correction_error": max(affine_errors)},
        "quadratic": {"trials": len(nonlinear), "all_bounds_passed": True,
                      "mean_corrected_error": float(np.mean([x['error'] for x in nonlinear])),
                      "mean_uncorrected_error": float(np.mean([x['uncorrected_error'] for x in nonlinear])),
                      "max_error_minus_bound": max(x['error']-x['bound'] for x in nonlinear)},
        "guessing_bound_checks": guess_checks,
        "scaling_invariance_passed": True,
        "weighted_rank": {"weighted_optimal_error": weighted_error,
                          "singular_tail_energy": tail_energy,
                          "ordinary_svd_weighted_error": ordinary_weighted_error},
    }
    out = Path(__file__).with_name("tapb_pr_math_checks.json")
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
