"""
Fit Gaussian-beam divergence to extract waist size w0 and waist location z0
from your beam_summary.csv (produced by the previous script).

Model (general, includes M^2):
    w(z)^2 = w0^2 + ( (M2 * λ) / (π w0) )^2 * (z - z0)^2

We convert your D4σ diameters to w via:
    w = D / 2
(because for a perfect Gaussian D4σ = D(1/e^2) = 2w; for non-ideal beams this is
still the standard way to map measured second-moment width into an equivalent w.)

Fits major/minor separately (so you get two waists if the beam is astigmatic).
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

# -------- settings --------
SUMMARY_CSV = Path(r"data/2505020/beam_summary.csv")  # <-- change this
LAMBDA_M = 1064e-9            # <-- change if not 1064 nm
Z_UNITS = "mm"                # "mm" if your filenames are like 275 meaning mm
USE_MAJOR_MINOR = True        # True: fit D_major/D_minor ; False: fit Dx/Dy
# -------------------------


def gaussian_w2(z, w0, z0, M2):
    """Return w(z)^2"""
    k = (M2 * LAMBDA_M) / (np.pi * w0)
    return w0**2 + (k**2) * (z - z0) ** 2


def fit_axis(z_m, w_m, axis_name="axis"):
    """Fit w(z) to get w0, z0, M2. Returns dict with results."""
    z_m = np.asarray(z_m, float)
    w_m = np.asarray(w_m, float)

    ok = np.isfinite(z_m) & np.isfinite(w_m) & (w_m > 0)
    z_m = z_m[ok]
    w_m = w_m[ok]

    if z_m.size < 4:
        raise ValueError(f"Not enough points to fit {axis_name} (need >= 4).")

    # Initial guesses:
    i_min = np.argmin(w_m)
    w0_guess = w_m[i_min]
    z0_guess = z_m[i_min]
    M2_guess = 1.2

    # Fit w^2 for more stable behavior
    y = w_m**2

    # Bounds: w0>0, M2>=1 (at least for physical-ish beams)
    p0 = [w0_guess, z0_guess, M2_guess]
    bounds = ([1e-12, -np.inf, 1.0], [np.inf, np.inf, 100.0])

    popt, pcov = curve_fit(gaussian_w2, z_m, y, p0=p0, bounds=bounds, maxfev=20000)
    w0, z0, M2 = popt
    perr = np.sqrt(np.diag(pcov))
    w0_e, z0_e, M2_e = perr

    # Derived: Rayleigh range and far-field half-angle divergence
    zR = (np.pi * w0**2) / (M2 * LAMBDA_M)             # meters
    theta = (M2 * LAMBDA_M) / (np.pi * w0)             # radians (half-angle)

    return {
        "axis": axis_name,
        "w0_m": w0, "w0_m_err": w0_e,
        "z0_m": z0, "z0_m_err": z0_e,
        "M2": M2, "M2_err": M2_e,
        "zR_m": zR,
        "theta_rad": theta,
        "theta_mrad": theta * 1e3,
    }


df = pd.read_csv(SUMMARY_CSV)
df = df.dropna(subset=["z_from_name"]).copy()
df = df.sort_values("z_from_name")

z = df["z_from_name"].to_numpy(dtype=float)
if Z_UNITS.lower() == "mm":
    z_m = z * 1e-3
elif Z_UNITS.lower() == "m":
    z_m = z
else:
    raise ValueError("Z_UNITS must be 'mm' or 'm'.")

if USE_MAJOR_MINOR:
    # If your summary has mm columns, use them; else fall back to µm
    if "D_major_mm" in df.columns and "D_minor_mm" in df.columns:
        Dmaj_m = df["D_major_mm"].to_numpy(float) * 1e-3
        Dmin_m = df["D_minor_mm"].to_numpy(float) * 1e-3
    else:
        Dmaj_m = df["D_major_um"].to_numpy(float) * 1e-6
        Dmin_m = df["D_minor_um"].to_numpy(float) * 1e-6

    wmaj_m = Dmaj_m / 2.0
    wmin_m = Dmin_m / 2.0

    res_major = fit_axis(z_m, wmaj_m, "major")
    res_minor = fit_axis(z_m, wmin_m, "minor")
    results = [res_major, res_minor]
else:
    # Fit the raw X/Y second-moment diameters
    Dx_m = df["D4s_x_um"].to_numpy(float) * 1e-6
    Dy_m = df["D4s_y_um"].to_numpy(float) * 1e-6
    wx_m = Dx_m / 2.0
    wy_m = Dy_m / 2.0

    res_x = fit_axis(z_m, wx_m, "x")
    res_y = fit_axis(z_m, wy_m, "y")
    results = [res_x, res_y]


# ---- print results nicely ----
for r in results:
    print(f"\n=== Fit: {r['axis']} ===")
    print(f"w0 = {r['w0_m']*1e6:.3f} ± {r['w0_m_err']*1e6:.3f} µm")
    print(f"z0 = {r['z0_m']*1e3:.3f} ± {r['z0_m_err']*1e3:.3f} mm   (relative to your filename-origin)")
    print(f"M^2 = {r['M2']:.3f} ± {r['M2_err']:.3f}")
    print(f"zR = {r['zR_m']*1e3:.3f} mm")
    print(f"divergence half-angle θ = {r['theta_mrad']:.3f} mrad")
    print(f"full-angle divergence = {2*r['theta_mrad']:.3f} mrad")
