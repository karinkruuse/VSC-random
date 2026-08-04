# misalignment_transmission_scan.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import c
from pykat import finesse
from simple_finesse_wrapper import FinesseGenerator

# -----------------------------
# Parameters
# -----------------------------
L = 0.30                 # cavity length [m]
RoC = 0.5                # radius of curvature of M2 [m]
wl = 1064e-9             # laser wavelength [m]

# Mirror amplitude reflectivity / transmissivity (typical high-finesse values)
R_amp = 0.99972
T_amp = 0.00028

# Frequency scan
freq_span = 200e6        # +/- scan [Hz]
n_points = 2000

# Tilt values to test (radians)
tilt_list = 5*np.array([0, 40e-6, 80e-6, 120e-6, 160e-6, 200e-6])

# -----------------------------
# Derived cavity params
# -----------------------------
FSR = c / (2.0 * L)
F = np.pi * np.sqrt(R_amp) / (1.0 - R_amp)   # rough finesse
linewidth = FSR / F

print(f"Cavity length: {L:.3f} m")
print(f"FSR ≈ {FSR/1e6:.2f} MHz, linewidth ≈ {linewidth/1e3:.2f} kHz, finesse ≈ {F:.0f}")

# -----------------------------
# Run scans
# -----------------------------
plt.figure(figsize=(9,5))
cmap = plt.get_cmap("plasma")
colors = cmap(np.linspace(0,1,len(tilt_list)))

for tilt, col in zip(tilt_list, colors):
    fg = FinesseGenerator()

    # Laser
    fg.laser("L1", 0.25, "n0", 0)
    fg.space("s1", 1, "n0", "n3")

    # Cavity
    fg.mirror("M1", R_amp, T_amp, 0, "n3", "n4")
    fg.space("s_cav", L, "n4", "n5")
    fg.mirror("M2", R_amp, T_amp, 0, "n5", "n6")
    fg.attr("M2", "Rc", RoC)
    fg.attr("M2", "xbeta", f"{tilt}")   # misalignment tilt

    fg.cav("cavity1", "M1", "n4", "M2", "n5")
    fg.maxtem(5)

    # Transmitted DC detector
    fg.add("pd trans n6")

    # Frequency scan
    fg.xaxis("L1", "f", "lin", f"{-freq_span}", f"{freq_span}", f"{n_points}")
    fg.yaxis("abs")

    # Run
    kat = finesse.kat()
    kat.parse(fg.get_lines())
    out = kat.run()

    freqs = out.x
    trans = out["trans"]

    plt.plot(freqs/1e6, trans, label=f"{tilt*1e6:.0f} µrad", color=col)

# -----------------------------
# Plot
# -----------------------------
plt.xlabel("Laser detuning [MHz]")
plt.ylabel("Transmitted power (a.u.)")
plt.title("Cavity transmission vs laser detuning — misalignment scan")
plt.legend(title="M2 tilt", bbox_to_anchor=(1.02,1), loc="upper left")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
