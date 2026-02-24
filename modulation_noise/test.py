import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.signal import detrend, welch


# === input ===
IN_CSV = Path("data\EOM_sideband_test_20260220_160507.csv")  # or r"C:\path\to\ttt.csv"

def read_moku_phasemeter_csv(path: Path) -> pd.DataFrame:
    """
    Read a Moku:Pro Phasemeter CSV with '%' metadata lines and a header line like:
      % Time (s), Input A Frequency (Hz), ...
    Returns a numeric DataFrame with a relative time column.
    """
    header_line = None
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.lstrip().startswith("% Time"):
                header_line = line.strip()
                break
    if header_line is None:
        raise ValueError("No '% Time (s), ...' header line found in the CSV.")

    colnames = [c.strip() for c in header_line.lstrip("%").split(",")]

    # Read numeric data, skipping all comment lines
    df = pd.read_csv(path, comment="%", header=None, names=colnames)

    # Convert to numeric (turns 'nan' strings into real NaNs)
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Keep only rows with time, and drop "all-NaN" glitch rows
    time_col = "Time (s)"
    df = df.dropna(subset=[time_col]).copy()
    df = df.dropna(
        how="all",
        subset=[c for c in df.columns if c != time_col]
    )

    # Sort and make relative time
    df = df.sort_values(time_col).reset_index(drop=True)
    df["t_rel (s)"] = df[time_col] - df[time_col].iloc[0]
    return df

df = read_moku_phasemeter_csv(IN_CSV)

t  = df["t_rel (s)"]
fA = df["Input B I (V)"]
fB = df["Input B I (V)"]

pA = df["Input A Phase (cyc)"]
pB = df["Input B Phase (cyc)"]

# Unwrap phase (stored in cycles): unwrap in radians, convert back to cycles
pA_unwrap = np.unwrap(2*np.pi*pA.to_numpy()) / (2*np.pi)
pB_unwrap = np.unwrap(2*np.pi*pB.to_numpy()) / (2*np.pi)

# === Plot: Frequency vs time ===
plt.figure(figsize=(10, 5))
#plt.plot(t, fA, label="Input A frequency (Hz)")
plt.plot(t, fB, label="Input B Amplitude (Hz)")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (Hz)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# === Plot: Phase vs time ===
plt.figure(figsize=(10, 5))
#plt.plot(t, pA_unwrap, label="Input A phase (cycles, unwrapped)")
plt.plot(t, pB_unwrap, label="Input B phase (cycles, unwrapped)")
plt.xlabel("Time (s)")
plt.ylabel("Phase (cycles)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
