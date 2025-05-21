class FinesseGenerator:
    def __init__(self):
        self.lines = []

    def add(self, line: str):
        self.lines.append(line)

    def laser(self, name, P, f, phase=None, node=None):
        self.add(f"l {name} {P} {f}" + (f" {phase}" if phase else "") + (f" {node}" if node else ""))

    def space(self, name, L, n=None, node1=None, node2=None):
        self.add(f"s {name} {L}" + (f" {n}" if n else "") + (f" {node1} {node2}" if node1 and node2 else ""))

    def mirror(self, name, R, T, phi, node1, node2):
        """
        In more detailed
        optical layouts it is often wise to use more realistic models for the optical components:
        a ’real’ mirror or beam splitter would consist of two optical surfaces with a substrate in
        between. To model this one needs to employ a number of basic Finesse components. A
        mirror then can be modeled as:
        m Mfront ...nM1 nMi1
        s Msubstrate ...nMi1 nMi2
        m Mback ...nMi2 nM2
        """
        self.add(f"m {name} {R} {T} {phi} {node1} {node2}")

    def beamsplitter(self, name, R, T, phi, alpha, n1, n2, n3, n4):
        self.add(f"bs {name} {R} {T} {phi} {alpha} {n1} {n2} {n3} {n4}")

    def modulator(self, name, f, midx, order, mode, phase=None, n1=None, n2=None):
        self.add(f"mod {name} {f} {midx} {order} {mode}" + (f" {phase}" if phase else "") + (f" {n1} {n2}" if n1 and n2 else ""))

    def photodiode(self, name, freqs=None, phases=None, nodes=None):
        line = f"pd{len(freqs or [])} {name}"
        if freqs:
            line += " " + " ".join(map(str, freqs))
        if phases:
            line += " " + " ".join(map(str, phases))
        if nodes:
            line += " " + " ".join(nodes)
        self.add(line)

    def qnoised(self, name, n, freqs_phases_nodes):
        self.add(f"qnoised {name} {n} " + " ".join(map(str, freqs_phases_nodes)))

    def qshot(self, name, num_demod, f, phase, nodes):
        self.add(f"qshot {name} {num_demod} {f} {phase} " + " ".join(nodes))

    def bp(self, name, direction, parameter, nodes):
        self.add(f"bp {name} {direction} {parameter} " + " ".join(nodes))

    def cp(self, cav_name, direction, parameter):
        self.add(f"cp {cav_name} {direction} {parameter}")

    def gouy(self, name, direction, spaces):
        self.add(f"gouy {name} {direction} {' '.join(spaces)}")

    def beam(self, name, f=None, nodes=None):
        self.add(f"beam {name}" + (f" {f}" if f else "") + (" " + " ".join(nodes) if nodes else ""))

    def fsig(self, name, component, sig_type, f, phase, amp=None):
        self.add(f"fsig {name} {component} {sig_type} {f} {phase}" + (f" {amp}" if amp else ""))

    def tem(self, comp, n, m, factor, phase):
        self.add(f"tem {comp} {n} {m} {factor} {phase}")

    def mask(self, detector, n, m, factor):
        self.add(f"mask {detector} {n} {m} {factor}")

    def attr(self, comp, mode, val):
        self.add(f"attr {comp} {mode} {val}")

    def gauss(self, name, comp, node, w0, z, wy0=None, zy=None):
        line = f"gauss {name} {comp} {node} {w0} {z}"
        if wy0 and zy:
            line += f" {wy0} {zy}"
        self.add(line)

    def cav(self, name, comp1, node1, comp2, node2):
        self.add(f"cav {name} {comp1} {node1} {comp2} {node2}")

    def startnode(self, node):
        self.add(f"startnode {node}")

    def phase(self, mode):
        self.add(f"phase {mode}")

    def xaxis(self, comp, param, mode, start, stop, steps):
        self.add(f"xaxis {comp} {param} {mode} {start} {stop} {steps}")

    def const(self, name, value):
        self.add(f"const {name} {value}")

    def variable(self, name, value):
        self.add(f"variable {name} {value}")

    def func(self, name, expression):
        self.add(f"func {name} = {expression}")

    def lock(self, name, variable, gain, accuracy):
        self.add(f"lock {name} {variable} {gain} {accuracy}")

    def tf(self, name, factor, phase, terms):
        line = f"tf {name} {factor} {phase} " + " ".join(f"{t[0]} {t[1]} {t[2]}" for t in terms)
        self.add(line)

    def trace(self, level):
        self.add(f"trace {level}")

    def yaxis(self, mode):
        self.add(f"yaxis {mode}")

    def scale(self, factor, output=None):
        self.add(f"scale {factor}" + (f" {output}" if output else ""))

    def print_frequency(self):
        self.add("printfrequency")

    def print_noises(self):
        self.add("printnoises")

    def save(self, filename="custom_finesse.kat"):
        path = f"input_files/{filename}"
        with open(path, "w") as f:
            f.write("\n".join(self.lines))
        return path


# Instantiate and save
finesse = FinesseGenerator()
finesse.laser("L1", 1, 0, 0, "n1")
finesse.space("s1", 0.5, node1="n1", node2="n2")
finesse.mirror("M1", 0.99, 0.01, 0, "n2", "n3")
finesse.beamsplitter("BS1", 0.5, 0.5, 0, 45, "n3", "n4", "n5", "n6")
finesse.modulator("EOM1", 1e6, 0.3, 1, "pm", 0, "n6", "n7")
finesse.photodiode("PD1", freqs=[1e6], phases=[0], nodes=["n7"])
finesse.qnoised("QPD1", 1, [1e6, 0, "n7"])
finesse.qshot("QS1", 1, 1e6, 0, ["n7"])
finesse.bp("BP1", "x", "w0", ["n7"])
finesse.cp("CAV1", "x", "length")
finesse.gouy("GOUY1", "x", ["s1"])
finesse.beam("CCD1", 1e6, ["n7"])
finesse.fsig("SIG1", "M1", "pm", 1e6, 0)
finesse.tem("L1", 0, 0, 1, 0)
finesse.mask("PD1", 0, 0, 1)
finesse.attr("M1", "Rcx", 2)
finesse.gauss("G1", "M1", "n2", 0.5, 0)
finesse.cav("CAV1", "M1", "n2", "M1", "n3")
finesse.startnode("n1")
finesse.phase(3)
finesse.xaxis("L1", "P", "lin", 0, 1, 100)
finesse.const("pi", 3.14159)
finesse.variable("v1", 1)
finesse.func("gain_func", "sin($x)")
finesse.lock("LOCK1", "$v1", 0.1, 1e-6)
finesse.tf("TF1", 1, 0, [("p", 10, 1), ("z", 100, 1)])
finesse.trace(2)
finesse.yaxis("abs:deg")
finesse.scale(1.0)
finesse.print_frequency()
finesse.print_noises()

# Save and return path
finesse.save()
