from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch, detrend

print("RUNNING:", __file__)

# -----------------------
# hardcode input
# -----------------------
DATA = Path(r"data\EOM_PLL_20260224_160232.npy")   # <-- change
TXT  = DATA.with_suffix(".txt")

# -----------------------
# styling
# -----------------------
c_purple = (130/255, 23/255, 112/255)
c_green  = (41/255, 95/255, 36/255)

# -----------------------
# load
# -----------------------
arr = np.load(DATA, allow_pickle=True)

# -----------------------
# sampling rate from header (fallback)
# -----------------------
fs = None
if TXT.exists():
    for line in TXT.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "Acquisition rate:" in line:
            fs = float(line.split("Acquisition rate:")[1].split("Hz")[0].strip())
            break
if fs is None:
    dt = np.median(np.diff(arr["Time (s)"]))
    fs = 1.0 / dt

print("fs =", fs)

# -----------------------
# pull columns (structured array!)
# -----------------------
t = arr["Time (s)"]

IC, QC = arr["Input 1 I (V)"], arr["Input 1 Q (V)"]   # Carrier
IL, QL = arr["Input 2 I (V)"], arr["Input 2 Q (V)"]   # LSB
IU, QU = arr["Input 3 I (V)"], arr["Input 3 Q (V)"]   # USB

# -----------------------
# optional cut start/end (same style as proper_3signal.py)
# -----------------------
cut_start_s = 0.0
cut_end_s   = 0.2 * 3600

mask = (t >= (t[0] + cut_start_s)) & (t <= (t[-1] - cut_end_s))
t = t[mask]
IC, QC = IC[mask], QC[mask]
IL, QL = IL[mask], QL[mask]
IU, QU = IU[mask], QU[mask]

# -----------------------
# amplitude = sqrt(I^2 + Q^2)
# -----------------------
AC = np.hypot(IC, QC)
AL = np.hypot(IL, QL)
AU = np.hypot(IU, QU)

print("Mean amplitude (V): Carrier=%.4g  LSB=%.4g  USB=%.4g" % (AC.mean(), AL.mean(), AU.mean()))

stem = DATA.with_suffix("").name

# -----------------------
# record absolute amplitude values
# -----------------------
out_summary = DATA.with_name(stem + "_amp_summary.txt")
summary_lines = [
    f"Source file: {DATA.name}",
    f"fs = {fs} Hz",
    "",
    "Channel   Mean (V)     Std (V)      Std/Mean (RIN, 1/sqrt-independent)",
    f"Carrier   {AC.mean():.6g}   {AC.std():.6g}   {AC.std()/AC.mean():.4%}",
    f"LSB       {AL.mean():.6g}   {AL.std():.6g}   {AL.std()/AL.mean():.4%}",
    f"USB       {AU.mean():.6g}   {AU.std():.6g}   {AU.std()/AU.mean():.4%}",
]
out_summary.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
print("Saved:", out_summary)

# -----------------------
# full time series (mean-subtracted amplitude)
# -----------------------
AC_centered = AC - np.mean(AC)
AL_centered = AL - np.mean(AL)
AU_centered = AU - np.mean(AU)

target_fs_plot = 2.0
stride = max(1, int(round(fs / target_fs_plot)))

t_plot = (t - t[0])[::stride]
AC_plot = AC_centered[::stride]
AL_plot = AL_centered[::stride]
AU_plot = AU_centered[::stride]

out_ts = DATA.with_name(stem + "_amp_full_timeseries.png")

plt.figure(figsize=(10, 4))
plt.plot(t_plot/3600.0, AC_plot, label="Carrier (mean subtracted)", linewidth=1, color="k")
plt.plot(t_plot/3600.0, AL_plot, label="LSB (mean subtracted)", linewidth=0.6, color=c_green)
plt.plot(t_plot/3600.0, AU_plot, label="USB (mean subtracted)", linewidth=0.6, color=c_purple, alpha=0.7)
plt.xlabel("Time (hours)")
plt.ylabel("Amplitude deviation (V)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_ts, dpi=200)
plt.close()

print("Saved:", out_ts)

# -----------------------
# PSD helper (same style as proper_3signal.py)
# -----------------------
def psd(x, fs, seg_s=16*2048):
    nperseg = int(seg_s * fs)
    nperseg = max(256, min(nperseg, len(x)))
    f, Pxx = welch(
        x, fs=fs, window="hann",
        nperseg=nperseg, noverlap=nperseg//2,
        detrend=False, scaling="density"
    )
    return f, Pxx

# -----------------------
# detrend amplitudes (removes slow drifts)
# -----------------------
AC_dt = detrend(AC, type="linear")
AL_dt = detrend(AL, type="linear")
AU_dt = detrend(AU, type="linear")

# also relative (fractional) amplitude noise, useful for RIN-style comparisons
AC_rel = AC_dt / np.mean(AC)
AL_rel = AL_dt / np.mean(AL)
AU_rel = AU_dt / np.mean(AU)

# -----------------------
# PSDs
# -----------------------
fC, PC = psd(AC_dt, fs)
fL, PL = psd(AL_dt, fs)
fU, PU = psd(AU_dt, fs)

fCr, PCr = psd(AC_rel, fs)
fLr, PLr = psd(AL_rel, fs)
fUr, PUr = psd(AU_rel, fs)

# -----------------------
# outputs
# -----------------------
out_psd_amp = DATA.with_name(stem + "_psd_amp.png")
out_asd_amp = DATA.with_name(stem + "_asd_amp.png")
out_asd_amp_rel = DATA.with_name(stem + "_asd_amp_rel.png")

# Amplitude PSD (V^2/Hz)
plt.figure()
plt.loglog(fC, PC, label="Carrier amplitude", color="k")
plt.loglog(fL, PL, label="LSB amplitude", color=c_green, alpha=0.7, linewidth=0.6)
plt.loglog(fU, PU, label="USB amplitude", color=c_purple, alpha=0.7, linewidth=0.6)
plt.xlabel("Fourier frequency (Hz)")
plt.ylabel("PSD (V$^2$/Hz)")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_psd_amp, dpi=200)
plt.close()

# Amplitude ASD (V/sqrt(Hz))
plt.figure()
plt.loglog(fC, np.sqrt(PC), label="Carrier amplitude", color="k")
plt.loglog(fL, np.sqrt(PL), label="LSB amplitude", color=c_green, alpha=0.7, linewidth=0.6)
plt.loglog(fU, np.sqrt(PU), label="USB amplitude", color=c_purple, alpha=0.7, linewidth=0.6)
plt.xlabel("Fourier frequency (Hz)")
plt.ylabel("ASD (V/√Hz)")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_asd_amp, dpi=200)
plt.close()

# Relative (fractional) amplitude ASD (1/sqrt(Hz)) -- RIN-style
plt.figure()
plt.loglog(fCr, np.sqrt(PCr), label="Carrier amplitude (rel.)", color="k")
plt.loglog(fLr, np.sqrt(PLr), label="LSB amplitude (rel.)", color=c_green, alpha=0.7, linewidth=0.6)
plt.loglog(fUr, np.sqrt(PUr), label="USB amplitude (rel.)", color=c_purple, alpha=0.7, linewidth=0.6)
plt.xlabel("Fourier frequency (Hz)")
plt.ylabel("Relative ASD (1/√Hz)")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_asd_amp_rel, dpi=200)
plt.close()

print("Saved:", out_psd_amp)
print("Saved:", out_asd_amp)
print("Saved:", out_asd_amp_rel)
