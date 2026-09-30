# How the readout-noise calculation works

The result is small because the assumed optical signals are strong: milliamps of beat current are being compared with tens of picoamps of noise per square root hertz. The arithmetic gives **3.40 × 10⁻⁹ cycles/√Hz for the carrier** and **1.24 × 10⁻⁸ cycles/√Hz for one sideband**. These are idealized input-readout estimates, not a prediction of the complete detector, ADC and phasemeter chain.

This note follows `make_component_figure.py`. Run `python artikel/make_component_figure.py` from the repository root to reproduce the figures and the parameter record in `images/performance/figure_parameters.json`.

## 1. How much signal reaches the detector?

We assume one modulated beam and one unmodulated reference beam, with **4 mW each at the detector**, after optical combining losses. There is no further factor of one-half for a beamsplitter in this calculation. If 4 mW refers to power before a combining loss, the inputs need to be changed.

| Input | Assumed value |
|---|---:|
| Modulation depth | 0.53 rad |
| Photodiode responsivity | 0.6 A/W |
| Optical overlap efficiency, as a power fraction | 0.9 |
| Loaded current-to-voltage gain before splitting | 50 V/A |
| Electrical distribution | Ideal three-way power split |
| Gain at each ADC | 50/√3 = 28.87 V/A |

The modulation puts about 86.7% of the modulated beam's power in the carrier and 6.54% in each first-order sideband. The relevant Bessel amplitudes are J₀(0.53) = 0.9310 and J₁(0.53) = 0.2558.

For a beat between the reference and optical order n, the peak current is

```text
peak beat current = 2 × responsivity × √(overlap × beam power × reference power) × |J_n|
```

This gives 4.24 mA for the carrier and 1.16 mA for each first-order sideband. At each ADC, the assumed peak voltages are about 122 mV and 33.6 mV. A three-way power split divides voltage by √3, not by 3.

The average total optical power is 8 mW. The maximum instantaneous power in the ideal two-field interference model is 15.59 mW. The corresponding full AC waveform is about 0.263 V peak-to-peak at an ADC, below the assumed 1 V input span. These checks establish consistency within this model; they are not measurements of receiver linearity.

