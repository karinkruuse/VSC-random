import re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

BASE = Path(__file__).resolve().parent
IN_DIR = BASE  / "data" / "2505020" / "converted"
OUT_PNG = IN_DIR / "all_heatmaps_shared_scale.png"
BASELINE_FRACTION = 0.10
ENCODING = "latin1"


def read_profile_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding=ENCODING)
    if df.shape[1] == 1:
        df = pd.read_csv(path, sep=";", engine="python", encoding=ENCODING)

    df = df.loc[:, ~df.columns.astype(str).str.contains(r"^Unnamed", regex=True)].copy()
    cols = list(df.columns)

    pos_cols = [c for c in cols if "pos" in str(c).lower()]
    int_cols = [c for c in cols if c not in pos_cols]

    if len(pos_cols) < 2 or len(int_cols) < 2:
        pos_cols = cols[:2]
        int_cols = cols[2:4]

    def pick(cands, axis):
        for c in cands:
            if re.search(rf"\b{axis}\b", str(c), flags=re.IGNORECASE):
                return c
        return None

    pos_x = pick(pos_cols, "X") or pos_cols[0]
    pos_y = pick(pos_cols, "Y") or pos_cols[1]
    int_x = pick(int_cols, "X") or int_cols[0]
    int_y = pick(int_cols, "Y") or int_cols[1]

    return pd.DataFrame({
        "x": pd.to_numeric(df[pos_x], errors="coerce"),
        "Ix": pd.to_numeric(df[int_x], errors="coerce"),
        "y": pd.to_numeric(df[pos_y], errors="coerce"),
        "Iy": pd.to_numeric(df[int_y], errors="coerce"),
    }).dropna()


def background_subtract(I):
    I = np.asarray(I, float)
    k = max(1, int(BASELINE_FRACTION * I.size))
    baseline = np.nanmedian(np.partition(I, k)[:k])
    I = I - baseline
    I[I < 0] = 0.0
    return I


def d4sigma(pos, I):
    s = I.sum()
    if s <= 0:
        return np.nan, np.nan
    x0 = (pos * I).sum() / s
    var = ((pos - x0) ** 2 * I).sum() / s
    return x0, 4 * np.sqrt(var)


def make_heatmap(x, Ix, y, Iy):
    ix = np.argsort(x)
    iy = np.argsort(y)
    x = x[ix]
    y = y[iy]
    Ix = Ix[ix]
    Iy = Iy[iy]
    I2D = np.outer(Iy, Ix)
    return x, y, I2D


# ---------- load all data first ----------
files = sorted([f for f in IN_DIR.glob("*.csv") if f.name != "beam_summary.csv"])

maps = []
meta = []

global_min = np.inf
global_max = -np.inf

for f in files:
    print(f"Processing: {f.name}")
    df = read_profile_csv(f)

    x = df["x"].to_numpy()
    y = df["y"].to_numpy()
    Ix = background_subtract(df["Ix"].to_numpy())
    Iy = background_subtract(df["Iy"].to_numpy())

    x0, Dx = d4sigma(x, Ix)
    y0, Dy = d4sigma(y, Iy)

    xs, ys, I2D = make_heatmap(x, Ix, y, Iy)

    global_min = min(global_min, I2D.min())
    global_max = max(global_max, I2D.max())

    maps.append((xs, ys, I2D))
    meta.append((f.name, x0, y0, Dx, Dy))


# ---------- plotting ----------
n = len(maps)
cols = int(np.ceil(np.sqrt(n)))
rows = int(np.ceil(n / cols))

fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows), squeeze=False)

for ax, (xs, ys, I2D), (name, x0, y0, Dx, Dy) in zip(axes.flat, maps, meta):
    extent = [xs.min(), xs.max(), ys.min(), ys.max()]
    im = ax.imshow(
        I2D,
        origin="lower",
        extent=extent,
        aspect="equal",
        vmin=global_min,
        vmax=global_max
    )

    ax.set_title(name, fontsize=9)
    ax.set_xlabel("x (µm)")
    ax.set_ylabel("y (µm)")

    # centroid
    ax.plot(x0, y0, "x", color="white")

    # ellipse + diameters
    if np.isfinite(Dx) and np.isfinite(Dy):
        ell = Ellipse((x0, y0), Dx, Dy, fill=False, edgecolor="white", linewidth=2)
        ax.add_patch(ell)
        ax.plot([x0 - Dx/2, x0 + Dx/2], [y0, y0], color="white", linewidth=1.5)
        ax.plot([x0, x0], [y0 - Dy/2, y0 + Dy/2], color="white", linewidth=1.5)

# remove empty subplots
for ax in axes.flat[len(maps):]:
    ax.axis("off")

# shared colorbar
cbar = fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.85)
cbar.set_label("arb. intensity (Ix · Iy)")

fig.suptitle("All beam profiles — shared colour scale, D4σ overlay", fontsize=14)
plt.tight_layout()
plt.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
plt.close()

print(f"Wrote: {OUT_PNG}")
