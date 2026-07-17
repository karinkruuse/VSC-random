"""
transfer_functions/base.py
--------------------------
Transfer function classes.

A transfer function H maps an input noise PSD to an output PSD:

    S_out(f) = |H(f)|^2 * S_in(f)

For PSD propagation we only need |H(f)|^2 (the power transfer function).
The complex H(f) is also available for cases where you need to combine
correlated noise sources properly (e.g. TDI combinations), but Stage 1
uses only the power transfer.

All transfer functions expose:
    .power_tf(f)   ->  |H(f)|^2   (dimensionless or with units)
    .apply(noise_source, f)  ->  output PSD array

Units note:
    A dimensionless gain just scales the PSD.
    A coupling coefficient with units [1/Hz] would convert clock phase
    noise to frequency noise, for example.  The units are tracked via
    the `input_unit` and `output_unit` attributes (informational only).
"""

from __future__ import annotations

import numpy as np
from abc import ABC, abstractmethod
from typing import Union, Callable

from noise_sources import NoiseSource

ArrayLike = Union[np.ndarray, float]


class TransferFunction(ABC):
    """
    Abstract base class for transfer functions.

    Parameters
    ----------
    name : str
    input_unit : str
        Unit of the input noise (informational).
    output_unit : str
        Unit of the output noise (informational).
    """

    def __init__(
        self,
        name: str,
        input_unit: str = "Hz/sqrt(Hz)",
        output_unit: str = "Hz/sqrt(Hz)",
    ):
        self.name = name
        self.input_unit = input_unit
        self.output_unit = output_unit

    @abstractmethod
    def power_tf(self, f: ArrayLike) -> np.ndarray:
        """
        Power transfer function  |H(f)|^2.

        Parameters
        ----------
        f : array_like  [Hz]

        Returns
        -------
        np.ndarray  — same shape as f, dimensionless (or with units^2)
        """

    def apply(self, noise: NoiseSource, f: ArrayLike) -> np.ndarray:
        """
        Apply this transfer function to a noise source.

        Returns the output PSD  S_out(f) = |H(f)|^2 * S_in(f).

        Parameters
        ----------
        noise : NoiseSource
        f : array_like  [Hz]

        Returns
        -------
        np.ndarray  — output PSD
        """
        f = np.asarray(f, dtype=float)
        return self.power_tf(f) * noise.psd(f)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


# ---------------------------------------------------------------------------
# Concrete transfer functions
# ---------------------------------------------------------------------------

class Unity(TransferFunction):
    """
    Identity transfer function:  |H|^2 = 1.

    Use when a noise source couples directly into the output with no
    modification (e.g. phasemeter readout noise at the output node).
    """

    def __init__(self, name: str = "unity"):
        super().__init__(name)

    def power_tf(self, f: ArrayLike) -> np.ndarray:
        return np.ones_like(np.asarray(f, dtype=float))


class Gain(TransferFunction):
    """
    Constant (frequency-independent) gain:  |H(f)|^2 = gain^2.

    Parameters
    ----------
    gain : float
        Linear gain amplitude.  The power TF is gain^2.
    """

    def __init__(self, name: str, gain: float):
        super().__init__(name)
        self.gain = gain

    def power_tf(self, f: ArrayLike) -> np.ndarray:
        f = np.asarray(f, dtype=float)
        return np.full_like(f, self.gain**2)


class FrequencyDependentGain(TransferFunction):
    """
    Gain defined by an arbitrary callable  g(f).

    |H(f)|^2 = g(f)^2

    Parameters
    ----------
    func : callable
        f -> g(f), where g is the amplitude gain (not power).
    """

    def __init__(self, name: str, func: Callable):
        super().__init__(name)
        self._func = func

    def power_tf(self, f: ArrayLike) -> np.ndarray:
        f = np.asarray(f, dtype=float)
        return np.asarray(self._func(f), dtype=float) ** 2


class FreqToPhase(TransferFunction):
    """
    Convert frequency noise to phase noise:  H(f) = 1 / (2*pi*f)

    |H(f)|^2 = 1 / (2*pi*f)^2

    Input:  frequency noise ASD  [Hz/sqrt(Hz)]  -> PSD [Hz^2/Hz]
    Output: phase noise ASD      [rad/sqrt(Hz)] -> PSD [rad^2/Hz]
    """

    def __init__(self, name: str = "freq_to_phase"):
        super().__init__(name, input_unit="Hz/sqrt(Hz)", output_unit="rad/sqrt(Hz)")

    def power_tf(self, f: ArrayLike) -> np.ndarray:
        f = np.asarray(f, dtype=float)
        return 1.0 / (2.0 * np.pi * f) ** 2


