from scipy.optimize import least_squares
import numpy as np

P1 = np.array([214, 219, 238, 247, 243, 205, 142, 81.6, 54.9, 72.8,
               126, 187, 229, 232, 193, 131, 76, 52.6, 69, 121])
P2 = np.array([253, 245, 236, 230, 233, 255, 296, 330, 341, 323,
               289, 248, 222, 222, 247, 286, 320, 333, 318, 286])
degrees = np.array([244, 245, 250, 255, 260, 270, 280, 290, 300, 310,
                    320, 330, 340, 350, 360, 370, 380, 390, 400, 410])
theta = np.deg2rad(degrees)

S = P1 + P2

# fit the sum as:  S(theta) = A + B*cos(4*theta + phase)
# A = mean, B = amplitude, pdl = 2B/A (approximately)
def model(p, th):
    A, B, phase = p
    return A + B * np.cos(4*th + phase)

def resid(p):
    return model(p, theta) - S

p0 = [S.mean(), (S.max()-S.min())/2, 0.0]
res = least_squares(resid, p0)
A, B, phase = res.x

print(f"Sum mean (A):      {A:.2f} uW")
print(f"Sum amplitude (B): {B:.2f} uW")
print(f"PDL from sum fit:  {2*abs(B)/A:.4f}")
print(f"True sum max:      {A+abs(B):.2f} uW")
print(f"True sum min:      {A-abs(B):.2f} uW")