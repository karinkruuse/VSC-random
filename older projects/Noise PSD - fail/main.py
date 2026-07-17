from config import FREQ_CONFIG, FREQ_PLAN, ARM_CONFIG
from helpers import make_freq_array_from_config, compute_coupling_coefficients
from noise_sources import LisaLaserNoise, ClockNoise, PowerLawNoise
from transfer_functions import Unity, Gain, TDILaserSuppression
from budget import NoiseBudget

f = make_freq_array_from_config(FREQ_CONFIG)
coeffs = compute_coupling_coefficients(FREQ_PLAN)

budget = NoiseBudget("My readout", f=f, output_unit="freq")

budget.add(LisaLaserNoise(), Unity(), label="Laser noise")
budget.add(LisaLaserNoise(), Unity(), label="Laser noise 2")
budget.add(ClockNoise(), Gain("alpha", gain=coeffs["alpha"]["SC2<-SC1"]))

budget.summary()
fig = budget.plot(save_path="noise_budget_example.png")