"""
Configure which channels to use with CHANNELS below. With >=3 channels the script
also solves for the individual per-channel floors n_i from the pairwise
differences (assuming they are mutually independent):
    S(a-b)^2 = n_a^2 + n_b^2   -> invertible for 3 channels.

Two "theta"-style estimators are reported for direct comparison with a
modulation measurement:
    half-difference  0.5*(chA - chB)         (matches theta_m = 0.5*(USB-LSB))
    per-channel n_i  (from the 3x3 solve)

Reads the same .npy structured-array format; sampling rate is taken from the
sibling .txt header ("Acquisition rate:") or the Time column.
"""

from pathlib import Path
import itertools
import numpy as np
from scipy.signal import welch, detrend

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
DATA = Path("data/PMtest_20260805_150546.npy")   # <-- input .npy
CHANNELS = [1, 2, 4]                          # <-- which Moku inputs to use (2 or more)
CUT_START_S = 0.0                            # trim from start
CUT_END_S   = 0.0                            # trim from end

# PSD segment lengths (s): long for low-f resolution, short for a clean hi-f floor
SEG_LONG_S  = 2000.0
SEG_SHORT_S = 200.0

# bands to report medians over (Hz)
BANDS = [(1e-3, 1e-2), (1e-2, 1e-1), (1e-1, 1.0), (1.0, 15.0)]
BAND_USE_SHORT = (1.0, 15.0)   # bands with lo >= this[0] use the short-segment PSD

# optional: check for a spectral peak in this window (e.g. a thermal line)
PEAK_WINDOW = (1.2e-3, 1.6e-3)
PEAK_SIDEBANDS = (2.5e-3, 5e-3)

MAKE_PLOT = True
PLOT_PATH = DATA.with_name(DATA.stem + "_floor.png")


# ------------------------------------------------------------------
# load
# ------------------------------------------------------------------
def get_fs(data_path):
    txt = data_path.with_suffix(".txt")
    if txt.exists():
        for line in txt.read_text(errors="ignore").splitlines():
            if "Acquisition rate:" in line:
                return float(line.split("Acquisition rate:")[1].split("Hz")[0])
    return None


def load(data_path, channels, cut_start, cut_end):
    arr = np.load(data_path, allow_pickle=True)
    fs = get_fs(data_path)
    t = arr["Time (s)"]
    if fs is None:
        fs = 1.0 / np.median(np.diff(t))
    mask = (t >= t[0] + cut_start) & (t <= t[-1] - cut_end)
    phases = {}
    for ch in channels:
        key = f"Input {ch} Phase (cyc)"
        if key not in arr.dtype.names:
            raise KeyError(f"{key} not in file; available: {arr.dtype.names}")
        phases[ch] = detrend(arr[key][mask].astype(float))
    return phases, fs


def psd(x, fs, seg_s):
    n = int(seg_s * fs)
    n = max(256, min(n, len(x)))
    f, P = welch(x, fs=fs, window="hann", nperseg=n, noverlap=n // 2,
                 detrend="linear", scaling="density")
    return f, P


def band_median(f, P, lo, hi):
    b = (f > lo) & (f < hi)
    return np.median(np.sqrt(P[b])) if b.any() else np.nan


def solve_channel_floors(diff_asd_sq, channels):
    """
    Given the *variances* (ASD^2) of every pairwise difference, solve for each
    channel's own variance assuming independence:
        S(a-b)^2 = n_a^2 + n_b^2.
    For exactly 3 channels this is exact:
        n_a^2 = (S_ab^2 + S_ac^2 - S_bc^2)/2, etc.
    For >3 channels a least-squares solve is used.
    """
    ch = list(channels)
    pairs = list(itertools.combinations(ch, 2))
    # build linear system A x = y, x = n_i^2
    A = np.zeros((len(pairs), len(ch)))
    y = np.zeros(len(pairs))
    for r, (a, b) in enumerate(pairs):
        A[r, ch.index(a)] = 1.0
        A[r, ch.index(b)] = 1.0
        y[r] = diff_asd_sq[(a, b)]
    x, *_ = np.linalg.lstsq(A, y, rcond=None)
    x = np.clip(x, 0, None)
    return {c: np.sqrt(v) for c, v in zip(ch, x)}


