from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

SUMMARY_CSV = Path("beam_clip_summary.csv")
OUT_DIR = SUMMARY_CSV.parent
USE_MM = True  # True -> mm, False -> µm

df = pd.read_csv(SUMMARY_CSV).dropna(subset=["z_from_name"]).sort_values("z_from_name")

z = df["z_from_name"].to_numpy()

# columns from the NEW clip-summary output
Dx = df["Dx_1e2_um"].to_numpy()
Dy = df["Dy_1e2_um"].to_numpy()
Dmaj = df["D_major_1e2_um"].to_numpy()
Dmin = df["D_minor_1e2_um"].to_numpy()
ell = df["ellipticity_major_over_minor"].to_numpy()

if USE_MM:
    s = 1 / 1000.0
    Dx, Dy, Dmaj, Dmin = Dx * s, Dy * s, Dmaj * s, Dmin * s
    dlabel = "Beam diameter (mm)"
else:
    dlabel = "Beam diameter (µm)"

# diameters (major/minor)
plt.figure()
plt.plot(z, Dmaj, "o-", label="Major (clip, 1/e²)")
plt.plot(z, Dmin, "o-", label="Minor (clip, 1/e²)")
plt.xlabel("Distance (from filename)")
plt.ylabel(dlabel)
plt.title("Beam diameters vs distance (clip 1/e²)")
plt.grid(True)
plt.legend()
diam_path = OUT_DIR / "diameters_vs_distance_clip.png"
plt.savefig(diam_path, dpi=200, bbox_inches="tight")
plt.close()

# Dx / Dy
plt.figure()
plt.plot(z, Dx, "o-", label="Dx (clip, 1/e²)")
plt.plot(z, Dy, "o-", label="Dy (clip, 1/e²)")
plt.xlabel("Distance (from filename)")
plt.ylabel(dlabel)
plt.title("Dx and Dy vs distance (clip 1/e²)")
plt.grid(True)
plt.legend()
dxy_path = OUT_DIR / "dx_dy_vs_distance_clip.png"
plt.savefig(dxy_path, dpi=200, bbox_inches="tight")
plt.close()

# ellipticity
plt.figure()
plt.plot(z, ell, "o-")
plt.xlabel("Distance (from filename)")
plt.ylabel("Ellipticity (major/minor)")
plt.title("Ellipticity vs distance (clip 1/e²)")
plt.grid(True)
ell_path = OUT_DIR / "ellipticity_vs_distance_clip.png"
plt.savefig(ell_path, dpi=200, bbox_inches="tight")
plt.close()

print("Wrote:")
print(diam_path)
print(dxy_path)
print(ell_path)
