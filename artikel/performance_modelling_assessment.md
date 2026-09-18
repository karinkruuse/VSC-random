# Material recovered for the performance section

Assessment date: 9 September 2026. Scope: all 11 notebooks and seven Python scripts in `miniLISA timining jitters`, the current article equations, the two local spectrum files, and selected measurement-generation and optical-budget scripts elsewhere in this workspace. This is a source audit, not a validated numerical performance prediction. Existing article and analysis files have not been changed.

## Main recommendation

There is enough useful machinery here to build the proposed section, but the existing plotted noise levels should not yet be used as publication results. The strongest reusable assets are the symbolic transfer-function engine, the measured modulation and delay-line spectra, and the separate optical readout models. The central result should initially be a **predicted secondary-noise floor assuming ideal laser and clock cancellation**, with explicit assumptions about the measurement-derived inputs. The folder does not yet establish a complete optical-testbed floor or a delay-accuracy requirement.

`main.tex` already includes `model.tex` immediately after the revised readout equations. `model.tex` is only a section outline. The revised equations in `main.tex` should be the authoritative model when rebuilding the budget.

## What to reuse

Paths below are relative to the workspace root.

| Asset | Useful content | Article role / qualification |
|---|---|---|
| `miniLISA timining jitters/plotting/tdi_core.py` | Symbolic carrier/sideband builders, X1/X2 combinations, clock correction, source-by-source transfer extraction | Best starting engine; reconcile signs, units and topology, then verify cancellation before use |
| `miniLISA timining jitters/plotting/plottingX2.py` | Noise inputs, per-source PSD propagation, quadrature totals and comparison curves | Workflow template; input conventions and comparison normalization require repair |
| `miniLISA timining jitters/plotting/build_modulation_tf.py` and `run_modulation_tf.py` | Separate expensive symbolic derivation from inexpensive modulation-frequency scans | Good architecture for the optional MHz/GHz figure; present implementation holds the input spectrum fixed |
| `miniLISA timining jitters/modulator_psd.csv` | 305,176 rows, two columns; first positive frequency about 61.0 microHz, last 18.6264 Hz | Measured modulation estimator, subject to the units/provenance issue below |
| `miniLISA timining jitters/baseline.csv` | 186,265 rows, two columns; first positive frequency about 0.100 mHz, last 18.6264 Hz; labelled cycles/sqrt(Hz) | Measured electronic-chain residual; establish its mapping to a final link readout before using it as b |
| `miniLISA timining jitters/modelling w plots.ipynb` | Static-arm transfer-function exploration and two embedded images | Historical diagnostics, not an audited final budget |
| `miniLISA timining jitters/miniLISA_TDI_modelling 2 arms.ipynb` | Two-arm symbolic construction | Relevant topology, but saved output includes `KeyError (2, 3)` in the reference-correction branch |
| `miniLISA timining jitters/miniLISA_TDI_modelling copy.ipynb` | Carrier/sideband and reference-based board correction exploration | Useful derivation history; reference correction requires channels actually present in the experiment |
| `miniLISA timining jitters/modelling TDI2.ipynb` and `miniLISA_TDI2.ipynb` | Time-varying delay compositions; latter adds reference-modulation and board-correction branches | Defer flexing-arm conclusions; not needed for the first static budget |
| `miniLISA timining jitters/modelling_w_ref_mod.ipynb` | Explicit shared reference-modulation model | Important architecture cross-check because the article says the reference laser is also modulated |
| `miniLISA timining jitters/modelling.ipynb`, `modelling copy.ipynb`, `modelling copy 2.ipynb`, `modelling topology 2.ipynb`, `miniLISA_TDI_modelling crazy.ipynb` | Alternative noise-sharing and sign/topology conventions | Keep as derivation history rather than merge their conclusions; `modelling copy.ipynb` also contains a saved missing-link error |
| `SB Noise Budgeting/miniLISA_sideband_noise_budget.py`, `noise_formulas.py`, `PM_readoutnoise_update.py`, `SB_readout_noise.ipynb` | More detailed optical/electronic readout modelling | Better starting material for the component readout panel than the simple optical placeholder in the TDI plotting script |

The optical-budget folder has four detector-specific TOML configurations under `conf`. Select the configuration for the actual detector and operating powers. Its sideband signal expression uses `sqrt(P_sb * P_REF)`; check how this maps to the article's sideband–sideband beat with a modulated reference before importing numerical values.

## Issues that materially affect the prediction

### 1. Modulation PSD units are inconsistent