# ------------------------------------------------------------------
# main
# ------------------------------------------------------------------
def main():
    phases, fs = load(DATA, CHANNELS, CUT_START_S, CUT_END_S)
    print(f"file: {DATA.name}   fs = {fs:.4f} Hz   channels = {CHANNELS}")
    print(f"samples = {len(next(iter(phases.values())))}\n")

    pairs = list(itertools.combinations(CHANNELS, 2))
    diffs = {(a, b): phases[a] - phases[b] for (a, b) in pairs}

    # PSDs of each difference at both resolutions
    P_long = {p: psd(d, fs, SEG_LONG_S) for p, d in diffs.items()}
    P_short = {p: psd(d, fs, SEG_SHORT_S) for p, d in diffs.items()}

    # ---- difference ASDs per band ----
    print("Pairwise difference ASD (cyc/rtHz), median per band:")
    header = "  band(Hz)      " + "".join(f"{a}-{b:<8}" for (a, b) in pairs)
    print(header)
    for lo, hi in BANDS:
        use_short = lo >= BAND_USE_SHORT[0]
        row = f"  {lo:.0e}-{hi:<7.0e}"
        for p in pairs:
            f_, P_ = P_short[p] if use_short else P_long[p]
            row += f"{band_median(f_, P_, lo, hi):<10.2e}"
        print(row)

    # ---- per-channel floors (needs >= 3 channels) ----
    if len(CHANNELS) >= 3:
        print("\nPer-channel floor n_i (cyc/rtHz), median per band:")
        print("  band(Hz)      " + "".join(f"n{c:<9}" for c in CHANNELS))
        for lo, hi in BANDS:
            use_short = lo >= BAND_USE_SHORT[0]
            dvar = {}
            for p in pairs:
                f_, P_ = P_short[p] if use_short else P_long[p]
                dvar[p] = band_median(f_, P_, lo, hi) ** 2
            n = solve_channel_floors(dvar, CHANNELS)
            row = f"  {lo:.0e}-{hi:<7.0e}"
            for c in CHANNELS:
                row += f"{n[c]:<10.2e}"
            print(row)
    else:
        print("\n(Need >= 3 channels to solve individual per-channel floors.)")

    # ---- theta_m-style half-difference of the first two channels ----
    a, b = CHANNELS[0], CHANNELS[1]
    theta = 0.5 * (phases[a] - phases[b])
    f_, P_ = psd(theta, fs, SEG_SHORT_S)
    print(f"\ntheta = 0.5*(ch{a}-ch{b}) floor, 1-15 Hz: "
          f"{band_median(f_, P_, 1, 15):.2e} cyc/rtHz")

    # ---- optional peak check on the first difference ----
    if PEAK_WINDOW:
        f_, P_ = P_long[pairs[0]]
        wb = (f_ > PEAK_WINDOW[0]) & (f_ < PEAK_WINDOW[1])
        sb = (f_ > PEAK_SIDEBANDS[0]) & (f_ < PEAK_SIDEBANDS[1])
        if wb.any() and sb.any():
            ratio = np.max(P_[wb]) / np.median(P_[sb])
            print(f"\nPeak check in {PEAK_WINDOW[0]:.1e}-{PEAK_WINDOW[1]:.1e} Hz "
                  f"(diff {pairs[0]}): peak/floor = {ratio:.1f}  (~1 => no peak)")

    # ---- plot ----
    if MAKE_PLOT:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.figure(figsize=(9, 5.5))
        for p in pairs:
            fl, Pl = P_long[p]
            fh, Ph = P_short[p]
            m = fl > 5e-4
            line, = plt.loglog(fl[m], np.sqrt(Pl[m]), lw=1, label=f"ch{p[0]}-ch{p[1]}")
            plt.loglog(fh[fh > 1], np.sqrt(Ph[fh > 1]), lw=1, color=line.get_color())
        plt.xlabel("Fourier frequency (Hz)")
        plt.ylabel(r"phase ASD (cyc/$\sqrt{\mathrm{Hz}}$)")
        plt.grid(True, which="both", alpha=0.3)
        plt.legend()
        plt.title(f"channel-difference phase noise: {DATA.name}")
        plt.tight_layout()
        plt.savefig(PLOT_PATH, dpi=150)
        print(f"\nsaved plot: {PLOT_PATH}")


if __name__ == "__main__":
    main()
