from pathlib import Path

p = Path('artikel/main.tex')
s = p.read_text(encoding='utf-8')
def replace(old, new):
    global s
    assert old in s, old[:100]
    s = s.replace(old, new, 1)
def section(start, end, new):
    global s
    a, b = s.index(start), s.index(end)
    s = s[:a] + new + '\n\n' + s[b:]

section(r'\subsection{Motivation for the Present Work}', r'\subsection{Measurement Philosophy}', r'''\subsection{Motivation for the Present Work}
The present work extends the electronic delay-line testbed with optical inputs and independent spacecraft clocks. It combines physical laser noise, sideband-based clock transfer, and hardware delays of several seconds, and uses component measurements to estimate the performance of the combined setup.

The delays allow us to study how light-travel times interact with clock synchronization and digital signal processing. Time-varying delays are particularly relevant: their order matters in TDI, and applying a delay before filtering need not give the same result as applying it afterwards. The hardware implementation makes these effects accessible to experimental tests.''')

section(r'\subsection{Measurement Philosophy}', r'\subsection{Optical Input}', r'''\subsection{Measurement Philosophy}
The testbed reproduces the laser-noise, clock-noise, and GW couplings of the LISA measurements. The first index of a link denotes the receiving \ac{SC}; source quantities carry a single spacecraft index, $\delta\phi_i$, $q_i$, and $\nu_i^m$. The target carrier phase fluctuations are
\begin{equation*}
    \delta\phi^{\mathrm c}_{ij}(t)
    =\mathbf D_{ij}\delta\phi_j(t)-\delta\phi_i(t)
    +\delta\phi^{\mathrm{GW}}_{ij}(t)-\alpha_{ij}q_i(t),
\end{equation*}
and the upper-sideband fluctuations are
\begin{align*}
    \delta\phi^{\mathrm{sb,+}}_{ij}(t)={}&
    \mathbf D_{ij}\delta\phi_j(t)-\delta\phi_i(t)
    +\delta\phi^{\mathrm{GW}}_{ij}(t)\\
    &-(\alpha_{ij}+\nu_j^m)q_i(t)+\nu_j^m\mathbf D_{ij}q_j(t).
\end{align*}
Here $\alpha_{ij}$ is the signed nominal carrier beat frequency. The sideband sampling coefficient is $\gamma_{ij}=\alpha_{ij}+\nu_j^m-\nu_i^m$; combining it with the local modulation phase gives the clock term above. Both channels use the common GW phase approximation of Section~\ref{sec:modelling}. We call a measurement \emph{LISA-like} when it reproduces these couplings. Modulation, board, and readout noises are added below.

An FPGA delay line supplies the propagation delay and the prescribed Doppler and GW frequency shifts. Heterodyning the optical fields with a common reference laser brings their phase information into the MHz range accessible to the electronics. The reference laser noise becomes part of the effective input laser noise, whose cancellation is discussed below.

The testbed omits the test-mass and reference interferometers, together with test-mass acceleration noise, optical-bench motion, backlink noise, and tilt-to-length coupling. Consequently, the local combinations $T_{ji}$ and $\xi_{ji}$ used to remove bench motion in Section~\ref{sec:modelling} are unnecessary. Identifying the two bench lasers on each spacecraft with a single source also removes the need for the reference differences $z_{ji}$: the synthesized links directly reproduce the three-laser structure of the $\eta$ observables.''')

