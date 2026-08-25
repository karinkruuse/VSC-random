"""
pll_floor_analysis.py

Extract the per-instrument PLL noise floor from a Moku:Pro run where ONE physical
input feeds SEVERAL phasemeter instruments (identical FPGA logic).

Because every instrument sees the same ADC stream and the same signal, the
difference between two instruments at the same frequency cancels both the ADC
noise and the signal -- what remains is pure per-instrument PLL/NCO noise.

Expected .npz keys (edit CARRIERS / PAIRS if yours differ):
  time_s
  carrier, carrier_1, carrier_2, carrier_3   (all instruments on the 30 MHz carrier)
  usb,  usb_1                                (two instruments on the USB)
  lsb,  lsb_1                                (two instruments on the LSB)
Phase columns are in cycles.

Outputs:
  - per-instrument PLL floor n_i (least-squares from all carrier pair differences)
  - a table of pairwise-difference ASDs
  - <stem>_pll_floor.png : every pairwise difference (thin) + per-instrument
    floor (thick) + the optical floor for reference
"""

from pathlib import Path
import itertools
import numpy as np
from scipy.signal import welch, detrend

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
DATA = Path("data/mod_1input/synced_phasemeter_data.npz")
CROP_START_S = 100.0                    # seconds to drop from the start of the record

# instrument label -> npz key for the CARRIER phase each instrument measured
CARRIERS = {
    "A": "carrier",
    "B": "carrier_1",
    "C": "carrier_2",
    "D": "carrier_3",
}
# extra same-frequency instrument pairs (label -> (keyA, keyB)) for cross-checks
EXTRA_PAIRS = {
    "USB (A-B)": ("usb", "usb_1"),
    "LSB (C-D)": ("lsb", "lsb_1"),
}

SEG_S = 600.0                         # Welch segment length (s)
BANDS = [(0.1, 1.0), (1.0, 5.0), (5.0, 15.0)]
OPTICAL_FLOOR = 1.3e-6               # cyc/rtHz, drawn as a reference line (or None)
PLOT_PATH = DATA.with_name(DATA.stem + "_pll_floor.png")


# ------------------------------------------------------------------
def psd(x, fs):
    n = int(SEG_S * fs)
    n = max(256, min(n, len(x)))
    f, P = welch(detrend(x), fs=fs, window="hann", nperseg=n, noverlap=n // 2,
                 detrend="linear", scaling="density")
    return f, P


def bmed(f, P, lo, hi):
    b = (f > lo) & (f < hi)
    return np.median(np.sqrt(P[b])) if b.any() else np.nan


