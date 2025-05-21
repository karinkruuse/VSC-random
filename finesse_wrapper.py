# Rewriting the Finesse script generator to include ALL commands and options listed by the user
from typing import Optional, List

class ComprehensiveFinesseGenerator:
    def __init__(self):
        self.commands = []

    def add(self, line: str):
        self.commands.append(line)

    def laser(self, name, P, f, phase=None, node=None):
        self.add(f"l {name} {P} {f}" + (f" {phase}" if phase is not None else "") + (f" {node}" if node else ""))

    def squeezer(self, name, f, r, angle, node):
        self.add(f"sq {name} {f} {r} {angle} {node}")

    def mirror(self, name, R, T, phi, node1, node2):
        self.add(f"m {name} {R} {T} {phi} {node1} {node2}")

    def space(self, name, L, n=None, node1=None, node2=None):
        self.add(f"s {name} {L}" + (f" {n}" if n else "") + (f" {node1} {node2}" if node1 and node2 else ""))

    def beamsplitter(self, name, R, T, phi, alpha, node1, node2, node3, node4):
        self.add(f"bs {name} {R} {T} {phi} {alpha} {node1} {node2} {node3} {node4}")

    def isolator(self, name, S, node1, node2):
        self.add(f"isol {name} {S} {node1} {node2}")

    def modulator(self, name, f, midx, order, mode, phase=None, node1=None, node2=None):
        self.add(f"mod {name} {f} {midx} {order} {mode}" + (f" {phase}" if phase else "") + (f" {node1} {node2}" if node1 and node2 else ""))

    def lens(self, f, node1, node2):
        self.add(f"lens {f} {node1} {node2}")

    def photodiode(self, name, freqs=None, phases=None, nodes=None):
        if freqs is None: freqs = []
        if phases is None: phases = []
        if nodes is None: nodes = []
        parts = [f"pd{len(freqs)} {name}"]
        parts += [str(f) for f in freqs]
        parts += [str(p) for p in phases]
        parts += nodes
        self.add(" ".join(parts))

    def amplitude_detector(self, name, f, n=None, m=None, nodes=None):
        self.add(f"ad {name}" + (f" {n} {m}" if n and m else "") + f" {f}" + (" " + " ".join(nodes) if nodes else ""))

    def quantum_detector(self, name, f, phase, nodes):
        self.add(f"qd {name} {f} {phase} " + " ".join(nodes))

    def squeezing_detector(self, name, f, n=None, m=None, nodes=None):
        self.add(f"sd {name} {f}" + (f" {n} {m}" if n and m else "") + (" " + " ".join(nodes) if nodes else ""))

    def qnoise_detector(self, name, n, freqs=None, phases=None, nodes=None):
        if freqs is None: freqs = []
        if phases is None: phases = []
        if nodes is None: nodes = []
        self.add(f"qnoised {name} {n} " + " ".join(map(str, freqs + phases + nodes)))

    def xaxis(self, component, param, scale, start, stop, steps):
        self.add(f"xaxis {component} {param} {scale} {start} {stop} {steps}")

    def yaxis(self, mode):
        self.add(f"yaxis {mode}")

    def const(self, name, value):
        self.add(f"const {name} {value}")

    def variable(self, name, value):
        self.add(f"variable {name} {value}")

    def set_command(self, name, comp, param):
        self.add(f"set {name} {comp} {param}")

    def save(self, filename="comprehensive_kat_file.kat"):
        path = f"/mnt/data/{filename}"
        with open(path, "w") as f:
            f.write("\n".join(self.commands))
        return path


# Generate a minimal example using new comprehensive functionality
comp_gen = ComprehensiveFinesseGenerator()
comp_gen.laser("laser", 1, 0, 0, "n1")
comp_gen.space("space", 1, None, "n1", "n2")
comp_gen.mirror("m1", 0.99, 0.01, 0, "n2", "n3")
comp_gen.modulator("eom", 10e6, 0.3, 1, "pm", 0, "n3", "n4")
comp_gen.photodiode("pd_test", freqs=[10e6], phases=[0], nodes=["n4"])
comp_gen.xaxis("laser", "P", "lin", 1, 10, 100)
comp_gen.yaxis("abs")

# Save and return the file path
comp_gen.save()
