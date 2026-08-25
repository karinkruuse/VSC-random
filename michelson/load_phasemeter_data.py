
import os
import re
import numpy as np
import matplotlib.pyplot as plt

from pytdi.dsp import timeshift
from pytdi.michelson import X1_ETA
from scipy.signal import welch

import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
IN_NPZ = os.path.join(DATA_DIR, "synced_phasemeter_data.npz")

_KEY_RE = re.compile(r"^(sc\d+)_(.+)$")


def load_data(npz_path=IN_NPZ):
    npz = np.load(npz_path)
    data = {"time_s": npz["time_s"]}

    for key in npz.files:
        if key == "time_s":
            continue
        m = _KEY_RE.match(key)
        if not m:
            raise ValueError(f"{npz_path}: unexpected key {key!r}, doesn't match '<slot>_<label>[_freq]'")
        slot, rest = m.group(1).upper(), m.group(2)

        is_freq = rest.endswith("_freq")
        label = rest[:-len("_freq")] if is_freq else rest

        channel = data.setdefault(slot, {}).setdefault(label, {})
        channel["freq" if is_freq else "phase"] = npz[key]

    return data



data = load_data()
"""
print(f"time_s: {data['time_s'].shape}, {data['time_s'][0]:.3f} to {data['time_s'][-1]:.3f} s")
for slot, channels in data.items():
    if slot == "time_s":
        continue
    print(f"{slot}:")
    for label, arrs in channels.items():
        print(f"  {label}: phase {arrs['phase'].shape}, freq {arrs['freq'].shape}")
"""

fs = 1.0 / np.median(np.diff(data['time_s']))
print(f"Sampling frequency: {fs:.3f} Hz, dt = {1/fs:.6f} s")


tau_12 = -8.085 * fs
tau_13 = -8.004 * fs
tau_31 = -8.085 * fs

## clock noise removal alla Hartwig
r = {
    (1, 2): (data["SC1"]["sb12"]["phase"]-data["SC1"]["c12"]["phase"]) / 11e6,
    (1, 3): (data["SC1"]["sb13"]["phase"]-data["SC1"]["c13"]["phase"]) / 11e6,
    (2, 1): -(data["SC2"]["sb"]["phase"]-data["SC2"]["c"]["phase"]) / 10e6,
    (3, 1): -(data["SC3"]["sb"]["phase"]-data["SC3"]["c"]["phase"]) / 10e6,
}




N = 2000

X1_built = X1_ETA.build(
    {"d_12": 8.085, "d_21": 8.085, "d_13": 8.004, "d_31": 8.085},
    fs,)

TDI11 = X1_built({
    "eta_12": data["SC1"]["c12"]["phase"],
    "eta_21": -data["SC2"]["c"]["phase"],
    "eta_13": data["SC1"]["c13"]["phase"],
    "eta_31": -data["SC3"]["c"]["phase"],
}, unit="phase")






eta_12 = data["SC1"]["c12"]["phase"]
eta_13 = data["SC1"]["c13"]["phase"]
eta_21 = -data["SC2"]["c"]["phase"] + 21e6 * r[(2, 1)]
eta_31 = -data["SC3"]["c"]["phase"] + 30e6 * r[(3, 1)]


phi_12 = eta_12 + timeshift(eta_21, tau_12)
phi_13 = eta_13 + timeshift(eta_31, tau_13)

P12 = phi_12 - timeshift(phi_12, 2*tau_13)
P13 = -(phi_13 - timeshift(phi_13, 2*tau_12))

TDI1 = P12 + P13 


fmin = 1e-3
nperseg = int(fs / fmin)


pm1 = data["SC1"]["sync"]["phase"]
pm2 = data["SC2"]["sync"]["phase"]
pm3 = data["SC3"]["sync"]["phase"]


"""
f, psd_12 = welch(r[(1, 2)], fs=fs, nperseg=nperseg)
f, psd_21 = welch(r[(2, 1)], fs=fs, nperseg=nperseg)
f, psd_13 = welch(r[(3, 1)], fs=fs, nperseg=nperseg)
f, psd_31 = welch(r[(1, 3)], fs=fs, nperseg=nperseg)
plt.loglog(f, 5e6*np.sqrt(psd_12), label= "r12")
plt.loglog(f, 5e6*np.sqrt(psd_21), label= "r21")
plt.loglog(f, 5e6*np.sqrt(psd_13), label= "r13")
plt.loglog(f, 5e6*np.sqrt(psd_31), label= "r31")


f, pm1pm2 = welch(pm1-pm2, fs=fs, nperseg=nperseg)
f, pm1pm3 = welch(pm1-pm3, fs=fs, nperseg=nperseg)
plt.loglog(f, np.sqrt(pm1pm2), label= "5 MHz r12")
plt.loglog(f, np.sqrt(pm1pm3), label= "5 MHz r13")
plt.legend()
plt.show()
"""

