"""
carrier_sideband_analysis.py

Analyse a Moku:Pro Phasemeter .npy log for a carrier + two sidebands (USB/LSB).

Computes, and compares:
  - single-tone phase ASDs (carrier, USB, LSB)  -- common noise lives here
  - theta_m = 0.5*(USB - LSB)                   -- the modulation-noise estimator
  - carrier-referenced differences (USB - c), (c - LSB)
  - diagnostic ASD ratios:
        theta_m / (c - LSB),  theta_m / (USB - c),  (USB - c)/(c - LSB)
    Interpretation (per-band, in ASD):
        ~0.5  -> additive per-channel floor dominates (ADC/readout)   [ratio test]
        ~1.0  -> antisymmetric signal-like term dominates (modulation, timing jitter)
        (USB-c)/(c-LSB) ~ 1 -> the two carrier-SB spectra match (symmetry OK)
  - per-channel floors n_c, n_U, n_L from the three pairwise differences
  - optional spectral-peak check (e.g. a thermal line) with the omega_m/omega_c
    optical-path prediction for how far it should drop into theta_m

Set which Moku input is carrier / USB / LSB below. Reads fs and set-frequencies
from the sibling .txt header.
"""

from pathlib import Path
import numpy as np
from scipy.signal import welch, detrend

# ------------------------------------------------------------------
# CONFIG  -- set channel roles (Moku input numbers)
# ------------------------------------------------------------------
DATA = Path("data/with modulation/PMtest_20260805_190157.npy")
CARRIER_CH = 1      # e.g. 19 MHz
LSB_CH     = 2      # e.g.  8 MHz  (carrier - f_mod)
USB_CH     = 4      # e.g. 30 MHz  (carrier + f_mod)

CUT_START_S = 0.0
CUT_END_S   = 0.0

SEG_LONG_S  = 2000.0     # low-f resolution
SEG_SHORT_S = 200.0      # clean hi-f floor
BANDS = [(1e-3, 1e-2), (1e-2, 1e-1), (1e-1, 1.0), (1.0, 15.0)]
BAND_USE_SHORT_FROM = 1.0

# optical wavelength only used for the omega_m/omega_c peak prediction
LAMBDA_M = 1064e-9
PEAK_WINDOW = None          # e.g. (1.2e-3, 1.6e-3) to check a thermal line, or None
PEAK_SIDEBANDS = (2.5e-3, 5e-3)

MAKE_PLOT = True
PLOT_PATH = DATA.with_name(DATA.stem + "_carrier_sb.png")
PLOT_PATH_RATIO = DATA.with_name(DATA.stem + "_uc_cl_vs_ul_ratio.png")


# ------------------------------------------------------------------
def read_header(txt):
    fs, freqs = None, {}
    if not txt.exists():
        return fs, freqs
    for line in txt.read_text(errors="ignore").splitlines():
        if "Acquisition rate:" in line:
            fs = float(line.split("Acquisition rate:")[1].split("Hz")[0])
        for ch in (1, 2, 3, 4):
            tag = f"Input {ch} ("
            if tag in line and "set frequency" in line:
                try:
                    s = line.split("set frequency")[1].split("MHz")[0]
                    freqs[ch] = float(s.replace(" ", "")) * 1e6
                except Exception:
                    pass
    return fs, freqs


def psd(x, fs, seg_s):
    n = int(seg_s * fs); n = max(256, min(n, len(x)))
    f, P = welch(x, fs=fs, window="hann", nperseg=n, noverlap=n // 2,
                 detrend="linear", scaling="density")
    return f, P


def bmed(f, P, lo, hi):
    b = (f > lo) & (f < hi)
    return np.median(np.sqrt(P[b])) if b.any() else np.nan


def bmax(f, P, lo, hi):
    b = (f > lo) & (f < hi)
    return np.max(np.sqrt(P[b])) if b.any() else np.nan


