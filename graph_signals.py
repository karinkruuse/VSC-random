import numpy as np
import matplotlib.pyplot as plt

# Define parameters
fs = 1000  # Sampling frequency (Hz)
duration = 2  # seconds
t = np.linspace(0, duration, fs * duration, endpoint=False)

# Define frequencies
f1 = 14  # Hz
f2 = 20  # Hz
fdiff = abs(f2 - f1)  # Hz

# Generate sinusoids
y1 = 0.25 * np.sin(2 * np.pi * f1 * t)
y2 = 0.25 * np.sin(2 * np.pi * f2 * t)
y_diff = 0.25 * np.sin(2 * np.pi * fdiff * t)

# Define colors
colors = [(187/255, 24/255, 47/255),  # RGB normalized
          (236/255, 27/255, 47/255),
          (102/255, 121/255, 130/255)]

# Function to save waveform as transparent PNG
def save_waveform(y, filename, color):
    fig, ax = plt.subplots(figsize=(6, 2), dpi=300)
    ax.plot(t, y, color=color, linewidth=2)
    ax.set_xlim(t[0], t[-1])
    ax.set_ylim(-0.3, 0.3)
    ax.axis('off')
    fig.patch.set_alpha(0)  # Transparent figure background
    ax.set_frame_on(False)  # Remove frame
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Remove margins
    plt.savefig(filename, dpi=100, transparent=True)
    plt.close()

# Save the waveforms
save_waveform(y1, "sinusoid_f1.png", colors[0])
save_waveform(y2, "sinusoid_f2.png", colors[1])
save_waveform(y_diff, "sinusoid_fdiff.png", colors[2])