The proposed [Newport detector](https://www.newport.com/p/F-PD-30-D-1064-FCA) is specified for optical input up to 20 mW. That does **not** by itself establish the loaded gain, low-frequency response or complete receiver noise. In particular, 50 Ω impedance must not automatically be interpreted as a measured 50 V/A gain: internal and external terminations and RF losses matter.

## 2. What noise is included?

All entries below are **one-sided ASDs**, referred to the photodiode current. Independent noise powers are added, meaning that the ASDs are squared, summed, and square-rooted.

| Contribution | Calculation | Result |
|---|---|---:|
| Shot noise, including dark current | √[2e × (mean photocurrent + dark current)] | 39.2 pA/√Hz |
| Thermal noise of the assumed 50 Ω load | √(4kT/R), at 300 K | 18.2 pA/√Hz |
| Additive intensity noise | Mean photocurrent × 9 × 10⁻⁹/√Hz | 43.2 pA/√Hz |
| Ideal ADC quantization, referred through the gain | Quantization voltage ASD / 28.87 V/A | 19.3 pA/√Hz |

The mean photocurrent is 4.8 mA and the assumed dark current is 100 nA. The intensity-noise term assumes the two beams' additive fluctuations add coherently. The quoted RIN must apply around the relevant RF beat frequencies, not simply at millihertz optical-power fluctuations.

For a 14-bit ADC with a 1 V peak-to-peak input span, the quantization step is 1/2¹⁴ = 61.0 μV. Under the white-quantization assumption:

```text
voltage ASD = quantization step / √(6 × sample rate)
            = 0.557 nV/√Hz, for 2 GS/s
```

The sample rate is the physical ADC rate, not the 125 MHz processing rate or the exported phase-data rate. Using 2 GS/s assumes that subsequent filtering prevents discarded high-frequency noise from folding into the retained band. The white-noise formula follows the usual quantization variance of step²/12 spread over the Nyquist band. Actual ADC noise can exceed it. [Analog Devices explanation](https://www.analog.com/media/en/training-seminars/design-handbooks/Practical-Analog-Design-Techniques/Section4.pdf)

## 3. Convert the current noise into phase noise

For additive noise that is approximately white around a selected RF beat:

```text
phase ASD in cycles/√Hz = √2 × current ASD / (2π × peak beat current)
```

The √2 accounts for noise on both RF sides of the beat. The 2π converts radians into cycles. No PLL bandwidth is multiplied into an ASD; bandwidth would be needed to calculate an integrated RMS phase error.

| Contribution | Carrier, cycles/√Hz | Sideband, cycles/√Hz |
|---|---:|---:|
| Shot + dark current | 2.08 × 10⁻⁹ | 7.58 × 10⁻⁹ |
| Thermal | 9.66 × 10⁻¹⁰ | 3.52 × 10⁻⁹ |
| Additive RIN | 2.29 × 10⁻⁹ | 8.35 × 10⁻⁹ |
| Ideal ADC quantization | 1.02 × 10⁻⁹ | 3.73 × 10⁻⁹ |
| **Quadrature total** | **3.40 × 10⁻⁹** | **1.24 × 10⁻⁸** |
| Detector terms without ADC | 3.24 × 10⁻⁹ | 1.18 × 10⁻⁸ |

The sideband is noisier because its beat amplitude is smaller. The ratio is J₀/J₁ ≈ 3.64, not the ratio of optical powers.

The totals are 21.4 and 77.8 nrad/√Hz. Multiplying the carrier result in cycles by 1064 nm gives 0.00362 pm/√Hz. This is an equivalent input displacement, not a measured GW sensitivity.

## 4. Why this can underestimate the real readout

The arithmetic is consistent with the stated assumptions. The uncertain part is how well those assumptions describe the future hardware:

- **ADC noise:** 14 nominal bits do not establish a 14-bit noise floor. The model omits excess conversion and phasemeter noise; the measured electronic baseline represents those contributions separately.
- **Gain and RF losses:** the 50 V/A loaded gain and ideal split are assumed. Splitter, cable and input losses reduce the beat amplitude relative to noise added downstream. Additional thermal noise from the distribution network is not explicitly included.
- **Filtering:** a wideband detector needs suitable filtering before sampling and decimation. Without it, out-of-band noise can fold into the measurement band. The present model assumes adequate filtering.
- **Intensity and phase coupling:** the white additive RIN term is not a complete model of laser intensity noise. Coupling around twice the beat frequency and amplitude-to-phase conversion can add noise. No numerical value is assigned without a suitable model or measurement. [Wissel et al.](https://doi.org/10.1103/PhysRevApplied.17.024025)

The following changes illustrate the sensitivity without claiming to describe the actual hardware. Only the stated parameter is changed in each row.

| Scenario | Carrier, cycles/√Hz | Sideband, cycles/√Hz |
|---|---:|---:|
| Current assumptions | 3.40 × 10⁻⁹ | 1.24 × 10⁻⁸ |
| 0.4 mW per beam instead of 4 mW | 1.57 × 10⁻⁸ | 5.72 × 10⁻⁸ |
| 10 ideal quantization bits instead of 14 | 1.67 × 10⁻⁸ | 6.08 × 10⁻⁸ |
| Half the voltage gain, unchanged input-current noise | 3.84 × 10⁻⁹ | 1.40 × 10⁻⁸ |

The 10-bit row is a white-noise sensitivity example, not a claim about measured ENOB. Halving the gain alone affects the ADC contribution here; a physical termination change could also change the thermal-noise model.

## 5. How this enters the article's combined curve

The readout figure shows the detector terms and ideal ADC quantization. For TDI propagation, detector fluctuations before the split are kept as shared source noises. Independent detector channels are assumed, but each channel's copies on different boards remain correlated. The reused carrier noise in clock correction is retained.

The combined curve uses the measured electronic baseline instead of adding another ADC quantization term. It also includes the modulation estimate and the assumed board-jitter spectrum. Treating the measured baseline and that board model as separate inputs assumes that the baseline is the timing-corrected electronic residual; timing noise already left in the baseline must not be counted twice.

The result describes the included contributions, not the noise of the current complete delay-line implementation. The low theoretical detector contribution is useful for estimating what the optical extension adds; it does not establish an equally low experimental floor.
