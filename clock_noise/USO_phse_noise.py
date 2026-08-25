import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

##############################################################################
# STYLE (validated categorical palette -- see dataviz skill palette.md)
##############################################################################

surface       = "#fcfcfb"
ink_primary   = "#0b0b0b"
ink_secondary = "#52514e"
ink_muted     = "#898781"
gridline      = "#e1e0d9"
baseline      = "#c3c2b7"

color_extrapolated = "#d71b2f"   # (215, 27, 47)  red
color_measured      = "#295f24"  # (41, 95, 36)   green
color_anchor        = color_extrapolated         # datasheet points match the line
color_requirement   = ink_primary                # black
color_modulator     = "#821770"  # (130, 23, 112) magenta
color_delayline     = "#2d13b4"  # (45, 19, 180)  blue
color_pd_noise      = ink_secondary  # neutral, dotted -- another noise floor
color_sideband      = "#eb6834"  # (235, 104, 52)  orange

# noise-region washes: a plain gray ramp, kept separate from the four data colors
region_colors = ["#f5f5f3", "#eaeae7", "#dfdfdc", "#d4d4d0", "#c9c9c5"]

plt.rcParams.update({
    "figure.facecolor": "none",
    "axes.facecolor":   "none",
    "savefig.facecolor": "none",
    "text.color":        ink_primary,
    "axes.labelcolor":   ink_secondary,
    "axes.edgecolor":    baseline,
    "xtick.color":       ink_secondary,
    "ytick.color":       ink_secondary,
    "font.family":       "sans-serif",
})

##############################################################################
# USER INPUT
##############################################################################

# Datasheet values
f_data = np.array([10, 100, 1e3, 1e4])
L_data = np.array([-130, -140, -150, -155])

# Carrier frequencies used to convert phase ASD into timing jitter ASD
# (x = phi / (2*pi*f_carrier)) -- these differ: the datasheet spec is for the
# oscillator's own 10 MHz output, but the TDI-derived measurement was taken
# on an 11 MHz carrier, so each curve needs its own conversion
f_carrier_datasheet   = 10e6
f_carrier_measurement = 11e6

# LISA path-length noise requirement, converted to an equivalent timing jitter:
# displacement -> fraction of an optical cycle (at the laser wavelength) ->
# re-expressed as a time using the clock's own period
lisa_displacement_req_m = 1e-12    # 1 pm/sqrt(Hz)
lisa_wavelength_m       = 1064e-9  # LISA laser wavelength
lisa_band               = (1e-4, 1e0)   # Hz, LISA measurement band

# Piecewise extrapolation below first datasheet point
segments = [
    (1e-4, 1e-2, 3),    # 0.1 mHz ...10 mHz : 1/f³
    (1e-2, 1e0, 2),     # 10 mHz ...1 Hz    : 1/f²
    (1e0, 1e1, 1),      # 1 Hz ...10 Hz     : 1/f
]

##############################################################################

fmin = 1e-4
fmax = 1e5

f = np.logspace(np.log10(fmin), np.log10(fmax), 4000)

##############################################################################
# Interpolation above 10 Hz
##############################################################################

interp = interp1d(
    np.log10(f_data),
    L_data,
    kind="linear",
    fill_value="extrapolate"
)

L = interp(np.log10(f))

##############################################################################
# Constant above highest specified point
##############################################################################

L[f > f_data[-1]] = L_data[-1]

##############################################################################
# Piecewise extrapolation (continuous)
##############################################################################

# Overwrite everything below the first datasheet point
mask = f < f_data[0]
L[mask] = np.nan

# Start from the first datasheet point
current_f = f_data[0]
current_L = L_data[0]

# Walk from highest frequencies to lowest
for f_low, f_high, n in reversed(segments):

    # frequencies inside this segment
    mask = (f >= f_low) & (f < f_high)

    # continuous with previous segment
    L[mask] = current_L + 10 * n * np.log10(current_f / f[mask])

    # value at the lower edge becomes the anchor for the next segment
    current_L = current_L + 10 * n * np.log10(current_f / f_low)
    current_f = f_low

##############################################################################
# Convert
##############################################################################

Sphi = 2 * 10**(L/10)
ASD = np.sqrt(Sphi)

##############################################################################
# Plot
##############################################################################

