from pathlib import Path
p=Path('artikel/model.tex');s=p.read_text(encoding='utf-8')
a=s.index('% This sounds');b=s.index(r'\subsection{Component',a)
s=s[:a]+r'''The component measurements identify which noises are likely to limit laser- and clock-noise suppression, and which parts of the setup need further characterization. We combine the measured electronic and modulation spectra with a calculation of the optical readout noise, then propagate them through TDI and clock correction. This gives an estimate of the residual noise expected from the characterized components, to be tested against the assembled instrument.

'''+s[b:]
a=s.index('% enough');b=s.index('The electronic input',a)
s=s[:a]+r'''The component spectra are shown as phase amplitude spectral densities in cycles/$\sqrt{\mathrm{Hz}}$.

The modulation characterization tracks the carrier and both sidebands of a local optical beat. The modulation and measurement clocks are referenced together so that their common timing fluctuations are intended to cancel. Taking half the upper-minus-lower sideband phase removes the common optical phase and retains the excess modulation phase. The measured spectrum therefore contains differential noise in the modulation chain together with readout noise and any imperfect rejection of the common timing fluctuations. It does not separately determine the timing contribution $N_i$ and the direct phase contribution $N_i^m$. For propagation through the three-spacecraft model, we assign this spectrum to independent source terms $m_i$.

'''+s[b:]
s=s.replace('as summarized in Table~\\ref{tab:readout_comparison}.', 'as summarized in Table~\\ref{tab:noise_comparison}.')
a=s.index(r'\begin{table}[t]');b=s.index(r'\end{table}',a)+len(r'\end{table}')
rows=[
('Laser frequency noise','Present','Present','Suppressed by TDI with matched delays; ideal cancellation in this estimate.'),
('Measurement-clock jitter $q_i$','Present','Present','Sideband-based post-processing correction; residual tone-generation noise remains.'),
('Modulation noise','Present','Present','Limits clock correction. Kept as source noise with its own transfer function.'),
('Optical readout noise','Weak received light; shot noise important','Bright beams; low predicted readout noise','Not removed. Added to the residual budget; shared input paths can introduce correlations.'),
('Carrier / sideband readout ASD','Allocations: $9\,\mathrm{pm}/\sqrt{\mathrm{Hz}}$ / $600\,\mu\mathrm{rad}/\sqrt{\mathrm{Hz}}$','Predictions: $0.0030\,\mathrm{pm}/\sqrt{\mathrm{Hz}}$ / $0.0637\,\mu\mathrm{rad}/\sqrt{\mathrm{Hz}}$','LISA plateau values versus the specified miniLISA detector operating point.'),
('Test-mass acceleration','Present','Not reproduced','Included only in the LISA comparison curve.'),
('Optical-bench motion and backlink noise','Present','Dedicated terms omitted','Local LISA combinations remove bench motion and reciprocal backlink terms.'),
('Tilt-to-length coupling','Present','Not explicitly modelled','Laboratory alignment and path noise can still enter the measured residual.'),
('Shared reference-laser noise','No laboratory reference laser','Present','Part of the effective source phase; suppressed by TDI in the ideal model.'),
('Delay-board timing jitter $\epsilon_i$','No electronic arm-delay board','Present','Needs an additional timing measurement and post-processing correction; residual not yet bounded here.'),
('Residual delay-board electronics','No electronic arm-delay board','Present','Measured baseline included as additive noise; not assumed to cancel.'),
('ADC and phasemeter noise','Present','Present','Ideal ADC quantization included; sampling jitter and residual electronics treated separately.'),
('Delay mismatch / processing residuals','Ranging and processing errors','Board-induced delay fluctuations and processing errors','Track effective delays; residuals require a separate bound beyond the static calculation.'),
]
table=r'''\begin{table*}[t]
\centering
\caption{Noise sources represented in miniLISA and their treatment in the present analysis. ``Not reproduced'' and ``omitted'' refer to the intended measurement model; they do not imply a noise-free laboratory. Readout numbers compare LISA science-interferometer allocations with calculated miniLISA detector noise, not measured total sensitivity.}
\label{tab:noise_comparison}
\small
\begin{tabular}{llll}
\hline
'''
for row in [('Noise source','LISA','miniLISA','Treatment / relevance')]+rows:
    table+=' & '.join(r'\parbox[t]{'+w+r'\textwidth}{'+c+'}' for w,c in zip(['0.19','0.20','0.20','0.32'],row))+r' \\[5pt]'+'\n'
    if row[0]=='Noise source':table+=r'\hline'+'\n'
