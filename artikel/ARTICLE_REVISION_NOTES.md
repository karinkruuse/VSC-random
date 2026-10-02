## Final update: shared-reference model and build fixes

This update supersedes the older pending-work and independent-board conclusions below.

- Restored the supplied `intro(1).tex` verbatim as `intro.tex`.
- Removed the entire Table I block headed "LISA sources not reproduced in miniLISA".
- Removed the Rb-standard input curve and its spectrum modelling discussion.
- Removed the independent full-oscillator board-jitter curve from the final plot and recomputed the included component sum.
- Removed redundant concluding prose about modulation improvements.
- Defined acronyms directly in the preamble using `\newacro`; rebuilt the bibliography and cross-references.

The board model separates shared timing from differential timing. Symbolic validation confirms the shared term has the laser-residual delay polynomial, with the expected frequency coefficient. Differential timing is assumed negligible, not measured to be zero. Laser-noise coupling from delay errors and imperfect delay implementation remain excluded and are identified in the text.

The final plot uses the archived electronic, modulation, detector and reference vector curves. Original measurement CSVs are absent; `rebuild_saved_component_plot.py` interpolates saved vertices in log coordinates and sums PSDs. The appendix discloses this precision limitation. The original SVG and metadata are retained in `images/performance/archive`; new metadata records provenance and its SHA256. No substitute measurements were used. `make_component_figure.py` is updated for regeneration when the original inputs are restored.

The conclusion is that electronics dominate the included sum over most of the band, with detector noise well below it. Differential timing must be checked experimentally before this becomes a complete hardware budget; TDI response minima do not establish strain sensitivity.

Validation: model cancellation and delay-ordering checks passed. The rebuilt PDF was visually checked for first-use acronym expansions and numbered citations. Bibliography generation succeeds.

---
Historical revision notes follow.

# Formal style revision and noise-section analysis

## Entry point

The revisions are incorporated into `main.tex`, which reads the revised section files and appendix. The temporary review entry point and its build artifacts have been removed.

Compiled article: `main.pdf`.

## Style and structure

Used the three user-supplied files in `previous writing` as writing examples. Retained their progression from physical mechanism to equation to interpretation, while removing conversational asides and using formal scientific prose. The examples' equations and numerical claims were not imported into the article.

Reworked the introduction, measurement-model explanations, design discussion, abstract, noise section and overall conclusion. Preserved the existing measurement equations and notation. The introduction now leads directly to unequal-arm noise cancellation, clock transfer and the purpose of the experiment. The design prose follows the signal path. The noise section explains what enters the calculation, how it is propagated and what the result implies.

## Latest comments addressed

- Replaced the Noise Contributions opening with the requested measured/calculated inputs and the OMS-plus-acceleration comparison.
- Removed the detailed readout conversion equation, breakdown table and receiver-component discussion from the article. Kept only approximate carrier and sideband totals (3e-9 and 1e-8 cycles/sqrt(Hz)); the underlying calculation and table assets remain available.
- Explained that the modulation measurement already contains readout noise and that separately adding a detector estimate can double-count a small contribution. Did not present the sum as independent measurements of every source.
- Explained propagation in terms of the noise terms in the carrier/sideband eta variables and their complete transfer functions. No algorithm implementation narrative was added.
- Replaced the unexplained epoch-averaging language with a physical description. Moved the exact averaging interval and explicit static-limit checks into the appendix and reran the model validation.
- Added the analytic Rb timing scale at 15 MHz to the input figure and removed the beam-power annotation. Because the original raw inputs are missing, this is a vector overlay on the archived figure, not regenerated measured data. The archived curve PDF remains unchanged. The overlay script checks its SHA256 before using the saved axis coordinates.

## Conclusion drawn from the final noise plot

The detector curve is well below the electronic and modulation curves. Among contributions based on measurements, electronics exceed the modulation estimate over most of the plotted band. Improving modulation alone would therefore leave an electronic limitation under the current assumptions.

The independent-board timing scenario drives much of the low-frequency total, but the boards actually share a reference. That curve demonstrates sensitivity to timing correlations; it does not show that actual board jitter dominates. Differential timing and delay-implementation errors remain unquantified.

The minima are TDI-response features and must not be described as intrinsic improvements in detector sensitivity. The OMS-plus-acceleration curve is a reference noise scale, not a demonstrated performance requirement met by the complete setup.

The section now ends with the experimental implication: strong optical beats make detector readout a small calculated contribution, while electronic residuals, differential timing and delay errors require characterisation before the component budget can predict the assembled system.

## Pending and validation

The final output plot remains unchanged. Its caption states that the black sum includes the independent-board timing scenario. Full regeneration still requires the original baseline and phase-PSD modulation inputs; the available similarly named CSVs differ in both hashes and the modulation unit label. No replacement data were substituted, and no numerical margin to the reference was invented.

The review article compiles with latexmk, pdfLaTeX and BibTeX, with no unresolved references/citations or overfull boxes in the final log. The input-figure overlay was rendered and visually checked. The existing model checks pass for clock cancellation, first-order laser cancellation, static gain, ordered delays, common board jitter and averaging convergence.
