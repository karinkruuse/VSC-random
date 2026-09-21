# PSD calculations in the article

This note explains and checks the spectral calculations in `model.tex`, the measurement equations in `main.tex` and `IDS.tex`, and `make_component_figure.py`. It describes the current performance model, not a measurement of the assembled testbed. The historical `old.tex` uses a different, first-generation example and is discussed at the end.

## 1. Spectral convention and units

All phase fluctuations are in **cycles**. For Fourier frequency `f > 0`, a one-sided phase power spectral density (PSD) `S_phi(f)` has units cycles²/Hz; its amplitude spectral density (ASD) is `A_phi(f) = sqrt(S_phi(f))`, in cycles/√Hz. Independent noises add as PSDs, so their ASDs add in quadrature. Correlated noises need cross spectra.

For phase `phi` in cycles, frequency fluctuation is `delta_nu = d phi/dt`. Consequently,

```text
S_delta_nu(f) = (2 pi f)^2 S_phi(f),
A_phi(f) = A_delta_nu(f)/(2 pi f).
```

For a timing error `q` in seconds and nominal frequency `nu` in Hz, the induced phase is `nu q`, with `S_phi = nu² S_q`. Its fractional-frequency error is `dq/dt`. Radian phase ASDs equal `2 pi` times cycle phase ASDs. A phase PSD must **not** be divided by `f²` merely because its CSV header mentions Hz.

For any linear delayed combination, a delay `d` has Fourier transfer `z = exp(-2 pi i f d)`. If physical noise sources `n_a` are independent, `S_out = sum_a |T_a|² S_a`. More generally, `S_out = T S_n T†`, where `S_n` includes cross spectra. One source reused in two measurements must first have its complex coefficients combined, then squared.

## 2. Measured modulation spectrum

The estimator in `model.tex` is `m_hat = (phi_U - phi_L)/2`. Opposite modulation-phase signs in upper and lower sidebands cancel their common optical phase. In `modulation_noise/proper_3signal.py`, the code forms precisely this **phase in cycles**, then calls SciPy `welch` with a Hann window, 50% overlap, `scaling="density"`, and no further segment detrending after phase preprocessing. Thus that calculation produces a phase PSD, cycles²/Hz. A nearby commented export labels it `PSD(Hz^2/Hz)`; that header conflicts with the calculated quantity. The exact run that produced the figure input has not been established.

The article takes the square root of the imported modulation PSD. That is correct **if** the file is the phase-derived estimator. If a supplied file is instead a frequency-noise PSD, it must first be divided by `(2 pi f)²`. The estimator includes differential sideband readout noise; it is not automatically the intrinsic noise of one modulator. The article assigns its PSD to each of three independent spacecraft sources as a modelling assumption. This may count readout noise twice when a separate readout budget is added.

The model writes `m_i = nu_i^m N_i + N_i^m`, where `N_i` is timing noise (seconds) and `N_i^m` is direct modulation phase noise (cycles). The measurement at one modulation frequency constrains the combination, not its two parts. In the clock variable, `m_i/nu_i^m = N_i + N_i^m/nu_i^m`: raising modulation frequency suppresses a **fixed direct phase** term, but not a **fixed timing** term. A frequency-scaling prediction requires an assumption about which term dominates and about whether the underlying hardware noise changes.

## 3. Measured electronic baseline

The likely generating scripts in `DL Baseline` form a delayed phase difference with a timing correction, then use SciPy `welch` and export `sqrt(PSD)` in cycles/√Hz. For example, `pretty_plot.py` computes `tdi = ch1_phase_d - ch3_phase_d - ch3_freq_dly*(tj_d - tj_dly_d)` and exports the ASD of its detrended residual. This is already a **combination** of channels, not the PSD of a single board or individual final-link readout.

`make_component_figure.py` plots the baseline's second column directly, consistent with an ASD. The performance model then provisionally assigns its *squared* value as the PSD of each independent carrier and sideband additive readout. That mapping is not derived from the baseline measurement transfer function, and the source run and included electronics are unverified. It is consequently a conditional proxy. If the baseline already contains ADC, phasemeter, timing, or sideband readout noise, adding the same physical noise again overestimates the total. Conversely, a residual can suppress some underlying noises, so using it as an individual-link bound is not guaranteed conservative.

## 4. Single-link comparison spectrum

`model.tex` defines the following *comparison*, converted from displacement to phase with `lambda = 1064 nm`:

```text
A_OMS = (15 pm/√Hz)/lambda * sqrt[1 + (2 mHz/f)^4]
A_acc = (3 fm s^-2/√Hz)/[(2 pi f)^2 lambda]
        * sqrt[1 + (0.4 mHz/f)^2] * sqrt[1 + (f/8 mHz)^4]
A_link = sqrt(A_OMS^2 + A_acc^2).
```

