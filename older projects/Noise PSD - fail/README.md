# lisa_noise_budget

A Python framework for building and visualising noise budgets for the
miniLISA TDI testbed.

## Structure

```
lisa_noise_budget/
│
├── config/
│   └── config.py          ← All system parameters: frequency plan,
│                             arm lengths, LISA requirements.
│                             Edit this file to reflect your setup.
│
├── noise_sources/
│   └── base.py            ← Noise source classes:
│                             PowerLawNoise, LisaLaserNoise, ClockNoise,
│                             AnalyticNoise, MeasuredNoise (from CSV)
│
├── transfer_functions/
│   └── base.py            ← Transfer function classes:
│                             Unity, Gain, FreqToPhase, DelayPowerTF,
│                             TDILaserSuppression, ClockCouplingTF,
│                             ChainedTF
│
├── budget/
│   └── budget.py          ← NoiseBudget: assembles terms, computes
│                             total PSD, plots, prints summary table.
│
├── utils/
│   └── helpers.py         ← Frequency grid, unit conversions,
│                             coupling coefficient computation,
│                             LISA requirement curves.
│
├── tests/                 ← (to be populated)
│
└── example_stage1.py      ← Runnable example demonstrating Stage 1.
```

## Units

All noise quantities are kept as **frequency noise ASD [Hz/√Hz]**
internally. The `NoiseBudget` class accepts an `output_unit` argument:

| Value    | Unit              |
|----------|-------------------|
| `"freq"` | Hz/√Hz (default)  |
| `"phase"`| rad/√Hz           |
| `"disp"` | m/√Hz             |

## Quickstart

```python
from config.config import FREQ_CONFIG, FREQ_PLAN, ARM_CONFIG
from utils.helpers import make_freq_array_from_config, compute_coupling_coefficients
from noise_sources.base import LisaLaserNoise, ClockNoise, PowerLawNoise
from transfer_functions.base import Unity, Gain, TDILaserSuppression
from budget.budget import NoiseBudget

f = make_freq_array_from_config(FREQ_CONFIG)
coeffs = compute_coupling_coefficients(FREQ_PLAN)

budget = NoiseBudget("My readout", f=f, output_unit="freq")

budget.add(LisaLaserNoise(), Unity(), label="Laser noise")
budget.add(ClockNoise(), Gain("alpha", gain=coeffs["alpha"]["SC2<-SC1"]))

budget.summary()
budget.plot()
```

## Development Stages

| Stage | Description                                      | Status     |
|-------|--------------------------------------------------|------------|
| 1     | Core framework, analytic noise models            | ✅ Done     |
| 2     | One-way LISA measurement equations as signal chain | Planned   |
| 3     | TDI combinations (X1, X2), clock correction     | Planned    |
| 4     | MeasuredNoise: plug in real lab data from CSV    | Stubbed    |

## Adding Measured Data (Stage 4)

Replace any analytic noise source with a `MeasuredNoise` instance:

```python
from noise_sources.base import MeasuredNoise

# From a CSV with columns [frequency_Hz, ASD_Hz_per_sqrtHz]
delay_line_meas = MeasuredNoise.from_csv(
    name="Delay line (measured)",
    filepath="data/delay_line_noise.csv",
    input_type="asd",
)

budget.add(delay_line_meas, Unity(), label="Delay line floor (measured)")
```

## Configuration

Edit `config/config.py` to set:
- Your frequency plan (beatnote frequencies, modulation frequencies,
  sampling frequency)
- Arm lengths / delay values
- Laser wavelength and carrier frequency

The coupling coefficients `alpha_ji` and `gamma_ji` are computed
automatically from the frequency plan by `compute_coupling_coefficients()`.
