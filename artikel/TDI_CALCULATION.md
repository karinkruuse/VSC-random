# What changed in the TDI calculation

The figure export now uses `tdi_component_model.py`, based on the ordered Michelson paths in `miniLISA timining jitters/miniLISA_TDI2.ipynb` and `plotting/plottingX2.py`. The original modelling files have not been edited.

## Changing arms

The example uses a one-way delay of 8.33910238 s at the middle of the calculation. Arm 12 grows at 5 × 10⁻⁸ s/s and arm 13 shrinks at the same rate; the reverse links use their respective arm's delay. The delay changes by ±2.16 ms between the midpoint and either end of a one-day interval.

Each link delay is evaluated at the time reached after all preceding delays. The code keeps the exact nested affine times. The original plotting example assigned identical delays and rates to every arm, which makes the paths commute; the opposite rates here avoid that degeneracy.

The path coefficients are the phase-domain version of Eq. (28) in [Hartwig and Bayle](https://arxiv.org/html/2005.02430v4). The phase-domain delay has no multiplicative delay-rate factor. A hardware implementation that stores frequency must include that factor when differentiating the delayed phase; this calculation assumes the intended phase response rather than emulating the present firmware.

## Clock correction

For this three-laser model, the nominal beat frequencies are constant and opposite in the two link directions. Consequently, the round-trip clock term is removed by

```text
corrected round trip = eta_1j + D_1j eta_j1 - alpha_1j r_1j.
```

Applying the ordered X2 paths to these corrected round trips cancels the spacecraft clock terms exactly in this reduced model. This replaces the previous static P/K weighting. It does not claim the same simple correction works for LISA's complete reference-interferometer model or for changing beat-frequency coefficients. The phase convention is the article's `r = (sideband - carrier) / remote modulation frequency`.

The spacecraft clock model is now the LISA fractional-frequency PSD 4 × 10⁻²⁷/f. The Rb extrapolation is used only for board timing. Its spectrum follows `clock_noise/USO_phse_noise.py`: −130 dBc/Hz at 10 Hz on a 10 MHz reference, then phase-PSD slopes −1 to 1 Hz, −2 to 10 mHz, and −3 below. The plotted example treats different boards as independent and applies no additional board-timing correction. Actual correlations can change this contribution.

## Meaning of the plotted spectra

For each physical source, the code sums its delayed appearances coherently before squaring the response. It evaluates that response at 25 epochs spanning one day, then averages the local powers. This is an adiabatic component-spectrum estimate for slowly varying delays, not an exact stationary PSD or a full time-domain orbital simulation. It includes retarded delay ordering and the changing delay values, but not the long-term redistribution of spectral power by time warping.

The source groups are shared detector inputs, source modulation, electronic link readouts, and independent board timing. The detector calculation excludes ADC quantization from the propagated detector term because the measured electronic baseline already represents the electronic chain. The sum omits current delay-implementation residuals and the product of delay jitter with laser-frequency fluctuations.

The input modulation estimator is provisionally assigned to source modulation noise. A repeat measurement may change that assignment. Similarly, separating the timing-corrected baseline from the assumed board term is a modelling assumption, not a new measurement.

## Checks

`validate()` checks that:

- The spacecraft clock terms cancel algebraically before any spectral calculation.
- The remote laser terms cancel. The remaining local-laser paths have the same delay through first order in arbitrary, unequal arm rates.
- The first-generation paths do not have that cancellation for unequal rates.
- Zero arm rates recover the standard equal-arm X2 noise gain.
- The chosen growing and shrinking arms have noncommuting delays.
- A clock fluctuation shared by all boards leaves only the same higher-order path residual as laser noise.

The numerical checks also compare ordered path responses with direct sinusoidal evaluation and check convergence of the local-power average. Regenerate with `python artikel/make_component_figure.py`. Parameters and source gains are saved beside the figures for reproducibility.
