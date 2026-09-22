from pathlib import Path
import re

p=Path('artikel/IDS.tex'); s=p.read_text(encoding='utf-8')
def rep(a,b):
    global s
    assert a in s,a[:80]
    s=s.replace(a,b,1)
rep('as a function of a common modelling time $t$:', 'as a function of time $t$:')
rep('Nominal frequencies are assumed constant. Laser phase fluctuations carry two MOSA indices here, $\\delta\\phi_{ij}$.', 'We use a single time coordinate, neglect relativistic time transformations, and retain constant nominal frequencies in the noise-coupling coefficients. The clock on spacecraft $i$ reads $t_i=t+q_i(t)$, where $q_i$ is its timing error.')
rep('As the beam propagates from \\ac{MOSA} $ij$ toward spacecraft $j$ and its \\ac{MOSA} $ji$, it accumulates phase contributions from Doppler shifts due to the relative spacecraft motion and from gravitational waves integrated along the arm.', 'Propagation from \\ac{MOSA} $ij$ to $ji$ delays the emitted phase and adds the GW response along the arm.')
rep('In the common-time model used here, this is a propagation-time decomposition; we do not include the transformations between spacecraft proper times contained in the proper pseudorange of \\cite{bayle_unified_2023}. ', '')
a=s.index('Keeping the nominal beat phase,'); b=s.index('The signal is then passed',a)
s=s[:a]+r'''After removing the nominal beat evolution, the sampled carrier phase fluctuations are
\begin{equation}\label{Main_LISA_eq}
    \begin{aligned}
    \delta\phi^{\mathrm c}_{ji}(t)={}&\mathbf D_{ji}\delta\phi_{ij}(t)-\delta\phi_{ji}(t)\\
    &+\delta\phi^{\mathrm{GW}}_{ji}(t)-\alpha_{ji}q_j(t).
    \end{aligned}
\end{equation}
Here $\alpha_{ji}$ is the beat frequency in the fixed-frequency approximation used for the noise model. For an orbit-dependent frequency plan, it would be replaced by the actual signed beat frequency, including Doppler shifts.

'''+s[b:]
rep('To complete the carrier readout model, we now include optical-bench motion and additive noise from the optical paths and readout electronics. The carrier phase measurement recorded on spacecraft $j$ for light received from spacecraft $i$ is', 'To connect this noise model to the measurements used for TDI, we also include the secondary disturbances in the science readout:')
rep('\\begin{align}\n    \\text{sci}^{\\text{c}}', '\\begin{align}\\label{eq:science_carrier}\n    \\text{sci}^{\\text{c}}')
rep('\\text{tm}_{ji}(t)= &', '\\text{tm}_{ji}(t)= &')
rep('\\bm{\\Delta}_{ji}(t)\\right),\\\\[5pt]', '\\bm{\\Delta}_{ji}(t)\\right),\\label{eq:testmass_readout}\\\\[5pt]')
rep('N^{\\text{ref}}_{ji}(t).\n\\end{align}', 'N^{\\text{ref}}_{ji}(t).\\label{eq:reference_readout}\n\\end{align}')
rep('The full LISA noise budget also includes tilt-to-length coupling, which is not represented in our testbed model. The testbed omits the test-mass and reference interferometers and does not reproduce optical-bench motion, backlink fiber noise, or test-mass acceleration noise; these terms are therefore omitted in the following sections.', 'These equations retain the terms needed to explain laser- and clock-noise suppression. A full instrument model includes further effects, such as tilt-to-length coupling and additional stray-light and optical-path disturbances. The miniLISA model omits the test-mass and reference interferometers and their associated bench-motion, backlink, and test-mass noise terms.')
rep('This illustrative conversion, is', 'This illustrative conversion is')
a=s.index('First-generation \\ac{TDI} combinations');b=s.index('Before \\ac{TDI} is implemented',a)
generation=s[a:s.index('Accurate knowledge',a)]
s=s[:a]+s[b:]
rep('Before \\ac{TDI} is implemented, intermediary variables are constructed. The reference and test-mass interferometer readings remove optical-bench displacement noise, as discussed in \\cite{otto2012tdi,tinto2018time}. ', 'The construction proceeds in two steps: local measurements first remove optical-bench motion and reduce the six laser noises to three; delayed combinations of the resulting links then suppress the remaining laser noise \\cite{otto2012tdi,tinto2018time}.')
rep('Using readouts (), (), and (), we can write', 'Using Eqs.~\\eqref{eq:science_carrier}, \\eqref{eq:testmass_readout}, and \\eqref{eq:reference_readout}, we form')
a=s.index('Further, as an example,');b=s.index('%\\begin{align*}',a)
s=s[:a]+r'''For the two-arm geometry used below, we use the Michelson observable $X_i$. Define the synthesized round-trip measurements
\begin{equation*}
    R_{ij}=\eta_{ij}+\mathcal D_{ij}\eta_{ji},\qquad
    R_{ik}=\eta_{ik}+\mathcal D_{ik}\eta_{ki}.
\end{equation*}
The first-generation combination is
\begin{equation}\label{eq:michelson_tdi}
    X_i=(1-\mathcal D_{ij}\mathcal D_{ji})R_{ik}
       -(1-\mathcal D_{ik}\mathcal D_{ki})R_{ij}.
\end{equation}
Here $\mathbf D$ describes propagation in the measurement chain, while $\mathcal D$ denotes a delay applied in post-processing. Cancellation requires the processing delays to match the physical delays. A mismatch $\delta d$ leaves a phase residual proportional to $\delta d\,\delta\dot\phi$, so either an inaccurate delay estimate or an untracked change in the physical delay can limit laser-noise suppression.

'''+generation+s[b:]
rep('For clock noise removal to work properly, the modulation must track the effective measurement-clock reference.', 'The modulation tone must carry the same timing fluctuations that enter the phase measurement. In LISA, pilot-tone correction removes the ADC sampling jitter, making the pilot tone the relevant clock reference. Noise added between this reference and the modulation tone limits the subsequent clock correction.')
a=s.index('Although both $N^m_{ij}$');b=s.index('The ultimate clock reference',a)
s=s[:a]+r'''Modulation and readout noise are kept separate because their transfer functions differ. A source modulation error appears in both local and delayed measurements, while a readout error is added in a particular measurement channel. Independent sources may be uncorrelated, but repeated appearances of the same source must still be combined before calculating its output noise power.

Dividing the modulation phase by its frequency gives $m_{ij}/\nu^m_{ij}=N_{ij}+N^m_{ij}/\nu^m_{ij}$. A higher modulation frequency therefore reduces the effect of a fixed phase noise, but leaves a fixed timing noise unchanged. Improving that timing-noise floor requires a quieter tone-generation chain. When the local and transmitted frequencies differ, the local timing contribution retains the factor $\nu^m_{ji}/\nu^m_{ij}$. A measurement at one modulation frequency cannot distinguish the two contributions.

'''+s[b:]
rep('The ultimate clock reference will be the pilot tone, which is also derived from the \\ac{USO} and is used to correct \\ac{ADC} sampling jitter within the \\ac{PMS}. ', '')
# Remove addressed review comments and superseded commented clock derivations.
s='\n'.join(l for l in s.split('\n') if not (l.startswith('% ') or l.startswith('%The local clock') or l.startswith('%Since a sample')))
p.write_text(s,encoding='utf-8')

