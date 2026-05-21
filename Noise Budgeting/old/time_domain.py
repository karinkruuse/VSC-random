import numpy as np
import matplotlib.pyplot as plt
import scipy.signal

# ══════════════════════════════════════════════════════════════════════════════
#  Simulation parameters
# ══════════════════════════════════════════════════════════════════════════════
fs       = 16.0          # sample rate [Hz]  (Nyquist = 8 Hz, well above LISA band)
duration = 20000.0       # [s]  →  minimum frequency bin ≈ 0.05 mHz
N        = int(fs * duration)
dt       = 1.0 / fs

tau      = 8.3           # one-way arm delay [s]
N_delay  = round(tau * fs)   # = 133 samples

rng = np.random.default_rng(42)

# Carrier and sideband beatnote frequencies
# (typical testbed values; in a real LISA these would be ~MHz)
f1 = 15000.0    # SC1 laser offset from reference [Hz]
f2 = 12000.0    # SC2 laser offset [Hz]
f_mod1 = 70.0   # SC1 modulation (sideband) frequency [Hz]
f_mod2 = 45.0   # SC2 modulation (sideband) frequency [Hz]


# ══════════════════════════════════════════════════════════════════════════════
#  Colored noise generation from a target PSD
# ══════════════════════════════════════════════════════════════════════════════
def gen_noise(psd_func, N, fs, rng):
    """
    Return a real time-domain signal with the given one-sided PSD [unit²/Hz].
    Uses spectral shaping of white Gaussian noise.
    """
    freqs = np.fft.rfftfreq(N, d=1.0 / fs)
    freqs[0] = freqs[1]                        # avoid DC singularity
    amp  = np.sqrt(psd_func(freqs) * fs / 2)
    phi  = rng.uniform(0, 2 * np.pi, len(freqs))
    spec = amp * np.exp(1j * phi)
    spec[0] = 0.0                              # zero mean
    return np.fft.irfft(spec, n=N)


# ══════════════════════════════════════════════════════════════════════════════
#  Laser noise
#  LISA requirement: S_ν(f) = 30² · (1 + (2 mHz / f)⁴)  [Hz²/Hz]
#  Integrate to get laser phase noise p [cycles]
# ══════════════════════════════════════════════════════════════════════════════
S_laser = lambda f: 30**2 * (1 + (2e-3 / f)**4)   # Hz²/Hz

dnu1 = gen_noise(S_laser, N, fs, rng)   # SC1 laser frequency noise [Hz]
dnu2 = gen_noise(S_laser, N, fs, rng)   # SC2 laser frequency noise [Hz]

p1 = np.cumsum(dnu1) * dt   # laser phase noise [cycles]
p2 = np.cumsum(dnu2) * dt


# ══════════════════════════════════════════════════════════════════════════════
#  Clock noise  (USO: ultra-stable oscillator)
#  LISA model: S_y(f) = 4×10⁻²⁷ / f  [1/Hz]  (fractional frequency noise)
#  Integrate to get clock time deviation q [seconds]
# ══════════════════════════════════════════════════════════════════════════════
S_clock = lambda f: 4e-27 / f            # fractional frequency noise [1/Hz]

y1 = gen_noise(S_clock, N, fs, rng)     # SC1 fractional frequency noise (dimensionless)
y2 = gen_noise(S_clock, N, fs, rng)     # SC2

q1 = np.cumsum(y1) * dt   # clock time deviation [s]
q2 = np.cumsum(y2) * dt


# ══════════════════════════════════════════════════════════════════════════════
#  Time-align arrays  (current time vs delayed time)
# ══════════════════════════════════════════════════════════════════════════════
p1_now = p1[N_delay:]      # p₁(t)
p2_now = p2[N_delay:]      # p₂(t)
p2_del = p2[:-N_delay]     # p₂(t − τ)
p1_del = p1[:-N_delay]     # p₁(t − τ)

q1_now = q1[N_delay:]      # q₁(t)
q2_now = q2[N_delay:]      # q₂(t)
q2_del = q2[:-N_delay]     # q₂(t − τ)
q1_del = q1[:-N_delay]     # q₁(t − τ)


