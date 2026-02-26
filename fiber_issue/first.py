import numpy as np
import matplotlib.pyplot as plt

degrees = np.array([0, 20, 40, 60, 80, 100, 120, 140, 160, 180])
red_fiber = np.array([208, 181, 80, 66, 172, 218, 124, 51, 109, 208])
white_fiber = np.array([111, 119, 154, 161, 126, 108, 139, 164, 144, 110])

red_fiber = red_fiber - np.mean(red_fiber)
white_fiber = white_fiber - np.mean(white_fiber)

red_fiber = red_fiber/np.max(red_fiber)
white_fiber = white_fiber/np.max(white_fiber)

fiber_sum = red_fiber + white_fiber

# Plot 1: Red fiber
plt.figure()
plt.plot(degrees, red_fiber, color='red', label="OUT 2")
plt.plot(degrees, white_fiber, color='gray', label="OUT 1")

plt.xlabel("HWP roation (Degrees)")
plt.ylabel("Power (uW)")
plt.legend()
plt.grid(True)
plt.show()
