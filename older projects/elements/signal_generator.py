"""
elements/signal_generator.py

LaserSignal: models a heterodyne laser beam with EOM phase modulation and
clock noise, as used in LISA phasemeter simulations.

Signal model
------------
The total phase of the laser field is:

    phi(t) = 2*pi * f_carrier * t
           + beta * sin(2*pi * f_mod * (t + q(t)))    # EOM sidebands, clock-jitter shifted
           + phi_laser(t)                              # free-running laser phase noise

where:
    beta        = mod_depth  [rad peak]
    q(t)        = clock timing error  [s]  (integrated white timing jitter)
    phi_laser(t) = integrated laser frequency noise  [rad]  (1/f^2 phase PSD)

The complex analytic signal returned by get_signal() is:

    s(t) = exp(j * phi(t))

i.e. unit-amplitude phasor — amplitude noise is not modelled here.
"""

import numpy as np
from scipy.constants import c


_DEFAULT_FREQ_NOISE_SQRT = 30.0      # free-running laser frequency noise ASD [Hz/sqrt(Hz)]


class LaserSignal:
    """
    Simulated laser signal with EOM phase modulation and optional clock noise.

    Typical usage
    -------------
        laser = LaserSignal.from_duration("SC1", wavelength=wl, duration=1000.0, dT=1/fADC)
        laser.generate_signal(mod_depth=0.1, f_mod=2.2e6, clock_noise_amplitude=1e-13)

        signal, t = laser.get_signal()        # complex phasor,         shape (N,)
        noise,  t = laser.get_laser_noise()   # laser phase noise [rad], shape (N,)
        q,      t = laser.get_clock_jitter()  # clock timing error [s],  shape (N,)
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def __init__(self, name: str, wavelength: float, N: int, dT: float):
        self.name = name
        self.wavelength = wavelength
        self.N = N
        self.dT = dT
        self.fADC = 1.0 / dT
        self.f_carrier = c / wavelength

        self._t = np.arange(N) * dT

        # Filled by generate_signal()
        self._signal       = None   # complex phasor  e^{j*phi(t)}
        self._laser_noise  = None   # phi_laser(t)  [rad]
        self._clock_jitter = None   # q(t)          [s]

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------
    @classmethod
    def from_duration(cls,
                      name: str,
                      wavelength: float,
                      duration: float,
                      dT: float) -> "LaserSignal":
        """
        Construct from total duration instead of sample count.

        Parameters
        ----------
        name       : label string (e.g. "SC1")
        wavelength : carrier wavelength [m]
        duration   : total signal length [s]
        dT         : sample interval [s]  (= 1/fADC)
        """
        N = int(np.round(duration / dT))
        return cls(name, wavelength, N, dT)

    # ------------------------------------------------------------------
    # Signal generation
    # ------------------------------------------------------------------
    def generate_signal(self,
                        mod_depth: float = 0.1,
                        f_mod: float = 1e6,
                        clock_noise_amplitude: float = 0.0,
                        laser_freq_noise_sqrt: float = _DEFAULT_FREQ_NOISE_SQRT,
                        seed: int = None):
        """
        Generate all internal signal buffers.

        Parameters
        ----------
        mod_depth             : EOM modulation depth beta [rad peak]
        f_mod                 : EOM / clock sideband frequency [Hz]
        clock_noise_amplitude : clock timing noise ASD [s/sqrt(Hz)].
                                Set to 0 to disable clock noise entirely.
        laser_freq_noise_sqrt : laser frequency noise ASD [Hz/sqrt(Hz)]
        seed                  : optional RNG seed for reproducibility
        """
        rng = np.random.default_rng(seed)
        t   = self._t
        N   = self.N
        dT  = self.dT

        # ----------------------------------------------------------
        # 1. Clock timing jitter  q(t)  [s]
        # ----------------------------------------------------------
        # White timing noise: ASD = clock_noise_amplitude [s/sqrt(Hz)].
        # Per-sample sigma: clock_noise_amplitude * sqrt(fADC).
        if clock_noise_amplitude > 0.0:
            sigma_sample = clock_noise_amplitude * np.sqrt(self.fADC)
            q = rng.normal(0.0, sigma_sample, N)
        else:
            q = np.zeros(N)

        self._clock_jitter = q

        # ----------------------------------------------------------
        # 2. Laser phase noise  phi_laser(t)  [rad]
        # ----------------------------------------------------------
        # S_nu(f) = laser_freq_noise_sqrt^2  [Hz^2/Hz]  (white frequency noise)
        # => S_phi(f) = (2*pi)^2 * laser_freq_noise_sqrt^2 / f^2  [rad^2/Hz]
        # Shape in frequency domain, then IFFT.
        freqs = np.fft.rfftfreq(N, d=dT)

        # Avoid DC divergence
        freqs_safe = freqs.copy()
        freqs_safe[0] = freqs[1]

        # Phase noise ASD [rad/sqrt(Hz)]
        S_phi_amp = (2.0 * np.pi * laser_freq_noise_sqrt) / freqs_safe
        S_phi_amp[0] = S_phi_amp[1]

        # White complex noise in frequency domain scaled to physical PSD
        noise_fft = (rng.normal(0.0, 1.0, len(freqs)) +
                     1j * rng.normal(0.0, 1.0, len(freqs)))
        noise_fft *= S_phi_amp * np.sqrt(self.fADC / 2.0)

        phi_laser = np.fft.irfft(noise_fft, n=N)
        self._laser_noise = phi_laser

        # ----------------------------------------------------------
        # 3. Assemble total phase and build complex phasor
        # ----------------------------------------------------------
        # EOM argument includes clock jitter: f_mod * (t + q(t))
        phi_mod   = mod_depth * np.sin(2.0 * np.pi * f_mod * (t + q))
        phi_total = 2.0 * np.pi * self.f_carrier * t + phi_mod + phi_laser

        self._signal = np.exp(1j * phi_total)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    def _check_generated(self):
        if self._signal is None:
            raise RuntimeError(
                f"[LaserSignal '{self.name}'] Call generate_signal() before accessing data."
            )

    def get_signal(self):
        """
        Return the complex analytic laser signal and time array.

        Returns
        -------
        signal : ndarray, complex, shape (N,)  –  exp(j * phi_total(t))
        t      : ndarray, float,   shape (N,)  –  time axis [s]
        """
        self._check_generated()
        return self._signal.copy(), self._t.copy()

    def get_laser_noise(self):
        """
        Return the laser phase noise contribution and time array.

        Returns
        -------
        phi_laser : ndarray, float, shape (N,)  –  laser phase noise [rad]
        t         : ndarray, float, shape (N,)  –  time axis [s]
        """
        self._check_generated()
        return self._laser_noise.copy(), self._t.copy()

    def get_clock_jitter(self):
        """
        Return the clock timing error and time array.

        Returns
        -------
        q : ndarray, float, shape (N,)  –  clock timing error [s]
        t : ndarray, float, shape (N,)  –  time axis [s]
        """
        self._check_generated()
        return self._clock_jitter.copy(), self._t.copy()