class PhaseToFreq(TransferFunction):
    """
    Convert phase noise to frequency noise:  H(f) = 2*pi*f

    |H(f)|^2 = (2*pi*f)^2

    Input:  phase noise PSD  [rad^2/Hz]
    Output: frequency noise PSD [Hz^2/Hz]
    """

    def __init__(self, name: str = "phase_to_freq"):
        super().__init__(name, input_unit="rad/sqrt(Hz)", output_unit="Hz/sqrt(Hz)")

    def power_tf(self, f: ArrayLike) -> np.ndarray:
        f = np.asarray(f, dtype=float)
        return (2.0 * np.pi * f) ** 2


class DelayPowerTF(TransferFunction):
    """
    Power transfer function of a pure time delay:  |e^{-2*pi*i*f*tau}|^2 = 1.

    A pure delay does not change the PSD magnitude, so this is equivalent
    to Unity.  Included explicitly for clarity when building signal chains,
    and because it becomes non-trivial in TDI combinations (Stage 3).

    Parameters
    ----------
    tau : float
        One-way delay  [s].
    """

    def __init__(self, name: str, tau: float):
        super().__init__(name)
        self.tau = tau

    def power_tf(self, f: ArrayLike) -> np.ndarray:
        return np.ones_like(np.asarray(f, dtype=float))


class TDILaserSuppression(TransferFunction):
    """
    Approximate power transfer function of a first-generation TDI X
    combination for laser frequency noise suppression.

    For equal arms (tau_1 = tau_2 = tau) the analytic result is:

        |H_TDI(f)|^2 = 16 * sin^2(pi*f*tau) * sin^2(2*pi*f*tau)

    This is zero at f = n / tau  (TDI nulls) and reaches a maximum
    of 16 between nulls.

    For unequal arms (tau_1 != tau_2) an approximate expression is used.

    This transfer function applies to the *laser noise* input to give the
    *residual laser noise* after TDI.

    Note: this is the Stage 1 placeholder.  A full treatment accounting
    for time-varying delays and second-generation TDI is in Stage 3.

    Parameters
    ----------
    tau1 : float
        One-way delay on arm 1  [s].
    tau2 : float
        One-way delay on arm 2  [s].
    """

    def __init__(self, name: str = "TDI_X_laser", tau1: float = 8.3, tau2: float = 8.3):
        super().__init__(name)
        self.tau1 = tau1
        self.tau2 = tau2

    def power_tf(self, f: ArrayLike) -> np.ndarray:
        f = np.asarray(f, dtype=float)
        tau1, tau2 = self.tau1, self.tau2
        # Equal-arm approximation if arms are close
        if np.isclose(tau1, tau2):
            tau = (tau1 + tau2) / 2.0
            return 16.0 * np.sin(np.pi * f * tau) ** 2 * np.sin(2.0 * np.pi * f * tau) ** 2
        else:
            # Unequal arms: approximate as product of two sinc-like factors
            # This is indicative only; exact expression depends on the
            # full TDI combination (see Stage 3).
            s1 = 2.0 * np.sin(np.pi * f * tau1)
            s2 = 2.0 * np.sin(np.pi * f * tau2)
            return (s1 * s2) ** 2


class ClockCouplingTF(TransferFunction):
    """
    Transfer function for clock (USO) noise coupling into the carrier
    phasemeter readout.

    From the LISA measurement model (eq. 3 in the paper draft):

        phi_out = ... - alpha_ji * q_i(t) + ...

    where  alpha_ji = Delta_nu_ji / f_sampling

    This TF is just a constant gain  |H|^2 = alpha_ji^2,
    converting clock frequency noise into beatnote phase noise.

    Parameters
    ----------
    delta_nu : float
        Heterodyne beatnote frequency  [Hz].
    f_sampling : float
        Phasemeter sampling frequency  [Hz].
    """

    def __init__(self, name: str, delta_nu: float, f_sampling: float):
        super().__init__(
            name,
            input_unit="fractional freq noise",
            output_unit="phase noise [rad/sqrt(Hz)]",
        )
        self.delta_nu = delta_nu
        self.f_sampling = f_sampling
        self.alpha = delta_nu / f_sampling

    def power_tf(self, f: ArrayLike) -> np.ndarray:
        f = np.asarray(f, dtype=float)
        return np.full_like(f, self.alpha**2)


class ChainedTF(TransferFunction):
    """
    Sequential composition of multiple transfer functions:

        |H_total|^2 = |H_1|^2 * |H_2|^2 * ...

    Parameters
    ----------
    name : str
    stages : list of TransferFunction
    """

    def __init__(self, name: str, stages: list[TransferFunction]):
        super().__init__(name)
        self.stages = stages

    def power_tf(self, f: ArrayLike) -> np.ndarray:
        f = np.asarray(f, dtype=float)
        result = np.ones_like(f)
        for stage in self.stages:
            result *= stage.power_tf(f)
        return result