pm1pm1 = pm1-pm2 - r[(2,1)]
pm2pm2 = pm2-pm1 - r[(1,2)]


f, irst = welch(pm1pm1, fs=fs, nperseg=nperseg)
f, second = welch(pm2pm2, fs=fs, nperseg=nperseg)
#plt.loglog(f, np.sqrt(irst), label= "5 MHz r12")
#plt.loglog(f, np.sqrt(second), label= "5 MHz r13")
#plt.show()

R = {}
R[(1, 2)] = -(r[(1, 3)] + timeshift(r[(3, 1)], tau_13))

R[(1, 3)] = r[(1, 2)] + timeshift(r[(2, 1)], tau_12)

R[(2, 1)] = (r[(1, 2)] - r[(1, 3)] - timeshift(r[(3, 1)], tau_13)
             - timeshift(r[(1, 2)], tau_13 + tau_31))

R[(3, 1)] = (-r[(1, 3)] + r[(1, 2)] + timeshift(r[(2, 1)], tau_12)
             + timeshift(r[(1, 3)], 2 * tau_12))

R[(2, 3)] = 0
R[(3, 2)] = 0

a = {
    (1, 2): 21e6,
    (2, 1): -21e6,
    (1, 3): 30e6,
    (3, 1): -30e6,
    (2, 3): 0,  
    (3, 2): 0,  
}

triplets = [(1, 2, 3), (2, 3, 1), (3, 1, 2)]
correction = 0
for (i, j, k) in triplets:
    correction -= (
        - a[(i, j)] * R[(i, j)]
        - a[(i, k)] * R[(i, k)]
    )

TDI1c = TDI11 - correction


REF_AB = (data["SC1"]["ref1"]["phase"] - data["SC1"]["ref2"]["phase"]) / 2e6
REF_AC = (data["SC1"]["ref3"]["phase"] - data["SC1"]["ref1"]["phase"]) / 2e6
REF_CB = (data["SC1"]["ref2"]["phase"] - data["SC1"]["ref3"]["phase"]) / 2e6

"""
f, psd_12 = welch(REF_AB, fs=fs, nperseg=nperseg)
f, psd_21 = welch(REF_AC, fs=fs, nperseg=nperseg)
f, psd_13 = welch(REF_CB, fs=fs, nperseg=nperseg)
plt.loglog(f, 17e6*np.sqrt(psd_12))
plt.loglog(f, 17e6*np.sqrt(psd_21))
plt.loglog(f, 17e6*np.sqrt(psd_13))
plt.show()
"""

omega1 = 17e6  # Hz

# reciprocal delays assumed (tau21=tau_12, tau31=tau_13), same as the R/a section above
Corr1 = omega1 * (timeshift(REF_AB, tau_12)
                   - timeshift(REF_AB, 2 * tau_12)
                   - timeshift(REF_AB, tau_12 + tau_13 + tau_31))

Corr2 = omega1 * (timeshift(REF_AC, tau_13)
                   - timeshift(REF_AC, tau_13 + tau_31)
                   - timeshift(REF_AC, 2 * tau_12 + tau_13))

Corr3 = -omega1 * timeshift(REF_CB, 2 * tau_12 + tau_13 + tau_31)


TDI1c_corr = TDI1c + (Corr1 + Corr2 + Corr3)


f, psd_eta12 = welch(eta_12, fs=fs, nperseg=nperseg)
f, psd_phi12 = welch(phi_12, fs=fs, nperseg=nperseg)
f, psd_tdi1 = welch(TDI1, fs=fs, nperseg=nperseg)
f, psd_tdi11 = welch(TDI11, fs=fs, nperseg=nperseg)
f, psd_clk = welch(TDI1c, fs=fs, nperseg=nperseg)
f, psd_correction = welch(correction, fs=fs, nperseg=nperseg)
f, psd_correction2 = welch((Corr1 + Corr2 + Corr3), fs=fs, nperseg=nperseg)
f, psd_TDI1c_corr = welch(TDI1c_corr, fs=fs, nperseg=nperseg)

plt.loglog(f, np.sqrt(psd_eta12), linewidth=0.5, label="η₁₂") # From these two we kinda see that the measurement is not carrier noise dominated
#plt.loglog(f, np.sqrt(psd_phi12))

plt.loglog(f, np.sqrt(psd_tdi1), label="TDI1")
plt.loglog(f, np.sqrt(psd_tdi11), label="TDI11")
plt.loglog(f, np.sqrt(psd_clk), linewidth=0.5, label="TDI1c")
#plt.loglog(f, np.sqrt(psd_correction), alpha=0.5,label="Correction")
#plt.loglog(f, np.sqrt(psd_correction2), alpha=0.3,label="Correction2")
#plt.loglog(f, np.sqrt(psd_TDI1c_corr), linewidth=0.5, label="TDI1c + Correction")
plt.legend()
#plt.show()
plt.savefig("TDI1c_correction.png", dpi=300)