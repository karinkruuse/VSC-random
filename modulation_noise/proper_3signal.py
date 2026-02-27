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
# NOTE: these must match your file's field names exactly.
# If yours are different, print(arr.dtype.names) and rename below.
# -----------------------
t = arr["Time (s)"]

# Carrier / LSB / USB phase (cycles)
phiC_cyc = arr["Input 1 Phase (cyc)"]        # <-- rename if needed
phiL_cyc = arr["Input 2 Phase (cyc)"]            # <-- rename if needed
phiU_cyc = arr["Input 3 Phase (cyc)"]            # <-- rename if needed

# Carrier / LSB / USB frequency (Hz) (optional but useful)
fC_Hz = arr["Input 1 Frequency (Hz)"]        # <-- rename if needed
fL_Hz = arr["Input 2 Frequency (Hz)"]            # <-- rename if needed
fU_Hz = arr["Input 3 Frequency (Hz)"]            # <-- rename if needed

# -----------------------
# optional cut start/end (copy your style; set to 0 if not needed)
# -----------------------
cut_start_s = 0.0
cut_end_s   = 0.2 * 3600

mask = (t >= (t[0] + cut_start_s)) & (t <= (t[-1] - cut_end_s))
t = t[mask]
phiC_cyc = phiC_cyc[mask]; phiL_cyc = phiL_cyc[mask]; phiU_cyc = phiU_cyc[mask]
fC_Hz = fC_Hz[mask]; fL_Hz = fL_Hz[mask]; fU_Hz = fU_Hz[mask]

# -----------------------
# full time series (mean-subtracted frequency) like your other script
# -----------------------
fC_centered = fC_Hz - np.mean(fC_Hz)
fL_centered = fL_Hz - np.mean(fL_Hz)
fU_centered = fU_Hz - np.mean(fU_Hz)

target_fs_plot = 2.0
stride = max(1, int(round(fs / target_fs_plot)))

t_plot = (t - t[0])[::stride]
fC_plot = fC_centered[::stride]
fL_plot = fL_centered[::stride]
fU_plot = fU_centered[::stride]

stem = DATA.with_suffix("").name
out_ts = DATA.with_name(stem + "_freq_full_timeseries.png")

plt.figure(figsize=(10, 4))
plt.plot(t_plot/3600.0, fC_plot, label="Carrier (mean subtracted)", linewidth=1, color="k")
plt.plot(t_plot/3600.0, fL_plot, label="LSB (mean subtracted)", linewidth=0.6, color=c_green)
plt.plot(t_plot/3600.0, fU_plot, label="USB (mean subtracted)", linewidth=0.6, color=c_purple, alpha=0.7)
plt.xlabel("Time (hours)")
plt.ylabel("Frequency deviation (Hz)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_ts, dpi=200)
plt.close()

print("Saved:", out_ts)

# -----------------------
# PSD helper (same style as yours)
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
# detrend phases (removes constant freq offsets/drift)
# -----------------------
phiC_dt = detrend(phiC_cyc, type="linear")
phiL_dt = detrend(phiL_cyc, type="linear")
phiU_dt = detrend(phiU_cyc, type="linear")

# -----------------------
# Best modulation-phase-noise estimator:
# φ_RF (cycles) = 0.5*(USB - LSB)
# cancels common optical phase noise
# -----------------------
theta_m_cyc = 0.5 * (phiU_dt - phiL_dt)

# diagnostics
u_minus_c_cyc = (phiU_dt - phiC_dt)
c_minus_l_cyc = (phiC_dt - phiL_dt)

# -----------------------
# frequency noise from frequency columns (detrend removes ramp)
# -----------------------
fC_dt_Hz = detrend(fC_Hz, type="linear")
fL_dt_Hz = detrend(fL_Hz, type="linear")
fU_dt_Hz = detrend(fU_Hz, type="linear")

# -----------------------
# PSDs
# -----------------------
fC, PC = psd(phiC_dt, fs)
fL, PL = psd(phiL_dt, fs)
fU, PU = psd(phiU_dt, fs)
fM, PM = psd(theta_m_cyc, fs)

fUC, PUC = psd(u_minus_c_cyc, fs)
fCL, PCL = psd(c_minus_l_cyc, fs)

ffC, PffC = psd(fC_dt_Hz, fs)
ffL, PffL = psd(fL_dt_Hz, fs)
ffU, PffU = psd(fU_dt_Hz, fs)

# useful: SB splitting (should be ~2*f_mod if referenced that way)
df_UL = fU_dt_Hz - fL_dt_Hz
ffd, Pffd = psd(df_UL, fs)

# -----------------------
# outputs
# -----------------------
out_psd_phase = DATA.with_name(stem + "_psd_phase.png")
out_asd_phase = DATA.with_name(stem + "_asd_phase.pdf")
out_psd_freq  = DATA.with_name(stem + "_psd_freq.png")
out_asd_freq  = DATA.with_name(stem + "_asd_freq.png")

# Phase PSD (cycles^2/Hz)
plt.figure()
plt.loglog(fC, PC, label="Carrier phase", color="k")
plt.loglog(fL, PL, label="LSB phase", color=c_green, alpha=0.7, linewidth=0.6)
plt.loglog(fU, PU, label="USB phase", color=c_purple, alpha=0.7, linewidth=0.5)
plt.loglog(fM, PM, label="theta_m = 0.5*(USB-LSB)", color="tab:blue")
plt.xlabel("Fourier frequency (Hz)")
plt.ylabel("PSD (cyc^2/Hz)")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_psd_phase, dpi=200)
plt.close()