start = s.index(r'\subsection{Optical Input}')
end = s.index('The role of the reference laser', start)
s = s[:start] + r'''\subsection{Optical Input}
Three lasers represent the spacecraft, each with an independent clock driving its modulation and phase measurement. A fourth laser provides the common optical reference. The setup supports frequency-offset locking between the spacecraft lasers and modulation for clock-tone transfer.
''' + s[end:]
replace('Both cavities are housed in a vacuum chamber surrounded by three layers of aluminum thermal shielding, which suppresses thermal fluctuations sufficiently to achieve LISA-like pre-stabilized \\ac{LFN} levels of around 30 Hz/$\\sqrt{\\text{Hz}}$ in the millihertz band.', 'Both cavities are housed in a vacuum chamber surrounded by three layers of aluminum thermal shielding. Based on simulations and experience with cavity stabilization, the target is a pre-stabilized \\ac{LFN} level of around 30 Hz/$\\sqrt{\\text{Hz}}$ in the millihertz band; this level has not yet been demonstrated in the present setup.')
replace('To enable a wider range of modulation frequencies, the reference laser is modulated as well, producing sideband-sideband beat notes on the photodetector. Otherwise, the electronic delay line ADCs pose a limitation on the modulation frequency. This modulation is currently used only for clock tone transfer. The beat notes entering the delay lines are therefore not themselves LISA-like; the final LISA-like observables are synthesised downstream using digital mixers.', 'The reference laser is unmodulated in the configuration described here, so the spacecraft carrier and sidebands each beat with the reference carrier. The modulation frequency must therefore keep all three electrical beat notes within the delay-line input bandwidth. These input tones carry the optical phase and clock information; the LISA-like carrier--carrier and sideband--sideband readouts are formed by digital subtraction downstream. Modulating the reference laser is a possible extension for higher modulation frequencies, discussed in Section~\\ref{sec:clock_extensions}.')
replace('in the IDS section. We retain both contributions', 'in Section~\\ref{clock noise}. We retain both contributions')
replace('The weaving of the photodetector signal between the delay line boards is illustrated in Figure 3.', 'The signal routing between the boards is illustrated in Fig.~\\ref{fig:triangular}.')

