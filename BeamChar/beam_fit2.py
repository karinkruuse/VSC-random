# beam_clip_fit.py
# Input: beam2_clip_summary.csv (the tidy CSV from the previous script)
# Plots: major/minor clip diameters + total power (2nd y-axis) + ellipticity (minor/major)
# Fits Gaussian propagation to get waist location z0 and Rayleigh range zR (for major+minor axes)

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

IN_CSV = Path("beam2_clip_summary.csv")          # <-- change if needed
OUT_PNG = IN_CSV.with_name("beam2_clip_fit.png")

def w_model(z_mm, w0_um, z0_mm, zR_mm):
    # w(z) = w0 * sqrt(1 + ((z - z0)/zR)^2)
    return w0_um * np.sqrt(1.0 + ((z_mm - z0_mm) / zR_mm) ** 2)

def fit_axis(z_mm, w_um, name="axis"):
    z_mm = np.asarray(z_mm, float)
    w_um = np.asarray(w_um, float)
    ok = np.isfinite(z_mm) & np.isfinite(w_um) & (w_um > 0)
    z_mm, w_um = z_mm[ok], w_um[ok]
    if z_mm.size < 4:
        raise ValueError(f"Need >=4 points to fit {name}")

    i = np.argmin(w_um)
    w0_guess = w_um[i]
    z0_guess = z_mm[i]
    zR_guess = max(1e-6, 0.25 * (z_mm.max() - z_mm.min()))

    # bounds: w0>0, zR>0
    p0 = [w0_guess, z0_guess, zR_guess]
    bounds = ([1e-9, -np.inf, 1e-9], [np.inf, np.inf, np.inf])

    popt, pcov = curve_fit(w_model, z_mm, w_um, p0=p0, bounds=bounds, maxfev=20000)
    perr = np.sqrt(np.diag(pcov))
    return popt, perr  # (w0,z0,zR), (errs...)

df = pd.read_csv(IN_CSV).dropna(subset=["z_mm"]).sort_values("z_mm")

z = df["z_mm"].to_numpy(float)

# diameters (µm)
Dmaj = df["clip_major_um"].to_numpy(float)
Dmin = df["clip_minor_um"].to_numpy(float)

# radii (µm) for propagation fit
wmaj = 0.5 * Dmaj
wmin = 0.5 * Dmin

# ellipticity (minor/major) going forward
ell = Dmin / Dmaj

# power (whatever units are in the file)
P = df["total_power"].to_numpy(float)

# fits
(pmaj, emaj) = fit_axis(z, wmaj, "major")
(pmin, emin) = fit_axis(z, wmin, "minor")
(w0M, z0M, zRM), (w0M_e, z0M_e, zRM_e) = pmaj, emaj
(w0m, z0m, zRm), (w0m_e, z0m_e, zRm_e) = pmin, emin

# dense z for curves
zfit = np.linspace(z.min(), z.max(), 600)

# ---- plot ----
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# top: diameters + power
ax1.plot(z, Dmaj, "o", label="Major diameter (clip 13.5%)")
ax1.plot(z, Dmin, "o", label="Minor diameter (clip 13.5%)")

ax1.plot(zfit, 2.0 * w_model(zfit, w0M, z0M, zRM), "-", label=f"Fit major (z0={z0M:.1f} mm, zR={zRM:.1f} mm)")
ax1.plot(zfit, 2.0 * w_model(zfit, w0m, z0m, zRm), "-", label=f"Fit minor (z0={z0m:.1f} mm, zR={zRm:.1f} mm)")

ax1.set_ylabel("Beam diameter (µm)")
ax1.grid(True)
ax1.legend(loc="upper left")

ax1b = ax1.twinx()
ax1b.plot(z, P, "o--", label="Total power")
ax1b.set_ylabel("Total power (as in file)")
ax1b.legend(loc="upper right")

# bottom: ellipticity
ax2.plot(z, ell, "o-")
ax2.set_xlabel("z (mm)")
ax2.set_ylabel("Ellipticity (minor/major)")
ax2.grid(True)

fig.suptitle("Clip-diameter beam characterisation + Gaussian propagation fit")
fig.tight_layout()
fig.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
plt.close(fig)

print(f"Wrote: {OUT_PNG}\n")

print("Major axis fit (radius w = D/2):")
print(f"  w0 = {w0M:.2f} ± {w0M_e:.2f} µm")
print(f"  z0 = {z0M:.2f} ± {z0M_e:.2f} mm")
print(f"  zR = {zRM:.2f} ± {zRM_e:.2f} mm\n")

print("Minor axis fit (radius w = D/2):")
print(f"  w0 = {w0m:.2f} ± {w0m_e:.2f} µm")
print(f"  z0 = {z0m:.2f} ± {z0m_e:.2f} mm")
print(f"  zR = {zRm:.2f} ± {zRm_e:.2f} mm")
