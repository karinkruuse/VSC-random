"""
config.py
---------
Central configuration for the LISA TDI testbed noise budget.

All frequencies in Hz unless stated otherwise.
All noise amplitudes in Hz/sqrt(Hz) (frequency noise ASD).

Edit this file to reflect your actual frequency plan once it is fixed.
The config is passed as a plain dict to all budget components so that
swapping parameters never requires touching the physics code.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Frequency grid
# ---------------------------------------------------------------------------
FREQ_CONFIG = {
    "f_min":        1e-4,       # Hz  — lower edge of budget plot
    "f_max":        10.0,       # Hz  — upper edge
    "n_points":     2000,       # number of points (log-spaced)
}

# ---------------------------------------------------------------------------
# Frequency plan  (PLACEHOLDER values — update once your plan is fixed)
# ---------------------------------------------------------------------------
FREQ_PLAN = {
    # USO / clock frequencies
    "f_uso":            10e6,       # Hz  — USO output (Rb clock)
    "f_pm_sampling":    80e6,       # Hz  — phasemeter ADC sampling clock
    "f_pilot_tone":     37.5e6,       # Hz  — pilot tone derived from USO

    # Modulation (sideband) frequencies per spacecraft  [PLACEHOLDERS]
    # In LISA these are ~2.4 GHz; here we use MHz because of ADC limits.
    # The offset between spacecraft modulation frequencies sets the
    # sideband-sideband beatnote offset from the carrier-carrier beatnote.
    "f_mod": {
        "SC1": 10.0e6,          # Hz
        "SC2": 11.0e6,          # Hz   (offset by 1 MHz → 1 MHz sb-sb offset)
        "SC3": 12.0e6,          # Hz   (placeholder for 3rd spacecraft)
    },

    # Heterodyne beatnote frequencies (spacecraft laser vs reference laser)
    # Must lie within phasemeter bandwidth (5–25 MHz for Moku:Pro).  [PLACEHOLDERS]
    "f_beat": {
        "SC1": 7.0e6,           # Hz
        "SC2": 14.0e6,          # Hz
        "SC3": 21.0e6,          # Hz
    },

    # Carrier laser frequency (optical)
    "nu_laser":         281e12,     # Hz  (~1064 nm Nd:YAG / fibre laser)
}

# ---------------------------------------------------------------------------
# Arm / delay parameters
# ---------------------------------------------------------------------------
ARM_CONFIG = {
    # One-way light travel times  [seconds]
    # LISA nominal: 8.3 s.  Set to LISA value as default placeholder.
    "tau": {
        "12": 8.3,      # SC1 → SC2
        "21": 8.3,      # SC2 → SC1
        "13": 8.3,      # SC1 → SC3
        "31": 8.3,      # SC3 → SC1
        "23": 8.3,      # SC2 → SC3
        "32": 8.3,      # SC3 → SC2
    },
    # Arm rate of change  [m/s]  — used for second-generation TDI
    "arm_rate": {
        "12": 0.0,
        "21": 0.0,
        "13": 0.0,
        "31": 0.0,
        "23": 0.0,
        "32": 0.0,
    },
}

# ---------------------------------------------------------------------------
# Clock noise coupling coefficients
# These are derived from the frequency plan:
#   alpha_ji = Delta_nu_ji / f_sampling
# where Delta_nu_ji is the heterodyne beatnote frequency.
# Computed automatically from FREQ_PLAN in utils/coupling.py.
# ---------------------------------------------------------------------------
# (Leave empty here — computed at runtime)
COUPLING_COEFFICIENTS = {}

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
CONSTANTS = {
    "c":        299792458.0,    # m/s  — speed of light
    "lambda_laser": 1064e-9,    # m    — laser wavelength (1064 nm)
    "nu_laser":     281e12,     # Hz   — laser carrier frequency (~1064 nm)
}

# ---------------------------------------------------------------------------
# LISA requirements  (for reference / plotting)
# These are approximate; update from the LISA Definition Study Report.
# ---------------------------------------------------------------------------
LISA_REQUIREMENTS = {
    # Displacement noise ASD  [m/sqrt(Hz)]
    # Secondary noise (acceleration + OMS combined), approximate flat value
    # in the mHz band.  Will be converted to frequency noise for plotting.
    "displacement_noise_asd":   3e-12,      # m/sqrt(Hz)  ~3 pm/sqrt(Hz)

    # Laser frequency noise requirement (pre-TDI, pre-stabilised)
    # ~30 Hz/sqrt(Hz) in the mHz band
    "laser_freq_noise_prestab": 30.0,       # Hz/sqrt(Hz)
}

# ---------------------------------------------------------------------------
# Plotting defaults
# ---------------------------------------------------------------------------
PLOT_CONFIG = {
    "figsize":      (10, 6),
    "freq_unit":    "Hz",
    "noise_unit":   "Hz/sqrt(Hz)",      # default — phase option also available
    "show_lisa_req": True,
    "show_total":    True,
    "alpha_individual": 0.8,
    "linewidth":    1.5,
}