fig, ax1 = plt.subplots(figsize=(11,6))

ax1.set_xscale("log")
ax1.plot(f, L, color=color_extrapolated, lw=2.2, label="Extrapolated (datasheet)")
ax1.scatter(
    f_data, L_data, color=color_anchor,
    s=45, zorder=5, label="Datasheet points"
)

ax1.set_ylabel("L(f) [dBc/Hz]")
ax1.grid(True, which="both", color=gridline, lw=0.8)
ax1.set_axisbelow(True)
for spine in ("top", "right"):
    ax1.spines[spine].set_visible(False)

##############################################################################
# Noise-regime shading
##############################################################################

# (f_low, f_high, label) -- gray bands, kept separate from the four data colors
# (the "white phase floor" region, f_data[-1] to fmax, is dropped: it falls
# entirely outside the 1e-4-1e4 Hz view since the datasheet's last point sits
# right at the new upper edge)
noise_regions = [
    (fmin,       1e-2,       "Flicker\nfrequency (f⁻³)"),
    (1e-2,       1e0,        "White\nfrequency (f⁻²)"),
    (1e0,        f_data[0],  "Flicker\nphase (f⁻¹)"),
    (f_data[0],  f_data[-1], "Datasheet\ninterpolation"),
]

for (f_lo, f_hi, label), color in zip(noise_regions, region_colors):
    ax1.axvspan(f_lo, f_hi, color=color, zorder=0)
    ax1.text(
        np.sqrt(f_lo * f_hi), 0.97, label,
        transform=ax1.get_xaxis_transform(),
        ha="center", va="top", fontsize=8, color=ink_secondary,
    )

##############################################################################

# rad/sqrt(Hz) -> s/sqrt(Hz) -> fs/sqrt(Hz)
def rad_asd_to_jitter_fs(rad_asd, f_carrier):
    return rad_asd / (2 * np.pi * f_carrier) * 1e15

lisa_timing_req_s  = (lisa_displacement_req_m / lisa_wavelength_m) / f_carrier_datasheet
lisa_timing_req_fs = lisa_timing_req_s * 1e15

# map limits from left axis -- left as matplotlib's autoscale, not forced to
# include the LISA line (which may fall outside the data's natural range)
yl = ax1.get_ylim()

##############################################################################

ax3 = ax1.twinx()
ax3.set_yscale("log")
ax3.set_ylabel(r"Timing jitter ASD [fs/$\sqrt{\rm Hz}$]")
for spine in ("top", "left"):
    ax3.spines[spine].set_visible(False)
ax3.spines["right"].set_color(baseline)

ax3.set_ylim(
    rad_asd_to_jitter_fs(np.sqrt(2*10**(yl[0]/10)), f_carrier_datasheet),
    rad_asd_to_jitter_fs(np.sqrt(2*10**(yl[1]/10)), f_carrier_datasheet)
)

ax3.plot(
    lisa_band, [lisa_timing_req_fs] * 2,
    color=color_requirement, ls="--", lw=1.5,
    label=f"LISA requirement ({lisa_displacement_req_m*1e12:.0f} pm/√Hz)"
)

##############################################################################
# Measured clock noise (from DL Baseline analysis, cyc/sqrt(Hz) -> fs/sqrt(Hz))
##############################################################################

measured_path = os.path.join(os.path.dirname(__file__), 'measured_clock_asd.csv')

if os.path.exists(measured_path):
    f_meas, asd_meas_cyc = np.loadtxt(measured_path, delimiter=',', skiprows=1, unpack=True)
    asd_meas_jitter_fs = rad_asd_to_jitter_fs(asd_meas_cyc * 2 * np.pi, f_carrier_measurement)
    ax3.plot(f_meas, asd_meas_jitter_fs, color=color_measured, lw=1.3, alpha=0.85, label="Measured (TDI-derived)")
else:
    print(f"No measured clock ASD found at {measured_path}, skipping overlay")

##############################################################################
# Modulator noise & delay-line intrinsic noise (measured noises/, cyc/sqrt(Hz)
# ASD or cyc^2/Hz PSD, both phase quantities -> fs/sqrt(Hz) via the 10 MHz carrier)
##############################################################################

measured_noises_dir = os.path.join(os.path.dirname(__file__), '..', 'measured noises')

