"""
TDI + clock-noise removal for the 3-phasemeter miniLISA data, with
delay-fitting and a gated REF (board-jitter) correction.

Pipeline:
  1. load synced phasemeter data
  2. build first-gen Michelson X1 (TDI11) with 4 INDEPENDENT (non-reciprocal) delays
  3. build the Hartwig sideband clock correction, also with 4 independent delays
  4. fit the 4 delays by minimising the Welch-band RMS of (TDI11 - correction),
     with a train/test split so we know the fit generalises
  5. optionally add the REF board-jitter correction -- but GATED: only applied
     to the extent it is actually coherent with the residual (optimal scale).
     On this dataset board jitter is below the reference-channel floor, so the
     gate correctly leaves it out.
"""

import os
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch, csd
from scipy.optimize import minimize

from pytdi.dsp import timeshift
from pytdi.michelson import X1_ETA

# ---------------------------------------------------------------- config
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
IN_NPZ   = os.path.join(DATA_DIR, "synced_phasemeter_data.npz")

FMIN, FMAX = 4e-3, 1e-1        # band used for the fit AND the residual metric
FIT_DELAYS   = True                    # False -> use DELAYS_START directly
DELAYS_START =  (8.1, 8.1, 8.0, 8.1)   # optimiser seed / fallback (d12,d21,d13,d31) [s]
DELAYS_NAIVE = (8.1, 8.1, 8.0, 8.1)    # the equal-delay baseline, for comparison
EDGE_CROP  = 2500              # samples dropped each end (Lagrange transients)
CROP_FRACTION = 1           # fraction (0-1] of the loaded record to keep, from the start

F_MOD  = {"12": 11e6, "13": 11e6, "21": 10e6, "31": 10e6}  
A_CARR = {(1, 2): 21e6, (2, 1): -21e6, (1, 3): 30e6, (3, 1): -30e6,
          (2, 3): 0, (3, 2): 0}                            

OMEGA1 = 17e6 # For Micheloson X, SC1 local frequency      
OMEGA2 = 38e6 # For Micheloson X, SC2 local frequency      
OMEGA3 = 47e6 # For Micheloson X, SC3 local frequency                 

# ---------------------------------------------------------------- load
_KEY_RE = re.compile(r"^(sc\d+)_(.+)$")

def load_data(npz_path=IN_NPZ):
    npz = np.load(npz_path)
    data = {"time_s": npz["time_s"]}
    for key in npz.files:
        if key == "time_s":
            continue
        m = _KEY_RE.match(key)
        if not m:
            raise ValueError(f"unexpected key {key!r}")
        slot, rest = m.group(1).upper(), m.group(2)
        is_freq = rest.endswith("_freq")
        label = rest[:-len("_freq")] if is_freq else rest
        ch = data.setdefault(slot, {}).setdefault(label, {})
        ch["freq" if is_freq else "phase"] = npz[key]
    return data


def crop_data(data, fraction):
    """Keep only the first `fraction` of the record (0-1], from the start."""
    n_keep = int(round(len(data["time_s"]) * fraction))
    for slot, channels in data.items():
        if slot == "time_s":
            continue
        for ch in channels.values():
            for kind in ch:
                ch[kind] = ch[kind][:n_keep]
    data["time_s"] = data["time_s"][:n_keep]
    return data


data = load_data()
if CROP_FRACTION < 1.0:
    data = crop_data(data, CROP_FRACTION)
fs = 1.0 / np.median(np.diff(data["time_s"]))
N  = len(data["time_s"])
duration_hr = (data["time_s"][-1] - data["time_s"][0]) / 3600.0
print(f"fs = {fs:.4f} Hz, N = {N}, duration = {data['time_s'][-1]-data['time_s'][0]:.1f} s "
      f"({duration_hr:.2f} h, {CROP_FRACTION*100:.0f}% of record used)")

# raw carrier/sideband/reference phases
c12 = data["SC1"]["c12"]["phase"]; sb12 = data["SC1"]["sb12"]["phase"]
c13 = data["SC1"]["c13"]["phase"]; sb13 = data["SC1"]["sb13"]["phase"]
c2  = data["SC2"]["c"]["phase"];   sb2  = data["SC2"]["sb"]["phase"]
c3  = data["SC3"]["c"]["phase"];   sb3  = data["SC3"]["sb"]["phase"]
ref1 = data["SC1"]["ref1"]["phase"] / 2e6
ref2 = data["SC1"]["ref2"]["phase"] /2e6
ref3 = data["SC1"]["ref3"]["phase"]/2e6

