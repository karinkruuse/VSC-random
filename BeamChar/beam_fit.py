# beam_waist_fit.py
# Fits Gaussian-beam radius evolution to your clip-level summary (beam_clip_summary.csv)
# and makes a plot like your screenshot (major+minor fit, z0 markers, laser head line).

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ---------------- settings ----------------
SUMMARY_CSV = Path("beam_clip_summary.csv")  # produced by the clip-level script
LAMBDA_M = 1064e-9                          # wavelength (m)
LASER_HEAD_Z_MM = 0.0                       # where to draw the black dashed line (mm)
OUT_PNG = Path("beam_fit.png")
# ------------------------------------------


def w_model(z_mm, w0_um, z0_mm):
    """
    Ideal Gaussian beam:
        w(z) = w0 * sqrt(1 + ((z - z0)/zR)^2)
        zR = pi w0^2 / lambda
    z in mm, w0 in µm.
    Returns w in µm.
    """
    w0_m = w0_um * 1e-6
    zR_m = np.pi * w0_m**2 / LAMBDA_M

    z_m = z_mm * 1e-3
    z0_m = z0_mm * 1e-3
    return (w0_m * np.sqrt(1.0 + ((z_m - z0_m) / zR_m) ** 2)) * 1e6


def fit_axis(z_mm, w_um):
    z_mm = np.asarray(z_mm, float)
    w_um = np.asarray(w_um, float)
    ok = np.isfinite(z_mm) & np.isfinite(w_um) & (w_um > 0)
    z_mm, w_um = z_mm[ok], w_um[ok]

    i0 = np.argmin(w_um)
    w0_guess = w_um[i0]
    z0_guess = z_mm[i0]

    # bounds: w0>0, z0 unconstrained
    popt, pcov = curve_fit(
        w_model,
        z_mm,
        w_um,
        p0=[w0_guess, z0_guess],
        bounds=([1e-6, -np.inf], [np.inf, np.inf]),
        maxfev=20000,
    )
    w0_um, z0_mm = popt
    perr = np.sqrt(np.diag(pcov))
    w0_err_um, z0_err_mm = perr

    # derived zR
    w0_m = w0_um * 1e-6
    zR_mm = (np.pi * w0_m**2 / LAMBDA_M) * 1e3

    return w0_um, w0_err_um, z0_mm, z0_err_mm, zR_mm


# --------- load clip summary ----------
df = pd.read_csv(SUMMARY_CSV).dropna(subset=["z_from_name"]).sort_values("z_from_name")

z = df["z_from_name"].to_numpy(float)

# clip diameters are in µm -> convert to radii (µm)
w_major = 0.5 * df["D_major_1e2_um"].to_numpy(float)
w_minor = 0.5 * df["D_minor_1e2_um"].to_numpy(float)

# --------- fit ----------
w0M, w0M_e, z0M, z0M_e, zRM = fit_axis(z, w_major)
w0m, w0m_e, z0m, z0m_e, zRm = fit_axis(z, w_minor)

# --------- plot ----------
z_plot = np.linspace(np.min(z), np.max(z), 500)

plt.figure(figsize=(10, 6))

# data points
plt.plot(z, w_major, "o", label="Data (major axis)")
plt.plot(z, w_minor, "o", label="Data (minor axis)")

# fit curves
plt.plot(z_plot, w_model(z_plot, w0M, z0M), "-", label="Beam fit (major axis)")
plt.plot(z_plot, w_model(z_plot, w0m, z0m), "-", label="Beam fit (minor axis)")

# z0 markers
plt.axvline(z0M, linestyle="--", label=f"z0 (major) = {z0M:.2f} mm")
plt.axvline(z0m, linestyle="--", label=f"z0 (minor) = {z0m:.2f} mm")

# laser head marker
plt.axvline(LASER_HEAD_Z_MM, color="k", linestyle="--", label="Laser head")

plt.xlabel("z (mm)")
plt.ylabel("Beam radius w (µm)   [from clip diameter: w = D/2]")
plt.title("Gaussian beam waist fit (clip 1/e² widths)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(OUT_PNG, dpi=200)
plt.close()

# --------- print results ----------
print(f"Wrote: {OUT_PNG}\n")

print("Major axis:")
print(f"  w0 = {w0M:.2f} ± {w0M_e:.2f} µm")
print(f"  z0 = {z0M:.2f} ± {z0M_e:.2f} mm")
print(f"  zR = {zRM:.2f} mm  (from zR = π w0² / λ)\n")

print("Minor axis:")
print(f"  w0 = {w0m:.2f} ± {w0m_e:.2f} µm")
print(f"  z0 = {z0m:.2f} ± {z0m_e:.2f} mm")
print(f"  zR = {zRm:.2f} mm  (from zR = π w0² / λ)")