p=Path('artikel/intro.tex');s=p.read_text(encoding='utf-8')
s=s.replace('The goal is for both noise sources, once processed through \\ac{TDI} and clock-noise calibration, to be reduced below the level required for gravitational-wave signal recovery across the core LISA measurement band.', 'More concretely, we look for residual laser and clock noise below the secondary-noise floor after processing, together with recovery of an injected GW signal at the expected amplitude and phase.')
s='\n'.join(l for l in s.split('\n') if not l.startswith('% This section'))
a=s.index('The article is divided as follows:')
s=s[:a]+r'''Section~\ref{sec:modelling} introduces the LISA measurements and noise-suppression combinations. Section~\ref{sec:setup} describes their laboratory implementation, and Section~\ref{sec:performance} estimates its performance from measured and calculated component noises. We then discuss possible extensions and remaining measurements.'''+ '\n'
p.write_text(s,encoding='utf-8')

p=Path('artikel/main.tex');s=p.read_text(encoding='utf-8')
s=s.replace('% honestly this paragraph sonds like a bunch of nonsense\n','')
s=s.replace('The delays allow us to study how light-travel times interact with clock synchronization and digital signal processing. Time-varying delays are particularly relevant: their order matters in TDI, and applying a delay before filtering need not give the same result as applying it afterwards. The hardware implementation makes these effects accessible to experimental tests.', 'The electronic delays place samples acquired several seconds apart in the same interferometric measurement. This lets us test noise cancellation with independently clocked hardware, including changes in the delay caused by the hardware clock itself.')
marker='We group the remaining uncorrelated board noise'
a=s.index(marker)
s=s[:a]+r'''The same board jitter also changes the physical duration of a programmed delay. For a constant command $d_{ij}$ in board time $u_i(t)=t+\epsilon_i(t)$, the input and output times satisfy $u_i(t)-u_i(t_{\mathrm{in}})=d_{ij}$. To first order,
\begin{align}
    d^{\mathrm{phys}}_{ij}(t)&=t-t_{\mathrm{in}}
      =d_{ij}+\delta d^\epsilon_{ij}(t),\\
    \delta d^\epsilon_{ij}(t)&=-(1-\mathbf D_{ij})\epsilon_i(t).
    \label{eq:board_delay_jitter}
\end{align}
Thus the physical delay can fluctuate even when its programmed value is known exactly. The resulting nominal carrier phase error $-\nu_{\mathrm R,j}\delta d^\epsilon_{ij}$ is already the board-jitter term above. Applying the perturbed delay to laser phase fluctuations also produces $-\delta d^\epsilon_{ij}\mathbf D_{ij}\delta\dot\phi_j^{\mathrm{eff}}$, a product of timing and laser-frequency noise omitted from the linear model. Its importance depends on the measured board jitter and input laser noise. A varying delay command additionally requires consistent conversion of the command timestamps between clock coordinates.

'''+s[a:]
marker='The additive phase noise $b^a_{ij}$'
a=s.index(marker)
s=s[:a]+r'''The board terms require an additional timing correction beyond the standard sideband correction for $q_i$. An independent timing measurement can be used to estimate and subtract their contributions from the carrier and sideband readouts. The remaining terms then depend on the timing-estimation error rather than the full $\epsilon_i$. This correction must also be consistent with the effective delays used in TDI; its residual is not determined by the additive electronic baseline alone.

'''+s[a:]
s=s.replace('reference to the common modelling time', 'reference to $t$')
s=s.replace('The waveform supplied for each directed link is evaluated at its reception time in the common modelling time coordinate.', 'Each directed-link waveform is evaluated at its reception time $t$.')
p.write_text(s,encoding='utf-8')
