from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

IN_CSV = Path("BEAM2.csv")       
OUT_GRAPH = IN_CSV.with_name("beam2_clip_fit.pdf")

def w_model(z_mm, w0_um, z0_mm, zR_mm):
    # w(z) = w0 * sqrt(1 + ((z - z0)/zR)^2)
    return w0_um * np.sqrt(1.0 + ((z_mm - z0_mm) / zR_mm) ** 2)


lambd = 1064
def w_model_wo_zR(z_mm, w0_um, z0_mm):
    # w(z) = w0 * sqrt(1 + ((z - z0)/zR)^2)
    return w0_um * np.sqrt(1.0 + (lambd*(z_mm - z0_mm) / np.pi/w0_um**2) ** 2)

# This function initialises the fitting and calls it
def fit_axis(z_mm, w_um, name="axis"):
    z_mm = np.asarray(z_mm, float)
    w_um = np.asarray(w_um, float)
    ok = np.isfinite(z_mm) & np.isfinite(w_um) & (w_um > 0)
    z_mm, w_um = z_mm[ok], w_um[ok]
    if z_mm.size < 4:
        raise ValueError(f"Need >=4 points to fit {name}")

    i = np.argmin(w_um)
    w0_guess = w_um[i]*0.5  # guess waist radius is half the smallest measured radius
    z0_guess = -150
    zR_guess = max(1e-6, 0.25 * (z_mm.max() - z_mm.min()))

    # bounds: w0>0, zR>0
    p0 = [w0_guess, z0_guess]
    bounds = ([1e-9, -np.inf], [np.inf, np.inf])

    popt, pcov = curve_fit(w_model_wo_zR, z_mm, w_um, p0=p0, bounds=bounds, maxfev=20000)
    perr = np.sqrt(np.diag(pcov))
    return popt, perr  # (w0,z0), (errs...)

df = pd.read_csv(IN_CSV).dropna(subset=["z_mm"]).sort_values("z_mm")

z = df["z_mm"].to_numpy(float)

# diameters (µm) rto radii
wmaj = 0.5 * df["Dmin_um"].to_numpy(float)
wmin = 0.5 * df["Dmaj_um"].to_numpy(float)


# fits
(pmaj, emaj) = fit_axis(z, wmaj, "major")
(pmin, emin) = fit_axis(z, wmin, "minor")
(w0M, z0M), (w0M_e, z0M_e) = pmaj, emaj
(w0m, z0m), (w0m_e, z0m_e) = pmin, emin

print(f"Wrote: {OUT_GRAPH}\n")

zRM = np.pi*w0M**2/lambd
theta_M = lambd/(np.pi*w0M)
theta_m = lambd/(np.pi*w0m)
print("Major axis fit:")
print(f"  w0 = {w0M:.2f} µm")
print(f"  z0 = {z0M:.2f} mm")
print(f"  zR = {zRM:.2f}  mm")
print(f"  θ = {theta_M:.2f} mrad")

zRm = np.pi*w0m**2/lambd
print("Minor axis fit:")
print(f"  w0 = {w0m:.2f} µm")
print(f"  z0 = {z0m:.2f} mm")
print(f"  zR = {zRm:.2f} mm")
print(f"  θ = {theta_m:.2f} mrad")


new_plot = True

# ---- plot ----
if new_plot:
    c_purple = (130/255, 23/255, 112/255)
    c_green = (41/255, 95/255, 36/255)

    fig, ax = plt.subplots(figsize=(6, 4))

    ax.plot(z, 2.0 * wmaj, "o", label="Major diameter", color=c_purple)
    ax.plot(z, 2.0 * wmin, "o", label="Minor diameter", color=c_green)

    zfit = np.linspace(z0M*2, z.max(), 1900)

    ax.plot(
        zfit, 2.0 * w_model_wo_zR(zfit, w0M, z0M),
        "-", color=c_purple
    )
    ax.plot(
        zfit, 2.0 * w_model_wo_zR(zfit, w0m, z0m),
        "-", color=c_green
    )

    # --- waist markers ---
    ax.axvline(
        z0M, color=c_purple, linestyle="--", alpha=0.6,
        label=f"Major waist z₀ = {z0M:.1f} mm"
    )
    ax.axvline(
        z0m, color=c_green, linestyle="--", alpha=0.6,
        label=f"Minor waist z₀ = {z0m:.1f} mm"
    )
    
    ax.axvline(
        0, color="black", linestyle="--", alpha=0.7,
        label=f"laser head"
    )


    ax.set_ylabel(r"Beam diameter $\omega_0$ (µm)")
    ax.set_xlabel("z (mm)")
    ax.grid(True)
    ax.legend(loc="upper left")

    fig.tight_layout()
    fig.savefig(OUT_GRAPH, dpi=300, bbox_inches="tight")
    plt.close(fig)





