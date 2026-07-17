"""
utils/helpers.py
----------------
Utility functions for the noise budget framework.

Includes:
  - frequency grid construction
  - unit conversions (frequency noise <-> phase noise <-> displacement)
  - computation of LISA coupling coefficients from frequency plan
  - LISA requirement curves
"""

from __future__ import annotations

import numpy as np
from typing import Union, Dict

ArrayLike = Union[np.ndarray, float]

# Speed of light
C = 299792458.0  # m/s


# ---------------------------------------------------------------------------
# Frequency grid
# ---------------------------------------------------------------------------

def make_freq_array(
    f_min: float = 1e-4,
    f_max: float = 10.0,
    n_points: int = 2000,
) -> np.ndarray:
    """
    Return a log-spaced frequency array.

    Parameters
    ----------
    f_min : float   [Hz]
    f_max : float   [Hz]
    n_points : int

    Returns
    -------
    np.ndarray  shape (n_points,)
    """
    return np.logspace(np.log10(f_min), np.log10(f_max), n_points)


def make_freq_array_from_config(freq_config: dict) -> np.ndarray:
    """Construct frequency array from a FREQ_CONFIG dict."""
    return make_freq_array(
        f_min=freq_config["f_min"],
        f_max=freq_config["f_max"],
        n_points=freq_config["n_points"],
    )


# ---------------------------------------------------------------------------
# Unit conversions
# ---------------------------------------------------------------------------

def freq_noise_to_phase_noise_psd(
    S_freq: ArrayLike,
    f: ArrayLike,
) -> np.ndarray:
    """
    Convert frequency noise PSD to phase noise PSD.

        S_phase(f) = S_freq(f) / (2*pi*f)^2

    Parameters
    ----------
    S_freq : array_like
        Frequency noise PSD  [Hz^2/Hz].
    f : array_like
        Frequencies  [Hz].

    Returns
    -------
    np.ndarray
        Phase noise PSD  [rad^2/Hz].
    """
    f = np.asarray(f, dtype=float)
    S_freq = np.asarray(S_freq, dtype=float)
    return S_freq / (2.0 * np.pi * f) ** 2


def phase_noise_to_freq_noise_psd(
    S_phase: ArrayLike,
    f: ArrayLike,
) -> np.ndarray:
    """
    Convert phase noise PSD to frequency noise PSD.

        S_freq(f) = S_phase(f) * (2*pi*f)^2

    Parameters
    ----------
    S_phase : array_like   [rad^2/Hz]
    f : array_like         [Hz]

    Returns
    -------
    np.ndarray  [Hz^2/Hz]
    """
    f = np.asarray(f, dtype=float)
    S_phase = np.asarray(S_phase, dtype=float)
    return S_phase * (2.0 * np.pi * f) ** 2


def freq_noise_asd_to_displacement_asd(
    asd_freq: ArrayLike,
    f: ArrayLike,
    nu_laser: float = 281e12,
) -> np.ndarray:
    """
    Convert frequency noise ASD to displacement noise ASD.

        x_tilde(f) = nu_tilde(f) * c / (2*pi*f * nu_laser)
                   = nu_tilde(f) / f * (c / (2*pi * nu_laser))
                   = nu_tilde(f) / f * lambda / (2*pi)

    where lambda = c / nu_laser.

    Parameters
    ----------
    asd_freq : array_like
        Frequency noise ASD  [Hz/sqrt(Hz)].
    f : array_like
        Frequencies  [Hz].
    nu_laser : float
        Laser carrier frequency  [Hz].  Default 281 THz (~1064 nm).

    Returns
    -------
    np.ndarray
        Displacement ASD  [m/sqrt(Hz)].
    """
    f = np.asarray(f, dtype=float)
    asd_freq = np.asarray(asd_freq, dtype=float)
    lam = C / nu_laser
    return asd_freq / f * lam / (2.0 * np.pi)


def displacement_asd_to_freq_noise_asd(
    asd_disp: ArrayLike,
    f: ArrayLike,
    nu_laser: float = 281e12,
) -> np.ndarray:
    """
    Convert displacement ASD to frequency noise ASD  (inverse of above).

    Parameters
    ----------
    asd_disp : array_like   [m/sqrt(Hz)]
    f : array_like          [Hz]
    nu_laser : float        [Hz]

    Returns
    -------
    np.ndarray  [Hz/sqrt(Hz)]
    """
    f = np.asarray(f, dtype=float)
    asd_disp = np.asarray(asd_disp, dtype=float)
    lam = C / nu_laser
    return asd_disp * f * 2.0 * np.pi / lam


