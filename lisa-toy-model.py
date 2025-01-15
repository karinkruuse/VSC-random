import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.constants import c
from scipy.signal import hilbert

from elements.signal_generator import LaserSignal

wl = lambda f: c / f

duration = 0.1

# f1 has to be bigger here
f1 = 15 * 10**6 # MHz order
wl1 = wl(f1)

f_mod1 = 22 * 10**3

laser1 = LaserSignal.from_duration("SC1", wavelength=wl1, duration=duration)
laser1.generate_signal(mod_depth=0.1, f_mod=f_mod1)
#laser1.plot_spectrum()

dT = laser1.dT
f2 = 12 * 10**6 # MHz order
wl2 = wl(f2)
f_mod2 = 13 * 10**3

laser2 = LaserSignal.from_duration("SC2", wavelength=wl2, duration=duration, dT=dT)
laser2.generate_signal(mod_depth=0, f_mod=f_mod2)
#laser2.plot_spectrum()


f3 = 10 * 10**6 # MHz order
wl3 = wl(f3)
f_mod3 = 10 * 10**3

laser3 = LaserSignal.from_duration("SC3", wavelength=wl3, duration=duration, dT=dT)
laser3.generate_signal(mod_depth=0, f_mod=f_mod3)


l1, t1 = laser1.get_signal()
l2, t2 = laser2.get_signal()
l3, t3 = laser3.get_signal()

N_to_delay = int(laser1.N / 5)
delay = N_to_delay * dT
print(f"Delay: {delay*1000} ms")

# In the beginning of the array are older values
print("12")
temp = l1[N_to_delay:] + l2[:-N_to_delay]
PD12 = np.real(temp) ** 2 + np.imag(temp) ** 2
n = len(PD12)
#L_mod_fft12 = fft(PD12)[1:n//2] * 2 / n

# Signal: Assume PD12 is the input signal
signal = PD12 - np.mean(PD12)  # Remove DC component if present

# Initial conditions for PLL
phase_est = 0  # Initial phase estimate
freq_est = 2 * np.pi * (f1 - f2)  # Frequency estimate in rad/s
phase_error = 0  # Phase error

# PLL parameters
Kp = 1.0  # Proportional gain
Ki = 0.1  # Integral gain
integrator = 0  # Integrator for loop filter

phase12 = []
for i in range(n):
    # Generate reference signal based on current phase estimate
    ref_signal = np.cos(phase_est)
    
    # Phase detector: Compute phase error
    phase_error = signal[i] * ref_signal
    
    # Loop filter: Proportional-Integral (PI) controller
    integrator += phase_error * dT
    control_signal = Kp * phase_error + Ki * integrator
    
    # Update phase estimate
    phase_est += (freq_est + control_signal) * dT
    phase12.append(phase_est)
phase12 = np.unwrap(phase12)


print("21")
temp = l1[:-N_to_delay] + l2[N_to_delay:]
PD21 = np.real(temp) ** 2 + np.imag(temp) ** 2
#L_mod_fft21 = fft(PD21)[1:n//2] * 2 / n

signal = PD21 - np.mean(PD21)  # Remove DC component if present

# Initial conditions for PLL
phase_est = 0  # Initial phase estimate
freq_est = 2 * np.pi * (f1 - f2)  # Frequency estimate in rad/s
phase_error = 0  # Phase error

integrator = 0  # Integrator for loop filter

phase21 = []
for i in range(n):
    # Generate reference signal based on current phase estimate
    ref_signal = np.cos(phase_est)
    
    # Phase detector: Compute phase error
    phase_error = signal[i] * ref_signal
    
    # Loop filter: Proportional-Integral (PI) controller
    integrator += phase_error * dT
    control_signal = Kp * phase_error + Ki * integrator
    
    # Update phase estimate
    phase_est += (freq_est + control_signal) * dT
    phase21.append(phase_est)
phase21 = np.unwrap(phase21)




print("13")
temp = l1[N_to_delay:] + l3[:-N_to_delay]
PD13 = np.real(temp) ** 2 + np.imag(temp) ** 2
#L_mod_fft13 = fft(PD13)[1:n//2] * 2 / n

signal = PD13 - np.mean(PD13)  # Remove DC component if present

# Initial conditions for PLL
phase_est = 0  # Initial phase estimate
freq_est = 2 * np.pi * (f1 - f3)  # Frequency estimate in rad/s
phase_error = 0  # Phase error

integrator = 0  # Integrator for loop filter

phase13 = []
for i in range(n):
    # Generate reference signal based on current phase estimate
    ref_signal = np.cos(phase_est)
    
    # Phase detector: Compute phase error
    phase_error = signal[i] * ref_signal
    
    # Loop filter: Proportional-Integral (PI) controller
    integrator += phase_error * dT
    control_signal = Kp * phase_error + Ki * integrator
    
    # Update phase estimate
    phase_est += (freq_est + control_signal) * dT
    phase13.append(phase_est)
phase13 = np.unwrap(phase13)



print("31")
temp = l1[:-N_to_delay] + l3[N_to_delay:]
PD31 = np.real(temp) ** 2 + np.imag(temp) ** 2
#L_mod_fft31 = fft(PD31)[1:n//2] * 2 / n
#freqs = fftfreq(n, dT)[1:n//2]
signal = PD31 - np.mean(PD31)  # Remove DC component if present

# Initial conditions for PLL
phase_est = 0  # Initial phase estimate
freq_est = 2 * np.pi * (f1 - f3)  # Frequency estimate in rad/s
phase_error = 0  # Phase error

integrator = 0  # Integrator for loop filter

phase31 = []
for i in range(n):
    # Generate reference signal based on current phase estimate
    ref_signal = np.cos(phase_est)
    
    # Phase detector: Compute phase error
    phase_error = signal[i] * ref_signal
    
    # Loop filter: Proportional-Integral (PI) controller
    integrator += phase_error * dT
    control_signal = Kp * phase_error + Ki * integrator
    
    # Update phase estimate
    phase_est += (freq_est + control_signal) * dT
    phase31.append(phase_est)
phase31 = np.unwrap(phase31)

"""

plot_PD = False
if plot_PD:
    fig, ax = plt.subplots(1, 2, sharey=True, figsize=(10, 6))
    #ax[0].plot(freqs/10**6, np.abs(L_mod_fft12), color="r")
    #ax[1].plot(freqs/10**6, np.abs(L_mod_fft21), color="black")

    #plt.xlim(1, 10)

    plt.title("Spectrum of the beatnote")
    ax[0].set_xlabel("Frequency (MHz)")
    ax[1].set_xlabel("Frequency (MHz)")
    ax[0].ylabel("Amplitude")
    ax[0].grid()
    ax[1].grid()
    plt.show()

"""
# X0 = η12 + D12η21 − η13 − D13η31
#N_to_delay = int(N_to_delay*1.6)
X0 = phase12[N_to_delay:] + phase21[:-N_to_delay] - phase13[N_to_delay:] - phase31[:-N_to_delay]
n = len(X0)
TDI_spec = fft(X0)[1:n//2] * 2 / n

freqs = fftfreq(n, dT)[1:n//2]

plt.figure(figsize=(10, 6))
plt.plot(freqs/10**6, np.abs(TDI_spec), color="r")
#plt.xlim(4.9, 5.1)
plt.title("TDI gen 0")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.grid()
plt.show()
