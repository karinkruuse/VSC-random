"""
carrier_sb_multiinstrument.py

Carrier + sideband analysis for a shared-ADC Moku:Pro run where several identical
phasemeter instruments watch ONE physical input:

  instrument A: carrier , usb        instrument B: carrier_1 , usb_1
  instrument C: carrier_2, lsb        instrument D: carrier_3 , lsb_1

Because the ADC and the signal are common to all instruments, differences isolate
per-instrument PLL noise, and having TWO instruments per sideband lets us:

  1. theta_m = 0.5*(USB - LSB)  and carrier-referenced differences + ratios
     (the usual modulation-noise diagnostics)
  2. per-sideband PLL floor from the duplicate instruments:
        (usb - usb_1)/sqrt2 ,  (lsb - lsb_1)/sqrt2
  3. CROSS-CORRELATION of two independent theta_m estimates
        theta^(1) = 0.5*(usb   - lsb  )   [instruments A,C]
        theta^(2) = 0.5*(usb_1 - lsb_1)   [instruments B,D]
     The common part (the source's modulation phase noise) survives; the
     independent PLL noise averages down as M^-1/4 -> reveals signal below the floor.

Phase keys are in cycles. Edit the KEY MAP if yours differ.
"""

from pathlib import Path
import numpy as np
from scipy.signal import welch, csd, detrend

# ------------------------------------------------------------------
# CONFIG  -- keys for each role. Two USB and two LSB instruments.
# ------------------------------------------------------------------
DATA = Path("data/mod_1input/synced_phasemeter_data.npz")
USB_KEYS  = ["usb", "usb_1"]                 # instruments A, B
LSB_KEYS  = ["lsb", "lsb_1"]                 # instruments C, D
# carrier measured by the same instrument as each sideband (for carrier-SB diffs)
CARRIER_FOR = {"usb": "carrier", "usb_1": "carrier_1",
               "lsb": "carrier_2", "lsb_1": "carrier_3"}

SEG_S = 60.0
BANDS = [(0.1, 1.0), (1.0, 5.0), (5.0, 15.0)]
PLOT_PATH = DATA.with_name(DATA.stem + "_carrier_sb_xcorr.png")


# ------------------------------------------------------------------
def get_np(x, fs):
    n = int(SEG_S * fs); return max(256, min(n, len(x)))

