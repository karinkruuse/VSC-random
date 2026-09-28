# miniLISA article TODO

Updated 28 September 2026. This is the central checklist. Purple draft notes also remain in `main.tex`, `model.tex` and `IDS.tex`; some describe later extensions rather than requirements for the current paper.

## Finish the current draft

- [ ] **Write the title and abstract, and complete the author information.** These are still placeholders in `main.tex`.
- [ ] **Update the drawings.** Show the six directed links, independent Rb → Moku references, and Moku → EOM drives. Match the example modulation frequencies (35, 36, 34 MHz). Keep the signal-generator alternative in the text unless it becomes the chosen setup. Check labels against both optical input tones and synthesized output tones.
- [ ] **Clarify the delay-board clock connections.** State what drives the board ADCs, DACs and delay counters, and whether the boards share a reference or use separate spacecraft references. This determines how board jitter relates to the common clock term `q_i`.
- [ ] **Settle the detector operating point used for the prediction.** The current example uses 4 mW per beam and an ideal three-way electrical split. Confirm that these are the intended assumptions and keep the text, table and figures consistent. Detector measurements can wait until the hardware is available.
- [ ] **Choose one simple GW injection example.** Specify its frequency and amplitude and give the expected processed amplitude and phase. A monochromatic signal is sufficient to make the proposed test concrete.
- [ ] **Keep the scope of the noise figure clear.** It is a component estimate with static delays and ideal laser/clock cancellation. Differential board timing and delay-error residuals are not yet quantified. This can remain a stated limitation; it does not require a new numerical floor for this draft.
- [ ] **Resolve or move the purple notes before submission.** Keep only decisions needed for the present design and calculation. Put work on varying delays and additional hardware in future work.

## Planned measurements and their follow-up

- [ ] **Remeasure the modulation noise.** Use the planned Rb-referenced Moku EOM drive. Establish how much of the sideband-difference spectrum comes from the readout before assigning the full spectrum to modulation noise. Replace the current input spectrum and regenerate the noise figures afterwards.
- [ ] **Use the Moku report to guide the readout check.** Request the existing same-DAC, two-ADC phase records and the signal amplitudes/readout settings. Those data may already provide the differential readout estimate needed; start there before arranging another measurement.
- [ ] **Decide whether an external signal generator is needed after the modulation test.** The relevant quantity is excess modulation-path noise relative to the phasemeter timing reference. The DAC report alone does not determine it.
- [ ] **After assembly, test noise suppression and GW recovery.** Compare the recovered signal with the amplitude and phase predicted using the same delays. Use the adopted laser requirement and Rb estimate for planning; new laser and clock spectra are not prerequisites for finishing the design paper.

## Later, if varying-delay results are added

- [ ] Extend the static calculation to ordered, time-varying delays and the corresponding clock correction. Check the delayed-frequency scaling, command range and tone separation for that configuration. The current static calculation does not demonstrate flexing-arm cancellation.

## What the new Moku report tells us

Source: Patrick Krieger, *Moku Delta Differential Phase Measurements*, 25 September 2026, supplied as `Moku Delta DAC measurement.pdf`.

The report compares two ADC observations of the same DAC with observations of different DACs. It also reports that changing the readout to a Moku Pro indicates a significant Delta phasemeter contribution. These are measurements of the combined signal and readout paths, not isolated DAC spectra. They are relevant to both the modulation source and the readout assumptions, but should not be added to the budget as a separate DAC floor without separating contributions already counted elsewhere.

**A simple ADC/readout check is already present in this setup:** split one sinusoidal source into two Moku inputs, record both phases, and subtract them. The common source phase cancels for matched paths. The difference retains differential input, cable and phasemeter noise. For equal, independent channel noises, dividing its ASD by √2 estimates the noise of one channel; shared errors are not measured by this difference.

If a repeat is needed, keep the amplitude at each ADC fixed while changing the signal frequency, then change amplitude at a fixed frequency. A contribution proportional to frequency is consistent with timing jitter; additive voltage noise generally produces a larger phase error at lower signal amplitude. These trends help interpret the result but do not uniquely identify a noise source. The reported frequency dependence is not consistent with a simple fixed-jitter explanation alone.

This is a straightforward readout-chain test, not a measurement of the ADC alone or of the full DAC-to-sampling timing relationship. Same-frequency channel subtraction rejects common sampling-clock noise. An ordinary self-loopback can also conceal shared DAC/ADC timing noise. The planned modulation measurement is still needed for the EOM-drive question.

The manufacturer's [phasemeter reference description](https://knowledge.liquidinstruments.com/en_US/mokupro-phasemeter/what-reference-does-the-phasemeter-measure-against) states that phase is measured against a local oscillator derived from the onboard clock. The [external-reference documentation](https://knowledge.liquidinstruments.com/mokupro/external-reference-clock) describes locking that clock to an external 10 MHz reference; the reference connection alone does not establish the residual noise between output and readout paths.