Acceleration ASD becomes displacement ASD after division by `(2 pi f)²`; division by wavelength then gives cycles/√Hz. The quadrature sum presumes independent OMS and acceleration terms. Acceleration is a reference allocation here, not a test-mass noise measured in this testbed. In the component plot these curves are *unfiltered input scales*; in the final budget the same equivalent link PSD is propagated through the TDI transfer.

## 5. Predicted optical and electronic readout PSDs

The optical calculation assumes one modulated and one unmodulated beam, each at `8 mW` at the detector, modulation index `beta = 0.53`, responsivity `R = 0.6 A/W`, and heterodyne efficiency `eta = 0.9`. For carrier (`n = 0`) or first sideband (`|n| = 1`), the peak beat current is

```text
I_n,pk = 2 R sqrt(eta P_SC P_ref) |J_n(beta)|.
```

Using `J_0 = 0.9310` and `J_1 = 0.2558` gives about `8.48 mA` and `2.33 mA`. The sideband therefore has a larger equivalent phase noise for the same additive current noise.

The assumed one-sided current ASDs are

```text
i_shot = sqrt[2 e (R(P_SC + P_ref) + I_dark)]
i_J    = sqrt(4 k_B T/R_load)
i_RIN  = R(P_SC + P_ref) A_RIN
i_ADC  = V_FS/[2^bits G sqrt(6 f_s)].
```

The last expression follows from uniform quantization error with step `V_FS/2^bits`, variance `step²/12`, and one-sided white density `step²/(6 f_s)`, referred to input current through gain `G`. The RIN formula assumes a coherent sum of the beams' intensity fluctuations at the relevant RF beat; it is a deliberately strong assumption, not a measured RF RIN spectrum. Dark-current shot noise is included in `i_shot`. The values used are `I_dark = 100 nA`, `T = 300 K`, `R_load = 50 ohm`, `A_RIN = 0.9e-8/√Hz`, `G = 50 V/A`, `V_FS = 1 V`, `bits = 14`, and `f_s = 2 GHz`.

For current noise white around the beat and ordinary demodulation, both RF sidebands contribute, so each current ASD becomes a cycle-phase ASD `A_phi,n^(k) = sqrt(2) i_k/(2 pi I_n,pk)`. Squaring and summing the independent contributions yields the stored totals:

| Beat | Shot + dark | Johnson | RIN | ADC | Quadrature total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Carrier | 1.472e-9 | 4.832e-10 | 2.294e-9 | 2.958e-10 | 2.784e-9 |
| First sideband | 5.359e-9 | 1.759e-9 | 8.347e-9 | 1.077e-9 | 1.013e-8 |

All entries are cycles/√Hz and come from `images/performance/figure_parameters.json`. The quadrature totals and the `J_0/|J_1| ≈ 3.64` carrier-to-sideband ratio are internally consistent. The corresponding radian ASDs are about `17.5` and `63.7 nrad/√Hz`. These estimates assume ideal white quantization, no clipping, and applicable white RF noise; they are not measured effective readout spectra. A setup where **both** beams are modulated has different beat amplitudes and needs recalculation.

## 6. Clock variable, TDI, and final PSD

With the receiving spacecraft indexed first, `main.tex` defines `r_ij = (eta_ij^sb,+ - eta_ij)/nu_j^m`, in seconds. Subtracting the displayed sideband and carrier equations gives

```text
r_ij = D_ij q_j - q_i
     + (D_ij m_j - m_i)/nu_j^m
     + (1-D_ij) epsilon_i
     + (b_ij^sb,+ - b_ij^c)/nu_j^m.
```

The signs and units in this subtraction check out, including the board term: its sideband-minus-carrier coefficient is `nu_j^m(1-D_ij) epsilon_i`. The common GW phase cancels under the article's common-carrier-and-sideband GW approximation.

Set `z_ij = exp(-2 pi i f d_ij)`, `A = z_12 z_21`, and `B = z_13 z_31`. The article's static Michelson is

```text
X = (1-A)(eta_13 + z_13 eta_31)
  - (1-B)(eta_12 + z_12 eta_21).
```

Its link weights are `P_13 = 1-A`, `P_31 = z_13(1-A)`, `P_12 = -(1-B)`, and `P_21 = -z_12(1-B)`. Clock-correction weights `K_ij` multiply the `r_ij` variables and are selected so the three `q_i` coefficients vanish. The static second-generation convention in the performance calculation is `X_2c = (1-AB) X_c`; the extra filter applies to science, correction, noise, and signal alike. This is a static-delay identity and does not establish performance for flexing arms.

Since the **same** carrier readout `b_ij^c` enters `eta_ij` and `r_ij`, its first-generation transfer is `T_c,ij = P_ij - K_ij/nu_j^m`; the sideband readout transfer is `T_sb,ij = K_ij/nu_j^m`. Multiply both by `(1-AB)` for this `X_2c`. The correct readout PSD is obtained from `|T_c,ij|² S_c,ij + |T_sb,ij|² S_sb,ij`, summing independent links, with a covariance treatment if any physical paths are shared. Squaring `P` and `K/nu` separately for one reused carrier would omit their cross term. The common reference laser must likewise be treated as one physical source; ideal laser cancellation is algebraic and does not require independent effective laser noises.

