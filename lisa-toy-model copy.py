import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.constants import c
import scipy.signal

from elements.signal_generator import LaserSignal

fADC = 1*10**4
carrier_order = 3
mod_order = 1
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

duration = 4000
delay12 = 8.3
delay23 = 8.5
delay13 = 8.4
# f1 has to be bigger here
f1 = 15 * 10**carrier_order
wl1 = wl(f1)

mod_depth = 0.1
clock_noise_amplitude = 0.0000
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

q1 = laser1.get_clock_jitter()
q2 = laser2.get_clock_jitter()
q3 = laser3.get_clock_jitter()


alpha12 = (f1 - f2) / fADC
alpha13 = (f1 - f3) / fADC
alpha23 = (f2 - f3) / fADC

gamma12 = alpha12 + (f_mod1 - f_mod2) / fADC
gamma13 = alpha13 + (f_mod1 - f_mod3) / fADC
gamma23 = alpha23 + (f_mod2 - f_mod3) / fADC

# This is supposed to be like the PM measurements. 
# In the beginning of the array are older values
carrier12 = - l1[N_to_delay12:] + l2[:-N_to_delay12] + alpha12 * q1[N_to_delay12:]
carrier21 = - l2[N_to_delay12:] + l1[:-N_to_delay12] + alpha12 * q2[N_to_delay12:]
carrier13 = - l1[N_to_delay13:] + l3[:-N_to_delay13] + alpha13 * q1[N_to_delay13:]
carrier31 = - l3[N_to_delay13:] + l1[:-N_to_delay13] + alpha13 * q3[N_to_delay13:]
carrier23 = - l2[N_to_delay23:] + l3[:-N_to_delay23] + alpha23 * q2[N_to_delay23:]
carrier32 = - l3[N_to_delay23:] + l2[:-N_to_delay23] + alpha23 * q3[N_to_delay23:]

sb12 = - l1[N_to_delay12:] + l2[:-N_to_delay12] - q1[N_to_delay12:] + q2[:-N_to_delay12] + gamma12 * q1[N_to_delay12:]
sb21 = - l2[N_to_delay12:] + l1[:-N_to_delay12] - q2[N_to_delay12:] + q1[:-N_to_delay12] + gamma12 * q2[N_to_delay12:]
sb13 = - l1[N_to_delay13:] + l3[:-N_to_delay13] - q1[N_to_delay13:] + q3[:-N_to_delay13] + gamma13 * q1[N_to_delay13:]
sb31 = - l3[N_to_delay13:] + l1[:-N_to_delay13] - q3[N_to_delay13:] + q1[:-N_to_delay13] + gamma13 * q3[N_to_delay13:]
sb23 = - l2[N_to_delay23:] + l3[:-N_to_delay23] - q2[N_to_delay23:] + q3[:-N_to_delay23] + gamma23 * q2[N_to_delay23:]
sb32 = - l3[N_to_delay23:] + l2[:-N_to_delay23] - q3[N_to_delay23:] + q2[:-N_to_delay23] + gamma23 * q3[N_to_delay23:]


