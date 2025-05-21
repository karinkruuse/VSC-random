import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.constants import c
import scipy.signal

from elements.signal_generator import LaserSignal


fADC = 1*10**5
carrier_order = 3
mod_order = 1
wl = lambda f: c / f

delay = 3.3
duration = 100
dT = 1/fADC
N_to_delay = int(delay / dT)
print(f"Delay: {N_to_delay} samples, {delay/duration*100}% of the signal duration")

t = np.arange(0, duration, dT)

fDev = 1.2*10**5
fLO = 17 * 10**carrier_order
f1 = 15 * 10**carrier_order
f_mod1 = 22 * 10**mod_order
f2 = 12 * 10**carrier_order
f_mod2 = 13 * 10**mod_order
f3 = 10 * 10**carrier_order
f_mod3 = 10 * 10**mod_order

alpha12 = (f2 - f1)/fADC
alpha13 = (f1 - f3)/fADC
alpha23 = (f3 - f2)/fADC

gamma12 = (f2 + f_mod2 - f1 - f_mod1)/fADC
gamma13 = (f1 + f_mod1 - f3 - f_mod3)/fADC
gamma23 = (f3 + f_mod3 - f2 - f_mod2)/fADC

sigma1 = (f1 - fLO)/fDev
sigma2 = (f2 - fLO)/fDev
sigma3 = (f3 - fLO)/fDev
sigma_mod1 = (f1 + f_mod1 - fLO)/fDev
sigma_mod2 = (f2 + f_mod2 - fLO)/fDev
sigma_mod3 = (f3 + f_mod3 - fLO)/fDev
sigma12 = (f2 - f1)/fDev
sigma23 = (f3 - f2)/fDev
sigma31 = (f1 - f3)/fDev
sigma_mod12 = (f2 + f_mod2 - f1 - f_mod1)/fDev
sigma_mod23 = (f3 + f_mod3 - f2 - f_mod2)/fDev
sigma_mod31 = (f1 + f_mod1 - f3 - f_mod3)/fDev


laser_noise_amplitude = 10**-14
clock_noise_amplitude = 10**-13
laser_noise_std = 0.1
clock_noise_std = 0.01

print("generating noise")
p1 = np.cumsum(laser_noise_amplitude * np.random.normal(0, laser_noise_std, len(t)))
p2 = np.cumsum(laser_noise_amplitude * np.random.normal(0, laser_noise_std, len(t)))
p3 = np.cumsum(laser_noise_amplitude * np.random.normal(0, laser_noise_std, len(t)))

q1 = np.cumsum(clock_noise_amplitude * np.random.normal(0, clock_noise_std, len(t)))
q2 = np.cumsum(clock_noise_amplitude * np.random.normal(0, clock_noise_std, len(t)))
q3 = np.cumsum(clock_noise_amplitude * np.random.normal(0, clock_noise_std, len(t)))

q_dev = np.cumsum(clock_noise_amplitude * np.random.normal(0, clock_noise_std, len(t)))


print("putting together the beatnotes and also the demodulation")

carrier12 = - p1[N_to_delay:] + p2[:-N_to_delay] + alpha12 * q1[N_to_delay:]
carrier21 = - p2[N_to_delay:] + p1[:-N_to_delay] + alpha12 * q2[N_to_delay:]
carrier13 = - p1[N_to_delay:] + p3[:-N_to_delay] + alpha13 * q1[N_to_delay:] 
carrier31 = - p3[N_to_delay:] + p1[:-N_to_delay] + alpha13 * q3[N_to_delay:] 
carrier23 = - p2[N_to_delay:] + p3[:-N_to_delay] + alpha23 * q2[N_to_delay:]
carrier32 = - p3[N_to_delay:] + p2[:-N_to_delay] + alpha23 * q3[N_to_delay:]