def solve_floors(diff_var, labels):
    """least-squares: S(i-j)^2 = n_i^2 + n_j^2  ->  n_i."""
    pairs = list(itertools.combinations(labels, 2))
    A = np.zeros((len(pairs), len(labels)))
    y = np.zeros(len(pairs))
    for r, (a, b) in enumerate(pairs):
        A[r, labels.index(a)] = 1.0
        A[r, labels.index(b)] = 1.0
        y[r] = diff_var[(a, b)]
    x, *_ = np.linalg.lstsq(A, y, rcond=None)
    return {c: np.sqrt(max(v, 0)) for c, v in zip(labels, np.clip(x, 0, None))}


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    d = np.load(DATA, allow_pickle=True)
    t = d["time_s"]
    fs = 1.0 / np.median(np.diff(t))

    keep = t >= (t[0] + CROP_START_S)
    t = t[keep]
    if CROP_START_S > 0:
        print(f"  cropped first {CROP_START_S:g}s -> {keep.sum()}/{len(keep)} samples kept")

    dur = t[-1] - t[0]
    print(f"{DATA.name}: N={len(t)}  dur={dur:.0f}s ({dur/60:.1f} min)  fs={fs:.3f} Hz")
    if dur < 600:
        print("  NOTE: short record -> reliable only above ~%.2g Hz; no mHz band." % (5 / dur))

    labels = list(CARRIERS)
    phase = {lab: d[key].astype(float)[keep] for lab, key in CARRIERS.items()}

    # ---- time-domain overlay: visual check that the carriers are actually
    # on the same synced timebase (fine structure should track together) ----
    plt.figure(figsize=(9, 4))
    for lab in labels:
        plt.plot(t, phase[lab], lw=0.8, label=f"carrier {lab} ({CARRIERS[lab]})")
    plt.xlabel("Common time (s)")
    plt.ylabel("Phase (cyc), detrended")
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=8)
    plt.title(f"Carriers on synced timebase: {DATA.name}")
    plt.tight_layout()
    carriers_plot_path = DATA.with_name(DATA.stem + "_carriers_timebase.png")
    plt.savefig(carriers_plot_path, dpi=150)
    print(f"saved plot: {carriers_plot_path}")

    # pairwise carrier differences (pure PLL)
    pair_psd = {}
    for a, b in itertools.combinations(labels, 2):
        pair_psd[(a, b)] = psd(phase[a] - phase[b], fs)

    print("\nCarrier-carrier difference ASD (cyc/rtHz)  [ADC + signal cancelled]:")
    print("  pair   " + "".join(f"{lo:g}-{hi:g}Hz   ".rjust(13) for lo, hi in BANDS))
    for (a, b), (f, P) in pair_psd.items():
        print(f"  {a}-{b}   " + "".join(f"{bmed(f, P, lo, hi):.2e}     " for lo, hi in BANDS))

    print("\nPer-instrument PLL floor n_i (cyc/rtHz):")
    print("  band(Hz)     " + "".join(f"n_{c}       " for c in labels))
    for lo, hi in BANDS:
        dv = {p: bmed(*pair_psd[p], lo, hi) ** 2 for p in pair_psd}
        n = solve_floors(dv, labels)
        print(f"  {lo:g}-{hi:<7g}" + "".join(f"{n[c]:.2e}  " for c in labels))

    for lab, (ka, kb) in EXTRA_PAIRS.items():
        if ka in d and kb in d:
            f, P = psd(d[ka].astype(float)[keep] - d[kb].astype(float)[keep], fs)
            print(f"\n{lab} difference: " +
                  "  ".join(f"{lo:g}-{hi:g}Hz={bmed(f, P, lo, hi):.2e}" for lo, hi in BANDS))

    # ---- plot ----
    plt.figure(figsize=(9, 5.5))
    # thin grey: every pairwise difference
    for (a, b), (f, P) in pair_psd.items():
        plt.loglog(f[f > 0], np.sqrt(P[f > 0]), color="0.75", lw=0.8)
    # thick: per-instrument floor, reconstructed as a smooth curve across the band
    # (compute n_i(f) bin-by-bin via the same 3-eq solve at each frequency)
    fgrid = pair_psd[(labels[0], labels[1])][0]
    stack = {p: pair_psd[p][1] for p in pair_psd}
    ncurve = {c: np.zeros_like(fgrid) for c in labels}
    for k in range(len(fgrid)):
        dv = {p: stack[p][k] for p in stack}     # variances at this bin
        sol = solve_floors(dv, labels)
        for c in labels:
            ncurve[c][k] = sol[c]
    colors = plt.cm.viridis(np.linspace(0, 0.85, len(labels)))
    for c, col in zip(labels, colors):
        m = (fgrid > 0) & (ncurve[c] > 0)
        plt.loglog(fgrid[m], ncurve[c][m], lw=1.8, color=col, label=f"PLL floor {c}")
    if OPTICAL_FLOOR:
        plt.axhline(OPTICAL_FLOOR, color="tab:red", ls="--", lw=1.2,
                    label=f"optical floor ~{OPTICAL_FLOOR:.0e}")
    plt.xlabel("Fourier frequency (Hz)")
    plt.ylabel(r"phase ASD (cyc/$\sqrt{\mathrm{Hz}}$)")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend(fontsize=8, ncol=2)
    plt.title(f"per-instrument PLL floor (shared ADC): {DATA.name}")
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=150)
    print(f"\nsaved plot: {PLOT_PATH}")


if __name__ == "__main__":
    main()