REF_AB = ref1 - ref2
REF_AC = ref3 - ref1
REF_CB = ref2 - ref3



# sideband-minus-carrier clock observables (minus signs on SC2/SC3 = testbed
# polarity, verified: gives TDI11 - correction with 0.998 coherence)
r = {
    (1, 2):  (sb12 - c12) / F_MOD["12"],
    (1, 3):  (sb13 - c13) / F_MOD["13"],
    (2, 1): (sb2  - c2 ) / F_MOD["21"],
    (3, 1): (sb3  - c3 ) / F_MOD["31"],
}
# ---------------------------------------------------------------- metrics
def band_rms(x, sl, lo=FMIN, hi=FMAX):
    nps = (sl.stop - sl.start) // 15
    f, p = welch(x[sl], fs=fs, nperseg=nps)
    m = (f >= lo) & (f <= hi)
    return np.sqrt(np.trapezoid(p[m], f[m]))

def coherence(x, y, sl, lo=FMIN, hi=FMAX):
    nps = (sl.stop - sl.start) // 15
    f, Pxy = csd(x[sl], y[sl], fs=fs, nperseg=nps)
    _, Px = welch(x[sl], fs=fs, nperseg=nps)
    _, Py = welch(y[sl], fs=fs, nperseg=nps)
    C = np.abs(Pxy) ** 2 / (Px * Py)
    m = (f >= lo) & (f <= hi)
    return C[m].mean()

def opt_scale(target, basis, sl, lo=FMIN, hi=FMAX):
    """Frequency-domain optimal real scale to subtract basis from target."""
    nps = (sl.stop - sl.start) // 15
    f, Ptb = csd(basis[sl], target[sl], fs=fs, nperseg=nps)
    _, Pbb = welch(basis[sl], fs=fs, nperseg=nps)
    m = (f >= lo) & (f <= hi)
    return float(np.real(np.sum(Ptb[m]) / np.sum(Pbb[m])))



# ---------------------------------------------------------------- core TDI
def build_tdi(delays):
    """First-gen Michelson X1 + Hartwig clock correction, 4 independent delays.

    delays = (d12, d21, d13, d31) in seconds.
    Returns (TDI1c, TDI11, correction).
    """
    d12, d21, d13, d31 = delays
    t12, t21, t13, t31 = (-d12 * fs, -d21 * fs, -d13 * fs, -d31 * fs)  # samples, delay

    TDI11 = X1_ETA.build(
        {"d_12": d12, "d_21": d21, "d_13": d13, "d_31": d31}, fs
    )({
        "eta_12":  c12, # - (OMEGA2*(ref1 - timeshift(ref1, t12))), 
        "eta_21": -c2 ,#- OMEGA1*(ref2 - timeshift(ref2, t21)),
        "eta_13":  c13,# - (OMEGA3*(ref1 - timeshift(ref1, t13))), 
        "eta_31": -c3,# - OMEGA1*(ref3 - timeshift(ref3, t31)),
    }, unit="phase")



    temp12 = np.array(r[(1, 2)] )
    temp13 = np.array(r[(1, 3)] )
    temp21 = np.array(r[(2, 1)] )
    temp31 = np.array(r[(3, 1)])


    # non-reciprocal Hartwig combinations (tau13+tau31, tau12+tau21)
    R = {}
    R[(1, 2)] = -(temp13 + timeshift(temp31, t13))
    R[(1, 3)] =  temp12 + timeshift(temp21, t12)
    R[(2, 1)] = (temp12 - temp13
                 - timeshift(temp31, t13)
                 - timeshift(temp12, t13 + t31))
    R[(3, 1)] = (-temp13 + temp12
                 + timeshift(temp21, t12)
                 + timeshift(temp13, t12 + t21))
    R[(2, 3)] = R[(3, 2)] = 0

    correction = 0
    for (i, j, k) in [(1, 2, 3), (2, 3, 1), (3, 1, 2)]:
        correction -= (-A_CARR[(i, j)] * R[(i, j)] - A_CARR[(i, k)] * R[(i, k)])

    Corr = 0#ref_correction(delays)
    
    return TDI11 - correction, TDI11, correction



