import numpy as np
from scipy.fft import fft, ifft, fftfreq
import matplotlib.pyplot as plt

T = 0.0001

t = np.arange(0, 0.5*np.pi, T)
f = 25
signal = np.sin(2*np.pi*f*t)

#signal2 = 2*np.sin(2*np.pi*f*t)

#signal[signal > 0] = 1
#signal[signal < 0] = 0


#noise_L = np.random.normal(0, 0.3, N)
#L = np.sin(f*t + noise_L)
#noise_L2 = np.random.normal(0, 1, N)
#L2 = np.sin(f*t + noise_L2)

fc = 50
carrier = np.sin(2*np.pi*fc*t + signal)
#carrier2 = np.sin(2*np.pi*fc*t + signal2)

plt.plot(t, signal)
plt.plot(t, carrier)

plt.show()



N = len(t)
x = np.linspace(0.0, N*T, N, endpoint=False)

yf = fft(carrier)
#yf2 = fft(carrier2)
xf = fftfreq(N, T)[:N//2]
plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
#plt.plot(xf, 2.0/N * np.abs(yf2[0:N//2]))
plt.grid()
plt.show()