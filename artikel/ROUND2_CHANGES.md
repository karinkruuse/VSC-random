# Round-2 article edits

The supplied review was treated as advice, not as an instruction to claim a completed TDI-2 migration. The article retains its static performance calculation. Purple Draft notes mark work requiring hardware facts, measurements, or a new analysis.

## Removed or condensed

- Original Fig. 5: the two-panel detector-noise breakdown was removed from the article; its PDF and other assets remain in the repository.
- Most of IV.B: removed the Bessel power breakdown, beat-current equation, individual current-noise equations, demodulated phase-ASD equation, voltage/headroom paragraph, detailed ADC-rate discussion, and LISA IRD allocation paragraph. Kept the optical operating point, peak beat currents, resulting ASDs, essential white-noise assumptions, and shared-detector cancellation explanation. Receiver parameters remain in the component-figure caption and saved figure metadata.
- Condensed the both-lasers-modulated caveat to a statement of which detection configuration the numbers describe.
- Original Fig. 2: removed the LISA clock/pilot-tone distribution figure and its long caption; retained a short description of the synthesis chains. The image file remains.
- Table I: removed the readout-ASD comparison row and the entire six-row block of LISA sources not reproduced in miniLISA. The omissions remain described in the measurement-model and design text.
- Removed the higher-order timing-times-laser-noise product paragraph from III.D; retained the physical-delay-jitter equations and delay-mismatch explanation.
- Removed the board-delay ASD equation from IV.D; retained the warning against double-counting board timing and added a note requesting a delay-error budget.
- Removed the speculative separate board-timing measurement/correction sentences from III.F; replaced them with a concrete request to identify the actual reference topology.
- Removed the four-independent-link ASD scaffolding, the four-unit-weight explanation, and the equal-arm sine-product aside from IV.C; retained the actual source/link propagation equations.
- Condensed GW firmware details to word widths and frequency resolution, removing the sign-extension explanation, numerical command range, and generic fidelity caveat. Added a concrete playback-validation note.
- Removed the optical-input paragraph about a forthcoming Moku measurement and fallback signal generator; measurement work remains in the conclusion and relevant notes.
- Condensed repeated modulation-frequency scaling explanations and repeated sensitivity disclaimers. Kept the main conditional-budget statement and the physical scaling explanation in the clock section.
- Folded the unquantified GW output equation into prose and requested a specified injection with an amplitude/recovery criterion.
- Removed the unverified ?negligible-arm-delay approximation? characterization of de Vine et al.; retained the short-optical-path description and reported suppression factors.

## Corrections and additions

- Added a descriptive draft title and abstract; left author identity explicitly unconfirmed.
- Reconciled the introduction with the static analysis and retained varying delays as an extension.
- Replaced nonexistent (a)/(b) figure references with upper/lower panel references; corrected reference oscillator to reference laser in the arm schematic caption.
- Added an explicit lower-sideband phase-sign convention when its signed electrical frequency is negative.
- Made common board timing a stated assumption rather than an undocumented hardware fact.
- Identified the sideband-difference estimator's source-noise assignment as an assumption, and requested an additive-channel alternative without claiming these are mathematical bounds.
- Added the raw 6.6 MHz clock coupling estimate (1.49e-5 cycles/sqrt(Hz) at 10 mHz), with a request for coherent propagation of shared clocks and an experimentally useful suppression margin.
- Explained the derivative of delayed phase and the specific missing-noise-scaling risk in the frequency-buffer implementation.
- Fixed Table I's stray capital ?Only?.
- Updated the frequency-planning bibliography entry to Physical Review D 110, 042002 (2024), DOI 10.1103/PhysRevD.110.042002.

## Deliberately pending

Purple notes request updated schematic artwork, actual board-reference wiring, clock and modulation measurements, delay-error/interpolation bounds, an orbit-consistent GW injection, and a validated varying-delay frequency plan and TDI-2 clock correction. Existing diagram assets were not redrawn from guessed hardware details. The Section II term-by-term algebra was retained because it supports the paper's measurement-model mapping.

The saved images/performance/figure_parameters.json already specifies 0.004 W per beam, the updated readout ASDs, shared pre-fanout detector channels, exclusion of ADC noise from that detector term, and a detector-difference PSD of 1.500080759384174e-16. This supports the updated configuration's provenance but is not an independent regeneration of the plotted curves; no curves were changed in this revision.

## Sources checked

- Published frequency-planning metadata: https://doi.org/10.1103/PhysRevD.110.042002
- Frequency-data Doppler weighting: https://arxiv.org/abs/2103.06976 (already cited in the article).

## Validation

Built artikel/ids-review-build/round2-review.pdf using pdfLaTeX and BibTeX. The review PDF includes visible editorial notes, so the review's proposed 11?12-page target is not a claimed result of these edits.