The figure exporter combines the already-propagated ASD columns from `conditional_budget.csv` as

```text
A_electronic = hypot(A_carrier_baseline, A_sideband_baseline)
A_readout    = hypot(A_Newport_carrier, A_Newport_sideband)
A_total      = sqrt(A_electronic² + A_modulation² + A_readout²).
```

This is valid only for independent *physical* contributions after their individual coherent transfer functions have been applied. Its reference is four independent equivalent link phase noises, each with `A_link`; it is not the unfiltered single-link curve. For equal arm delay `L`, the link weights above with the additional `(1-AB)` filter give `sum_links |T_link|² = 64 sin²(2 pi f L) sin²(4 pi f L)`. Hence `A_reference,X2 = 8 |sin(2 pi f L) sin(4 pi f L)| A_link`. This checks the normalization of the independent-link reference under the stated convention. Transfer nulls also suppress a GW signal and cannot alone be interpreted as better sensitivity.

## 7. What was checked and what remains conditional

- The phase/frequency conversion, clock-variable subtraction, readout quadrature totals, and equal-arm independent-link transfer factor are consistent with the article's stated conventions.
- The current calculation now reads `measured noises/baseline.csv` and the **first PSD column** of `measured noises/modulator_psd.csv` directly. The baseline file labels its second column as cycles/√Hz; the four-column modulation file labels its PSD columns as cycles²/Hz. The other two modulation PSD columns are diagnostic differences and are not added to the budget. The selected modulation file's first positive bin is about 0.244 mHz, so the recalculated plotted band starts at 0.25 mHz and ends at 1 Hz, entirely inside the measured support.
- The notebook `miniLISA timining jitters/article_performance_model.ipynb` regenerated `article_model_outputs/conditional_budget.csv` and its assumptions from those inputs; `artikel/make_component_figure.py` then regenerated the component and total figures. The recorded input paths and SHA-256 hashes in `images/performance/figure_parameters.json` identify this new calculation. The earlier figure inputs were not byte-identical to these files, so the new figures are a recalculation, not a recovery of the earlier numerical curves.
- The modulation CSV's historical `Hz²/Hz` header conflicts with the phase-estimator code. Recovering the exact export run is needed before treating that interpretation as certain.
- The baseline-to-independent-readout mapping, possible overlap between measured estimator noise and predicted readout noise, and RF RIN/ADC assumptions remain the main limitations of the final budget. The model also omits a separately measured board-timing contribution and residuals from delay, synchronization, and interpolation errors.
- `old.tex` contains a historical `X_1` calculation with a `24 MHz` modulation example and a 1 pm allocation. Its readout-difference PSD correctly includes the `-2 Re(S_sb,c)` cross term, but its numerical figure and conclusions should not be combined with the current `35 MHz`, static `X_2c` budget without recalculation under common inputs.

## 8. Audit of `modulation_noise/proper_3signal.py`

The raw recording is `modulation_noise/data/EOM_PLL_20260224_160232.npy`. Its companion header identifies input 1 as carrier, input 2 as lower sideband, and input 3 as upper sideband, with an acquisition rate of about 37.2529 Hz. The retained samples are uniformly spaced at about 0.0268435 s. The analysis removes the final 720 s. The modulation estimate is `0.5 * (upper phase - lower phase)` **after** applying the same linear detrend to each phase channel. Since detrending is linear, this is equivalent to detrending the half-difference directly. The observed half-difference has no large sample jumps in the retained data; its maximum one-sample change is about 0.00273 cycles. Thus the factor of one half and the use of phase rather than frequency samples are correct for the stated sideband-sign convention.

`proper_3signal.py` uses one-sided Welch density with a Hann window and 50% overlap. Its default segment duration is 16,384 s, yielding a first positive bin near 0.061 mHz. The available `measured noises/modulator_psd.csv` was generated using the **4,096 s** segment setting in `proper_3signal copy.py`, yielding a first positive bin near 0.244 mHz. These are both valid PSD estimates with different frequency resolution and averaging. I recalculated the 4,096 s estimator directly from the raw recording: its first PSD column matches the article's selected CSV across 0.25 mHz–1 Hz, including the value about `5.6803e-9 cycles²/Hz` at the nearest bin to 1 mHz. No numerical correction to the article's modulation input is needed.

The script did have two presentation and maintenance problems: a commented export called the phase PSD `Hz²/Hz`, and the data path depended on the shell's working directory. These were corrected. The requirement curve is in radians/√Hz and is divided by `2π` before plotting alongside cycle-phase ASDs; the script's comment now states that correctly and omits the singular DC point. The active export header in `proper_3signal copy.py` was also corrected to cycles²/Hz. None of these changes alters the already-used modulation CSV or the article figures.
