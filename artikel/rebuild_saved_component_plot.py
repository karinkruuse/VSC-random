"""Re-sum saved vector curves when original measured CSV inputs are unavailable.
This preserves plotted component ordinates, not the precision of raw spectra.
Run make_component_figure.py instead when the original input files are restored.
"""
from pathlib import Path
import hashlib, json, re
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent / "images/performance"
SOURCE = OUT / "archive/independent_board_total_noise_tdi2_corrected_budget.svg"
root = ET.parse(SOURCE).getroot()
ns = {"s": "http://www.w3.org/2000/svg"}
def curve(number):
    group = root.find(f".//s:g[@id='line2d_{number}']", ns)
    path = group.find("s:path", ns)
    d = path.attrib["d"]
    assert set(re.findall(r"[A-Za-z]", re.sub(r"[eE][-+]?\d+", "", d))) <= {"M", "L"}
    xy = np.array([float(v) for v in re.findall(r"[-+]?(?:\d*\.)?\d+(?:[eE][-+]?\d+)?", d)]).reshape(-1, 2)
    assert np.all(np.diff(xy[:, 0]) >= 0)
    # Axis calibration from saved major ticks: 1e-3, 1e-2 and 1e-12, 1e-10.
    f = 10 ** (-3 + (xy[:, 0] - 132.926568) / (253.257712 - 132.926568))
    asd = 10 ** (-12 + 2 * (xy[:, 1] - 246.664864) / (192.684343 - 246.664864))
    return f, asd
curves = [curve(i) for i in (240, 241, 242)]
reference = curve(244)
freq = np.unique(np.concatenate([f for f, _ in curves]))
values = np.array([np.exp(np.interp(np.log(freq), np.log(f), np.log(a))) for f, a in curves])
total = np.sqrt(np.sum(values**2, axis=0))
assert np.all(total >= np.max(values, axis=0))
for components, name in [(True, "total_noise_tdi2_corrected_budget"), (False, "total_noise_tdi2_corrected")]:
    with plt.rc_context({"font.size": 10, "axes.labelsize": 11, "legend.fontsize": 8}):
        fig, ax = plt.subplots(figsize=(7, 4.8))
        if components:
            for (f, a), color, label in zip(curves, ["#d71b2f", "#821770", "#295f24"],
                    ["Electronic baseline contribution", "Modulation estimate", "Shared detector contribution"]):
                ax.loglog(f, a, color=color, lw=.9, label=label)
        ax.loglog(*reference, color="#777777", ls="--", lw=1.2,
                  label="Single-link reference propagated through TDI 2")
        ax.loglog(freq, total, color="black", lw=1.3, label="Electronics + modulation + detector")
        ax.set(xlim=(.00025, 1), xlabel="Fourier frequency (Hz)",
               ylabel=r"Phase ASD (cycles/$\sqrt{\mathrm{Hz}}$)")
        ax.grid(which="major", color="#dedede", lw=.5, ls="--")
        ax.legend(loc="lower left")
        ax.set_title("Varying-arm TDI 2 + clock correction; component estimate", fontsize=9)
        fig.text(.54, .045, "Shared reference suppressed; differential board timing assumed negligible", ha="center", fontsize=8)
        fig.subplots_adjust(left=.12, right=.98, bottom=.18, top=.94)
        for extension in ["pdf", "svg", "png"]:
            target = OUT / f"{name}.{extension}"
            temporary = OUT / f"{name}_rebuilt.{extension}"
            fig.savefig(temporary, dpi=300)
            temporary.replace(target)
        plt.close(fig)
np.savetxt(OUT / "total_noise_tdi2_shared_reference.csv", np.column_stack([freq, total, values.T]),
           delimiter=",", header="Reconstructed from archived SVG vertices; not raw measured data.\nHz,included_sum_ASD,electronic_ASD,modulation_ASD,detector_ASD")
config_path = OUT / "figure_parameters.json"
config = json.loads(config_path.read_text())
config["board_model"] = {"source_basis": "eps_i = eps_common + deps_i",
    "common": "coherently suppressed to laser-noise cancellation order",
    "differential": "assumed negligible; no measured PSD assigned", "independent_Rb_spectra": False}
config["curve_provenance"] = {"method": "Saved SVG component vertices; log-log interpolation and PSD sum",
    "source": str(SOURCE.relative_to(OUT)), "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "limitation": "Original input CSVs unavailable; vector-export precision only. No new raw-data evaluation."}
config_path.write_text(json.dumps(config, indent=2) + "\n")
print("Rebuilt shared-reference plots from archived component curves; PSD sum verified.")