# Phase ASD (rad/sqrt(Hz))  [cycles -> rad via *2π]
plt.figure()
S_req = 60e-6 * (1.0 + 0.07 / fC)  # rad/√Hz

plt.loglog(fC, S_req,
           linestyle="--",
           color="k",
           linewidth=1.2,
           label=r"Requirement: $60\left(1+\frac{70\,\mathrm{mHz}}{f}\right)\,\mu$rad/$\sqrt{\mathrm{Hz}}$")
plt.loglog(fC, np.sqrt(PC)*2*np.pi, label="Carrier phase", color="k")
plt.loglog(fL, np.sqrt(PL)*2*np.pi, label="LSB phase", color=c_green, alpha=0.7, linewidth=0.6)
plt.loglog(fU, np.sqrt(PU)*2*np.pi, label="USB phase", color=c_purple, alpha=0.7, linewidth=0.6)
plt.loglog(fM, np.sqrt(PM)*2*np.pi, label=r'$\delta\phi_m = \frac{1}{2}(\mathrm{USB} - \mathrm{LSB})$', color="tab:blue")
plt.loglog(fUC, np.sqrt(PUC)*2*np.pi, label="USB-Carrier", color=c_purple, alpha=0.35)
plt.loglog(fCL, np.sqrt(PCL)*2*np.pi, label="Carrier-LSB", color=c_green, alpha=0.35)
plt.xlabel("Fourier frequency (Hz)")
plt.ylabel("ASD (rad/√Hz)")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_asd_phase, dpi=400)
plt.close()

# Frequency PSD (Hz^2/Hz)
plt.figure()
plt.loglog(ffC, PffC, label="Carrier frequency", color="k")
plt.loglog(ffL, PffL, label="LSB frequency", color=c_green, alpha=0.7, linewidth=0.6)
plt.loglog(ffU, PffU, label="USB frequency", color=c_purple, alpha=0.7, linewidth=0.6)
plt.xlabel("Fourier frequency (Hz)")
plt.ylabel("PSD (Hz^2/Hz)")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_psd_freq, dpi=200)
plt.close()

# Frequency ASD (Hz/√Hz)
plt.figure()
plt.loglog(ffC, np.sqrt(PffC), label="Carrier frequency", color="k")
plt.loglog(ffL, np.sqrt(PffL), label="LSB frequency", color=c_green, alpha=0.7, linewidth=0.6)
plt.loglog(ffU, np.sqrt(PffU), label="USB frequency", color=c_purple, alpha=0.7, linewidth=0.6)
plt.loglog(ffd, np.sqrt(Pffd), label="USB-LSB (diag)", color="tab:blue", alpha=0.8)
plt.xlabel("Fourier frequency (Hz)")
plt.ylabel("ASD (Hz/√Hz)")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_asd_freq, dpi=200)
plt.close()

print("Saved:", out_psd_phase)
print("Saved:", out_asd_phase)
print("Saved:", out_psd_freq)
print("Saved:", out_asd_freq)