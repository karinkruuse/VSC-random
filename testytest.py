import numpy as np
import matplotlib.pyplot as plt

# PLL and signal parameters
fs = 10e6  # Sampling frequency (10 MHz)
duration = 0.05  # Signal duration in seconds (10 ms)
t = np.linspace(0, duration, int(fs * duration), endpoint=False)

signal_frequency = 1.e3  # Signal frequency (1 kHz)
true_phase_offset = 0
laser_noise = np.cumsum(np.random.normal(0, 0.005, len(t)))
signal = np.cos(2 * np.pi * signal_frequency * t + true_phase_offset + laser_noise)

# PLL Parameters
Kp = 2.2
Ki = 8
alpha = 0.1  # Filter smoothing factor

# Initialize PLL variables
phase_est = 0
freq_est = 2 * np.pi * signal_frequency
integrator = 0
filtered_error = 0
phase_estimates = []

# PLL loop
for n in range(len(t)):
    # Generate reference signal
    ref_signal = np.cos(phase_est)
    
    # Phase detector
    phase_error = signal[n] * ref_signal
    
    # Apply low-pass filter
    filtered_error = alpha * phase_error + (1 - alpha) * (filtered_error if n > 0 else 0)
    
    # Loop filter (PI controller)
    integrator += filtered_error * (1 / fs)
    control_signal = Kp * filtered_error + Ki * integrator
    
    # Update phase estimate
    phase_est += (freq_est + control_signal) * (1 / fs)
    phase_estimates.append(phase_est)

# Convert phase estimates to radians and unwrap
phase_estimates = np.unwrap(phase_estimates)

# Plot results
plt.figure(figsize=(12, 8))
plt.plot(t, signal, label="Input Signal", alpha=0.6)
plt.plot(t, np.cos(phase_estimates), label="PLL Output (Cosine of Phase Estimate)", linestyle="--")
#plt.axhline(true_phase_offset, color="red", linestyle="--", label="True Phase Offset")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude / Phase (radians)")
plt.title("PLL Phase Tracking vs Input Signal")
plt.legend()
plt.grid(True)
plt.show()
