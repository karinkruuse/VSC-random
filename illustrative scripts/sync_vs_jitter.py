import numpy as np

# ----------------------------
# Helpers
# ----------------------------
def randwalk(n, step_std):
    """Discrete random walk (integrated white noise)."""
    return np.cumsum(np.random.normal(0.0, step_std, size=n))

def interp_to_uniform(t_nonuniform, x_nonuniform, t_uniform):
    """Resample nonuniform samples back onto uniform grid."""
    return np.interp(t_uniform, t_nonuniform, x_nonuniform)

def wrap_phase(ph):
    """Wrap phase to [-pi, pi)."""
    return (ph + np.pi) % (2*np.pi) - np.pi

# ----------------------------
# Simulation setup
# ----------------------------
np.random.seed(0)

fs = 10_000.0          # sampling rate [Hz]
T  = 2.0               # duration [s]
N  = int(fs*T)
t  = np.arange(N) / fs

f0 = 200.0             # "beatnote" frequency [Hz] (keep low for clarity)
phi_true = 2*np.pi*f0*t

# Clock phase noise q(t) [radians] as a random walk
q = randwalk(N, step_std=2e-3)

# Timing jitter delta_t(t) [seconds] derived from the same clock phase noise
# delta_t = q / (2*pi*f_clk). Use f_clk large so jitter is small but nonzero.
f_clk = 10e6
delta_t = q / (2*np.pi*f_clk)

# Measured phase has TWO effects:
# (1) sampled at wrong times (timing jitter)
# (2) additive clock coupling alpha*q (phasemeter sampling / frequency ratio)
alpha = 0.8
t_meas = t + delta_t
phi_meas = 2*np.pi*f0*t_meas + alpha*q

# ----------------------------
# "Step 1": timestamp correction (resample to uniform time base)
# Assume we know delta_t(t) perfectly (best case)
# ----------------------------
# We have nonuniform samples: (t_meas, phi_meas). Bring them back to uniform t.
phi_after_sync = interp_to_uniform(t_meas, phi_meas, t)

# Compare residual phase error after only timestamp correction
err_sync_only = wrap_phase(phi_after_sync - phi_true)

# ----------------------------
# "Step 2": clock-jitter removal (subtract additive alpha*q term)
# Assume we can estimate q(t) perfectly (best case, like perfect sideband-based estimate)
# ----------------------------
phi_after_both = phi_after_sync - alpha*q
err_both = wrap_phase(phi_after_both - phi_true)

# ----------------------------
# Report simple metrics
# ----------------------------
rms_sync_only = np.std(err_sync_only)
rms_both      = np.std(err_both)

print(f"RMS phase error after timestamp correction only: {rms_sync_only:.3e} rad")
print(f"RMS phase error after timestamp + subtract alpha*q: {rms_both:.3e} rad")

# Also show that timestamp correction removes the timing part:
# If alpha=0 (no additive coupling), timestamp correction alone should nearly solve it.
phi_meas_noadd = 2*np.pi*f0*t_meas
phi_sync_noadd = interp_to_uniform(t_meas, phi_meas_noadd, t)
err_noadd = wrap_phase(phi_sync_noadd - phi_true)
print(f"RMS phase error with alpha=0 (timestamp correction only): {np.std(err_noadd):.3e} rad")
