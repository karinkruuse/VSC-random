"""
Delay-line phase correction sweep (cleaned up)

What it does:
1) Load structured .npy measurement data (fields like 'Time (s)', 'Input 1 Phase (cyc)', etc.)
2) Throw away a settling interval
3) Build a clock-jitter proxy from the DDS channel: jit_poly ≈ (detrended phi2)/f2   [seconds]
4) Estimate the actual delay tau_hat by minimizing residual mean-square
5) Sweep tau = tau_hat + Δ and overlay ASDs (corrected) on one fucking plot, plus the uncorrected baseline

Dependencies:
- numpy, scipy, matplotlib
- pytdi (for pytdi.dsp.timeshift)

Notes / fixes vs your notebook:
- Uses *consistent* detrending before doing delay-estimation and correction (mixing detrended/non-detrended is a classic way to lie to yourself).
- Cuts edges *once* using the worst-case tau in the sweep so all ASDs are computed on identical-length vectors (otherwise you’re comparing apples to random-length apples).
- Welch nperseg is clamped to data length so it doesn’t silently do something dumb.
"""

from __future__ import annotations

import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.optimize import minimize_scalar

from pytdi.dsp import timeshift


# ----------------------------
# helpers
# ----------------------------
def detrend_lin(t: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Remove best-fit line vs time (good for big ramps/drifts in phase)."""
    p = np.polyfit(t, x, 1)
    return x - np.polyval(p, t)


def D(x: np.ndarray, dt: float, tau: float, order: int = 31) -> np.ndarray:
    """Fractional delay by tau seconds using pytdi.timeshift."""
    return timeshift(np.asarray(x, float), (tau / dt), order=order)


def asd(x: np.ndarray, fs: float, nperseg: int = 2**20):
    """Amplitude spectral density via Welch. nperseg is clamped to len(x)."""
    x = np.asarray(x, float)
    nperseg = int(min(nperseg, len(x)))
    if nperseg < 8:
        raise ValueError("Too few samples for ASD (after cutting).")
    f, Pxx = welch(x, fs=fs, nperseg=nperseg, scaling="density")
    return f, np.sqrt(Pxx)


def edge_cut_samples(tau: float, dt: float, order: int) -> int:
    """
    Safe edge cut for fractional-delay filters.
    Matches your notebook logic: ceil(|tau|/dt) + order + 2
    """
    return int(np.ceil(abs(tau / dt))) + order + 2


# ----------------------------
# core logic
# ----------------------------
def estimate_delay(
    t: np.ndarray,
    phi1: np.ndarray,
    phi3: np.ndarray,
    f1: np.ndarray,
    jit_poly: np.ndarray,
    dt: float,
    tau0: float,
    order: int = 31,
    win: float = 0.2,
) -> float:
    """
    Estimate tau by minimizing residual mean-square:
        r(tau) = phi1 - D(phi3,tau) + D(f1*jit,tau) - D(f1,tau)*jit
    (then mean-remove r, and minimize mean(r^2))
    """
    # Cut edges for the *search* window tau in [tau0-win, tau0+win]
    k = edge_cut_samples(tau0 + win, dt, order)
    sl = slice(k, -k)

    phi1_ds = phi1[sl]
    phi3_ds = phi3[sl]
    f1_ds = f1[sl]
    jit_ds = jit_poly[sl]

    def J(tau: float) -> float:
        r = (
            phi1_ds
            - D(phi3_ds, dt, tau, order)
            + D(f1_ds * jit_ds, dt, tau, order)
            - D(f1_ds, dt, tau, order) * jit_ds
        )
        r = r - np.mean(r)
        return float(np.mean(r * r))

    res = minimize_scalar(J, bounds=(tau0 - win, tau0 + win), method="bounded")
    if not res.success:
        raise RuntimeError(f"Delay estimation failed: {res}")
    return float(res.x)


def corrected_residual(
    phi1: np.ndarray,
    phi3: np.ndarray,
    f1: np.ndarray,
    jit_poly: np.ndarray,
    dt: float,
    tau: float,
    order: int,
) -> np.ndarray:
    """
    Apply the same algebra you used:
        D_phi1_corr = phi1 + D(f1*jit,tau) - D(f1,tau)*jit
        res = D_phi1_corr - D(phi3,tau)
    """
    Df1j = D(f1 * jit_poly, dt, tau, order)
    Df1 = D(f1, dt, tau, order)
    Dphi3 = D(phi3, dt, tau, order)
    D_phi1_corr = phi1 + Df1j - Df1 * jit_poly
    return D_phi1_corr - Dphi3


# ----------------------------
# script entrypoint
# ----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="Path to .npy structured array file")
    ap.add_argument("--settling", type=float, default=15000.0, help="Seconds to discard at start")
    ap.add_argument("--set-delay", type=float, default=8.1, help="Nominal delay (s), used as tau0")
    ap.add_argument("--order", type=int, default=31, help="Fractional delay filter order")
    ap.add_argument("--win", type=float, default=0.2, help="Search half-window around tau0 (s)")
    ap.add_argument(
        "--tau-offsets",
        type=float,
        nargs="+",
        default=[-0.02, -0.01, 0.0, 0.01, 0.02, 0.0305],
        help="Offsets Δ (s) applied to tau_hat for ASD overlay",
    )
    ap.add_argument("--nperseg", type=int, default=2**20, help="Welch nperseg (clamped to data length)")
    args = ap.parse_args()

    data = np.load(args.file, mmap_mode="r")

    # ---- extract channels (names match your notebook) ----
    t_all = data["Time (s)"]
    m = t_all >= (t_all[0] + args.settling)

    t = t_all[m]
    f1 = data["Input 1 Frequency (Hz)"][m]
    phi1 = data["Input 1 Phase (cyc)"][m]

    f2 = data["Input 2 Frequency (Hz)"][m]
    phi2 = data["Input 2 Phase (cyc)"][m]

    f3 = data["Input 3 Frequency (Hz)"][m]
    phi3 = data["Input 3 Phase (cyc)"][m]

    # ---- sampling ----
    dt = float(np.mean(np.diff(t)))
    fs = 1.0 / dt

    # ---- detrend phases consistently ----
    phi1_d = detrend_lin(t, phi1)
    phi2_d = detrend_lin(t, phi2)
    phi3_d = detrend_lin(t, phi3)

    # ---- jitter proxy in seconds ----
    # This assumes phi2_d is dominated by timing jitter mapped into phase via f2.
    # If f2 varies a lot, this is a crude approximation; it’s what your notebook did.
    jit_poly = phi2_d / f2

    # ---- estimate delay ----
    tau0 = float(args.set_delay)
    tau_hat = estimate_delay(
        t=t,
        phi1=phi1_d,
        phi3=phi3_d,
        f1=f1,
        jit_poly=jit_poly,
        dt=dt,
        tau0=tau0,
        order=args.order,
        win=args.win,
    )
    print(f"tau_hat = {tau_hat:.9f} s   (tau_hat - tau0 = {tau_hat - tau0:+.9f} s)")

    # ---- choose a single edge cut so every curve uses identical samples ----
    tau_candidates = [tau_hat + d for d in args.tau_offsets] + [tau_hat]
    k = edge_cut_samples(max(tau_candidates, key=lambda x: abs(x)), dt, args.order)
    sl = slice(k, -k)

    # ---- baseline (uncorrected) ----
    res_unc = (phi1_d - D(phi3_d, dt, tau_hat, args.order))[sl]
    res_unc = res_unc - np.mean(res_unc)
    f, A_unc = asd(res_unc, fs, nperseg=args.nperseg)

    # ---- plot ----
    plt.figure()
    plt.loglog(f, A_unc, linewidth=3, alpha=0.6, label="uncorrected (tau_hat)")

    for d in args.tau_offsets:
        tau = tau_hat + float(d)

        res = corrected_residual(
            phi1=phi1_d,
            phi3=phi3_d,
            f1=f1,
            jit_poly=jit_poly,
            dt=dt,
            tau=tau,
            order=args.order,
        )[sl]
        res = res - np.mean(res)

        f, A = asd(res, fs, nperseg=args.nperseg)
        plt.loglog(f, A, label=f"corrected (Δ={d:+.6f} s)")

    plt.xlabel("Hz")
    plt.ylabel("ASD [cycles/√Hz]")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
