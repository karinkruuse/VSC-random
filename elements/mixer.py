import numpy as np
from scipy.fft import fft, ifft, fftfreq
import matplotlib.pyplot as plt

T = 0.005

t = np.arange(0, 100*np.pi, T)
f = 25
signal = np.sin(2*np.pi*f*t)

fLO = 10
signalLO = np.sin(2*np.pi*fLO*t)

N = len(t)
noise = np.random.normal(0, 1, N)


input = signal + signalLO + noise
output = input.clip(0, 10)

in_spec = 2.0/N*fft(input)[1:N//2]
out_spec = 2.0/N*fft(output)[1:N//2]

xf = fftfreq(N, T)[1:N//2]


plt.plot(xf, in_spec, color="gray", linewidth=2)
plt.plot(xf, out_spec, zorder=10)


axes = plt.gca()
bottom, top = axes.get_ylim()
plt.vlines(f, bottom, top, color="grey", linestyles="--")
plt.vlines(fLO, bottom, top, color="grey", linestyles="--")
plt.vlines(f-fLO, bottom, top, color="black", linestyles="--")
plt.vlines(f+fLO, bottom, top, color="black", linestyles="--")

plt.grid()

plt.show()