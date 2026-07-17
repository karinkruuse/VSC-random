"""
noise_sources/base.py
---------------------
Base class and concrete implementations for noise sources.

All PSDs are in units of  (Hz/sqrt(Hz))^2 = Hz^2/Hz  i.e. one-sided
frequency noise power spectral density.

ASDs (amplitude spectral densities) are in Hz/sqrt(Hz).

Convention throughout:
  - psd(f)  returns the one-sided PSD  S(f)  [Hz^2/Hz]
  - asd(f)  returns sqrt(S(f))              [Hz/sqrt(Hz)]
"""

from __future__ import annotations

import numpy as np
from abc import ABC, abstractmethod
from typing import Union, Optional
import warnings


ArrayLike = Union[np.ndarray, float]


class NoiseSource(ABC):
    """
    Abstract base class for all noise sources.

    Subclasses must implement `psd(f)`.

    Parameters
    ----------
    name : str
        Human-readable label used in plots and summaries.
    unit : str
        Unit string, default 'Hz/sqrt(Hz)'.  Currently informational only.
    """

    def __init__(self, name: str, unit: str = "Hz/sqrt(Hz)"):
        self.name = name
        self.unit = unit

    @abstractmethod
    def psd(self, f: ArrayLike) -> np.ndarray:
        """
        One-sided power spectral density  S(f)  [Hz^2/Hz].

        Parameters
        ----------
        f : array_like
            Frequency array [Hz].  Must be positive.

        Returns
        -------
        np.ndarray
            PSD values, same shape as f.
        """

    def asd(self, f: ArrayLike) -> np.ndarray:
        """Amplitude spectral density sqrt(S(f))  [Hz/sqrt(Hz)]."""
        return np.sqrt(self.psd(f))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


# ---------------------------------------------------------------------------
# Analytic noise sources
# ---------------------------------------------------------------------------

class PowerLawNoise(NoiseSource):
    """
    Single power-law noise:

        S(f) = amplitude^2 * (f / f_ref)^exponent

    Examples
    --------
    White frequency noise (flat ASD):
        PowerLawNoise("white", amplitude=30.0, exponent=0)

    1/f frequency noise (ASD ~ 1/sqrt(f)):
        PowerLawNoise("1/f", amplitude=1e-3, exponent=-1)

    Parameters
    ----------
    name : str
    amplitude : float
        ASD value at f = f_ref  [Hz/sqrt(Hz)].
    exponent : float
        Spectral index of the PSD.  0 = white, -1 = 1/f, +2 = f^2 etc.
    f_ref : float
        Reference frequency [Hz].  Default 1.0 Hz.
    """

    def __init__(
        self,
        name: str,
        amplitude: float,
        exponent: float = 0.0,
        f_ref: float = 1.0,
    ):
        super().__init__(name)
        self.amplitude = amplitude
        self.exponent = exponent
        self.f_ref = f_ref

    def psd(self, f: ArrayLike) -> np.ndarray:
        f = np.asarray(f, dtype=float)
        return self.amplitude**2 * (f / self.f_ref) ** self.exponent


class SumNoise(NoiseSource):
    """
    Incoherent sum of multiple noise sources (quadrature sum of PSDs).

    Useful for modelling a noise floor that has both a white and a 1/f
    component, for example.

    Parameters
    ----------
    name : str
    components : list of NoiseSource
    """

    def __init__(self, name: str, components: list[NoiseSource]):
        super().__init__(name)
        self.components = components

    def psd(self, f: ArrayLike) -> np.ndarray:
        f = np.asarray(f, dtype=float)
        return sum(src.psd(f) for src in self.components)


class AnalyticNoise(NoiseSource):
    """
    Noise defined by an arbitrary callable  S(f).

    Parameters
    ----------
    name : str
    func : callable
        Function f -> S(f) where S is the one-sided PSD [Hz^2/Hz].
    """

    def __init__(self, name: str, func):
        super().__init__(name)
        self._func = func

    def psd(self, f: ArrayLike) -> np.ndarray:
        f = np.asarray(f, dtype=float)
        return np.asarray(self._func(f), dtype=float)


class LisaLaserNoise(NoiseSource):
    """
    Approximate LISA pre-stabilised laser frequency noise model.

        S(f) = S0 * [1 + (f_knee / f)^2]

    with S0 chosen to give ~30 Hz/sqrt(Hz) at high frequency and
    a 1/f rise below f_knee.

    Parameters
    ----------
    name : str
    asd_white : float
        High-frequency (white) ASD level  [Hz/sqrt(Hz)].  Default 30.0.
    f_knee : float
        Corner frequency below which noise rises as 1/f  [Hz].
    """

    def __init__(
        self,
        name: str = "LISA laser noise",
        asd_white: float = 30.0,
        f_knee: float = 2e-3,
    ):
        super().__init__(name)
        self.asd_white = asd_white
        self.f_knee = f_knee

    def psd(self, f: ArrayLike) -> np.ndarray:
        f = np.asarray(f, dtype=float)
        return self.asd_white**2 * (1.0 + (self.f_knee / f) ** 2)


