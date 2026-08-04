import numpy as np

def R_from_F(F):
    """
    Equal-mirror reflectivity R for a lossless symmetric Fabry–Pérot
    given finesse F (intensity-based reflectivity).
    Formula: F = π*sqrt(R)/(1 - R)
             => sqrt(R) = (2F)/(sqrt(π^2 + 4F**2) + π)
             => R = [ ... ]^2
    """
    F = float(F)
    if F <= 0:
        raise ValueError("Finesse must be positive.")
    root = np.sqrt(np.pi**2 + 4*F**2)
    x = (2*F) / (root + np.pi)          # x = sqrt(R)
    return x**2

def F_from_R(R):
    """
    Finesse for equal mirrors, given intensity reflectivity R in (0,1).
    """
    R = float(R)
    if not (0 < R < 1):
        raise ValueError("R must be in (0, 1).")
    return np.pi*np.sqrt(R)/(1 - R)

# Example
if __name__ == "__main__":
    F = 8000.0
    R = R_from_F(F)
    F_back = F_from_R(R)
    print(f"F = {F:.6f}  ->  R = {R:.9f}  ->  F_back = {F_back:.6f}")