# Downconversion
f_slow = 40 # Hz, still too much
decimation_factor = int(fADC // f_slow)
print("decimating by", decimation_factor)
t1_decimated = (t1[:-N_to_delay12])[::decimation_factor]  # Adjust time array accordingly
N_to_delay12_2 = N_to_delay12 // decimation_factor
N_to_delay23_2 = N_to_delay23 // decimation_factor
N_to_delay13_2 = N_to_delay13 // decimation_factor
carrier12_decimated = scipy.signal.decimate(carrier12, decimation_factor, ftype='iir')
carrier21_decimated = scipy.signal.decimate(carrier21, decimation_factor, ftype='iir')
carrier13_decimated = scipy.signal.decimate(carrier13, decimation_factor, ftype='iir')
carrier31_decimated = scipy.signal.decimate(carrier31, decimation_factor, ftype='iir')
carrier23_decimated = scipy.signal.decimate(carrier23, decimation_factor, ftype='iir')
carrier32_decimated = scipy.signal.decimate(carrier32, decimation_factor, ftype='iir')

"""
print("decimating sidebands")
sb12_decimated = scipy.signal.decimate(sb12, decimation_factor, ftype='iir')
sb21_decimated = scipy.signal.decimate(sb21, decimation_factor, ftype='iir')
sb13_decimated = scipy.signal.decimate(sb13, decimation_factor, ftype='iir')
sb31_decimated = scipy.signal.decimate(sb31, decimation_factor, ftype='iir')
sb23_decimated = scipy.signal.decimate(sb23, decimation_factor, ftype='iir')
sb32_decimated = scipy.signal.decimate(sb32, decimation_factor, ftype='iir')



#N_to_delay2 = int(laser1.N / 5.0001)
#delay2 = N_to_delay2 * dT
#print(f"Delay2: {delay2*1000} ms")

Precleaning
Q12 = carrier12_decimated
Q23 = carrier23_decimated - alpha23*(carrier21_decimated - sb21_decimated)/(alpha12 + 1 - gamma12)
Q31 = carrier31_decimated - alpha13*(carrier31_decimated - sb31_decimated)/(alpha13 + 1 - gamma13)
Q13 = carrier13_decimated
Q21 = carrier21_decimated - alpha12*(carrier21_decimated - sb21_decimated)/(alpha12 + 1 - gamma12)
Q32 = carrier32_decimated - alpha23*(carrier31_decimated - sb31_decimated)/(alpha13 + 1 - gamma13)
"""

#X0 = carrier12_decimated[N_to_delay12_2:] + carrier21_decimated[:-N_to_delay12_2] - carrier13_decimated[N_to_delay13_2:] - carrier31_decimated[:-N_to_delay13_2]
to_skip = 300
#X0 = X0[to_skip:-to_skip]

# Bc im using the indices, I have to make sure the signals actually start at the same time
# by using the difference of D_1213 and D1312
# Also I currently know ITS NEGATIVE
diff = N_to_delay12_2 - N_to_delay13_2

X1 = carrier12_decimated[N_to_delay13_2 + N_to_delay12_2 + N_to_delay12_2 - diff:] + carrier21_decimated[N_to_delay13_2 + N_to_delay12_2 - diff: - N_to_delay12_2 ] +\
     carrier13_decimated[N_to_delay13_2 - diff: - N_to_delay12_2 - N_to_delay12_2] + carrier31_decimated[-diff: - N_to_delay13_2 - N_to_delay12_2 - N_to_delay12_2] -\
     carrier13_decimated[N_to_delay12_2 + N_to_delay13_2 + N_to_delay13_2:] - carrier31_decimated[N_to_delay12_2 + N_to_delay13_2: - N_to_delay13_2] - \
     carrier12_decimated[N_to_delay12_2: - N_to_delay13_2 - N_to_delay13_2] - carrier21_decimated[: - N_to_delay13_2 - N_to_delay12_2 - N_to_delay13_2]
X1 = X1[to_skip:-to_skip]

#X0_c = Q12[N_to_delay2:] + Q21[:-N_to_delay2] - Q13[N_to_delay2:] - Q31[:-N_to_delay2]
#X0_c = X0_c[to_skip:-to_skip]
#plt.plot(t1[N_to_delay+N_to_delay2:], X0)
#plt.grid()
#plt.show()

#N = len(X0)
#L_mod_fft = fft(X0)[1:N//2] * 2 / N
#freqs = fftfreq(N, dT)[1:N//2]
# Plotting original and processed signals
plt.figure(figsize=(12, 8))
"""
ax = plt.subplot(2, 1, 1)
plot_fft(ax, laser_signal1, laser1.dT, "Original Laser (L1)")

ax = plt.subplot(2, 1, 2)
temp = laser_signal2[:-N_to_delay] - laser_signal1[N_to_delay:]
PD12 = np.real(temp) ** 2 + np.imag(temp) ** 2
plot_fft(ax, PD12, laser1.dT, "Photodetector 12 signal")
"""

plt.plot(X1)
plt.show()


print("Welching")	
ax = plt.subplot(2, 1, 1)
f, basic_psd_X2 = scipy.signal.welch(X1, fs = f_slow, nperseg= len(X1))
ax.loglog(f[2:], np.sqrt(basic_psd_X2)[2:])
#ax.vlines(1/delay, np.min(np.sqrt(basic_psd_X2)), np.max(np.sqrt(basic_psd_X2)[2:]), color="black")
ax.set_title("TDI Signal (X0, not accounting for clock jitter)")
ax.set_xlabel("Frequency (Hz)")
#ax.set_ylabel("Amplitude")
ax.grid()
"""
ax = plt.subplot(2, 1, 2)
f, basic_psd_X2 = scipy.signal.welch(X0_c, fs = f_slow, nperseg= len(X0_c))
ax.loglog(f[2:], np.sqrt(basic_psd_X2)[2:])
ax.set_title("TDI Signal (X0 with Sidebands)")
ax.set_xlabel("Frequency (Hz)")
#ax.set_ylabel("Amplitude")
ax.grid()
"""
plt.tight_layout()
plt.show()
