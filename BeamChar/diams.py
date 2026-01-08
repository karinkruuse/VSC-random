import re
from pathlib import Path
import numpy as np
import pandas as pd

# -------- settings --------
BASE = Path(__file__).resolve().parent
IN_DIR = BASE  / "data" / "2505020" / "converted"
OUT_CSV = IN_DIR / "beam_summary.csv"

# Beam diameter definition:
# ISO 11146 second-moment "D4σ" on the 1D marginal profiles:
# D = 4 * sqrt( <(x-x0)^2>_I )
BASELINE_FRACTION = 0.02   # estimate background from lowest 10% of samples

# -------------------------

def read_profile_csv(path: Path) -> pd.DataFrame:
    """
    Robustly read your files (some end up being single-column semicolon-separated).
    Returns a dataframe with columns: position_x, intensity_x, position_y, intensity_y
    """
    # 1) try normal CSV
    df = pd.read_csv(path, encoding="latin1")
    if df.shape[1] == 1:
        # likely semicolon-separated lines preserved as one column
        df = pd.read_csv(path, sep=";", engine="python", encoding="latin1")

    # drop trailing empty column if present
    df = df.loc[:, ~df.columns.str.contains(r"^Unnamed", case=False, regex=True)].copy()

    # normalize column names a bit
    cols = list(df.columns)

    # Find position columns (contain "Pos") and intensity columns (the remaining two)
    pos_cols = [c for c in cols if "pos" in c.lower()]
    if len(pos_cols) < 2:
        raise ValueError(f"{path.name}: couldn't find two position columns. Columns={cols}")

    # Heuristic: intensity columns are the non-pos numeric columns (often named "X" and "Y")
    int_cols = [c for c in cols if c not in pos_cols]
    if len(int_cols) < 2:
        # fallback: take the next two after the first two
        if len(cols) >= 4:
            pos_cols = cols[:2]
            int_cols = cols[2:4]
        else:
            raise ValueError(f"{path.name}: couldn't find two intensity columns. Columns={cols}")

    # In your sample: ['Pos X [µm]', 'X', 'Pos Y [µm]', 'Y']
    # Map them explicitly by matching X/Y in the name; fallback to order.
    def pick_by_axis(candidates, axis_letter):
        for c in candidates:
            if re.search(rf"\b{axis_letter}\b", str(c), flags=re.IGNORECASE):
                return c
        return None

    pos_x = pick_by_axis(pos_cols, "X") or pos_cols[0]
    pos_y = pick_by_axis(pos_cols, "Y") or pos_cols[1]

    int_x = pick_by_axis(int_cols, "X") or int_cols[0]
    int_y = pick_by_axis(int_cols, "Y") or int_cols[1]

    out = pd.DataFrame({
        "pos_x": pd.to_numeric(df[pos_x], errors="coerce"),
        "I_x":   pd.to_numeric(df[int_x], errors="coerce"),
        "pos_y": pd.to_numeric(df[pos_y], errors="coerce"),
        "I_y":   pd.to_numeric(df[int_y], errors="coerce"),
    }).dropna()

    return out


def d4sigma(pos, I, baseline_fraction=0.10):
    """Return (centroid, D4σ) in same units as pos."""
    pos = np.asarray(pos, dtype=float)
    I = np.asarray(I, dtype=float)

    # background subtract (handles negative junk)
    k = max(1, int(baseline_fraction * I.size))
    baseline = np.nanmedian(np.partition(I, k)[:k])
    I = I - baseline
    I[I < 0] = 0.0

    s = I.sum()
    if not np.isfinite(s) or s <= 0:
        return np.nan, np.nan

    x0 = (pos * I).sum() / s
    var = ((pos - x0) ** 2 * I).sum() / s

    D = 4.0 * np.sqrt(var)
    return x0, D


def parse_z_from_filename(path: Path):
    """If file is named like '275.csv' -> z=275 (float). Otherwise NaN."""
    try:
        return float(path.stem)
    except Exception:
        return np.nan


rows = []
for f in sorted(IN_DIR.glob("*.csv")):
    if f.name == OUT_CSV.name:
        continue

    df = read_profile_csv(f)

    x0, Dx = d4sigma(df["pos_x"], df["I_x"], BASELINE_FRACTION)
    y0, Dy = d4sigma(df["pos_y"], df["I_y"], BASELINE_FRACTION)

    major = np.nanmax([Dx, Dy])
    minor = np.nanmin([Dx, Dy])

    # Two common definitions; you can pick one:
    ellipticity_ratio = minor /  major if np.isfinite(major) and np.isfinite(minor) and major > 0 else np.nan
    ellipticity_1minus = 1.0 - (minor / major) if np.isfinite(major) and np.isfinite(minor) and major > 0 else np.nan

    rows.append({
        "file": f.name,
        "z_from_name": parse_z_from_filename(f),
        "x0_um": x0,
        "y0_um": y0,
        "D4s_x_um": Dx,
        "D4s_y_um": Dy,
        "D_major_um": major,
        "D_minor_um": minor,
        "ellipticity_major_over_minor": ellipticity_ratio,
        "ellipticity_1_minus_minor_over_major": ellipticity_1minus,
        "D_major_mm": major / 1000.0 if np.isfinite(major) else np.nan,
        "D_minor_mm": minor / 1000.0 if np.isfinite(minor) else np.nan,
    })

summary = pd.DataFrame(rows)
summary.to_csv(OUT_CSV, index=False)
print(f"Wrote: {OUT_CSV}")
