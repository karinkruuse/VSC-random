import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.constants import c
import scipy.signal

from elements.signal_generator import LaserSignal

fADC = 2*10**4
carrier_order = 4
mod_order = 2
wl = lambda f: c / f

# Helper function for FFT plots
def plot_fft(ax, signal, dT, title):
    N = len(signal)
    fft_values = fft(signal)[1:N//2] * 2 / N
    freqs = fftfreq(N, dT)[1:N//2]
    ax.loglog(freqs, np.abs(fft_values))
    ax.set_title(title)
    ax.set_xlabel("Frequency (Hz)")
    #ax.set_ylabel("Amplitude")
    ax.grid()

duration = 1000
delay12 = 3.3
delay23 = 3.5
delay13 = 3.4
# f1 has to be bigger here
f1 = 15 * 10**carrier_order
wl1 = wl(f1)

mod_depth = 0.1
clock_noise_amplitude = 10**-13
f_mod1 = 22 * 10**mod_order

laser1 = LaserSignal.from_duration("SC1", wavelength=wl1, duration=duration, dT=1/fADC)
laser1.generate_signal(mod_depth=mod_depth, f_mod=f_mod1, clock_noise_amplitude=0)
#laser1.plot_spectrum()

dT = laser1.dT
f2 = 12 * 10**carrier_order
wl2 = wl(f2)
f_mod2 = 13 * 10**mod_order

N_to_delay12 = int(delay12 / dT)
N_to_delay23 = int(delay23 / dT)
N_to_delay13 = int(delay13 / dT)
print(f"Delay: {N_to_delay12} samples, {delay12/duration*100}% of the signal duration")

laser2 = LaserSignal.from_duration("SC2", wavelength=wl2, duration=duration, dT=dT)
laser2.generate_signal(mod_depth=mod_depth, f_mod=f_mod2, clock_noise_amplitude=clock_noise_amplitude)
#laser2.plot_spectrum()

f3 = 10 * 10**carrier_order
wl3 = wl(f3)
f_mod3 = 10 * 10**mod_order

laser3 = LaserSignal.from_duration("SC3", wavelength=wl3, duration=duration, dT=dT)
laser3.generate_signal(mod_depth=mod_depth, f_mod=f_mod3, clock_noise_amplitude=clock_noise_amplitude)

laser_signal1, t1 = laser1.get_signal()
laser_signal2, t1 = laser2.get_signal()

l1, t1 = laser1.get_laser_noise()
l2, t2 = laser2.get_laser_noise()
l3, t3 = laser3.get_laser_noise()

q1, _ = laser1.get_clock_jitter()
q2, _ = laser2.get_clock_jitter()
q3, _ = laser3.get_clock_jitter()


alpha12 = (f1 - f2) / fADC
alpha13 = (f1 - f3) / fADC
alpha23 = (f2 - f3) / fADC

gamma12 = alpha12 + (f_mod1 - f_mod2) / fADC
gamma13 = alpha13 + (f_mod1 - f_mod3) / fADC
gamma23 = alpha23 + (f_mod2 - f_mod3) / fADC

diff1 = N_to_delay12 - N_to_delay23
diff2 = N_to_delay13 - N_to_delay23
#print(diff1, diff2)

# This is supposed to be like the PM measurements. 
# In the beginning of the array are older values
carrier12 = - l1[N_to_delay12-diff1:] + l2[-diff1:-N_to_delay12] + alpha12 * q1[N_to_delay12-diff1:]
carrier21 = - l2[N_to_delay12-diff1:] + l1[-diff1:-N_to_delay12] + alpha12 * q2[N_to_delay12-diff1:]
carrier13 = - l1[N_to_delay13-diff2:] + l3[-diff2:-N_to_delay13] + alpha13 * q1[N_to_delay13-diff2:]
carrier31 = - l3[N_to_delay13-diff2:] + l1[-diff2:-N_to_delay13] + alpha13 * q3[N_to_delay13-diff2:]
carrier23 = - l2[N_to_delay23:] + l3[:-N_to_delay23] + alpha23 * q2[N_to_delay23:]
carrier32 = - l3[N_to_delay23:] + l2[:-N_to_delay23] + alpha23 * q3[N_to_delay23:]
#print(len(carrier12), len(carrier21), len(carrier13), len(carrier31), len(carrier23), len(carrier32))

sb12 = - l1[N_to_delay12-diff1:] + l2[-diff1:-N_to_delay12] - q1[N_to_delay12-diff1:] + q2[-diff1:-N_to_delay12] + gamma12 * q1[N_to_delay12-diff1:]
sb21 = - l2[N_to_delay12-diff1:] + l1[-diff1:-N_to_delay12] - q2[N_to_delay12-diff1:] + q1[-diff1:-N_to_delay12] + gamma12 * q2[N_to_delay12-diff1:]
sb13 = - l1[N_to_delay13-diff2:] + l3[-diff2:-N_to_delay13] - q1[N_to_delay13-diff2:] + q3[-diff2:-N_to_delay13] + gamma13 * q1[N_to_delay13-diff2:]
sb31 = - l3[N_to_delay13-diff2:] + l1[-diff2:-N_to_delay13] - q3[N_to_delay13-diff2:] + q1[-diff2:-N_to_delay13] + gamma13 * q3[N_to_delay13-diff2:]
sb23 = - l2[N_to_delay23:] + l3[:-N_to_delay23] - q2[N_to_delay23:] + q3[:-N_to_delay23] + gamma23 * q2[N_to_delay23:]
sb32 = - l3[N_to_delay23:] + l2[:-N_to_delay23] - q3[N_to_delay23:] + q2[:-N_to_delay23] + gamma23 * q3[N_to_delay23:]


# Downconversion
f_slow = 50 # Hz, still too much
decimation_factor = int(fADC // f_slow)
print(f"delay 12 {N_to_delay12} samples")
print(f"delay 13 {N_to_delay13} samples")
print(f"delay 32 {N_to_delay23} samples")
print("decimating by", decimation_factor)
t1_decimated = (t1[:-N_to_delay12])[::decimation_factor]  # Adjust time array accordingly
N_to_delay12_2 = N_to_delay12 // decimation_factor
N_to_delay23_2 = N_to_delay23 // decimation_factor
N_to_delay13_2 = N_to_delay13 // decimation_factor



down = decimation_factor
up = 1
carrier12_decimated = scipy.signal.resample_poly(carrier12, up, down)
carrier21_decimated = scipy.signal.resample_poly(carrier21, up, down)
carrier13_decimated = scipy.signal.resample_poly(carrier13, up, down)
carrier31_decimated = scipy.signal.resample_poly(carrier31, up, down)
carrier23_decimated = scipy.signal.resample_poly(carrier23, up, down)
carrier32_decimated = scipy.signal.resample_poly(carrier32, up, down)

sb12_decimated = scipy.signal.resample_poly(sb12, up, down)
sb21_decimated = scipy.signal.resample_poly(sb21, up, down)
sb13_decimated = scipy.signal.resample_poly(sb13, up, down)
sb31_decimated = scipy.signal.resample_poly(sb31, up, down)
sb23_decimated = scipy.signal.resample_poly(sb23, up, down)
sb32_decimated = scipy.signal.resample_poly(sb32, up, down)

l1_decimated = scipy.signal.resample_poly(l1, up, down)
l2_decimated = scipy.signal.resample_poly(l2, up, down)
l3_decimated = scipy.signal.resample_poly(l3, up, down)
q1_decimated = scipy.signal.resample_poly(q1, up, down)
q2_decimated = scipy.signal.resample_poly(q2, up, down)
q3_decimated = scipy.signal.resample_poly(q3, up, down)



Q12 = carrier12_decimated
Q13 = carrier13_decimated
Q21 = carrier21_decimated - alpha12*(carrier21_decimated - sb21_decimated)/(alpha12 + 1 - gamma12)
Q31 = carrier31_decimated - alpha13*(carrier31_decimated - sb31_decimated)/(alpha13 + 1 - gamma13)
Q23 = carrier23_decimated - alpha23*(carrier23_decimated - sb23_decimated)/(alpha23 + 1 - gamma23)
Q32 = carrier32_decimated - alpha23*(carrier32_decimated - sb32_decimated)/(alpha23 + 1 - gamma23)


#X0 = carrier12_decimated[N_to_delay12_2:] + carrier21_decimated[:-N_to_delay12_2] - carrier13_decimated[N_to_delay13_2:] - carrier31_decimated[:-N_to_delay13_2]
to_skip = 300
#X0 = X0[to_skip:-to_skip]

# Bc im using the indices, I have to make sure the signals actually start at the same time
# by using the difference of D_1213 and D1312
# ie the relative delays should still stay correct
# Also I currently know ITS NEGATIVE
diff = 0 
diff = N_to_delay12_2 - N_to_delay13_2
"""
print(diff)
print(N_to_delay13_2 + N_to_delay12_2 + N_to_delay12_2 - diff, "0", len(carrier12_decimated))
print(N_to_delay13_2 + N_to_delay12_2 - diff, - N_to_delay12_2, len(carrier21_decimated))
print(N_to_delay13_2 - diff, - N_to_delay12_2 - N_to_delay12_2, len(carrier13_decimated))
print(-diff, - N_to_delay13_2 - N_to_delay12_2 - N_to_delay12_2, len(carrier31_decimated))
print(N_to_delay12_2 + N_to_delay13_2 + N_to_delay13_2, "0", len(carrier13_decimated))
print(N_to_delay12_2 + N_to_delay13_2, - N_to_delay13_2, len(carrier31_decimated))
print(N_to_delay12_2, - N_to_delay13_2 - N_to_delay13_2, len(carrier12_decimated))
print("0", - N_to_delay13_2 - N_to_delay12_2 - N_to_delay13_2, len(carrier21_decimated))
"""
X1 = carrier12_decimated[N_to_delay13_2 + N_to_delay12_2 + N_to_delay12_2 - diff:] + carrier21_decimated[N_to_delay13_2 + N_to_delay12_2 - diff: - N_to_delay12_2 ] +\
     carrier13_decimated[N_to_delay13_2 - diff: - N_to_delay12_2 - N_to_delay12_2] + carrier31_decimated[-diff: - N_to_delay13_2 - N_to_delay12_2 - N_to_delay12_2] -\
     carrier13_decimated[N_to_delay12_2 + N_to_delay13_2 + N_to_delay13_2:] - carrier31_decimated[N_to_delay12_2 + N_to_delay13_2: - N_to_delay13_2] - \
     carrier12_decimated[N_to_delay12_2: - N_to_delay13_2 - N_to_delay13_2] - carrier21_decimated[: - N_to_delay13_2 - N_to_delay12_2 - N_to_delay13_2]
X1 = X1[to_skip:-to_skip]

X1_c = Q12[N_to_delay13_2 + N_to_delay12_2 + N_to_delay12_2 - diff:] + Q21[N_to_delay13_2 + N_to_delay12_2 - diff: - N_to_delay12_2 ] +\
     Q13[N_to_delay13_2 - diff: - N_to_delay12_2 - N_to_delay12_2] + Q31[-diff: - N_to_delay13_2 - N_to_delay12_2 - N_to_delay12_2] -\
     Q13[N_to_delay12_2 + N_to_delay13_2 + N_to_delay13_2:] - Q31[N_to_delay12_2 + N_to_delay13_2: - N_to_delay13_2] - \
     Q12[N_to_delay12_2: - N_to_delay13_2 - N_to_delay13_2] - Q21[: - N_to_delay13_2 - N_to_delay12_2 - N_to_delay13_2]
X1_c = X1_c[to_skip:-to_skip]



# ── Laser-only signals ────────────────────────────────────────────────────────
carrier12_l = - l1[N_to_delay12-diff1:] + l2[-diff1:-N_to_delay12]
carrier21_l = - l2[N_to_delay12-diff1:] + l1[-diff1:-N_to_delay12]
carrier13_l = - l1[N_to_delay13-diff2:] + l3[-diff2:-N_to_delay13]
carrier31_l = - l3[N_to_delay13-diff2:] + l1[-diff2:-N_to_delay13]
carrier23_l = - l2[N_to_delay23:] + l3[:-N_to_delay23]
carrier32_l = - l3[N_to_delay23:] + l2[:-N_to_delay23]

print(len(carrier12_l), len(carrier13_l), len(carrier23_l))
# ── TDI X1 without decimation, using full-rate delay indices ──────────────────
# Total delay offset for each arm of X1
offset_arm1 = N_to_delay13 + N_to_delay12 + N_to_delay12 - diff1  # 204000
offset_arm2 = N_to_delay12 + N_to_delay13 + N_to_delay13          # 202000
offset = max(offset_arm1, offset_arm2)                             # 204000
extra = offset - offset_arm2                                       # 2000

X1_laser_nd = carrier12_l[offset:] + \
              carrier21_l[offset - N_to_delay12: -N_to_delay12] + \
              carrier13_l[offset - N_to_delay12 - N_to_delay12: -N_to_delay12 - N_to_delay12] + \
              carrier31_l[offset - N_to_delay13 - N_to_delay12 - N_to_delay12: -N_to_delay13 - N_to_delay12 - N_to_delay12] - \
              carrier13_l[offset:] - \
              carrier31_l[offset - N_to_delay13: -N_to_delay13] - \
              carrier12_l[offset - N_to_delay13 - N_to_delay13: -N_to_delay13 - N_to_delay13] - \
              carrier21_l[offset - N_to_delay13 - N_to_delay13 - N_to_delay12: -N_to_delay13 - N_to_delay13 - N_to_delay12]
X1_laser_nd = X1_laser_nd[to_skip:-to_skip]

# ── TDI X1 with decimation ────────────────────────────────────────────────────
carrier12_l_d = scipy.signal.resample_poly(carrier12_l, 1, decimation_factor)
carrier21_l_d = scipy.signal.resample_poly(carrier21_l, 1, decimation_factor)
carrier13_l_d = scipy.signal.resample_poly(carrier13_l, 1, decimation_factor)
carrier31_l_d = scipy.signal.resample_poly(carrier31_l, 1, decimation_factor)
carrier23_l_d = scipy.signal.resample_poly(carrier23_l, 1, decimation_factor)
carrier32_l_d = scipy.signal.resample_poly(carrier32_l, 1, decimation_factor)


X1_laser_d = carrier12_l_d[N_to_delay13_2 + N_to_delay12_2 + N_to_delay12_2 - diff:] + \
             carrier21_l_d[N_to_delay13_2 + N_to_delay12_2 - diff: -N_to_delay12_2] + \
             carrier13_l_d[N_to_delay13_2 - diff: -N_to_delay12_2 - N_to_delay12_2] + \
             carrier31_l_d[-diff: -N_to_delay13_2 - N_to_delay12_2 - N_to_delay12_2] - \
             carrier13_l_d[N_to_delay12_2 + N_to_delay13_2 + N_to_delay13_2:] - \
             carrier31_l_d[N_to_delay12_2 + N_to_delay13_2: -N_to_delay13_2] - \
             carrier12_l_d[N_to_delay12_2: -N_to_delay13_2 - N_to_delay13_2] - \
             carrier21_l_d[: -N_to_delay13_2 - N_to_delay12_2 - N_to_delay13_2]
X1_laser_d = X1_laser_d[to_skip:-to_skip]

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

f_nd, psd_nd = scipy.signal.welch(X1_laser_nd, fs=fADC, nperseg=len(X1_laser_nd)//4)
f_d,  psd_d  = scipy.signal.welch(X1_laser_d,  fs=f_slow, nperseg=len(X1_laser_d)//4)

axes[0].loglog(f_nd[2:], np.sqrt(psd_nd)[2:], label='X1 laser only')
axes[0].set_title("Laser-only TDI (no decimation)")
axes[0].set_xlabel("Frequency (Hz)")
axes[0].set_ylabel(r"ASD [rad/$\sqrt{\mathrm{Hz}}$]")
axes[0].legend()
axes[0].grid()

axes[1].loglog(f_d[2:], np.sqrt(psd_d)[2:], label='X1 laser only (decimated)')
axes[1].set_title("Laser-only TDI (decimated)")
axes[1].set_xlabel("Frequency (Hz)")
axes[1].set_ylabel(r"ASD [rad/$\sqrt{\mathrm{Hz}}$]")
axes[1].legend()
axes[1].grid()

plt.tight_layout()
plt.savefig("TDI_laser_only.png", dpi=300)
plt.show()


plt.figure(figsize=(12, 8))
print("Welching")

PSD_len = len(l1_decimated) // 4
ax = plt.subplot(3, 1, 1)
f, basic_psd_X2 = scipy.signal.welch(carrier12_decimated, fs = f_slow, nperseg= len(carrier12_decimated))
fffffff, laser_noise_PSD = scipy.signal.welch(l1_decimated, fs = f_slow, nperseg= PSD_len)
fffffff, clock_noise_PSD = scipy.signal.welch(q2_decimated, fs = f_slow, nperseg= PSD_len)

f_plot = f[2:]

print("Clock noise for SC1 is 0 as we use that as the timing reference")
print("Limiting factor currently seems to be the decimation")
ax.loglog(f_plot, np.sqrt(basic_psd_X2)[2:], label=r'$s_{12}$')
ax.loglog(fffffff, np.sqrt(laser_noise_PSD), 'r--', lw=1, label=r'laser noise: $\sqrt{2}\cdot 2\pi S_\nu / f$')
ax.loglog(fffffff, 2 * np.pi * abs(f1 - f2)/ fADC *np.sqrt(clock_noise_PSD), 'g--', lw=1, label=r'clock noise: $2\pi|f_1-f_2|\,S_q$')
ax.set_title(r'$s_{12}$')
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel(r"ASD [rad/$\sqrt{\mathrm{Hz}}$]")
ax.legend(fontsize=7, loc='upper right')
ax.grid()

ax = plt.subplot(3, 1, 2)
f, basic_psd_X2 = scipy.signal.welch(X1, fs = f_slow, nperseg= len(X1))
f_plot = f[2:]
ax.loglog(f_plot, np.sqrt(basic_psd_X2)[2:], label='X1')
ax.loglog(fffffff, 2 * np.pi * abs(f1 - f2)/ fADC *np.sqrt(clock_noise_PSD), 'g--', lw=1, label=r'clock noise: $2\pi|f_1-f_2|\,S_q$')
ax.vlines(1/delay13, np.min(np.sqrt(basic_psd_X2)), np.max(np.sqrt(basic_psd_X2)[2:]), color="black", linewidth=1)
ax.set_title("TDI Signal (X1, not accounting for clock jitter)")
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel(r"ASD [rad/$\sqrt{\mathrm{Hz}}$]")
ax.legend(fontsize=7, loc='upper right')
ax.grid()

ax = plt.subplot(3, 1, 3)
f, basic_psd_X2_c = scipy.signal.welch(X1_c, fs = f_slow, nperseg= len(X1_c))
f_plot = f[2:]
ax.loglog(f_plot, np.sqrt(basic_psd_X2_c)[2:], label='X1 (clock-corrected)')
ax.loglog(fffffff, 2 * np.pi * abs(f1 - f2)/ fADC *np.sqrt(clock_noise_PSD), 'g--', lw=1, label=r'clock noise: $2\pi|f_1-f_2|\,S_q$')
ax.set_title("TDI Signal (X1 with clock correction)")
ax.vlines(1/delay13, np.min(np.sqrt(basic_psd_X2_c)), np.max(np.sqrt(basic_psd_X2_c)[2:]), color="black", linewidth=1)
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel(r"ASD [rad/$\sqrt{\mathrm{Hz}}$]")
ax.legend(fontsize=7, loc='upper right')
ax.grid()

plt.tight_layout()
#plt.show()
plt.savefig("TDI_X1_w_clock2.png", dpi=300)
