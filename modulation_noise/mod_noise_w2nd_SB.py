from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch, detrend

# ---- hardcode input ----
DATA = Path(r"data\EOM_sideband_test_20260220_160507.npy")   # change if needed
TXT  = DATA.with_suffix(".txt")

# ---- load ----
arr = np.load(DATA, allow_pickle=True)

# ---- sampling rate from header (fallback) ----
fs = None
if TXT.exists():
    for line in TXT.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "Acquisition rate:" in line:
            fs = float(line.split("Acquisition rate:")[1].split("Hz")[0].strip())
            break
if fs is None:
    dt = np.median(np.diff(arr["Time (s)"]))
    fs = 1.0 / dt

# ---- pull columns (structured array!) ----
t = arr["Time (s)"]
phiA_cyc = arr["Input A Phase (cyc)"]
phiB_cyc = arr["Input B Phase (cyc)"]
fA_Hz = arr["Input A Frequency (Hz)"]
fB_Hz = arr["Input B Frequency (Hz)"]

# ---- cut start/end ----
mask = (
    (t >= (t[0] + 2.1*3600)) &
    (t <= (t[-1] - 3.1*3600))
)
t = t[mask]
phiA_cyc = phiA_cyc[mask]
phiB_cyc = phiB_cyc[mask]
fA_Hz = fA_Hz[mask]
fB_Hz = fB_Hz[mask]

# ---- full time series (mean-subtracted frequency) ----
fA_centered = fA_Hz - np.mean(fA_Hz)
fB_centered = fB_Hz - np.mean(fB_Hz)

target_fs_plot = 2.0
stride = max(1, int(round(fs / target_fs_plot)))

t_plot = (t - t[0])[::stride]
fA_plot = fA_centered[::stride]
fB_plot = fB_centered[::stride]

out_ts = DATA.with_name(DATA.with_suffix("").name + "_freq_full_timeseries.png")

plt.figure(figsize=(10, 4))
plt.plot(t_plot/3600.0, fA_plot, label="Input A (mean subtracted)", linewidth=1.0)
plt.plot(t_plot/3600.0, fB_plot, label="Input B (mean subtracted)", linewidth=1.0)
plt.xlabel("Time (hours)")
plt.ylabel("Frequency deviation (Hz)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_ts, dpi=200)
plt.close()

print("Saved:", out_ts)

# ---- PSD helper ----
def psd(x, fs, seg_s=16*2048):
    nperseg = int(seg_s * fs)
    nperseg = max(256, min(nperseg, len(x)))
    f, Pxx = welch(
        x, fs=fs, window="hann",
        nperseg=nperseg, noverlap=nperseg//2,
        detrend=False, scaling="density"
    )
    return f, Pxx

# ---- detrend phases (removes constant freq offsets/drift) ----
phiA_dt = detrend(phiA_cyc, type="linear")
phiB_dt = detrend(phiB_cyc, type="linear")

# modulation phase estimate (cycles)
theta_m = 0.5 * (phiA_dt - phiB_dt)

# ---- frequency noise (Hz) ASD/PSD from the frequency columns ----
# (detrend removes slow drift so the very-low-f end isn't dominated by ramp)
fA_dt_Hz = detrend(fA_Hz, type="linear")
fB_dt_Hz = detrend(fB_Hz, type="linear")

ffA, PffA = psd(fA_dt_Hz, fs)  # Hz^2/Hz
ffB, PffB = psd(fB_dt_Hz, fs)


# ---- frequency difference (Hz) ----
df_Hz = fA_dt_Hz - fB_dt_Hz

ffd, Pffd = psd(df_Hz, fs)

# ---- phase PSDs ----
fA, PA = psd(phiA_dt, fs)
fB, PB = psd(phiB_dt, fs)
fM, PM = psd(theta_m, fs)

# ---- plots ----
stem = DATA.with_suffix("").name

out_psd = DATA.with_name(stem + "_psd_phase.png")
out_asd = DATA.with_name(stem + "_asd_phase.png")
out_psd_f = DATA.with_name(stem + "_psd_freq.png")
out_asd_f = DATA.with_name(stem + "_asd_freq.png")


c_purple = (130/255, 23/255, 112/255)
c_green = (41/255, 95/255, 36/255)

# Phase PSD
plt.figure()
plt.loglog(fA, PA, label="Carrier phase")
plt.loglog(fB, PB, label="2nd SB phase")
plt.loglog(fM, PM, label="theta_m = 0.5*(A-B)")
plt.xlabel("Fourier frequency (Hz)")
plt.ylabel("PSD (cyc^2/Hz)")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_psd, dpi=200)
plt.close()

# Phase ASD
plt.figure()
plt.loglog(fA, np.sqrt(PA)*2*np.pi, label="carrier phase")
plt.loglog(fB, np.sqrt(PB)*2*np.pi, label="2nd SB phase")
plt.loglog(fM, np.sqrt(PM)*2*np.pi, label="theta_m = 0.5*(A-B)")
plt.xlabel("Fourier frequency (Hz)")
plt.ylabel("ASD (rad/√Hz)")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_asd, dpi=200)
plt.close()

# Frequency PSD (this is the comparable-to-your-colleague plot quantity)
plt.figure()
plt.loglog(ffA, PffA, label="Carrier frequency")
plt.loglog(ffB, PffB, label="2nd SB frequency")
plt.xlabel("Fourier frequency (Hz)")
plt.ylabel("PSD (Hz^2/Hz)")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_psd_f, dpi=200)
plt.close()

plt.figure()
plt.loglog(ffA, np.sqrt(PffA), label="Carrier frequency")
plt.loglog(ffB, np.sqrt(PffB), label="2nd SB frequency")
plt.loglog(ffd, np.sqrt(Pffd), label="A - B (frequency diff)")
plt.xlabel("Fourier frequency (Hz)")
plt.ylabel("ASD (Hz/√Hz)")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_asd_f, dpi=200)
plt.close()


print("fs =", fs)
print("Saved:", out_psd)
print("Saved:", out_asd)
print("Saved:", out_psd_f)
print("Saved:", out_asd_f)