def psd(x, fs):
    f, P = welch(detrend(x), fs=fs, window="hann", nperseg=get_np(x, fs),
                 noverlap=get_np(x, fs) // 2, detrend="linear", scaling="density")
    return f, P

def crosspsd(x, y, fs):
    f, Pxy = csd(detrend(x), detrend(y), fs=fs, window="hann", nperseg=get_np(x, fs),
                 noverlap=get_np(x, fs) // 2, detrend="linear", scaling="density")
    return f, Pxy

def bmed(f, P, lo, hi):
    b = (f > lo) & (f < hi)
    return np.median(np.sqrt(np.abs(P[b]))) if b.any() else np.nan


def main():
    d = np.load(DATA, allow_pickle=True)
    t = d["time_s"]; fs = 1.0 / np.median(np.diff(t)); dur = t[-1] - t[0]
    print(f"{DATA.name}: dur={dur/60:.1f} min  fs={fs:.3f} Hz"
          + ("   (short -> above ~%.2g Hz only)" % (5 / dur) if dur < 600 else ""))
    g = lambda k: d[k].astype(float)

    usbA, usbB = g(USB_KEYS[0]), g(USB_KEYS[1])
    lsbA, lsbB = g(LSB_KEYS[0]), g(LSB_KEYS[1])

    # theta_m estimates (two independent instrument sets)
    th1 = 0.5 * (usbA - lsbA)          # A,C
    th2 = 0.5 * (usbB - lsbB)          # B,D
    # carrier-referenced differences (use one instrument set)
    uc = usbA - g(CARRIER_FOR[USB_KEYS[0]])   # USB - carrier
    cl = g(CARRIER_FOR[LSB_KEYS[0]]) - lsbA   # carrier - LSB
    # per-sideband PLL floor from duplicate instruments
    pll_usb = (usbA - usbB) / np.sqrt(2)
    pll_lsb = (lsbA - lsbB) / np.sqrt(2)

    fT, PT1 = psd(th1, fs); _, PT2 = psd(th2, fs)
    fUC, PUC = psd(uc, fs); fCL, PCL = psd(cl, fs)
    fPU, PPU = psd(pll_usb, fs); fPL, PPL = psd(pll_lsb, fs)
    # cross-correlated theta_m (real part of cross-spectrum)
    fX, PX = crosspsd(th1, th2, fs)
    xc = np.sqrt(np.abs(PX.real))

    print("\nASD per band (cyc/rtHz):")
    print("  band       theta_m   USB-c     c-LSB     PLL(usb)  PLL(lsb)  xcorr(th1,th2)")
    for lo, hi in BANDS:
        print(f"  {lo:g}-{hi:<5g} "
              f"{bmed(fT,PT1,lo,hi):.2e}  {bmed(fUC,PUC,lo,hi):.2e}  {bmed(fCL,PCL,lo,hi):.2e}  "
              f"{bmed(fPU,PPU,lo,hi):.2e}  {bmed(fPL,PPL,lo,hi):.2e}  "
              f"{bmed(fX,PX.real,lo,hi):.2e}")

    print("\nDiagnostic ratios (0.5=additive floor, 1=signal-like):")
    for lo, hi in BANDS:
        tm = bmed(fT, PT1, lo, hi); u = bmed(fUC, PUC, lo, hi); c = bmed(fCL, PCL, lo, hi)
        print(f"  {lo:g}-{hi:<5g}  theta/(c-LSB)={tm/c:.3f}  theta/(USB-c)={tm/u:.3f}")

    print("\nCross-corr vs auto theta_m (how far below the floor it reaches):")
    for lo, hi in BANDS:
        auto = bmed(fT, PT1, lo, hi); x = bmed(fX, PX.real, lo, hi)
        print(f"  {lo:g}-{hi:<5g}  auto={auto:.2e}  |xcorr|={x:.2e}  suppression={auto/x:.1f}x")

    # ---- plot ----
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.figure(figsize=(9, 5.5))
    m = fT > 0
    plt.loglog(fT[m], np.sqrt(PT1[m]), color="tab:blue", lw=1.4, label=r"$\theta_m$ (auto, A/C)")
    plt.loglog(fT[m], np.sqrt(PT2[m]), color="tab:cyan", lw=0.8, alpha=0.7, label=r"$\theta_m$ (auto, B/D)")
    plt.loglog(fUC[m], np.sqrt(PUC[m]), color="tab:purple", lw=1, alpha=0.7, label="USB-carrier")
    plt.loglog(fCL[m], np.sqrt(PCL[m]), color="tab:green", lw=1, alpha=0.7, label="carrier-LSB")
    plt.loglog(fPU[m], np.sqrt(PPU[m]), color="0.5", lw=1, label="PLL floor (usb-usb_1)/$\\sqrt{2}$")
    plt.loglog(fPL[m], np.sqrt(PPL[m]), color="0.7", lw=1, label="PLL floor (lsb-lsb_1)/$\\sqrt{2}$")
    plt.loglog(fX[m], xc[m], color="tab:red", lw=1.8, label=r"cross-corr $\theta_m$ (Re)")
    plt.xlabel("Fourier frequency (Hz)"); plt.ylabel(r"phase ASD (cyc/$\sqrt{\mathrm{Hz}}$)")
    plt.grid(True, which="both", alpha=0.3); plt.legend(fontsize=8, ncol=2)
    plt.title(f"carrier/sideband + cross-correlation: {DATA.name}")
    plt.tight_layout(); plt.savefig(PLOT_PATH, dpi=150)
    print(f"\nsaved plot: {PLOT_PATH}")


if __name__ == "__main__":
    main()