# ══════════════════════════════════════════════════════════════════════════════
#  Phasemeter measurements  (all in cycles)
#
#  Carrier at SC1 (SC1 beats its local laser against the received beam from SC2):
#    s₁₂ = p₂(t−τ) − p₁(t)  +  f_beat · q₁(t)
#    The last term: the phasemeter samples the beatnote at the wrong moment
#    (shifted by q₁ seconds), so the measured phase shifts by f_beat × q₁ cycles.
#
#  Sideband at SC1 (same but for the modulation sidebands):
#    sb₁₂ = p₂(t−τ) − p₁(t)  +  (f₂ + f_mod2) · q₂(t−τ)  −  (f₁ + f_mod1) · q₁(t)
#    Both clocks enter via their own sideband frequency; taking the difference
#    gives a different linear combination of q₁ and q₂ than the carrier does.
# ══════════════════════════════════════════════════════════════════════════════
f_beat_carrier  = f2 - f1                              # carrier beatnote [Hz]  (< 0 here)
f_beat_sideband = (f2 + f_mod2) - (f1 + f_mod1)       # sideband beatnote [Hz]

# Carrier
s12 = (p2_del - p1_now) + f_beat_carrier * q1_now      # SC1 measures SC2
s21 = (p1_del - p2_now) - f_beat_carrier * q2_now      # SC2 measures SC1

# Sideband
sb12 = (p2_del - p1_now) + (f2 + f_mod2) * q2_del - (f1 + f_mod1) * q1_now
sb21 = (p1_del - p2_now) + (f1 + f_mod1) * q1_del - (f2 + f_mod2) * q2_now

# Isolate the clock noise contribution in each channel (for reference)
clock_s12  = f_beat_carrier * q1_now
clock_sb12 = (f2 + f_mod2) * q2_del - (f1 + f_mod1) * q1_now


# ══════════════════════════════════════════════════════════════════════════════
#  PSD estimation  (Welch)
# ══════════════════════════════════════════════════════════════════════════════
nperseg = N // 8

fw, Sp1        = scipy.signal.welch(p1_now,    fs=fs, nperseg=nperseg)
fw, Ss12       = scipy.signal.welch(s12,        fs=fs, nperseg=nperseg)
fw, Ssb12      = scipy.signal.welch(sb12,       fs=fs, nperseg=nperseg)
fw, Sclock_s   = scipy.signal.welch(clock_s12,  fs=fs, nperseg=nperseg)
fw, Sclock_sb  = scipy.signal.welch(clock_sb12, fs=fs, nperseg=nperseg)


# ══════════════════════════════════════════════════════════════════════════════
#  Plot
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 6))

ax.loglog(fw[1:], np.sqrt(Sp1[1:]),       lw=2,
          label='Laser phase noise p₁  (input)')
ax.loglog(fw[1:], np.sqrt(Ss12[1:]),      lw=2, ls='--',
          label='Carrier s₁₂  (laser + clock)')
ax.loglog(fw[1:], np.sqrt(Ssb12[1:]),     lw=2, ls=':',
          label='Sideband sb₁₂  (laser + clock)')
ax.loglog(fw[1:], np.sqrt(Sclock_s[1:]),  lw=1.5, ls='-.', color='gray',
          label=f'Clock noise in carrier only  (f_beat = {abs(f_beat_carrier):.0f} Hz)')
ax.loglog(fw[1:], np.sqrt(Sclock_sb[1:]), lw=1.5, ls=(0,(3,1,1,1)), color='darkgray',
          label=f'Clock noise in sideband only  (f_mod ≈ {f_mod1:.0f} Hz)')

ax.set_xlabel('Frequency  [Hz]')
ax.set_ylabel('ASD  [cycles / √Hz]')
ax.set_title('Two-laser LISA phasemeter outputs with clock noise modulation')
ax.legend(fontsize=10)
ax.grid(True, which='both', alpha=0.3)
ax.set_xlim(fw[1], fw[-1])

plt.tight_layout()
plt.show()