The local CSV header says `PSD(Hz^2/Hz)`. However, `modulation_noise/proper_3signal.py` computes `PM` from `theta_m_cyc = 0.5*(phiU_dt - phiL_dt)` and contains a commented two-column export with exactly this header. `proper_3signal copy.py` actively exports the same phase-derived quantity, plus two diagnostic columns, under frequency-PSD headers. This is strong evidence of a misleading header, but it does not by itself prove which run generated the local two-column file.

`plottingX2.py:S_modulation` and `run_modulation_tf.py:S_modulation` divide the imported PSD by f². `from_meas.py` instead takes its square root directly as phase ASD. Those interpretations cannot both be correct.

For phase in cycles and frequency fluctuation in Hz, differentiation gives S_frequency = (2 pi f)² S_phase. Thus:

- If the file contains the phase-derived PM, use it directly as a phase PSD.
- If it truly contains frequency PSD, divide by (2 pi f)², not f², to obtain phase PSD in cycles²/Hz.

Under the phase-PSD interpretation, the current extra division by f² inflates the input phase ASD by 1/f, numerically a factor 1,000 at 1 mHz. This can change both the apparent dominant noise and the MHz/GHz conclusion. Recover the generating run or reproduce the export before quoting levels.

The sideband-difference estimator also contains differential readout noise. It constrains an equivalent modulation measurement; it is not automatically the intrinsic noise of one EOM. Establish which modulators/reference paths contribute and whether readout noise is negligible, subtracted, or retained as a measured upper estimate. Do not then add that same readout contribution again.

### 2. The electronic baseline is a processed residual

`DL Baseline/analysis_w_debug.py` exports `asd_tdi` to `baseline.csv`; `pretty_plot.py` also exports a residual constructed from a delayed phase difference and a timing correction. The exact originating run of the copied file remains unverified, but these exports show why the name alone is insufficient to identify a single-board or single-link noise PSD.

Before assigning this curve independently to every carrier and sideband b, document the measurement combination, delay, timing correction, operating frequencies/powers and included readouts. Derive the transfer from underlying electronics to that measured residual, or explicitly justify using the residual as a phenomenological final-readout estimate. Do not divide by sqrt(2) without a demonstrated two-equal-independent-source model. Do not count the measured residual and all of its constituent ADC, phasemeter or timing noises twice.

### 3. Reconcile the revised measurement equations with the engine

The article uses r = (sideband - carrier)/nu_m and sideband modulation D m_j - m_i. The core uses r = (carrier - sideband)/omega_m and sideband modulation m_i - D m_j. An opposite definition of r is permissible if the correction changes consistently; it is not independently evidence of a failed correction. Likewise, reversing the whole modulation transfer leaves an isolated independent modulation PSD unchanged, but matters for source conventions and cross-correlations.

Use frequencies in Hz, phase in cycles and timing errors in seconds throughout the article implementation. Distinguish the remote electrical input frequency nu_R,j in board coupling from the signed final carrier beat alpha_ij. The current engine obtains both from its spacecraft frequency symbols, which embeds a particular relation between them.

Retain the same b variable in carrier TDI and in r. The core already reuses its per-readout noise symbols before extracting transfer functions: preserve this useful feature when combining optical and electronic contributions into b. For X_corr = sum(P eta + K r), the carrier coefficient is P - K/nu_m and the sideband coefficient is K/nu_m under the article convention. Square the complete carrier coefficient, not its two pieces separately.

The shared reference-modulation branches require explicit reconciliation with the simplified article equations. Determine whether the hardware removes those terms, they can be absorbed into the stated noise variables with their correlations retained, or additional terms are needed. Do not import a reference-assisted jitter-cancellation result into a two-arm model that lacks its reference channels.

### 4. Timing spectra and readout models are assumptions

`plottingX2.py` assigns both clock and board spectra the same `4e-27/f` law. No measurement file or calibration is attached to these functions. Do not call this a measured board-jitter bound. The distinction between timing PSD and fractional-frequency PSD must also be explicit before interpreting the conversions in the evaluator.

Its `S_optical` is a single analytic curve scaled by a frequency ratio, rather than a shot/RIN/detector/ADC calculation at the article's operating point. Recover those components from the dedicated optical-budget work. Carrier and sideband powers generally require separate readout estimates.

### 5. Static X2 normalization and the comparison curve

The plotting script says static X2 reduces to X1 exactly. Algebraically, its own path polynomials instead give X2 = -(1 - A B) X1 for static delays, with A = D12 D21 and B = D13 D31. This additional filter affects every noise and signal curve and must also appear in any comparison.

