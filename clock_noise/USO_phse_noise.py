import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

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
ax1.plot(f, L, lw=2)
ax1.scatter(f_data, L_data, color="red", zorder=5)

ax1.set_ylabel("L(f) [dBc/Hz]")
ax1.grid(True, which="both")

##############################################################################
# Noise-regime shading
##############################################################################

# (f_low, f_high, label, fill color) -- fixed categorical order, low to high f
noise_regions = [
    (fmin,       1e-2,       "Flicker\nfrequency (f⁻³)", "#2a78d6"),
    (1e-2,       1e0,        "White\nfrequency (f⁻²)",   "#eb6834"),
    (1e0,        f_data[0],  "Flicker\nphase (f⁻¹)",     "#1baf7a"),
    (f_data[0],  f_data[-1], "Datasheet\ninterpolation", "#eda100"),
    (f_data[-1], fmax,       "White phase\n(floor)",     "#e87ba4"),
]

label_ink = "#52514e"

for f_lo, f_hi, label, color in noise_regions:
    ax1.axvspan(f_lo, f_hi, color=color, alpha=0.12, zorder=0)
    ax1.text(
        np.sqrt(f_lo * f_hi), 0.97, label,
        transform=ax1.get_xaxis_transform(),
        ha="center", va="top", fontsize=8, color=label_ink,
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

ax3.set_ylim(
    rad_asd_to_jitter_fs(np.sqrt(2*10**(yl[0]/10)), f_carrier_datasheet),
    rad_asd_to_jitter_fs(np.sqrt(2*10**(yl[1]/10)), f_carrier_datasheet)
)

ax3.plot(
    lisa_band, [lisa_timing_req_fs] * 2,
    color="black", ls="--", lw=1.5,
    label=f"LISA requirement ({lisa_displacement_req_m*1e12:.0f} pm/√Hz)"
)

##############################################################################
# Measured clock noise (from DL Baseline analysis, cyc/sqrt(Hz) -> fs/sqrt(Hz))
##############################################################################

measured_path = os.path.join(os.path.dirname(__file__), 'measured_clock_asd.csv')

if os.path.exists(measured_path):
    f_meas, asd_meas_cyc = np.loadtxt(measured_path, delimiter=',', skiprows=1, unpack=True)
    asd_meas_jitter_fs = rad_asd_to_jitter_fs(asd_meas_cyc * 2 * np.pi, f_carrier_measurement)
    ax3.plot(f_meas, asd_meas_jitter_fs, color="green", lw=1.5, label="Measured (TDI-derived)")
else:
    print(f"No measured clock ASD found at {measured_path}, skipping overlay")

ax3.legend(loc="lower right")

##############################################################################

ax1.set_xlabel("Fourier frequency [Hz]")
plt.title(
    "Oscillator Phase Noise / Timing Jitter\n"
    f"(datasheet @ {f_carrier_datasheet/1e6:.0f} MHz, measured @ {f_carrier_measurement/1e6:.0f} MHz)"
)

plt.tight_layout()
plt.savefig("oscillator_phase_noise.png", dpi=300)