section(r'\subsection{The Delay Line}', r'\subsection{GW Signal Injection}', r'''\subsection{The Delay Line}
\label{sec:delay_line}
The digital delay line emulates the light-travel time along each directed link. Its architecture and electrical validation are described in Chapters~4--7 of \cite{ferguson_thesis_2026}; here we summarize the parts relevant to the optical testbed. The implementation described there supports delays up to 16 s, covering LISA's nominal one-way light-travel time of about 8.3 s. The available delay range depends on the memory allocation and the rate at which tracked frequency records are stored.

The implementation uses an AMD Xilinx ZCU208 RFSoC evaluation board, with integrated ADCs and DACs, FPGA programmable logic, and an embedded \ac{PS}. For each mixed link output, two ADC paths supply the remote and local electrical signals. Separate DPLLs track their carriers and sidebands. The remote frequency records are filtered, decimated, and stored in DDR4 memory; the local records supply the undelayed input to the digital subtraction. In the thesis configuration, the converters run at 2 GHz, the FPGA signal path at 125 MHz, and the remote records are stored at 15.625 MHz.

Orbital delays and GW link responses are computed in advance in Python and uploaded to the \ac{PS}. During playback, the \ac{PS} converts the model inputs into fixed-point commands and streams timestamped records to the programmable logic. The initial delay sets the memory read--write separation. Subsequent delay-rate commands control traversal through the stored records, with linear interpolation between adjacent records providing the fractional delay. The FPGA applies each command at its scheduled clock cycle; software supplies the stream without determining the precise actuation time. The interpolation grid alone does not establish the achieved delay accuracy, which also depends on filtering, signal bandwidth, and numerical precision.

After delayed readout, the FPGA adds the prescribed Doppler and GW frequency offsets and subtracts the tracked local frequency. It accumulates the resulting frequency separately for the carrier and both sidebands, synthesizes the three sinusoids, and combines them for the mixed DAC output. Doppler offsets evolve by accumulating the streamed Doppler-rate commands, whereas the GW command is added directly as a frequency offset. Section~\ref{sec:gw_injection} describes its optical scaling. Omitting the nominal frequency evolution, the intended carrier phase is
\begin{equation*}
    \mathbf D_{ij}\delta\phi_j^{\mathrm{eff}}
    -\delta\phi_i^{\mathrm{eff}}+\delta\phi^{\mathrm{GW}}_{ij},
    \qquad
    \delta\phi_i^{\mathrm{eff}}=\delta\phi_i-\delta\phi_{\mathrm R}.
\end{equation*}

Timing errors in the two ADC paths and the output DAC add phase errors at different frequencies. To retain this distinction, let $\epsilon^{\mathrm{A,r}}_{ij}$, $\epsilon^{\mathrm{A,l}}_{ij}$, and $\epsilon^{\mathrm D}_{ij}$ denote the remote-input ADC, local-input ADC, and output DAC timing errors relative to the common modelling time, with the clock-reading convention used in Section~\ref{sec:modelling}. For constant nominal frequencies and ideal transfer through the tracking and reconstruction stages, their contribution to channel $a\in\{\mathrm c,\mathrm{sb,+}\}$ is
\begin{align*}
    E^a_{ij}(t)={}&-f^a_{\mathrm r,ij}\mathbf D_{ij}\epsilon^{\mathrm{A,r}}_{ij}(t)
    +f^a_{\mathrm l,ij}\epsilon^{\mathrm{A,l}}_{ij}(t)\\
    &+f^a_{\mathrm{out},ij}\epsilon^{\mathrm D}_{ij}(t).
\end{align*}
Here $f^{\mathrm c}_{\mathrm r,ij}=\nu_{\mathrm R,j}$ and $f^{\mathrm c}_{\mathrm l,ij}=\nu_{\mathrm R,i}$; the upper-sideband input frequencies additionally contain $\nu_j^m$ and $\nu_i^m$, respectively. The signed synthesized frequency $f^a_{\mathrm{out},ij}$ includes any programmed output offset. The remote ADC error is delayed, the local ADC error changes sign in the subtraction, and the DAC error couples at the synthesized output frequency. This extends the ADC--mixer--DAC timing accounting in Section~6.1.2 of \cite{ferguson_thesis_2026} to distinct optical input frequencies. Shared clock distribution can correlate the three timing errors; it does not make their coupling frequencies interchangeable.

Only when all three timing errors equal $\epsilon_i$ and $f^a_{\mathrm{out},ij}=f^a_{\mathrm r,ij}-f^a_{\mathrm l,ij}$ does this reduce to $f^a_{\mathrm r,ij}(1-\mathbf D_{ij})\epsilon_i$. We retain $E^a_{ij}$ below to allow for the actual mixing and clock configuration. A time-dependent frequency plan additionally requires the corresponding time-dependent coefficients and processing response.

Other board phase noise is grouped with optical and final-phasemeter readout noise in $b^a_{ij}$ below, since the performance model treats these contributions as additive phase errors at the final link readout. This grouping is an approximation for the uncorrelated residuals. Modulation noise remains separate because it follows each source through shared local and delayed paths. The measured electronic baseline constrains the residual of its particular characterization chain; any timing or readout noise already included in that measurement must not be added again as an independent contribution.''')