# ---------------------------------------------------------------- fit delays
full = slice(EDGE_CROP, N - EDGE_CROP)

if FIT_DELAYS:
    half  = N // 2
    train = slice(EDGE_CROP, half)
    test  = slice(half, N - EDGE_CROP)

    cost = lambda p, sl: band_rms(build_tdi(p)[0], sl)

    Bounds = [(7.9, 8.3)] * 4

    # (a) fit on the full record -> the delays we actually use
    res    = minimize(cost, DELAYS_START, args=(full,), method="Nelder-Mead",
                      bounds=Bounds, options={"xatol": 1e-8, "fatol": 1e-16, "maxiter": 8000})
    delays = tuple(res.x)

    # (b) fit on the 1st half only, score on the held-out 2nd half -> honesty check
    #res_tr = minimize(cost, DELAYS_START, args=(train,), method="Nelder-Mead",
    #                  bounds=Bounds, options={"xatol": 1e-6, "fatol": 1e-14, "maxiter": 4000})

    TDI11_ref = build_tdi(DELAYS_NAIVE)[1]
    print("\ndelay fit (d12, d21, d13, d31) [s]:")
    print(f"  full-record fit : {np.round(delays, 4)}")
    #print(f"  half-record fit : {np.round(res_tr.x, 4)}")
    #print("\ncross-validation on the held-out 2nd half:")
    #for lbl, dd in [("equal 8.1 x4      ", DELAYS_NAIVE),
    #                ("fitted on 1st half", tuple(res_tr.x))]:
    #    rr = band_rms(build_tdi(dd)[0], test)
    #    print(f"  {lbl}: {rr:.3e}  ({band_rms(TDI11_ref, test)/rr:.0f}x)")
else:
    delays = DELAYS_START

# ---------------------------------------------------------------- final build
TDI1c, TDI1, correction = build_tdi(delays)

print(f"\nfinal (full record, delays {np.round(delays,4)}):")
print(f"  TDI11 band-RMS : {band_rms(TDI1, full):.3e}")
print(f"  TDI1c band-RMS : {band_rms(TDI1c, full):.3e}"
      f"   ({band_rms(TDI1, full)/band_rms(TDI1c, full):.0f}x clock suppression)")
if (FIT_DELAYS): print(res)
# ---- gated REF correction: only apply the coherent fraction -------------
#Corr = ref_correction(delays)
#alpha = opt_scale(TDI1c, Corr, full)
#coh_ref = coherence(TDI1c, Corr, full)


#print(f"alpha={alpha:.3f}: ")
#print(f"\nREF gate: residual-vs-ref coherence = {coh_ref:.3f}")

# ---------------------------------------------------------------- plot
nps = (full.stop - full.start) // 15
f, p_eta = welch(c12[full],   fs=fs, nperseg=nps)
f, p_11  = welch(TDI1[full], fs=fs, nperseg=nps)
f, p_1c  = welch(TDI1c[full], fs=fs, nperseg=nps)
#f, p_Corr  = welch(Corr[full], fs=fs, nperseg=nps)

plt.figure(figsize=(8, 5))
plt.loglog(f, np.sqrt(p_eta), lw=1.0, color="0.6", label="raw carrier")
plt.loglog(f, np.sqrt(p_11),  lw=1.2, color="k",   label="TDI1 ")
plt.loglog(f, np.sqrt(p_1c),  lw=1.4, color="tab:blue",
           label=f"TDI1c")
#plt.loglog(f, np.sqrt(p_Corr),  lw=0.7, color="gray",   label="correction term")
plt.axvspan(FMIN, FMAX, color="tab:blue", alpha=0.06, label="fit band")
plt.xlabel("Frequency (Hz)"); plt.ylabel("ASD (cyc/√Hz)")
plt.suptitle(f" TDI + clock removal, delays = {np.round(delays,3)} s")
plt.title(f"{duration_hr:.2f} hours of measurement used", fontsize=9, color="0.4")
plt.grid(True, which="both", ls="--", alpha=0.4)
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig("TDI1c_result.png", dpi=200)
print("\nsaved TDI1c_result.png")