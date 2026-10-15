# Modulation-noise data

- `multi_PM/mod19_20261014_1316`: 19 MHz two-phasemeter run acquired at 13:16.
- `multi_PM/mod19_20261014_1345`: 19 MHz two-phasemeter run acquired at 13:45.
- `multi_PM/mod19_20261014_1358`: 19 MHz two-phasemeter run acquired at 13:58.
- `multi_PM/mod19_20261014_1629`: 19 MHz two-phasemeter run acquired at 16:29 after relocking.
- `multi_PM/mod27_20261002_1635`: 27 MHz two-phasemeter run acquired at 16:35.
- `multi_PM/comparisons`: plots and summaries comparing separate runs.
- `old`: earlier single-phasemeter EOM/PLL data.

Each measurement folder contains its raw phasemeter files and any synchronized data,
plots, numerical spectra, summaries, and transient lists produced from that run.

Run `python modulation_noise/amplitude_frequency_coupling.py` from the repository
root to regenerate the fractional-amplitude ASD and amplitude/frequency coherence
diagnostics for every synchronized multi-phasemeter measurement.