table+=r'''\hline
\end{tabular}
\end{table*}'''
s=s[:a]+table+s[b:]
marker=r'\subsection{Propagation Through TDI and Clock Correction}'
s=s.replace(marker,r'''In miniLISA, detector noise enters before the electronic delay and digital subtraction, so copies of one input readout can be shared between links. Its exact propagation is therefore not identical to a noise added independently to each final LISA readout. The present estimate uses independent equivalent readout terms without taking credit for cancellation of shared inputs. Their small predicted contribution supports this approximation at the current operating point; stochasticity alone would not justify discarding correlations.

'''+marker)
s=s.replace('Board timing noise requires a measured spectrum or bound, and residual laser noise from imperfect delay knowledge requires a processing-error calculation.', 'The residual after board-timing correction requires a measured spectrum or bound. Delay-related laser residuals also need a calculation using the actual hardware timebase and the delays applied in post-processing.')
marker=r'\subsection{Further Characterization}'
s=s.replace(marker,r'''\subsection{Board Timing and Effective Delay}

A delay mismatch in miniLISA need not originate from an inaccurate estimate of the programmed delay. Equation~\eqref{eq:board_delay_jitter} shows that board timing fluctuations change its physical duration. For a constant delay $d_{ij}$ and stationary board jitter, the corresponding delay ASD is
\begin{equation}
 A_{\delta d^\epsilon_{ij}}(f)
 =2\left|\sin(\pi f d_{ij})\right|A_{\epsilon_i}(f).
\end{equation}
This provides a direct way to estimate the effect from a board-timing measurement. Its importance for TDI depends on the difference between the physical delay and the delay actually used in processing. If that variation is tracked, the relevant uncertainty is the residual tracking error.

The carrier coupling of this delay fluctuation is already included in the explicit $\epsilon_i$ term and must not be added again as independent ranging noise. The additional coupling to laser-frequency fluctuations is a product of two noise processes, so its spectrum cannot be obtained simply by multiplying their ASDs. A useful next test is to propagate a known laser-noise time series through the delay driven by the measured board timing, then apply the same timing correction and TDI delays used for the experiment. This would quantify the remaining delay error without assuming that it dominates the measured baseline.

'''+marker)
p.write_text(s,encoding='utf-8')

# Bring the conclusion into agreement with the conditional component estimate.
p=Path('artikel/main.tex');s=p.read_text(encoding='utf-8')
a=s.index('The current noise budget shows a mixed picture.');b=s.index('%\\newpage',a)
s=s[:a]+r'''The component measurements and readout calculation identify electronic and modulation noise as the larger contributions in the present estimate. Bright laboratory beams keep the predicted photodetector readout noise below the LISA science-interferometer allocations. Board timing introduces an additional coupling, including fluctuations of the effective delay, whose residual after timing correction still needs to be bounded. The component estimate therefore guides the next measurements; it does not yet establish the sensitivity of the complete optical testbed.

Further work will characterize the timing-correction residual, test cancellation with varying delays, and verify recovery of injected GW signals. A third inter-spacecraft arm and higher modulation frequencies would extend the configurations accessible to these tests. Higher modulation frequencies reduce the effect of fixed phase noise in clock transfer, while differential timing noise requires improvements to the clock-distribution and modulation chains themselves.

'''+s[b:]
p.write_text(s,encoding='utf-8')
