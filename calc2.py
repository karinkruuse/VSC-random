import numpy as np
import matplotlib.pyplot as plt

# Parameters
fs = 10000  # Sampling frequency (Hz)
duration = 1.0  # Duration of the signal (s)
t = np.linspace(0, duration, int(fs * duration), endpoint=False)  # Time array

# Frequencies of the sinusoids
f1 = 50  # Frequency of the first sinusoid (Hz)
f2 = 55  # Frequency of the second sinusoid (Hz)

# Time delay (in seconds)
delay = 0.08  # 10 ms

# Generate the sinusoids
signal1 = np.exp(1j*2 * np.pi * f1 * t)
signal2 = np.exp(1j*2 * np.pi * f2 * t)
signal22 = np.exp(1j*2 * np.pi * f2 * (t - delay))

# Combine the signals to form a "beatnote"
temp = signal1 + signal2
beatnote = np.real(temp) ** 2 + np.imag(temp) ** 2
temp = signal1 + signal22
delayed_beatnote = np.real(temp) ** 2 + np.imag(temp) ** 2

# Plot the signals
plt.figure(figsize=(12, 6))

# Plot the first sinusoid
plt.subplot(4, 1, 1)
plt.plot(t, signal1, label=f"Signal 1 (f = {f1} Hz)")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.title("Signal 1")
plt.legend()

# Plot the delayed second sinusoid
plt.subplot(4, 1, 2)
plt.plot(t, signal2, label=f"Signal 2 (f = {f2} Hz, delayed by {delay} s)")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.title("Signal 2")
plt.legend()

# Plot the combined beatnote
plt.subplot(4, 1, 3)
plt.plot(t, beatnote, label="Beatnote")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.title("Combined Beatnote")
plt.legend()

# Plot the combined beatnote
plt.subplot(4, 1, 3)
plt.plot(t, delayed_beatnote, label="Beatnote")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.title("Combined Beatnote")
plt.legend()

plt.tight_layout()
plt.show()
