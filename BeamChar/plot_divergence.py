from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ---- settings ----
SUMMARY_CSV = Path(r"data/2505020/beam_summary.csv")  # <-- change this
OUT_DIR = SUMMARY_CSV.parent
USE_MM = True  # plot diameters in mm (True) or µm (False)
# ------------------

df = pd.read_csv(SUMMARY_CSV)

# keep only rows with a usable distance
df = df.dropna(subset=["z_from_name"]).copy()
df = df.sort_values("z_from_name")

z = df["z_from_name"].to_numpy()

# choose diameter columns + label
if USE_MM:
    dmaj = df["D_major_mm"].to_numpy()
    dmin = df["D_minor_mm"].to_numpy()
    dx = (df["D4s_x_um"] / 1000.0).to_numpy()
    dy = (df["D4s_y_um"] / 1000.0).to_numpy()
    dlabel = "Beam diameter (mm)"
else:
    dmaj = df["D_major_um"].to_numpy()
    dmin = df["D_minor_um"].to_numpy()
    dx = df["D4s_x_um"].to_numpy()
    dy = df["D4s_y_um"].to_numpy()
    dlabel = "Beam diameter (µm)"

ell = df["ellipticity_major_over_minor"].to_numpy()

# ---- plot diameters ----
plt.figure()
plt.plot(z, dmaj, marker="o", label="Major (from Dx/Dy)")
plt.plot(z, dmin, marker="o", label="Minor (from Dx/Dy)")
plt.xlabel("Distance (from filename)")
plt.ylabel(dlabel)
plt.title("Beam diameters vs distance (D4σ)")
plt.grid(True, which="both")
plt.legend()
diam_path = OUT_DIR / "diameters_vs_distance.png"
plt.savefig(diam_path, dpi=200, bbox_inches="tight")
plt.close()

# Optional: also plot Dx and Dy directly (useful if you want to see axis swap etc.)
plt.figure()
plt.plot(z, dx, marker="o", label="Dx (D4σ)")
plt.plot(z, dy, marker="o", label="Dy (D4σ)")
plt.xlabel("Distance (from filename)")
plt.ylabel(dlabel)
plt.title("Dx and Dy vs distance (D4σ)")
plt.grid(True, which="both")
plt.legend()
dxy_path = OUT_DIR / "dx_dy_vs_distance.png"
plt.savefig(dxy_path, dpi=200, bbox_inches="tight")
plt.close()

# ---- plot ellipticity ----
plt.figure()
plt.plot(z, ell, marker="o")
plt.xlabel("Distance (from filename)")
plt.ylabel("Ellipticity (major/minor)")
plt.title("Ellipticity vs distance")
plt.grid(True, which="both")
ell_path = OUT_DIR / "ellipticity_vs_distance.png"
plt.savefig(ell_path, dpi=200, bbox_inches="tight")
plt.close()

print("Wrote:")
print(diam_path)
print(dxy_path)
print(ell_path)