# ------------------------------------------------------------------
def main():
    arr = np.load(DATA, allow_pickle=True)
    fs, freqs = read_header(DATA.with_suffix(".txt"))
    t = arr["Time (s)"]
    if fs is None:
        fs = 1.0 / np.median(np.diff(t))
    mask = (t >= t[0] + CUT_START_S) & (t <= t[-1] - CUT_END_S)

    if freqs:
        fc = freqs.get(CARRIER_CH); fu = freqs.get(USB_CH); fl_ = freqs.get(LSB_CH)
        if fc and fu and fl_:
            fmod = ((fu - fc) + (fc - fl_)) / 2
            print(f"carrier={fc/1e6:.3f} MHz  USB={fu/1e6:.3f}  LSB={fl_/1e6:.3f}  "
                  f"=> f_mod~{fmod/1e6:.3f} MHz, spacing symmetric to "
                  f"{abs((fu-fc)-(fc-fl_)):.1f} Hz")
    print(f"fs={fs:.4f} Hz  "
          f"(carrier=ch{CARRIER_CH}, USB=ch{USB_CH}, LSB=ch{LSB_CH})\n")

    
    def ph(ch, ff):
        x = arr[f"Input {ch} Phase (cyc)"][mask].astype(float)/ff*10**7
        x = x - x[0]          # make the initial phase zero
        return detrend(x)

    pc, pu, pl = ph(CARRIER_CH, fc), ph(USB_CH, fu), ph(LSB_CH, fl_)


    theta = 0.5 * (pu - pl)
    uc = pu - pc          # USB - carrier
    cl = pc - pl          # carrier - LSB
    # pairwise diffs for per-channel floors:  ul = USB - LSB = 2*theta
    ul = pu - pl

    # PSDs at both resolutions
    def both(x):
        return psd(x, fs, SEG_LONG_S), psd(x, fs, SEG_SHORT_S)
    (fTl, Tl), (fTs, Ts) = both(theta)
    (fUCl, UCl), (fUCs, UCs) = both(uc)
    (fCLl, CLl), (fCLs, CLs) = both(cl)
    (fULl, ULl), (fULs, ULs) = both(ul)
    (_, PCl), (_, PCs) = both(pc)
    (_, PUl), (_, PUs) = both(pu)
    (_, PLl), (_, PLs) = both(pl)

    def pick(lo, fl_, Pl_, fs_, Ps_):
        return (fs_, Ps_) if lo >= BAND_USE_SHORT_FROM else (fl_, Pl_)

    # sideband-sideband (USB-LSB) ASD -> CSV, splicing long-seg (low f) with short-seg (high f)
    sb_lo = fULl < BAND_USE_SHORT_FROM
    sb_hi = fULs >= BAND_USE_SHORT_FROM
    f_sb = np.concatenate([fULl[sb_lo], fULs[sb_hi]])
    asd_sb = np.concatenate([np.sqrt(ULl[sb_lo]), np.sqrt(ULs[sb_hi])])
    order = np.argsort(f_sb)
    csv_path = DATA.with_name(DATA.stem + "_USB-LSB_asd.csv")
    np.savetxt(csv_path, np.column_stack([f_sb[order], asd_sb[order]]),
               delimiter=",", header="freq_Hz,asd_USB-LSB_cyc_per_rtHz", comments="")
    print(f"saved sideband-sideband ASD: {csv_path}")

    print("ASD per band (cyc/rtHz):  theta_m | USB-c | c-LSB | carrier(single)")
    for lo, hi in BANDS:
        fT, PT = pick(lo, fTl, Tl, fTs, Ts)
        fUC, PUC = pick(lo, fUCl, UCl, fUCs, UCs)
        fCL, PCL = pick(lo, fCLl, CLl, fCLs, CLs)
        fC, PC = pick(lo, fTl, PCl, fTs, PCs)  # carrier single tone
        print(f"  {lo:.0e}-{hi:<7.0e} {bmed(fT,PT,lo,hi):.2e} | "
              f"{bmed(fUC,PUC,lo,hi):.2e} | {bmed(fCL,PCL,lo,hi):.2e} | "
              f"{bmed(fC,PC,lo,hi):.2e}")

    print("\nDiagnostic ASD ratios (0.5 => additive floor, 1.0 => signal-like):")
    print("  band(Hz)      tm/(c-LSB)  tm/(USB-c)  (USB-c)/(c-LSB)")
    for lo, hi in BANDS:
        fT, PT = pick(lo, fTl, Tl, fTs, Ts)
        fUC, PUC = pick(lo, fUCl, UCl, fUCs, UCs)
        fCL, PCL = pick(lo, fCLl, CLl, fCLs, CLs)
        tm = bmed(fT, PT, lo, hi); u = bmed(fUC, PUC, lo, hi); c = bmed(fCL, PCL, lo, hi)
        print(f"  {lo:.0e}-{hi:<7.0e} {tm/c:>9.3f}   {tm/u:>9.3f}   {u/c:>9.3f}")

    # per-channel floors from the three pairwise differences (independent assumption)
    #   (USB-c)^2 = nU^2 + nC^2 ; (c-LSB)^2 = nC^2 + nL^2 ; (USB-LSB)^2 = nU^2 + nL^2
    print("\nPer-channel floor (cyc/rtHz):  n_carrier | n_USB | n_LSB")
    for lo, hi in BANDS:
        fUC, PUC = pick(lo, fUCl, UCl, fUCs, UCs)
        fCL, PCL = pick(lo, fCLl, CLl, fCLs, CLs)
        fUL, PUL = pick(lo, fULl, ULl, fULs, ULs)
        a = bmed(fUC, PUC, lo, hi)**2   # nU^2+nC^2
        b = bmed(fCL, PCL, lo, hi)**2   # nC^2+nL^2
        d = bmed(fUL, PUL, lo, hi)**2   # nU^2+nL^2
        nC = np.sqrt(max((a + b - d)/2, 0))
        nU = np.sqrt(max((a + d - b)/2, 0))
        nL = np.sqrt(max((b + d - a)/2, 0))
        print(f"  {lo:.0e}-{hi:<7.0e} {nC:.2e} | {nU:.2e} | {nL:.2e}")


    if MAKE_PLOT:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.figure(figsize=(9, 5.5))
        def draw(fl_, Pl_, fs_, Ps_, **kw):
            m = fl_ > 5e-4
            plt.loglog(fl_[m], np.sqrt(Pl_[m]), **kw)
            plt.loglog(fs_[fs_ > 1], np.sqrt(Ps_[fs_ > 1]), **{k: v for k, v in kw.items() if k != "label"})
        draw(fTl, PCl, fTs, PCs, color="k", lw=1, label="carrier (single tone)")
        draw(fCLl, CLl, fCLs, CLs, color="tab:green", lw=1, label="carrier-LSB")
        draw(fUCl, UCl, fUCs, UCs, color="tab:purple", lw=1, label="USB-carrier")
        draw(fTl, Tl, fTs, Ts, color="tab:blue", lw=1.6, label=r"$\theta_m=\frac{1}{2}$(USB-LSB)")
        plt.loglog(fCLl[fCLl > 5e-4], np.sqrt(CLl[fCLl > 5e-4]) / 2, "r--", lw=1,
                   label="(carrier-LSB)/2 [additive pred.]")
        plt.xlabel("Fourier frequency (Hz)"); plt.ylabel(r"phase ASD (cyc/$\sqrt{\mathrm{Hz}}$)")
        plt.grid(True, which="both", alpha=0.3); plt.legend(fontsize=8)
        plt.title(f"carrier + sidebands, scaled to 10 MHz: {DATA.name}")
        plt.tight_layout(); plt.savefig(PLOT_PATH, dpi=150)
        print(f"\nsaved plot: {PLOT_PATH}")

        # -------- ratio plot: ASD(USB-c) / ASD(USB-LSB) and ASD(c-LSB) / ASD(USB-LSB) --------
        plt.figure(figsize=(9, 5.5))
        def draw_ratio(fl_, Pnum_l, Pden_l, fs_, Pnum_s, Pden_s, **kw):
            ml = fl_ > 5e-4
            plt.loglog(fl_[ml], np.sqrt(Pnum_l[ml] / Pden_l[ml]), **kw)
            ms = fs_ > 1
            plt.loglog(fs_[ms], np.sqrt(Pnum_s[ms] / Pden_s[ms]),
                       **{k: v for k, v in kw.items() if k != "label"})
        draw_ratio(fUCl, UCl, ULl, fUCs, UCs, ULs, color="tab:purple", lw=1.4,
                   label="ASD(USB-c) / ASD(USB-LSB)")
        draw_ratio(fCLl, CLl, ULl, fCLs, CLs, ULs, color="tab:green", lw=1.4,
                   label="ASD(c-LSB) / ASD(USB-LSB)")
        plt.axhline(1 / np.sqrt(2), color="gray", ls="--", lw=1,
                    label=r"$1/\sqrt{2}$ (equal, uncorrelated halves)")
        plt.xlabel("Fourier frequency (Hz)"); plt.ylabel("ASD ratio")
        plt.grid(True, which="both", alpha=0.3); plt.legend(fontsize=8)
        plt.title(f"USB-c, c-LSB relative to USB-LSB: {DATA.name}")
        plt.tight_layout(); plt.savefig(PLOT_PATH_RATIO, dpi=150)
        print(f"saved plot: {PLOT_PATH_RATIO}")





if __name__ == "__main__":
    main()
