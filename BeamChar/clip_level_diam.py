from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
IN_DIR = BASE  / "data" / "2505020" / "converted"
CLIP = 0.1353   # 13.53% = 1/e^2

OUT_FILE = "beam_clip_summary.csv"

def clip_diameter(x, I, clip=0.1353):
    x = np.asarray(x, float)
    I = np.asarray(I, float)

    order = np.argsort(x)
    x = x[order]
    I = I[order]

    I = I - np.min(I)
    I[I < 0] = 0.0

    Imax = I.max()
    if Imax <= 0:
        return np.nan

    level = clip * Imax
    above = I >= level
    idx = np.where(above)[0]

    if idx.size < 2:
        return np.nan

    i1, i2 = idx[0], idx[-1]

    def interp(iL, iR):
        xL, xR = x[iL], x[iR]
        yL, yR = I[iL], I[iR]
        return xL + (level - yL) * (xR - xL) / (yR - yL)

    if i1 == 0:
        x_left = x[0]
    else:
        x_left = interp(i1 - 1, i1)

    if i2 == len(I) - 1:
        x_right = x[-1]
    else:
        x_right = interp(i2, i2 + 1)

    return x_right - x_left




rows = []

for f in sorted(IN_DIR.glob("*.csv")):

    df = pd.read_csv(f, sep=";", encoding="latin1")

    x  = df.iloc[:, 0].to_numpy()
    Ix = df.iloc[:, 1].to_numpy()
    y  = df.iloc[:, 2].to_numpy()
    Iy = df.iloc[:, 3].to_numpy()

    Dx = clip_diameter(x, Ix, CLIP)
    Dy = clip_diameter(y, Iy, CLIP)

    major = np.nanmax([Dx, Dy])
    minor = np.nanmin([Dx, Dy])
    ellip =  minor / major if np.isfinite(minor) and major > 0 else np.nan

    # distance from filename if numeric (e.g. 275.csv)
    try:
        z = float(f.stem)
    except:
        z = np.nan

    rows.append({
        "file": f.name,
        "z_from_name": z,
        "Dx_1e2_um": Dx,
        "Dy_1e2_um": Dy,
        "D_major_1e2_um": major,
        "D_minor_1e2_um": minor,
        "ellipticity_major_over_minor": ellip,
    })

pd.DataFrame(rows).to_csv(OUT_FILE, index=False)
print(f"Wrote: {OUT_FILE}")