to_skip = 100
f_slow = 50 # Hz, still too much
decimation_factor = int(fADC // f_slow)
print("decimating by", decimation_factor)
t_decimated = (t[:-N_to_delay])[::decimation_factor]  # Adjust time array accordingly
N_to_delay_2 = N_to_delay // decimation_factor
carrier12_decimated = scipy.signal.decimate(carrier12, decimation_factor, ftype='iir')
carrier21_decimated = scipy.signal.decimate(carrier21, decimation_factor, ftype='iir')
carrier13_decimated = scipy.signal.decimate(carrier13, decimation_factor, ftype='iir')
carrier31_decimated = scipy.signal.decimate(carrier31, decimation_factor, ftype='iir')
carrier23_decimated = scipy.signal.decimate(carrier23, decimation_factor, ftype='iir')
carrier32_decimated = scipy.signal.decimate(carrier32, decimation_factor, ftype='iir')

X0_LISA = carrier12_decimated[N_to_delay_2:] + carrier21_decimated[:-N_to_delay_2] - carrier13_decimated[N_to_delay_2:] - carrier31_decimated[:-N_to_delay_2]
X0_LISA = X0_LISA[to_skip:-to_skip]

noise12 = - sigma1*q_dev[N_to_delay:] + sigma2*q_dev[:-N_to_delay:] - sigma12*q_dev[N_to_delay:]
noise21 = - sigma2*q_dev[N_to_delay:] + sigma1*q_dev[:-N_to_delay:] + sigma12*q_dev[N_to_delay:]
noise13 = - sigma1*q_dev[N_to_delay:] + sigma3*q_dev[:-N_to_delay:] - sigma31*q_dev[N_to_delay:]
noise31 = - sigma3*q_dev[N_to_delay:] + sigma1*q_dev[:-N_to_delay:] + sigma31*q_dev[N_to_delay:]
noise23 = - sigma2*q_dev[N_to_delay:] + sigma3*q_dev[:-N_to_delay:] - sigma23*q_dev[N_to_delay:]
noise32 = - sigma3*q_dev[N_to_delay:] + sigma2*q_dev[:-N_to_delay:] + sigma23*q_dev[N_to_delay:]

carrier12 = - p1[N_to_delay:] + p2[:-N_to_delay] + alpha12 * q1[N_to_delay:] + noise12
carrier21 = - p2[N_to_delay:] + p1[:-N_to_delay] + alpha12 * q2[N_to_delay:] + noise21
carrier13 = - p1[N_to_delay:] + p3[:-N_to_delay] + alpha13 * q1[N_to_delay:] + noise13
carrier31 = - p3[N_to_delay:] + p1[:-N_to_delay] + alpha13 * q3[N_to_delay:] + noise31
carrier23 = - p2[N_to_delay:] + p3[:-N_to_delay] + alpha23 * q2[N_to_delay:] + noise23
carrier32 = - p3[N_to_delay:] + p2[:-N_to_delay] + alpha23 * q3[N_to_delay:] + noise12
carrier12_decimated = scipy.signal.decimate(carrier12, decimation_factor, ftype='iir')
carrier21_decimated = scipy.signal.decimate(carrier21, decimation_factor, ftype='iir')
carrier13_decimated = scipy.signal.decimate(carrier13, decimation_factor, ftype='iir')
carrier31_decimated = scipy.signal.decimate(carrier31, decimation_factor, ftype='iir')
carrier23_decimated = scipy.signal.decimate(carrier23, decimation_factor, ftype='iir')
carrier32_decimated = scipy.signal.decimate(carrier32, decimation_factor, ftype='iir')

X0_dev = carrier12_decimated[N_to_delay_2:] + carrier21_decimated[:-N_to_delay_2] - carrier13_decimated[N_to_delay_2:] - carrier31_decimated[:-N_to_delay_2]
X0_dev = X0_dev[to_skip:-to_skip]

plt.figure(figsize=(15, 8))
print("Welching")	
ax = plt.subplot(4, 1, 1)
f, basic_psd_X2 = scipy.signal.welch(carrier12_decimated, fs = f_slow, nperseg= len(carrier12_decimated))
ax.loglog(f[2:], np.sqrt(basic_psd_X2)[2:])
ax.set_title(r'$s_{{12}}$')
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("ASD [/sqrt(Hz)]")
ax.grid()

ax = plt.subplot(4, 1, 2)
f, basic_psd_X2 = scipy.signal.welch(X0_LISA, fs = f_slow, nperseg= len(X0_LISA))
ax.loglog(f[2:], np.sqrt(basic_psd_X2)[2:])
ax.set_title("LISA TDI0")
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("ASD [/sqrt(Hz)]")
ax.grid()

ax = plt.subplot(4, 1, 3)
f, basic_psd_X2 = scipy.signal.welch(X0_dev, fs = f_slow, nperseg= len(X0_dev))
ax.loglog(f[2:], np.sqrt(basic_psd_X2)[2:])
ax.set_title("Testbed TDI0")
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("ASD [/sqrt(Hz)]")
ax.grid()

ax = plt.subplot(4, 1, 4)
f, basic_psd_X2 = scipy.signal.welch(noise12, fs = f_slow, nperseg= len(noise12))
ax.loglog(f[2:], np.sqrt(basic_psd_X2)[2:])
ax.set_title("Testbed TDI0")
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("ASD [/sqrt(Hz)]")
ax.grid()

plt.tight_layout()
#plt.show()
plt.savefig("sdfsdf.png", dpi=300)
"""
sb12 = - p1[N_to_delay:] + p2[:-N_to_delay] - q1[N_to_delay:] + q2[:-N_to_delay] + gamma12 * q1[N_to_delay:]
sb21 = - p2[N_to_delay:] + p1[:-N_to_delay] - q2[N_to_delay:] + q1[:-N_to_delay] + gamma12 * q2[N_to_delay:]
sb13 = - p1[N_to_delay:] + p3[:-N_to_delay] - q1[N_to_delay:] + q3[:-N_to_delay] + gamma13 * q1[N_to_delay:]
sb31 = - p3[N_to_delay:] + p1[:-N_to_delay] - q3[N_to_delay:] + q1[:-N_to_delay] + gamma13 * q3[N_to_delay:]
sb23 = - p2[N_to_delay:] + p3[:-N_to_delay] - q2[N_to_delay:] + q3[:-N_to_delay] + gamma23 * q2[N_to_delay:]
sb32 = - p3[N_to_delay:] + p2[:-N_to_delay] - q3[N_to_delay:] + q2[:-N_to_delay] + gamma23 * q3[N_to_delay:]
"""