# ---------------------------------------------------------------------------
# Coupling coefficients from frequency plan
# ---------------------------------------------------------------------------

def compute_coupling_coefficients(freq_plan: dict) -> dict:
    """
    Compute the clock noise coupling coefficients alpha_ji and gamma_ji
    from the frequency plan.

    alpha_ji = Delta_nu_ji / f_sampling
    where Delta_nu_ji is the heterodyne beatnote frequency between
    spacecraft i and j (carrier-carrier).

    gamma_ji = (Delta_nu_ji + Delta_nu_m_ji) / f_sampling
    where Delta_nu_m_ji = nu_m_ij - nu_m_ji  is the sideband offset.

    Parameters
    ----------
    freq_plan : dict
        Must contain keys: 'f_pm_sampling', 'f_beat', 'f_mod'.

    Returns
    -------
    dict with keys 'alpha' and 'gamma', each a nested dict keyed by
    spacecraft pair strings e.g. 'SC1->SC2'.
    """
    f_s = freq_plan["f_pm_sampling"]
    f_beat = freq_plan["f_beat"]
    f_mod = freq_plan["f_mod"]

    spacecraft = list(f_beat.keys())
    alpha = {}
    gamma = {}

    for sc_recv in spacecraft:
        for sc_emit in spacecraft:
            if sc_recv == sc_emit:
                continue
            key = f"{sc_recv}<-{sc_emit}"

            # Carrier coupling coefficient
            delta_nu = f_beat[sc_recv]   # beatnote at receiving spacecraft
            alpha[key] = delta_nu / f_s

            # Sideband coupling coefficient
            delta_nu_m = f_mod[sc_emit] - f_mod[sc_recv]
            gamma[key] = (delta_nu + delta_nu_m) / f_s

    return {"alpha": alpha, "gamma": gamma}


# ---------------------------------------------------------------------------
# LISA requirement curves
# ---------------------------------------------------------------------------

def lisa_laser_noise_requirement(f: ArrayLike) -> np.ndarray:
    """
    LISA pre-stabilised laser frequency noise requirement.

    Approximately 30 Hz/sqrt(Hz) (white) in the LISA band.

    Returns ASD  [Hz/sqrt(Hz)].
    """
    f = np.asarray(f, dtype=float)
    return np.full_like(f, 30.0)


def lisa_secondary_noise_displacement(f: ArrayLike) -> np.ndarray:
    """
    LISA secondary noise requirement (approximate) as displacement ASD.

    This combines test-mass acceleration noise and OMS readout noise.
    A simplified model:

        S_x(f) = S_acc + S_oms

    with:
        S_acc^{1/2} = 3e-15 * sqrt(1 + (0.4e-3/f)^2) * (1/(2*pi*f)^2)  m/sqrt(Hz)
        S_oms^{1/2} = 1.5e-11 * sqrt(1 + (2e-3/f)^4)                    m/sqrt(Hz)

    Returns displacement ASD  [m/sqrt(Hz)].
    """
    f = np.asarray(f, dtype=float)
    f2 = (2.0 * np.pi * f) ** 2

    # Acceleration noise (converted to displacement)
    acc_asd = 3e-15 * np.sqrt(1.0 + (0.4e-3 / f) ** 2) / f2

    # OMS (optical metrology system) readout noise
    oms_asd = 1.5e-11 * np.sqrt(1.0 + (2e-3 / f) ** 4)

    return np.sqrt(acc_asd**2 + oms_asd**2)


def lisa_secondary_noise_freq(
    f: ArrayLike,
    nu_laser: float = 281e12,
) -> np.ndarray:
    """
    LISA secondary noise requirement converted to frequency noise ASD.

    Parameters
    ----------
    f : array_like
    nu_laser : float  [Hz]

    Returns
    -------
    np.ndarray  [Hz/sqrt(Hz)]
    """
    disp = lisa_secondary_noise_displacement(f)
    return displacement_asd_to_freq_noise_asd(disp, f, nu_laser=nu_laser)


# ---------------------------------------------------------------------------
# Convenience: PSD <-> ASD
# ---------------------------------------------------------------------------

def asd_to_psd(asd: ArrayLike) -> np.ndarray:
    """Square an ASD to get PSD."""
    return np.asarray(asd, dtype=float) ** 2


def psd_to_asd(psd: ArrayLike) -> np.ndarray:
    """Square-root a PSD to get ASD."""
    return np.sqrt(np.asarray(psd, dtype=float))