delayline_path = os.path.join(measured_noises_dir, 'baseline.csv')
if os.path.exists(delayline_path):
    f_dl, asd_dl_cyc = np.loadtxt(delayline_path, delimiter=',', skiprows=1, unpack=True)
    keep = f_dl > 0   # drop the DC bin, log axis can't show f=0
    dl_jitter_fs = rad_asd_to_jitter_fs(asd_dl_cyc[keep] * 2 * np.pi, f_carrier_datasheet)
    ax3.plot(f_dl[keep], dl_jitter_fs, color=color_delayline, lw=1, alpha=0.85, label="Delay line intrinsic noise")
else:
    print(f"No delay line noise found at {delayline_path}, skipping overlay")

# note: this file's header says "PSD(Hz^2/Hz)" but the generating script
# (modulation_noise/proper_3signal.py) computes it from a phase quantity in
# cycles (theta_m = 0.5*(USB-LSB) phase) -- the header units are mislabeled,
# the values are actually a phase PSD in cyc^2/Hz
modulator_path = os.path.join(measured_noises_dir, 'modulator_psd.csv')
if os.path.exists(modulator_path):
    f_mod, psd_mod_cyc2 = np.loadtxt(modulator_path, delimiter=',', skiprows=1, unpack=True)
    keep = f_mod > 0
    asd_mod_cyc = np.sqrt(psd_mod_cyc2[keep])
    mod_jitter_fs = rad_asd_to_jitter_fs(asd_mod_cyc * 2 * np.pi, f_carrier_datasheet)
    ax3.plot(f_mod[keep], mod_jitter_fs, color=color_modulator, lw=1, alpha=0.85, label="Modulator noise")
else:
    print(f"No modulator noise found at {modulator_path}, skipping overlay")

"""
sideband_path = os.path.join(measured_noises_dir, 'PMtest_20260805_190157_USB-LSB_asd.csv')
if os.path.exists(sideband_path):
    f_sb, asd_sb_cyc = np.loadtxt(sideband_path, delimiter=',', skiprows=1, unpack=True)
    keep = f_sb > 0
    sb_jitter_fs = rad_asd_to_jitter_fs(asd_sb_cyc[keep] * 2 * np.pi, f_carrier_datasheet)
    ax3.plot(f_sb[keep], sb_jitter_fs, color=color_sideband, lw=1, alpha=0.85, label="Moku Lab timing jitters")
else:
    print(f"No USB-LSB sideband ASD found at {sideband_path}, skipping overlay")
"""
##############################################################################
# Newport PD noise floor (total shot+Johnson+RIN, flat/white -> fs/sqrt(Hz))
##############################################################################

pd_noise_path = os.path.join(os.path.dirname(__file__), 'newport_pd_noise_floor.csv')
if os.path.exists(pd_noise_path):
    pd_noise_rad = np.loadtxt(pd_noise_path, delimiter=',', skiprows=1)
    pd_noise_fs = rad_asd_to_jitter_fs(float(pd_noise_rad), f_carrier_datasheet)
    ax3.plot(
        (fmin, 1e4), [pd_noise_fs] * 2,
        color=color_pd_noise, ls=":", lw=1.5,
        label="Newport PD noise floor (1 mW/beam)"
    )
else:
    print(f"No PD noise floor found at {pd_noise_path}, skipping overlay")

handles1, labels1 = ax1.get_legend_handles_labels()
handles3, labels3 = ax3.get_legend_handles_labels()
legend = ax3.legend(
    handles1 + handles3, labels1 + labels3,
    loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=4,
    frameon=True, facecolor=surface,
    edgecolor=baseline, labelcolor=ink_primary
)
legend.get_frame().set_linewidth(0.8)

##############################################################################

ax1.set_xlim(1e-4, 1e4)

ax1.set_xlabel("Fourier frequency [Hz]")
plt.title(
    "Oscillator Phase Noise / Timing Jitter\n"
    f"(datasheet @ {f_carrier_datasheet/1e6:.0f} MHz, measured @ {f_carrier_measurement/1e6:.0f} MHz)",
    color=ink_primary
)

plt.tight_layout()
plt.savefig("oscillator_phase_noise.png", dpi=300, transparent=True, bbox_inches="tight")