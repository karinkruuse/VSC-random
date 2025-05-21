from collections import defaultdict

class FullNodeAwareFinesseGenerator:
    def __init__(self):
        self.lines = []
        self.node_counter = 0
        self.node_connections = defaultdict(set)
        self.current_node = self._new_node()

    def _new_node(self):
        node = f"n{self.node_counter}"
        self.node_counter += 1
        return node

    def _add_connection(self, component, *nodes):
        for node in nodes:
            self.node_connections[node].add(component)

    def _add(self, line):
        self.lines.append(line)

    def laser(self, name, P, f, phase=0):
        node = self.current_node
        self._add(f"l {name} {P} {f} {phase} {node}")
        self._add_connection(name, node)

    def space(self, name, L, n=1):
        n1 = self.current_node
        n2 = self._new_node()
        self._add(f"s {name} {L} {n} {n1} {n2}")
        self._add_connection(name, n1, n2)
        self.current_node = n2

    def mirror(self, name, R, T, phi=0):
        n1 = self.current_node
        n2 = self._new_node()
        self._add(f"m {name} {R} {T} {phi} {n1} {n2}")
        self._add_connection(name, n1, n2)
        self.current_node = n2

    def beamsplitter(self, name, R, T, phi, alpha):
        n1, n2, n3, n4 = self._new_node(), self._new_node(), self._new_node(), self._new_node()
        self._add(f"bs {name} {R} {T} {phi} {alpha} {n1} {n2} {n3} {n4}")
        self._add_connection(name, n1, n2, n3, n4)

    def isolator(self, name, S):
        n1 = self.current_node
        n2 = self._new_node()
        self._add(f"isol {name} {S} {n1} {n2}")
        self._add_connection(name, n1, n2)
        self.current_node = n2

    def modulator(self, name, f, midx, order, mode, phase=0):
        n1 = self.current_node
        n2 = self._new_node()
        self._add(f"mod {name} {f} {midx} {order} {mode} {phase} {n1} {n2}")
        self._add_connection(name, n1, n2)
        self.current_node = n2

    def lens(self, name, f):
        n1 = self.current_node
        n2 = self._new_node()
        self._add(f"lens {name} {f} {n1} {n2}")
        self._add_connection(name, n1, n2)
        self.current_node = n2

    def photodiode(self, name, freqs=None, phases=None):
        line = f"pd{len(freqs or [])} {name}"
        if freqs:
            line += " " + " ".join(map(str, freqs))
        if phases:
            line += " " + " ".join(map(str, phases))
        line += f" {self.current_node}"
        self._add(line)
        self._add_connection(name, self.current_node)

    def qnoised(self, name, n, freqs_phases_nodes):
        self._add(f"qnoised {name} {n} " + " ".join(map(str, freqs_phases_nodes)))

    def qshot(self, name, num_demod, f, phase):
        self._add(f"qshot {name} {num_demod} {f} {phase} {self.current_node}")
        self._add_connection(name, self.current_node)

    def bp(self, name, direction, parameter):
        self._add(f"bp {name} {direction} {parameter} {self.current_node}")
        self._add_connection(name, self.current_node)

    def cp(self, cav_name, direction, parameter):
        self._add(f"cp {cav_name} {direction} {parameter}")

    def gouy(self, name, direction, spaces):
        self._add(f"gouy {name} {direction} {' '.join(spaces)}")

    def beam(self, name, f=None):
        self._add(f"beam {name}" + (f" {f}" if f else "") + f" {self.current_node}")
        self._add_connection(name, self.current_node)

    def fsig(self, name, component, sig_type, f, phase, amp=None):
        self._add(f"fsig {name} {component} {sig_type} {f} {phase}" + (f" {amp}" if amp else ""))

    def tem(self, input, n, m, factor, phase):
        self._add(f"tem {input} {n} {m} {factor} {phase}")

    def mask(self, detector, n, m, factor):
        self._add(f"mask {detector} {n} {m} {factor}")

    def attr(self, component, mode, val):
        self._add(f"attr {component} {mode} {val}")

    def gauss(self, name, component, node, w0, z, wy0=None, zy0=None):
        line = f"gauss {name} {component} {node} {w0} {z}"
        if wy0 and zy0:
            line += f" {wy0} {zy0}"
        self._add(line)

    def cav(self, name, comp1, node1, comp2, node2):
        self._add(f"cav {name} {comp1} {node1} {comp2} {node2}")

    def startnode(self, node):
        self._add(f"startnode {node}")

    def phase(self, mode):
        self._add(f"phase {mode}")

    def xaxis(self, comp, param, mode, start, stop, steps):
        self._add(f"xaxis {comp} {param} {mode} {start} {stop} {steps}")

    def const(self, name, value):
        self._add(f"const {name} {value}")

    def variable(self, name, value):
        self._add(f"variable {name} {value}")

    def func(self, name, expression):
        self._add(f"func {name} = {expression}")

    def lock(self, name, variable, gain, accuracy):
        self._add(f"lock {name} {variable} {gain} {accuracy}")

    def tf(self, name, factor, phase, terms):
        line = f"tf {name} {factor} {phase} " + " ".join(f"{t[0]} {t[1]} {t[2]}" for t in terms)
        self._add(line)

    def trace(self, level):
        self._add(f"trace {level}")

    def yaxis(self, mode):
        self._add(f"yaxis {mode}")

    def scale(self, factor, output=None):
        self._add(f"scale {factor}" + (f" {output}" if output else ""))

    def print_frequency(self):
        self._add("printfrequency")

    def print_noises(self):
        self._add("printnoises")

    def check_nodes(self):
        issues = []
        for node, comps in self.node_connections.items():
            if len(comps) < 2:
                issues.append(f"Warning: node '{node}' is only connected to: {comps}")
        return issues

    def save(self, filename="full_node_aware_finesse.kat"):
        path = f"/mnt/data/{filename}"
        with open(path, "w") as f:
            f.write("\n".join(self.lines))
        return path, self.check_nodes()


# Example test
gen = FullNodeAwareFinesseGenerator()
gen.laser("L1", 1, 0)
gen.space("s1", 1)
gen.modulator("EOM1", 10e6, 0.1, 1, "pm")

gen.mirror("M1", 0.99, 0.01)
gen.photodiode("PD1", freqs=[10e6], phases=[0])
gen.xaxis("L1", "f", "lin", -10e6, 10e6, 100)
gen.yaxis("abs")
gen.print_frequency()
gen.print_noises()

gen.save()