class ClockNoise(NoiseSource):
    """
    USO / clock fractional frequency noise model.

    The fractional frequency noise y(t) = dν/ν has an Allan deviation
    sigma_y(tau).  We convert to frequency noise ASD via:

        S_freq(f) = (nu_carrier)^2 * S_y(f)

    A simple two-component model:
        S_y(f) = h0/2 * (white) + h_m1 / f  (flicker)

    Allan deviation at 1 s:  sigma_y(1) ≈ sqrt(h0 / 2)  for white FM.

    Parameters
    ----------
    name : str
    nu_carrier : float
        Carrier frequency [Hz] that the clock drives (e.g. 10e6 for USO).
    sigma_y_1s : float
        Allan deviation at 1 s averaging time.  Default 1e-13 (LISA USO spec).
    f_flicker : float
        Knee frequency below which flicker noise dominates  [Hz].
    """

    def __init__(
        self,
        name: str = "USO clock noise",
        nu_carrier: float = 10e6,
        sigma_y_1s: float = 1e-13,
        f_flicker: float = 1e-3,
    ):
        super().__init__(name)
        self.nu_carrier = nu_carrier
        self.sigma_y_1s = sigma_y_1s
        self.f_flicker = f_flicker

    def psd(self, f: ArrayLike) -> np.ndarray:
        f = np.asarray(f, dtype=float)
        # white FM: h0 ~ 2 * sigma_y^2
        h0 = 2.0 * self.sigma_y_1s**2
        # fractional frequency noise PSD
        S_y = h0 / 2.0 * (1.0 + (self.f_flicker / f))
        # convert to frequency noise [Hz^2/Hz]
        return self.nu_carrier**2 * S_y


# ---------------------------------------------------------------------------
# Measured noise source  (Stage 4 — stubbed here for interface completeness)
# ---------------------------------------------------------------------------

class MeasuredNoise(NoiseSource):
    """
    Noise source defined by interpolating a measured spectrum.

    The input can be an ASD or PSD; specify with `input_type`.

    Parameters
    ----------
    name : str
    frequencies : array_like
        Frequency array of the measurement  [Hz].
    values : array_like
        Measured ASD [Hz/sqrt(Hz)] or PSD [Hz^2/Hz] values.
    input_type : {'asd', 'psd'}
        Whether `values` is an ASD or PSD.
    interpolation : {'log', 'linear'}
        Interpolation method.  Log-log interpolation is usually better
        for noise spectra.
    extrapolation : {'edge', 'nan', 'zero'}
        Behaviour outside the measured frequency range.
        'edge' repeats the edge value; 'nan' returns NaN; 'zero' returns 0.
    """

    def __init__(
        self,
        name: str,
        frequencies: ArrayLike,
        values: ArrayLike,
        input_type: str = "asd",
        interpolation: str = "log",
        extrapolation: str = "edge",
    ):
        super().__init__(name)
        self._f_meas = np.asarray(frequencies, dtype=float)
        values = np.asarray(values, dtype=float)

        if input_type == "asd":
            self._psd_meas = values**2
        elif input_type == "psd":
            self._psd_meas = values
        else:
            raise ValueError(f"input_type must be 'asd' or 'psd', got '{input_type}'")

        if interpolation not in ("log", "linear"):
            raise ValueError("interpolation must be 'log' or 'linear'")
        self._interp = interpolation

        if extrapolation not in ("edge", "nan", "zero"):
            raise ValueError("extrapolation must be 'edge', 'nan', or 'zero'")
        self._extrap = extrapolation

        # Pre-sort by frequency
        sort_idx = np.argsort(self._f_meas)
        self._f_meas = self._f_meas[sort_idx]
        self._psd_meas = self._psd_meas[sort_idx]

    def psd(self, f: ArrayLike) -> np.ndarray:
        f = np.asarray(f, dtype=float)

        if self._interp == "log":
            log_psd = np.interp(
                np.log10(f),
                np.log10(self._f_meas),
                np.log10(self._psd_meas),
                left=np.nan,
                right=np.nan,
            )
            result = 10.0**log_psd
        else:
            result = np.interp(
                f,
                self._f_meas,
                self._psd_meas,
                left=np.nan,
                right=np.nan,
            )

        # Handle extrapolation
        out_of_range = np.isnan(result)
        if np.any(out_of_range):
            if self._extrap == "edge":
                below = f < self._f_meas[0]
                above = f > self._f_meas[-1]
                result[below] = self._psd_meas[0]
                result[above] = self._psd_meas[-1]
            elif self._extrap == "zero":
                result[out_of_range] = 0.0
            elif self._extrap == "nan":
                pass  # leave as NaN
            else:
                warnings.warn(
                    f"MeasuredNoise '{self.name}': some frequencies are outside "
                    f"the measured range [{self._f_meas[0]:.2e}, {self._f_meas[-1]:.2e}] Hz. "
                    f"Using extrapolation='{self._extrap}'."
                )

        return result

    @classmethod
    def from_csv(
        cls,
        name: str,
        filepath: str,
        freq_col: int = 0,
        value_col: int = 1,
        input_type: str = "asd",
        skiprows: int = 0,
        delimiter: str = ",",
        **kwargs,
    ) -> "MeasuredNoise":
        """
        Load a measured spectrum from a CSV file.

        Parameters
        ----------
        filepath : str
            Path to CSV file.
        freq_col : int
            Column index for frequencies.
        value_col : int
            Column index for ASD or PSD values.
        input_type : str
            'asd' or 'psd'.
        skiprows : int
            Number of header rows to skip.
        delimiter : str
            Column delimiter.
        """
        data = np.loadtxt(
            filepath,
            delimiter=delimiter,
            skiprows=skiprows,
        )
        frequencies = data[:, freq_col]
        values = data[:, value_col]
        return cls(name, frequencies, values, input_type=input_type, **kwargs)
