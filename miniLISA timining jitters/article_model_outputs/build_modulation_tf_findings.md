# Actual builder/evaluator comparison

Ran `build_modulation_tf.build_modulation_transfer_functions` unchanged with its defaults, writing a separate `audit_modulation_tf_X2.pkl` rather than overwriting a user cache. Then ran `run_modulation_tf.evaluate_modulation_asd` at 350 MHz on each spacecraft. The only evaluator override was redirecting its PSD loader to the existing local `miniLISA timining jitters/modulator_psd.csv`; its configured `measured noises` path is absent here.

## Result

The builder uses L = 8.3391023799538 s, dL = 5e-8 s/s, and electrical frequencies 15, 10.9 and 21.6 MHz. At 1 mHz its modulation amplitude transfer is 0.999999716 times the notebook's static equal-arm closed form at the same 350 MHz. Thus the default arm rate does not explain an orders-of-magnitude difference there. Close to transfer zeros, relative differences can be larger.

The evaluator loads the confirmed phase PSD and divides it by Fourier frequency squared in `S_modulation`. Consequently its `total_phase` is larger than the correctly propagated phase ASD by 1/f. Its `total_freq` then multiplies by f, undoing this division in amplitude. Both panels have phase-ASD labels although the variables claim different quantities.

| Fourier frequency | Propagated phase ASD / legacy left panel | Legacy right panel (`total_phase`) | Right/left |
|---|---:|---:|---:|
| 1 mHz | 4.39674e-8 | 4.39674e-5 | 1000 |
| 3 mHz | 1.23862e-7 | 4.12873e-5 | 333.333 |
| 10 mHz | 2.85463e-7 | 2.85463e-5 | 100 |

ASDs are numerical values for the same input and transfer; the correct phase ASD has units cycles/sqrt(Hz). The old right-panel values are incorrectly converted for the confirmed phase PSD.

The table uses the legacy loader's linear interpolation of PSD. The article notebook uses log-log interpolation, so pointwise numbers between measured bins differ slightly (for example, the notebook's 1 mHz result at 350 MHz is about 4.25122e-8). This interpolation difference is separate from the factor of 1000.

The notebook currently uses 35 MHz; the runner's default first curve is 350 MHz. Compare identical modulation settings: at fixed phase PSD a 35 MHz residual is ten times the 350 MHz residual.

## Required corrections if modernizing the legacy runner

1. Load the confirmed phase PSD directly, without dividing by f squared.
2. Plot `sqrt(sum(abs(H_i)**2 * S_phase_i))` as phase ASD.
3. If a frequency-ASD panel is wanted, multiply phase ASD by **2*pi*f**, with units Hz/sqrt(Hz).
4. Construct the displacement allocation in phase first; its current `omega**2` followed by division by f leaves an extra 2*pi in the nominal phase allocation.
5. Resolve data paths relative to the script and display the cached builder parameters. L, dL and electrical frequencies are frozen into the pickle; changing them requires rebuilding.

No original analysis scripts were edited. `build_modulation_tf_audit.csv` records the numerical builder comparison; `build_modulation_tf_audit.log` records the actual symbolic build.