For the implemented equal-arm static X2, four equal independent additive link phase PSDs give a total factor 64 sin²(2 pi f L) sin²(4 pi f L). Thus a displacement allocation x_ASD corresponds to phase ASD sqrt(factor) * x_ASD/lambda for this specific independent-link comparison. The current allocation code additionally multiplies the PSD by omega² and then divides its ASD by f for its phase panel, leaving an extra 2 pi relative to this phase convention. Rebuild the comparison directly in the chosen observable.

The 1 pm and 15 pm curves in these scripts are displacement allocations, not a complete LISA sensitivity including all noise sources and GW response. Label them accordingly unless a full matched comparison is constructed.

Use static delays first. `dL = 5e-8` is an assumed arm rate, not a ranging error. Setting time to zero after deriving time-varying delays does not by itself establish a stationary transfer-function description for a flexing-arm experiment.

### 6. Reproducibility repairs

The plotting scripts look for `../../measured noises/...`; the recovered CSVs are instead in the parent `miniLISA timining jitters` directory. Resolve inputs relative to the script and record their provenance. `from_meas.py` expects four modulation columns, whereas this local file has two. The cached modulation transfer pickle is not present in the plotting folder and must be regenerated.

The interpolation routines extend spectra using endpoint values outside the measured band. Avoid presenting this as measured coverage. Restrict the central result to a justified band or explicitly label extrapolation. First nonzero Fourier bins do not establish reliable performance at the low-frequency edge; averaging and detrending need to be reported.

There is also a `(3,2)` optical-noise dictionary entry mapped to `N3_3/n3_3` in the core. It does not affect the four-link Michelson, but should be corrected before using all six links.

## Proposed article figures

1. **Component characterization:** measured delay-line residual and modulation estimator in separate panels, plus calculated carrier/sideband readout contributions. Include operating conditions, estimator definitions, units, averaging and useful measurement band. Existing measurement scripts supply the first two; the dedicated optical budget supplies the third.
2. **Central corrected-Michelson budget:** combined additive b, modulation m, and total secondary floor. Include board jitter only with a defensible spectrum/bound and consistent treatment of what is already in the baseline. State ideal laser/clock cancellation when processing residuals are omitted. Use a matched displacement allocation or fully specified LISA comparison.
3. **Delay-error sensitivity:** not yet delivered by this folder. Perturb processing delays while retaining the physical measurement delays; propagate the assumed laser-frequency spectrum through the actual combination. Include the shared reference laser as one physical source, since effective laser noises are correlated. Choose delay errors that bracket the secondary floor; derive the requirement from that crossing rather than a generic link estimate.
4. **Optical locking:** no lock-performance dataset or figure was identified in the timing-jitter folder. Obtain residual/tracking evidence from the locking work. Establish where the residual enters the measurement before assigning it an irreducible secondary-noise contribution.
5. **Optional modulation-frequency scan:** reuse the cached-transfer workflow after fixing units. Compare fixed direct phase noise with fixed timing noise, normalized to the same measurement at its actual modulation frequency. The present 350 MHz/2 GHz scan is a scenario, not evidence that 350 MHz was the measured operating point. Specify sideband powers/readout noise for both cases.

## Suggested opening for model.tex

“We estimate the secondary-noise floor of the optical testbed by propagating component noise spectra through a clock-corrected Michelson observable. We use static propagation delays and constant nominal beat-note and modulation frequencies. Each physical noise source is retained consistently in the carrier measurement and in the sideband-derived clock correction before its transfer function is evaluated. Measured electronic and modulation spectra provide empirical inputs, while optical readout noise is calculated for the chosen operating point. The resulting estimate assumes ideal cancellation of laser and measurement-clock noise; residuals from imperfect delay knowledge are considered separately.”

Use this as the section's methodological opening once the stated calculation has been implemented. Follow with the source/parameter table, the corrected-observable definition, component characterization, the central budget, and the delay-error study. Do not yet add a numerical sensitivity or dominant-noise claim.

## Validation needed for a numerical result

Before generating the central figure, demonstrate algebraic laser and clock cancellation for unequal static delays; verify X2's static filtering relative to X1; and check the complex transfer of one reused carrier-noise source with a sinusoidal injection through both science and correction paths. These checks address the specific risks above. Then trace the two CSVs to their source runs, select the actual operating configuration, and recompute the budget in one phase convention.

The existing clock-correction literature reference can be anchored to [Hartwig and Bayle, Physical Review D 103, 123027 (2021)](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.103.123027). Its published subject is clock-jitter reduction in TDI; the local code's equation-number attribution still needs checking against the precise source it used. The code audit above is based on the local implementation, not on assuming that attribution validates it.
