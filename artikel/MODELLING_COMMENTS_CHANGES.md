# Modelling comments, 1 October 2026

Addressed the current inline comments, retaining the newer varying-delay model.

- Rewrote the opening around the noise calculation, without attributing modulation noise generically to optics.
- Removed the Laser and Clock Noise subsection and its two unused input-spectrum equations. Retained the scope statement about unmodelled delay-error residuals.
- Explicitly assigned the complete modulation estimator to direct source phase noise, with the timing term zero in this calculation.
- Replaced the flat detector-breakdown figure with a table generated from the existing saved figure parameters. Original image files remain.
- Qualified shared detector-phase noise by matched demodulation phase and tracking response; added a note to measure cross-spectra. Shared photocurrent alone is not proof of cancellation.
- Rewrote propagation around coherent physical-source transfer functions and the source cross-spectral matrix, with the existing Hartwig?Bayle citation.
- Moved numerical frequencies, the affine delay example, and the explicit corrected Michelson construction to noise_parameters.tex (appendix). Removed the four-unit-weight aside.
- Recorded the shared Rb board reference and explained common-mode suppression through TDI plus clock correction. Kept differential timing unquantified rather than inventing a correlation fraction.
- Added the requested 15 MHz timing conversion in prose: 3.38e-5 cycles/sqrt(Hz) at 10 mHz.

## Plot update pending original data

The script expects measured noises/baseline.csv and measured noises/modulator_psd.csv, which are absent. Files with the same names in miniLISA timining jitters fail the saved SHA256 checks even after CRLF normalization. The available modulation CSV is labelled PSD(Hz^2/Hz), whereas the saved plot configuration requires phase PSD. They were not substituted.

The figure script is prepared to add the Rb scale to the input plot, export the detector table, and exclude the independent-board scenario from the black component sum. Its original input-hash checks remain intact. The existing plotted assets were retained, and captions explicitly say that the black curve still includes the independent-board scenario. Once the original inputs are restored, rerun the script and update those pending captions. The existing output CSV also has a different schema from the current generator, so it was not used to reconstruct the figures.

## Checks

The ordered-delay validation passes: clock cancellation, first-order laser cancellation, static limit, noncommuting arms, shared-board residual equivalence, direct nested-delay evaluation, and epoch convergence. The figure script parses, and the table matches saved receiver values. Full figure regeneration is blocked by the missing original inputs.

Compiled review: ids-review-build/modelling-comments.pdf. No unresolved citation/reference warnings or overfull boxes in the checked build.