replace('With one laser per \\ac{SC}, the required phase on the link from $j$ to $i$ is', 'The required phase on the link from $j$ to $i$ is')
replace('the first-order propagation model of the IDS section', 'the first-order propagation model of Section~\\ref{sec:modelling}')
replace('used in the IDS equations.', 'used in Section~\\ref{sec:modelling}.')
replace('% If the response is supplied as a fractional-frequency signal $y_{ij}=-\\dot H_{ij}$, the required command is simply $\\delta\\nu^{\\mathrm{inj}}_{ij}=\\nu_jy_{ij}$. ', 'The thesis supplies the link response as a fractional-frequency signal $y_{ij}=-\\dot H_{ij}$, so the command is $\\delta\\nu^{\\mathrm{inj}}_{ij}=\\nu_jy_{ij}$, using $\\nu_j\\simeq c/(1064\\,\\mathrm{nm})$ for the optical scale. This is the conversion in Eq.~(4.18) of \\cite{ferguson_thesis_2026}.')
replace('In the current delay-line implementation, a signed 32-bit GW word', 'In the implementation described in Section~4.4 of \\cite{ferguson_thesis_2026}, a signed 32-bit GW word')
replace('The frequency command is held between timestamped updates.', 'The signed word is extended to 64 bits without changing its frequency scale and is applied equally to the carrier and both sideband lanes. The frequency command is held between timestamped updates; the thesis uses a 4 Hz playback cadence for the mission-model experiment.')
replace("These are injection-path properties to be characterized or taken from the electrical implementation's characterization [REF: electrical delay-line work]; the equations here describe the intended signal response.", 'The command resolution is therefore not, by itself, a measurement of injection fidelity; the equations here specify the intended response of the optical testbed.')
replace('Now, at the level of the measurement model, the testbed corresponds to a LISA-like constellation in which there is no backlink noise and the two lasers on each \\ac{SC} are assumed to be perfectly phase-locked with zero offset. We further assume ideal reference and test-mass measurement and neglect optical-bench jitter. The optical modulation, board and readout noises introduced above are retained in the following measurements.', 'With the local-interferometer simplifications described above, the synthesized links can be used directly as $\\eta$ observables. Retaining the modulation, board, and readout noises gives the following measurement model.')
replace(r'\nu_{\mathrm{R},j}(1-\mathbf D_{ij})\epsilon_i(t)', r'E^{\mathrm c}_{ij}(t)')
replace(r'(\nu_{\mathrm{R},j}+\nu_j^m)(1-\mathbf D_{ij})\epsilon_i(t)', r'E^{\mathrm{sb,+}}_{ij}(t)')
replace('while the board timing error enters explicitly through $\\epsilon_i$.', 'while $E^a_{ij}$ contains the two ADC and output DAC timing contributions defined in Section~\\ref{sec:delay_line}. The final sampling coefficients are the signed output beat frequencies, $\\alpha_{ij}=f^{\\mathrm c}_{\\mathrm{out},ij}$ and $\\gamma_{ij}=f^{\\mathrm{sb,+}}_{\\mathrm{out},ij}$; the intended sideband spacing gives $\\gamma_{ij}-\\alpha_{ij}=\\nu_j^m-\\nu_i^m$.')
replace('The effective \\ac{SC} timing error $q_i$ and the board timing error $\\epsilon_i$ may be correlated through their reference distribution and are not assumed to be independent.', 'The effective \\ac{SC} timing error $q_i$ and the board timing errors may be correlated through their reference distribution and are not assumed to be independent.')
replace(r'&+(1-\mathbf D_{ij})\epsilon_i', r'&+\frac{E^{\mathrm{sb,+}}_{ij}-E^{\mathrm c}_{ij}}{\nu_j^m}')
replace(r'\subsection{Future Extensions: Changes to the Clock Noise Transfer System}', r'\subsection{Future Extensions: Changes to the Clock Noise Transfer System}'+'\n'+r'\label{sec:clock_extensions}')

# Remove the addressed review comments, preserving unrelated commented material.
a, b = s.index(r'\section{miniLISA Design}'), s.index(r'\input{model}')
part = '\n'.join(line for line in s[a:b].split('\n') if not line.lstrip().startswith('%'))
s = s[:a] + part + s[b:]
s = '\n'.join(line.rstrip() for line in s.split('\n'))
p.write_text(s, encoding='utf-8')

bib = Path('artikel/citations.bib')
entry = r'''

@phdthesis{ferguson_thesis_2026,
  author = {Ferguson, Reid},
  title = {Hardware Simulations of Inter-satellite Interactions for the Laser Interferometer Space Antenna},
  school = {Leibniz University Hanover},
  year = {2026},
  month = sep,
  note = {Thesis manuscript dated September 8, 2026}
}
'''
assert 'ferguson_thesis_2026' not in bib.read_text(encoding='utf-8')
with bib.open('a', encoding='utf-8') as f:
    f.write(entry)
