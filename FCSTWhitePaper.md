LISA Frequency Control White Paper
Daniel Shaddock1,2, Kirk McKenzie1, Robert Spero1, Jeffrey Livas3, Ira Thorpe3,
Brent Ware1, Glenn de Vine1, Danielle Wuchenich1,2, Kenji Numata3, Gerhard
Heinzel4, Benjamin Sheard4, Juan Jos´e Esteban Delgado4, Felipe Guzm´an4,
Antonio Francisco Garcia Marin4, Peter Gath5, Hans-Reiner Schulte5, David
Robertson6, Harry Ward6, Jordan Camp3, Guido Mueller7, Roger Diehl1, Moshe
Pniel1, Robin Stebbins3, Mansoor Ahmed3, Stephen Merkowitz3, Vinzenz Wand7,
Yinan Yu7, Dylan Sweeney7, Alix Preston7, Shawn Mitryk7, Oliver Jennrich8, Paul
McNamara8, Marcello Sallusti8, Alberto Gianolio8, Luigi D’Arcio8, Karsten
Danzmann4, Dennis Weise5, Pete Bender9, and Bill Klipstein1
1Jet Propulsion Laboratory, California Institute of Technology
2The Australian National University
3NASA Goddard Space Flight Center
4Max Planck Institut fu¨r Gravitationsphysik (Albert Einstein Institut)
5Astrium
6University of Glasgow
7University of Florida
8European Space Agency
9JILA, University of Colorado, Boulder
July 30, 2009

| CONTENTS |     |     |     | 2   |
| -------- | --- | --- | --- | --- |
Contents
| 1 Introduction      |           |                    |     | 4   |
| ------------------- | --------- | ------------------ | --- | --- |
| I Laser             | Frequency | Control Subsystems |     | 5   |
| 2 Pre-stabilization |           |                    |     | 5   |
2.1 Cavity Stabilization . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
2.2 Tunable Stabilized Lasers . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
2.3 Frequency Acquisition . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
2.4 Iodine Stabilization . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
2.5 Mach-Zehnder Stabilization . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
| 3 Arm | Locking |     |     | 26  |
| ----- | ------- | --- | --- | --- |
3.1 Measurement Architecture for Arm Locking . . . . . . . . . . . . . . . . . . 26
3.2 Frequency Noise After Arm Locking . . . . . . . . . . . . . . . . . . . . . . 27
3.3 Modified Dual Arm Locking . . . . . . . . . . . . . . . . . . . . . . . . . . . 28
3.4 Laser Frequency Pulling . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30
3.5 Noise Limits . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34
3.6 The Arm Locking Controller . . . . . . . . . . . . . . . . . . . . . . . . . . 37
3.7 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 41
| 4 Time-Delay | Interferometry |     |     | 43  |
| ------------ | -------------- | --- | --- | --- |
4.1 Ranging Limited Performance . . . . . . . . . . . . . . . . . . . . . . . . . . 43
4.2 Ranging System . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 46
4.3 Algorithm Errors . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 51
4.4 Interpolation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 52
4.5 Analog Chain . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 56
4.6 Phasemeter Digital Signal Processing . . . . . . . . . . . . . . . . . . . . . . 60
4.7 Scattered Light . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 61
4.8 Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 64
| II Frequency | Noise  | Suppression | System Options | 65  |
| ------------ | ------ | ----------- | -------------- | --- |
| 5 Fixed      | Cavity |             |                | 66  |
5.1 Design Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 66
5.2 Performance . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 67

| CONTENTS      |      |     | 3   |
| ------------- | ---- | --- | --- |
| 6 Arm Locking | Only |     | 67  |
6.1 Design Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 68
6.2 Performance . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 68
| 7 Arm Locking | with Tunable | Cavity Pre-stabilization | 68  |
| ------------- | ------------ | ------------------------ | --- |
7.1 Design Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 69
7.2 Performance . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 71
| 8 Arm Locking | with Mach-Zehnder | Pre-stabilization | 71  |
| ------------- | ----------------- | ----------------- | --- |
8.1 Design Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 71
8.2 Performance . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 74

1 INTRODUCTION 4
1 Introduction
The LISA Frequency Control Study Team was established to provide a forum for practi-
tioners to understand existing work in the field. The study team, formed in July 2008,
participated in a series of teleconferences leading up to a meeting at Caltech from Octo-
ber 28-30, 2008. This white paper documents the state of knowledge in the area of laser
frequency control for LISA.
Part I summarizes the performance of component subsystems for laser frequency noise
control and suppression. Section 2 describes techniques for laser pre-stabilization to length
references and atomic transitions. Section 3 presents a possible implementation of arm
locking along with a detailed analysis of the predicted performance. Section 4 summarizes
the noise suppression capabilities of Time-Delay Interferometry. Part II describes how in-
dividual frequency noise suppression techniques are combined into systems and estimates
their levels of frequency stability. Four options are considered: fixed cavity; arm lock-
ing; cavity pre-stabilization and arm locking; and Mach-Zehnder pre-stabilization and arm
locking.
106
104
102
100
10−2
10−4 10−3 10−2 10−1 100 101
Frequency[Hz]
]zHtr/zH[
esioN
TDI Capability
Arm locking only
Cavity only
Mach-Zehnder prestabilization
and arm locking
Cavity prestabilization
and arm locking
Figure 1: Comparison of predicted laser frequency noise for different stabilization system
options. Arm length mismatch of ∆τ = 0.026s. Also shown is the noise suppression
capability of TDI, assuming 1m ranging error.
The predicted frequency noise produced by these four options is shown in Figure 1.
Also shown is the noise suppression capability of Time-Delay Interferometry (assuming
1m arm length knowledge accuracy). This level represents the maximum allowable laser
frequency noise consistent with the LISA error allocation.

5
Part I
Laser Frequency Control Subsystems
2 Pre-stabilization
Pre-stabilization is the term given to the first stage of frequency noise control that reduces
the free-running noise of a laser by locking the laser to a reference. The reference can be
either an absolute reference, such as an atomic or molecular system, or it can be a relative
reference, such as an optical cavity. Only one pre-stabilization system is required at any
time to stabilize the master laser. The other lasers will inherit the frequency stability of
the master laser via phase-locking.
2.1 Cavity Stabilization
Optical cavities provide a relatively simple form of frequency stabilization that has been
well studied in the laboratory. A cavity is formed from two or more low-loss mirrors
arranged so that light may circulate between them [1]. A laser beam is coupled into the
cavityviaoneofthemirrors. Iftheincidentandcirculatingbeamsareinphase,lightbuilds
up in the cavity and it is said to be on resonance. Cavity-based laser stabilization works
by diverting a small fraction of light from the laser to the cavity, detecting the resonant
light, and controlling the laser frequency to maintain the resonance condition with high
accuracy. The ultimate achievable frequency stability, ∆ν, is limited by the fractional
length stability, ∆L/L. By building the cavity with thermally stable materials, ∆L/L can
be 10−13 or smaller, which would give ∆ν = 30Hz.
Itisimportanttonotethatthecavitydoesnotprovideanabsolutefrequencyreference.
Instead, there is a comb of transmission peaks spaced by the cavity’s free spectral range,
any one of which can provide the reference signal.
The standard technique used for stabilizing lasers to optical cavities for high precision
applications is based on a method known as Pound-Drever-Hall (PDH) locking [2, 3].
By phase-modulating the incident beam and demodulating the reflected power at the same
frequency,PDHgeneratesazero-crossingerrorsignalcenteredaroundthecavityresonance.
This error signal is then used by a control system to match the incident laser field to the
cavity resonance. Using the reflected beam for the error signal avoids a time delay and
therefore the resulting gain limitation that occurs when using a cavity with a very long
storage time.
2.1.1 Key Parameters and Requirements
The cavity should have a moderately high finesse (∼10,000) to maximize the slope of
the error signal while avoiding the technical issues associated with extremely high finesse

| 2 PRE-STABILIZATION |     |     |     |     |     |     |     | 6   |
| ------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
cavities. For the LISA application, the cavity should be designed to minimize thermally-
induced changes in the optical path length, typically the dominant source of noise at
sub-Hz Fourier frequencies. Laboratory cavities used in this regime are typically Fabry-
Perot cavities consisting of low-loss mirrors that are contacted or otherwise bonded onto a
rigid spacer of low-expansion material such as Zerodur or ULE. The cavity is then placed
in a vacuum chamber and isolated from environmental disturbances such as temperature
fluctuations and vibration. Table 1 shows some of the typical parameters for a Fabry-Perot
style cavity. High finesse cavities require careful spatial alignment and mode matching for
| optimum   | performance. |          |         |             |           |          |                   |     |
| --------- | ------------ | -------- | ------- | ----------- | --------- | -------- | ----------------- | --- |
|           |              | Table 1: | Typical | Fabry-Perot | Reference |          | Cavity Parameters |     |
| Parameter |              |          |         | Value       |           | Comments |                   |     |
| Cavity    | Parameters   |          |         |             |           |          |                   |     |
Free Spectral Range (FSR) ∼ 500MHz ∼ 30cm length cavity spacer
| Finesse |           |        |     | ∼ 10,000 |     | Large       | error signal slope |     |
| ------- | --------- | ------ | --- | -------- | --- | ----------- | ------------------ | --- |
| Cavity  | Linewidth | (FWHM) |     | 50kHz    |     | FSR/Finesse |                    |     |
∼
Power into cavity 1mW Performance limited by thermal fluctua-
∼
|     |     |     |     |     |     | tions, | not shot noise |     |
| --- | --- | --- | --- | --- | --- | ------ | -------------- | --- |
PDH Parameters
Modulation Frequency >5MHz Above the band of technical laser noise
Loop Bandwidth 10kHz - 30kHz Limited by piezo-electric laser frequency
∼
actuator
| 2.1.2 Basic | System |     | Configuration |     |     |     |     |     |
| ----------- | ------ | --- | ------------- | --- | --- | --- | --- | --- |
Figure 2 shows the basic configuration of a PDH frequency stabilization system with the
| components      | listed | in detail   | in Table | 2.  |     |     |     |     |
| --------------- | ------ | ----------- | -------- | --- | --- | --- | --- | --- |
| 2.1.3 Reference |        | Performance |          |     |     |     |     |     |
The frequency stability requirement from the LISA pre-Phase A report[5] is a residual
| frequency | noise | spectral | density | in the | LISA measurement |     | band of: |     |
| --------- | ----- | -------- | ------- | ------ | ---------------- | --- | -------- | --- |
√
|     |     |     | ν(f) = | 30Hz/ | Hz· (cid:112) | 1+(3mHz/f)4. |     | (1) |
| --- | --- | --- | ------ | ----- | ------------- | ------------ | --- | --- |
This performance level has been achieved in several laboratories, for example,[6].

| 2 PRE-STABILIZATION |     |     |     |     |     |     | 7   |
| ------------------- | --- | --- | --- | --- | --- | --- | --- |
Table 2: List of the most commonly used components for the standard Pound-Hall-Drever
| frequency stabilization | to a fixed cavity | reference scheme. |     |          |     |     |     |
| ----------------------- | ----------------- | ----------------- | --- | -------- | --- | --- | --- |
| Device                  | Type              | Function          |     | Comments |     |     |     |
Laser Optical Light source to be sta- Must have sufficient fre-
|     |     | bilized |     | quency       | tuning | bandwidth |          |
| --- | --- | ------- | --- | ------------ | ------ | --------- | -------- |
|     |     |         |     | (∼100kHz)    |        | to        | suppress |
|     |     |         |     | free-running |        | noise.    |          |
Phase modulator Electro-Optical Modulates optical Typically an electro-optic
|     |     | phase of beam   | accord- | modulator |          | (EOM).    | Bulk-  |
| --- | --- | --------------- | ------- | --------- | -------- | --------- | ------ |
|     |     | ing to electric | drive   | crystal   | versions | must      | be     |
|     |     | amplitude       |         | made      | resonant | to        | reduce |
|     |     |                 |         | drive     | voltage. | Waveguide |        |
|     |     |                 |         | versions  | have     | naturally | low    |
drive voltage.
Polarizing Beam Optical Separates incoming Unnecessary in a ring cavity
| Splitter (PBS) |     | from outgoing | beams |     |     |     |     |
| -------------- | --- | ------------- | ----- | --- | --- | --- | --- |
Quarter wave Optical Separates incoming Unnecessary in a ring cavity
| plate (QWP) |     | from outgoing | beams |     |     |     |     |
| ----------- | --- | ------------- | ----- | --- | --- | --- | --- |
Local Oscillator Electronic Sinusoidalsignalsource. Could be analog or digital
| (LO) |     | Drives modulator | and | (NCO) |     |     |     |
| ---- | --- | ---------------- | --- | ----- | --- | --- | --- |
demodulator
Demodulator Electronic Demodulates light to Could be analog (mixer) or
|     |     | generate error | signal | digital | (multiplier) |     |     |
| --- | --- | -------------- | ------ | ------- | ------------ | --- | --- |
Filter Electronic Shapes error signal to Could be analog or digital
|     |     | generate laser | control |     |     |     |     |
| --- | --- | -------------- | ------- | --- | --- | --- | --- |
signal
| Photoreceiver | Electronic | Detects reflected | power |     |     |     |     |
| ------------- | ---------- | ----------------- | ----- | --- | --- | --- | --- |
| (PR)          |            | from the cavity   |       |     |     |     |     |

2 PRE-STABILIZATION 8
Figure 2: Block diagram of a standard Pound-Drever-Hall laser stabilization system show-
ing a reference cavity, phase modulator, polarizing beam splitter (Pol. BS), quarter-wave
plate (QWP), and photoreceiver (PR). The local oscillator (LO) is the sinusoidal signal
source driving the modulator and demodulator.
2.2 Tunable Stabilized Lasers
The ability to tune the central frequency of a pre-stabilized reference without substan-
tially compromising the frequency noise performance is important for combining and/or
cascading the pre-stabilization with other frequency references such as the arms of the
LISA constellation. In this section we consider modifications to the basic cavity locking
techniques that allow the central frequency to be tuned. Other methods for achieving tun-
ability, such as acousto-optic modulators and offset-locked lasers, are possible but are not
discussed here.
2.2.1 Tunability Requirements
Afrequencytuningrangeofmorethanafreespectralrangeofthereferencecavity,typically
several hundred MHz (see Table 1), would provide the greatest flexibility. In Section 3 we
show that arm locking could pull the laser frequency by up to 300MHz from its nominal
value due to errors in the Doppler estimate. However, this Doppler estimate is obtained
√
assuming no pre-stabilization. With 30Hz/ Hz pre-stabilization and 200s for Doppler
estimation, the expected frequency pulling is less than 10MHz. In addition, the frequency
response of the tunability should be sufficient to support a high gain auxiliary locking
scheme such as arm locking. Furthermore, the tuning capability must not substantially
degrade the pre-stabilized noise performance within the LISA measurement band.

2 PRE-STABILIZATION 9
| 2.2.2 PZT Tunable | Cavities |     |     |     |     |
| ----------------- | -------- | --- | --- | --- | --- |
One way to make a frequency reference tunable is to include an actuator that can change
the optical path length inside the resonant cavity. This can be accomplished by changing
the cavity length. Figure 3 shows an example design for a Fabry-Perot cavity with a piezo-
electric element in the cavity. The PZT has a silver coating on the wide faces that allow
hydroxide bonding to be used in joining the fused silica mirror and the Zerodur spacer.
|     |             | PZT Material | Zerodur |               |     |
| --- | ----------- | ------------ | ------- | ------------- | --- |
|     | Flat Mirror |              |         | Curved Mirror |     |
Optical
Hydroxide Bonds
Contact
|     | Figure | 3: Side | view of | the PZT cavity. |     |
| --- | ------ | ------- | ------- | --------------- | --- |
The best measurements achieved so far with this technique show excess noise (∼
√
2kHz/ Hz).
| 2.2.3 Electro-optic | Modulator |     | Tuning |     |     |
| ------------------- | --------- | --- | ------ | --- | --- |
Another method for tuning a laser pre-stabilized to a fixed frequency reference is through
the use of sideband locking[7]. In sideband locking, an additional tone is added to the
phase modulator drive that generates the PDH error signal. This tone, a sideband to the
laser carrier, is locked to the reference cavity and as the frequency of the tone is varied,
the center frequency of the pre-stabilized laser is tuned. The required components are
identical to those shown in the block diagram in Figure 2, except that the modulator
must be broadband, not resonant, to allow for tunability, and the electronic signal driving
the modulator must be a slightly more complex waveform than the sinusoidal reference
required for standard PDH locking. No modifications to the reference cavity are required,
andstandardPDHisrecoveredbyremovingthesidebandtone. Thistechniqueisdescribed
in detail in Reference[7]. Similar performance as compared to a standard PDH system has
√
| been demonstrated | (Figure | 4), however | not at the | level of 30Hz/ | Hz. |
| ----------------- | ------- | ----------- | ---------- | -------------- | --- |

2 PRE-STABILIZATION 10
Figure 4: Measured frequency noise of a sideband-locked pre-stabilized laser[7].
Figure 5: Simplified interface drawing showing key interactions with other systems needed
for frequency stabilization. Not shown are standard interfaces to the spacecraft bus for
electrical power, housekeeping information, and normal command and control.

2 PRE-STABILIZATION 11
2.3 Frequency Acquisition
The process of setting a given laser to a specified frequency offset from the incoming
laser frequency is known as “frequency acquisition” and is necessary to make the science
measurements. The relative offsets of each laser in the LISA system are pre-computed and
uploadedtoeachspacecraftaspartofthefrequencyplan. Theuseofanabsolutefrequency
referencemakesitpossibleinprincipletouseadeterministicproceduretosettheindividual
laserstospecificoffsetfrequencies. Ifalllasersarefirstlockedtothisreference, theycanbe
offsetlockedbythespecifiedamountsimplybytuning. Alternatively, anabsolutereference
can be used as a diagnostic device to measure the frequency of a laser locked to a relative
reference and to decide how to tune the offsets to the correct value.
Without an absolute frequency reference, it is necessary to search for the correct fre-
quency offset by changing the operating state of one in a pair of heterodyning lasers.
Although the absolute frequency is not known as precisely as it could be when determined
with an absolute reference, it is known approximately from the characterization of the
lasers during ground testing. For example, the lasing frequency of a non-planar ring oscil-
lator (NPRO) is a function of the pumping conditions (the current to the pump diode) and
the temperature of the crystal. The frequency of the laser can be measured as a function of
these parameters and then the parameters may be used to set the correct operating point
of the laser frequency. The parameters may be swept while monitoring for a beat note.
Preliminary tests [8] of a scanning procedure have shown beat note acquisition of lasers up
to 5GHz apart is possible in less than 1 minute using the 20MHz bandwidth analog chain
and phasemeter. Although these tests did not use representative LISA power levels, the
algorithm was designed to work with the anticipated LISA signal-to-noise ratio.
2.4 Iodine Stabilization
Laser frequency stabilization employing iodine has many similarities to cavity stabilization
[9]. Instead of stabilizing the frequency to the resonance of an optical cavity, the laser
frequency is referenced to a hyperfine transition of molecular iodine, I . An additional
2
complexity over cavity stabilization is the need to frequency-double a small portion of
power from the fundamental laser frequency, changing the wavelength from 1064nm to
532nm in order to access the strong, narrow hyperfine transitions of iodine. The frequency
of the transition is determined by the molecular physics of the iodine system; this transi-
tion frequency provides an absolute frequency reference. Known molecular transitions at
1064nm are many orders-of-magnitude weaker than iodine at 532nm and would require
more complex arrangements to obtain the required frequency stability.
Like an optical cavity, the iodine transition has both an amplitude and phase response.
Anumberofdifferentmethodscanbeemployedtoextractanerrorsignalfromtheabsolute
frequencyofthehyperfinetransition. Alasercanbelockedonresonancewiththetransition
inasimilarfeedbackschemetothePDHtechnique[10,11]. Thenarrowhyperfinetransition

2 PRE-STABILIZATION 12
isaccessedbyusingtwocounter-propagatingbeamstolimitDopplereffects,whilethebroad
| absorption | features |     | are accessed |     | by a single | transmitted | beam. |
| ---------- | -------- | --- | ------------ | --- | ----------- | ----------- | ----- |
FrequencystabilizationwithiodinecouldofferanumberoffeaturesforLISA,including:
An absolute frequency reference for reducing risk in frequency lock acquisition. To
•
ensure that the lasers on separate spacecraft have frequencies within 20MHz (so
that their beat notes will appear on the photodiode), it will be necessary to use
a frequency-scanning algorithm that will be implemented in parallel with a spatial
acquisition algorithm. There is no wavefront sensing available until the beat note is
< 20MHz. The use of iodine would fix the laser frequencies to an absolute value, so
|     | that their | absolute | frequencies |     | are within | a few | kHz; |
| --- | ---------- | -------- | ----------- | --- | ---------- | ----- | ---- |
• The iodine system is less sensitive to environmental disturbances than a cavity, thus
its use may simplify aspects of the payload systems engineering. Iodine would not
requireanyexternaltemperaturestabilization(foremploymentasawavemeteronly),
potentially eliminating the need for the additional mass associated with thermal
isolation. Its requirement for alignment control is also reduced by approximately a
|     | factor of | 10 compared |     | to a | cavity; |     |     |
| --- | --------- | ----------- | --- | ---- | ------- | --- | --- |
• Many of the iodine components have been flight qualified: including gas cells, dou-
|     | bling crystal, | modulator, |     | and | optics. |     |     |
| --- | -------------- | ---------- | --- | --- | ------- | --- | --- |
A number of options exist for the iodine implementation, of varying degrees of com-
plexity. They range from full pre-stabilization of the laser, including feedback control, to a
simple wavemeter which only reads out the absolute laser frequency. All options have the
| following | characteristics: |     |     |     |     |     |     |
| --------- | ---------------- | --- | --- | --- | --- | --- | --- |
• A high efficiency doubling waveguide, providing several mW of green (532nm) light
with ∼100mW IR (1064nm) light input. The waveguide is operated at room tem-
|     | perature, | eliminating |     | the need | for a heater; |     |     |
| --- | --------- | ----------- | --- | -------- | ------------- | --- | --- |
• A fully fiber-coupled implementation, including waveguide, gas cell, and modulators.
Below we describe in more detail the options for the iodine implementation, including
| schematic | layouts | and | noise | performance. |     |     |     |
| --------- | ------- | --- | ----- | ------------ | --- | --- | --- |
1. Pre-stabilization: this configuration will allow for pre-stabilization of the in-band
laserfrequency,aswellasfixtheabsolutefrequency. Itrequirestheuseofmodulators
and a cooler. Two sub-options are given, along with measured noise of each option.
|     | (a) Complete |     | setup | (Figure | 6): |     |     |
| --- | ------------ | --- | ----- | ------- | --- | --- | --- |
√
|     | i.  | 50Hz/ | Hz       | at 1mHz;  |     |     |     |
| --- | --- | ----- | -------- | --------- | --- | --- | --- |
|     | ii. | ∼kHz  | absolute | accuracy. |     |     |     |

2 PRE-STABILIZATION 13
|     |            | Figure | 6: Complete   |     | iodine frequency | stabilization | setup. |
| --- | ---------- | ------ | ------------- | --- | ---------------- | ------------- | ------ |
| (b) | Simplified |        | setup (Figure | 7): |                  |               |        |
√
|     | i.  | 200Hz/  | Hz at         | 1mHz;     |                  |               |        |
| --- | --- | ------- | ------------- | --------- | ---------------- | ------------- | ------ |
|     | ii. | ∼10 kHz | absolute      | accuracy. |                  |               |        |
|     |     | Figure  | 7: Simplified |           | iodine frequency | stabilization | setup. |
2. Wavemeter: this option provides solely for the absolute frequency reference. It is a
very simplified setup, using no modulators, heater, cooler, or feedback electronics.
| (a) | Fine   | wavemeter    | configuration |         | (Figure    | 8):            |     |
| --- | ------ | ------------ | ------------- | ------- | ---------- | -------------- | --- |
|     | i.     | Mechanical   | modulation    |         | on mirror; |                |     |
|     | ii.    | On hyperfine | resonance:    |         | ∼10kHz;    |                |     |
|     | iii.   | Coarse       | knowledge:    | ∼10MHz. |            |                |     |
|     |        |              | Figure        | 8: Fine | wavemeter  | configuration. |     |
| (b) | Coarse | wavemeter    | configuration |         | (Figure    | 9):            |     |

2 PRE-STABILIZATION 14
|       | i. Coarse   | knowledge:  |     | ∼10MHz. |           |                |     |
| ----- | ----------- | ----------- | --- | ------- | --------- | -------------- | --- |
|       |             | Figure      | 9:  | Course  | wavemeter | configuration. |     |
| 2.4.1 | Performance | Improvement |     | Options |           |                |     |
Additional research on the iodine system will involve looking into further simplifications.
For example, it may be possible to simultaneously shorten the iodine cell to several cen-
timeters in length while raising the iodine gas density by eliminating the cooler. This
could result in a simpler and more compact system, though the noise and stability of this
| possibility | remains    | to be quantified. |          |            |     |          |            |
| ----------- | ---------- | ----------------- | -------- | ---------- | --- | -------- | ---------- |
| 2.4.2       | Comparison | of                | Absolute | References |     | at 532nm | and 1064nm |
A comparison of possible absolute optical frequency references at 532nm and 1064nm is
shown in Table 3. Although there are other alternatives, it appears that Doppler-free
| operation        | of molecular | iodine        | offers | the best | performance. |     |     |
| ---------------- | ------------ | ------------- | ------ | -------- | ------------ | --- | --- |
| 2.5 Mach-Zehnder |              | Stabilization |        |          |              |     |     |
The LISA Technology Package (LTP) on board LISA Pathfinder uses an unequal path
length, heterodyne Mach-Zehnder interferometer to measure and actively stabilize the
laser frequency fluctuations[12, 13]. In this approach the path length mismatch of the
interferometer is used as the frequency reference. In comparison to an optical cavity or
molecular reference, the technique has a wide operating range and does not require a com-
plex lock acquisition procedure. Frequency tuning can be provided by purely electronic
means and does not require physically changing the path length (or resonance frequency)
| of the frequency | reference.         |     |     |     |     |     |     |
| ---------------- | ------------------ | --- | --- | --- | --- | --- | --- |
| 2.5.1            | System Description |     |     |     |     |     |     |
Figure 10 shows the basic system layout for a heterodyne Mach-Zehnder interferometer
with a path length mismatch that could be integrated on the LISA optical bench. The
reference interferometer measures the phase difference (φ ) between the lasers on adjacent
R
optical benches within one LISA satellite. This reference interferometer already exists in
the current LISA optical bench design. An additional interferometer with unequal path
lengths could be placed on the optical bench to measure the frequency noise of the master
| laser, as | will be implemented |     | in LISA | Pathfinder[12, |     | 13]. |     |
| --------- | ------------------- | --- | ------- | -------------- | --- | ---- | --- |

| 2 PRE-STABILIZATION |       |               |             |           |            |         |        | 15  |
| ------------------- | ----- | ------------- | ----------- | --------- | ---------- | ------- | ------ | --- |
|                     | Table | 3: Comparison | of Absolute | Frequency | References |         |        |     |
| System              |       | Linewidth     | Pros        |           | Cons &     | Special | Issues |     |
Iodine (I ) @ ∼1MHz Long History DoublingCrystalNeeded(30-50◦C)
2
| 532nm, | Doppler- |     |     |     |     |     |     |     |
| ------ | -------- | --- | --- | --- | --- | --- | --- | --- |
free
|     |     |     | Well-identified | lines   | Cell cooling   | prefereable |      | (∼5◦C) |
| --- | --- | --- | --------------- | ------- | -------------- | ----------- | ---- | ------ |
|     |     |     | High Stability  | demo-ed | Repeatability: |             | >few | kHz    |
Iodine (I ) @ ∼700MHz Simple Setup (Heated) Doubling Crystal Needed
2
| 532nm, | Doppler- |     |     |     | (30-50◦C) |     |     |     |
| ------ | -------- | --- | --- | --- | --------- | --- | --- | --- |
Broadened
|     |     |     | Very Strong | lines | Cell cooling | may       | be  | needed        |
| --- | --- | --- | ----------- | ----- | ------------ | --------- | --- | ------------- |
|     |     |     |             |       | 103× worse   | stability |     | than Doppler- |
free
|     |     |     |     |     | Repeatability: |     | > few | MHz |
| --- | --- | --- | --- | --- | -------------- | --- | ----- | --- |
Cesium (Cs ) ∼10MHz Well-known RF refer- Weakness of line, large temperature
2
|           |     |       | ence        |                 | shift           |         |        |     |
| --------- | --- | ----- | ----------- | --------------- | --------------- | ------- | ------ | --- |
|           |     |       | Flight      | heritage in GPS | Heater (∼200◦C) |         | needed |     |
|           |     |       | No doubling | crystal         | Cavity may      | be      | needed |     |
| Acetylene | C H | ∼1MHz | Well-known  | 1.5µm ref-      | Weakness        | of line |        |     |
2 2
| or  | C HD, |     | erence |     |     |     |     |     |
| --- | ----- | --- | ------ | --- | --- | --- | --- | --- |
2
Doppler-free
|     |     |     | No doubling | crystal | Cavity may | be  | needed |     |
| --- | --- | --- | ----------- | ------- | ---------- | --- | ------ | --- |
No heater
| Carbon | dioxide | ∼2GHz | No Doubling | Crystal | Weakness | of line |     |     |
| ------ | ------- | ----- | ----------- | ------- | -------- | ------- | --- | --- |
(CO )
2
|     |     |     |     |     | Small number |     | of demonstrations |     |
| --- | --- | --- | --- | --- | ------------ | --- | ----------------- | --- |
The main difference between this system and that of LTP is that the beat note is
generatedbyinterferencewithanoffsetphase-lockedlaseratavariablefrequencydifference
of 2 to 20MHz rather than interference between two beams produced by acousto-optic
| modulators | at a constant | frequency | difference | of 1 to 2kHz. |     |     |     |     |
| ---------- | ------------- | --------- | ---------- | ------------- | --- | --- | --- | --- |
The output of this additional interferometer (φ ) could be used to measure frequency
F
fluctuations of the laser and to actively stabilize the master laser frequency. Thus the
| proposed | configuration | contains | two control | loops: |     |     |     |     |
| -------- | ------------- | -------- | ----------- | ------ | --- | --- | --- | --- |
• (φ − frequency offset) Locks the slave laser to the master laser as in the LISA
R
baseline;

| 2   | PRE-STABILIZATION |     |     |     |     |     |     |     |     |     |     | 16  |
| --- | ----------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
• (φ −φ − tuning bias) Locks the master laser frequency to the length difference.
|     | F   | R   |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
The laser on the other bench (the slave laser) is offset phase-locked to the master with
| high | gain/bandwidth |     | with | a constant |     | frequency |      | offset: |     |     |     |     |
| ---- | -------------- | --- | ---- | ---------- | --- | --------- | ---- | ------- | --- | --- | --- | --- |
|      |                |     |      |            |     | ν =       | ν +f | ,       |     |     |     | (2) |
|      |                |     |      |            |     | s         | M    | het     |     |     |     |     |
with2MHz ≤ f ≤ 20MHz. Thisphase-lockingarrangementwillbeusedinanycase.
het
Z
+
Σ
+
Master Laser
|     |     |     |     |          |     |     |     | φ R |     |     |     |     |
| --- | --- | --- | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
|     |     |     |     | Backlink |     |     |     |     |     |     | G2  |     |
Fibre
Slave Laser
E2
φ F
|     | f   | r e q u e n c y     |     |     |     |     |     |     |         |     | +   |     |
| --- | --- | ------------------- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | --- |
|     | c   | o n t r o ll e r G1 |     |     |     |     |     |     | mixer / |     | Σ + |     |
phasemeter
|     |     |     |     | ε1  |     |     |     |     |     |     | - ε2 |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | --- |
mixer /
|     |     |     | E1  | Σ   |     |     | phasemeter |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------- | --- | --- | --- | --- | --- |
LO
Figure10: Basicsystemschematic. Theinterferometerwiththeφ readoutisinthecurrent
R
LISAopticalbenchdesign. Theφ interferometeristheproposedadditionalinterferometer
F
for measuring and actively suppressing the laser frequency noise, as in LISA Pathfinder.
After phase-locking, the closed loop phase noise of the slave laser is given (in the
| frequency |     | domain1) | by  |      |     |     |     |              |     |      |     |     |
| --------- | --- | -------- | --- | ---- | --- | --- | --- | ------------ | --- | ---- | --- | --- |
|           |     |          |     |      | G   |     | G   |              | 1   |      |     |     |
|           |     |          | P   | =    | 1   | P   |     | 1 (cid:15) + |     | P ,  |     | (3) |
|           |     |          |     | s|cl |     | M − |     | 1            |     | s|fr |     |     |
|           |     |          |     |      | 1+G |     | 1+G |              | 1+G |      |     |     |
|           |     |          |     |      | 1   |     |     | 1            |     | 1    |     |     |
where
|     | P   | - free-running |     | slave | laser phase |     | noise; |     |     |     |     |     |
| --- | --- | -------------- | --- | ----- | ----------- | --- | ------ | --- | --- | --- | --- | --- |
• s|fr
|     | • P | - closed | loop | slave laser | phase | noise; |     |     |     |     |     |     |
| --- | --- | -------- | ---- | ----------- | ----- | ------ | --- | --- | --- | --- | --- | --- |
s|cl
|     | • P - | master | laser | phase | noise; |     |     |     |     |     |     |     |
| --- | ----- | ------ | ----- | ----- | ------ | --- | --- | --- | --- | --- | --- | --- |
M
|     | (cid:15) - | error point | noise | (sensor | noise) |     | for loop | 1;  |     |     |     |     |
| --- | ---------- | ----------- | ----- | ------- | ------ | --- | -------- | --- | --- | --- | --- | --- |
•
1
1Notethatsofarnoassumptionshavebeenmadeaboutthepropertiesofthesignals(e.g. correlations)
and so the quantities should be considered as Fourier transforms with phase information and not spectral
| densities, | which | would | be added | in  | quadrature | for | uncorrelated |     | noise sources. |     |     |     |
| ---------- | ----- | ----- | -------- | --- | ---------- | --- | ------------ | --- | -------------- | --- | --- | --- |

| 2   | PRE-STABILIZATION |     |     |     |     |     |     |     |     |     | 17  |
| --- | ----------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
• G - controller transfer function for loop 1 (e.g. P, PI controller, integrator “built-in”
1
|     | from frequency   |         | to phase | conversion). |       |                |     |     |     |     |     |
| --- | ---------------- | ------- | -------- | ------------ | ----- | -------------- | --- | --- | --- | --- | --- |
|     | Equation         | 3 shows | that in  | the          | high  | gain limit:    |     |     |     |     |     |
|     | The free-running |         | slave    | phase        | noise | is suppressed; |     |     |     |     |     |
•
|     | • The performance |     | is limited |     | by sensor | noise | (cid:15) ; |     |     |     |     |
| --- | ----------------- | --- | ---------- | --- | --------- | ----- | ---------- | --- | --- | --- | --- |
1
The slave laser tracks the master laser phase noise with accuracy G1 1.
|     | •   |     |     |     |     |     |     |     |     | ≈   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
1+G1
Offset phase-locking the slave laser fixes the beat note frequency for both the φ and
R
φ interferometers to the chosen frequency offset, but does not have any effect on the
F
frequency of the master laser. The master laser can be freely tuned, while the slave laser
tracks these changes. Thus, the first loop only controls the frequency difference between
the two lasers.
| 2.5.2 | Master | Laser | Frequency |     | Control |     | Loop |     |     |     |     |
| ----- | ------ | ----- | --------- | --- | ------- | --- | ---- | --- | --- | --- | --- |
Measuringthephaseofthebeatnotefortheφ interferometerproducesthefollowingerror
F
signal for the second control loop (used to stabilize the master laser frequency):
|     |     |     |     | E   | = (cid:15) | −P  | e−jωτ +P | .    |     |     | (4) |
| --- | --- | --- | --- | --- | ---------- | --- | -------- | ---- | --- | --- | --- |
|     |     |     |     |     | 2 2        | M   |          | s|cl |     |     |     |
This assumes that the propagation delay from the slave laser to φ is identical to the delay
F
toφ . Themaster laserhas anadditional propagationdelay ofτ = ∆L/cforφ compared
|     | R   |     |     |     |     |     |     |     |     | F   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
to φ .
R
Introducinganoffset(cid:15) totheerrorpointofthemasterlasercontrolloopcanbeusedto
2
tune the master laser frequency (which the slave laser tracks due to the offset phase-lock).
Substituting the closed loop slave laser noise given in Equation 3 into Equation 4 gives:
|     |     |     | (cid:20)   | G   |        | (cid:21) |     | G            | 1   |     |     |
| --- | --- | --- | ---------- | --- | ------ | -------- | --- | ------------ | --- | --- | --- |
|     |     | E = | (cid:15) + | 1   | −e−jωτ | P        |     | 1 (cid:15) + |     | P . | (5) |
−
|     |     | 2   | 2   | 1+G |     |     | M 1+G | 1   | 1+G | s|fr |     |
| --- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | ---- | --- |
|     |     |     |     |     | 1   |     |       | 1   |     | 1    |     |
Thereforetheapproachofusingonlythephasemeasurementfortheφ interferometerleads
F
toatransferfunctionformasterlaserphasenoisethatdependsontheslavelasercontroller
design, siginificantly complicating the controller design for the master laser control loop.
However, the technique can be modified as described in the next subsection to simplify the
response to the master laser frequency and make the design independent of the slave laser
control loop.

| 2 PRE-STABILIZATION |             |       |       |          |            |       |          |       |     |     |     | 18  |
| ------------------- | ----------- | ----- | ----- | -------- | ---------- | ----- | -------- | ----- | --- | --- | --- | --- |
| 2.5.3               | Subtraction |       | of    | Residual | Phase-Lock |       |          | Error |     |     |     |     |
| The closed          | loop        | error | point | for      | the slave  | laser | is given |       | by: |     |     |     |
P
|     |     |     |     |      |     | G   |      |           | G   |              |     |     |
| --- | --- | --- | --- | ---- | --- | --- | ---- | --------- | --- | ------------ | --- | --- |
|     |     |     | E = | s|fr | +   | 1   | P −P | +(cid:15) |     | 1 (cid:15) . |     | (6) |
|     |     |     | 1   |      |     |     | M    | M         | 1 − | 1            |     |     |
|     |     |     |     | 1+G  | 1+G |     |      |           | 1+G |              |     |     |
|     |     |     |     |      | 1   | 1   |      |           |     | 1            |     |     |
Subtracting this from the error point for the second control loop leads to:
|     |     |     |     | (cid:18) | (cid:26)       |        |     |          | (cid:26)(cid:19) |     |     |     |
| --- | --- | --- | --- | -------- | -------------- | ------ | --- | -------- | ---------------- | --- | --- | --- |
|     |     |     |     |          | G (cid:26)1    |        |     |          | G (cid:26)1      |     |     |     |
|     |     | E   | −E  | =        |                | −e−jωτ | +1− |          | P                |     |     |     |
|     |     | 2   | 1   |          | 1 (cid:26) + G |        |     | 1        | (cid:26) + G     | M   |     |     |
|     |     |     |     | (cid:26) |                |        |     | (cid:26) |                  |     |     |     |
|     |     |     |     |          | 1              |        |     |          | 1                |     |     |     |
(cid:8)
|     |     |     |     |           | 1 (cid:8) |       | P (cid:26)    |                    | G (cid:8) (cid:8)   | G                | (cid:8) (cid:8)   |     |
| --- | --- | --- | --- | --------- | --------- | ----- | ------------- | ------------------ | ------------------- | ---------------- | ----------------- | --- |
|     |     |     |     |           | (cid:8)P  |       | s|(cid:26) fr |                    | (cid:8)1 (cid:15) + |                  | (cid:8)1 (cid:15) |     |
|     |     |     |     |           | (cid:8)   | −     | (cid:26)      | − (cid:8)1(cid:8)+ | 1                   | (cid:8)1(cid:8)+ | 1                 |     |
|     |     |     |     | 1(cid:8)+ | G         | s |fr | 1 + G         |                    | G                   |                  | G                 |     |
|     |     |     |     | (cid:8)   | 1         |       | (cid:26)      | 1                  | 1                   |                  | 1                 |     |
|     |     |     |     | +(cid:15) | −(cid:15) |       |               |                    |                     |                  |                   | (7) |
2 1
|     |     |     | ,   | = (cid:2)1−e−jωτ(cid:3)P |     |     | +(cid:15) | −(cid:15) , |     |     |     | (8) |
| --- | --- | --- | --- | ------------------------ | --- | --- | --------- | ----------- | --- | --- | --- | --- |
|     |     |     |     |                          |     | M   | 2         | 1           |     |     |     |     |
which is independent of G and P . This approach allows the design of the second (master
|     |     |     |     | 1   | s   |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
laser) control loop to be independent of the first (slave laser) control loop. Although this
suggests that if the subtraction has perfect fidelity the slave laser need not be locked to
the master, the slave laser still needs to be phase-locked in order to keep the beat note
| frequency | within | the | photodiode/phasemeter |     |     |     | bandwidth. |     |     |     |     |     |
| --------- | ------ | --- | --------------------- | --- | --- | --- | ---------- | --- | --- | --- | --- | --- |
Forfrequenciesbelowtheinversedelaytimeτ−1,thetransducergainofthemismatched
| path length | interferometer |     |     | is: |     |     |      |     |     |     |     |     |
| ----------- | -------------- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- |
|             |                |     |     |     |     | δΦ  | 2π∆L |     |     |     |     |     |
|             |                |     |     |     |     | F ≈ |      | ,   |     |     |     | (9) |
|             |                |     |     |     |     | δν  | c    |     |     |     |     |     |
M
thus providing an error signal which can be used to control the frequency of the master
laser.
| 2.5.4 | Master | Laser | Closed |     | Loop | Noise |     |     |     |     |     |     |
| ----- | ------ | ----- | ------ | --- | ---- | ----- | --- | --- | --- | --- | --- | --- |
Defining:
|                 |     |        |       |       | L       | = G   | (cid:2)1−e−jωτ(cid:3), |     |     |     |     | (10) |
| --------------- | --- | ------ | ----- | ----- | ------- | ----- | ---------------------- | --- | --- | --- | --- | ---- |
|                 |     |        |       |       | 2       | 2     |                        |     |     |     |     |      |
| the closed-loop |     | master | laser | noise | is then | given | by:                    |     |     |     |     |      |
P
|     |     |     |     |      |      |     | G   |            | G          |     |     |      |
| --- | --- | --- | --- | ---- | ---- | --- | --- | ---------- | ---------- | --- | --- | ---- |
|     |     |     |     | P =  | M|fr | −   | 2   | (cid:15) − | 2 (cid:15) | .   |     | (11) |
|     |     |     |     | M|cl |      |     |     | 1          | 2          |     |     |      |
|     |     |     |     |      | 1+L  |     | 1+L |            | 1+L        |     |     |      |
|     |     |     |     |      |      | 2   | 2   |            | 2          |     |     |      |
The effect of offsets in the error point of the phase of the master laser is given by:
|     |     |     |     |     | ∂P  |     | G   | 1   |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
M|cl
|     |     |     |     |     |           | =   | 2   | ≈   | ,   |     |     | (12) |
| --- | --- | --- | --- | --- | --------- | --- | --- | --- | --- | --- | --- | ---- |
|     |     |     |     |     | ∂(cid:15) | 1+L |     | jωτ |     |     |     |      |
|     |     |     |     |     | 2         |     | 2   |     |     |     |     |      |

2 PRE-STABILIZATION 19
wheretheapproximationisvalidforlargegainandfrequencieslowcomparedtotheinverse
delay time. In terms of the master laser frequency this corresponds to:
∂ν 1
M|cl ≈ , (13)
∂(cid:15) 2πτ
2
which is the frequency tuning response at low frequencies for high loop gain.
2.5.5 Controller Transfer Functions (Preliminary Design)
A slave laser phase-lock bandwidth of 20kHz is assumed. Figure 11 shows preliminary
controller designs for the two controllers shown in Figure 10. The corresponding Nyquist
diagrams are shown in Figure 12.
500
400
300
200
100
0
−100
10−4 10−2 100 102 104 106
Frequency [Hz]
]Bd[
edutingaM G 1
G
2
200
100
0
−100
−200
10−4 10−2 100 102 104 106
Frequency [Hz]
]seerged[
esahP
Figure11: Preliminarycontrollerdesigns. Notethatthecontrollertransferfunctionsshown
include a pole at DC due to frequency-to-phase conversion (i.e. the laser actuators act on
frequency and not phase directly).

2 PRE-STABILIZATION 20
|     |     | G1 partly logarithmic nyquist plot |     |     |     |     | L2 partly logarithmic nyquist plot |
| --- | --- | ---------------------------------- | --- | --- | --- | --- | ---------------------------------- |
1
10
102
103
104
105
|     |        |     |             | 102     | 10 1 |            |     |
| --- | ------ | --- | ----------- | ------- | ---- | ---------- | --- |
|     |        |     | 107 106 105 | 104 103 |      |            | 106 |
|     |        | 108 |             |         |      |            | 107 |
|     | traP ℑ |     |             |         |      | 108 traP ℑ |     |
ℜ Part ℜ Part
Figure 12: Partly logarithmic Nyquist plot for the slave (left) and master (right) laser
control loops.
| 2.5.6 | Interfaces  |     | with Other |     | Subsystems |     |     |
| ----- | ----------- | --- | ---------- | --- | ---------- | --- | --- |
| Phase | Measurement |     | Subsystem  |     | Interfaces |     |     |
• Assuming that the two lasers are phase-locked with a fixed frequency offset using the
φ interferometeroutputastheerrorsignal, therearetwowaystogeneratetheoffset
R
locking error signal: use the tracking phasemeter’s phase output and numerically
subtract a ramp of the desired slope; or implement a separate multiplier (mixer)
which is not tracking but instead driven by a sine wave of the desired frequency.
The phasemeter’s performance above 1Hz is also important and will influence the
•
|     | optimal | unity | gain frequency |     | of the | feedback. |     |
| --- | ------- | ----- | -------------- | --- | ------ | --------- | --- |
√
Anycorrectionsrequiredtoreach1pm/ Hzperformance(e.g. ADCjittercorrection)
•
may need to implemented in real-time on the fast phasemeter outputs, unless it is
|       | common    | to both  | phase | measurements |     | (e.g. clock | noise). |
| ----- | --------- | -------- | ----- | ------------ | --- | ----------- | ------- |
| Laser | Frequency | Actuator |       | Interfaces   |     |             |         |
Thesamelaseractuatorinterfaceasforstandardoffsetphase-lockingisrequired. Thesplit
actuation due to limiting the bandwidth of the master laser control loop in order not to
significantly increase the noise level at high frequencies is applied externally to the laser
subsystem. Therefore no change to the laser frequency actuator interface is expected to be
necessary.

2 PRE-STABILIZATION 21
| Frequency | Tunability | for Arm | Locking |     |     |     |
| --------- | ---------- | ------- | ------- | --- | --- | --- |
Figure 13 shows the frequency tuning response for injecting offsets into the master laser
frequency control loop (blue curve). Notice that for this input the bandwidth is restricted
by the low loop bandwidth used in order reduce the degradation of the laser noise above
10Hz. The green curve shows the frequency tuning response for the input labeled Z in
Figure 10, scaled by a factor of 1/(2πτ) in order to compensate for the gain of the interfer-
ometer. The sum is shown as the red curve. Injecting the same signal into the offset and
directly to the laser (compensating for the interferometer gain) provides a high bandwidth
frequency actuation for implementing arm locking. The achievable tuning bandwidth in
thisapproachislimitedbythelaserfrequencyactuators. Thissplitactuationapproachmay
also be useful for other types of tunable frequency references. Further investigation of the
split actuation scheme for frequency tuning, in particular an experimental demonstration,
is needed.
Frequency tuning response to offsets
|     | 1010 |     |     |     |     |     |
| --- | ---- | --- | --- | --- | --- | --- |
]V/zH[ edutingaM
105
|     | 100 |     |     | G/(1+L)/(jf) |     |     |
| --- | --- | --- | --- | ------------ | --- | --- |
|     |     |     |     | 2 2          |     |     |
1/(1+L)*(1/2πτ)
2
Sum
10−5
|     | 10−4 | 10−2 | 100 | 102 | 104 | 106 |
| --- | ---- | ---- | --- | --- | --- | --- |
Frequency [Hz]
200
100
]seerged[ esahP
0
−100
|     | −200 10−4 | 10−2 | 100 | 102 | 104 | 106 |
| --- | --------- | ---- | --- | --- | --- | --- |
Frequency [Hz]
|     |     | Figure | 13: Frequency | tuning response. |     |     |
| --- | --- | ------ | ------------- | ---------------- | --- | --- |

| 2 PRE-STABILIZATION |     |             |     |             |     |     |     | 22  |
| ------------------- | --- | ----------- | --- | ----------- | --- | --- | --- | --- |
| 2.5.7 System        |     | Performance | and | Limitations |     |     |     |     |
Like an optical cavity, the ultimate performance of this system is limited by stability of
the reference:
|     |     |     |     | δν(f)     | δx(f)       |     |     |      |
| --- | --- | --- | --- | --------- | ----------- | --- | --- | ---- |
|     |     |     |     | (cid:102) | = (cid:102) | ,   |     | (14) |
|     |     |     |     | ν         | ∆L          |     |     |      |
whereδx(f)representsthepathlengthfluctuationsoftheinterferometer. (cid:102) However, ad-
ditional noise introduced by associated readout electronics (photodetectors and phaseme-
| ters) can | also limit | performance. |     |     |     |     |     |     |
| --------- | ---------- | ------------ | --- | --- | --- | --- | --- | --- |
Figure 14 shows the predicted system performance assuming a 50cm path length mis-
√
match and typical free-running laser frequency noise (10kHz/ Hz at 1Hz with 1/f noise
| shape). The | assumed | combined | phasemeter |     | and | path length | noise is |     |
| ----------- | ------- | -------- | ---------- | --- | --- | ----------- | -------- | --- |
(cid:115)
|     |     |          | 2π      | √   |     | (cid:18)2.8mHz(cid:19)4 |     |      |
| --- | --- | -------- | ------- | --- | --- | ----------------------- | --- | ---- |
|     |     | (cid:15) | = ×1pm/ |     | Hz× | 1+                      | .   | (15) |
|     |     |          | i λ     |     |     | fHz                     |     |      |
The phasemeter/path length noise of the two channels is assumed to be uncorrelated.
Notice that the closed loop frequency noise level intersects the free-running noise level
at approximately 10Hz for typical Nd:YAG NPRO lasers. For closed loop bandwidths
above this frequency, the closed loop noise level would be higher than the free-running
laser noise (which has a potential impact on the performance of other subsystems, e.g.
the phasemeter). Therefore in the proposed design the bandwidth of the second loop is
| restricted | to approximately |     | 20Hz. |     |     |     |     |     |
| ---------- | ---------------- | --- | ----- | --- | --- | --- | --- | --- |
In this simple model the closed loop frequency is limited primarily by the phasemeter
noise of the two phasemeter channels used and results in a closed loop frequency noise level
√
for the master laser of approximately 800 Hz/ Hz in the 10mHz to 1Hz range.
| 2.5.8 Reference |     | (LTP | Engineering |     | Model) | Performance |     |     |
| --------------- | --- | ---- | ----------- | --- | ------ | ----------- | --- | --- |
Figure 15 shows the laser frequency stability achieved with a free-running standard NPRO
stabilized to the frequency interferometer of the LTP optical bench engineering model
measured by beating with an iodine-stabilized NPRO. The observed frequency stability
| matches | the noise | projection | in the | LTP | band. |     |     |     |
| ------- | --------- | ---------- | ------ | --- | ----- | --- | --- | --- |
Figure 16 shows the closed loop frequency noise stability achieved with the LTP optical
bench engineering model at the AEI Hannover. The red curve shows a comparison be-
tween an iodine-stabilized laser and a NPRO laser stabilized using the LTP optical bench
engineering model. The red curve is therefore an “out-of-loop” measurement of the laser
frequencystability. Notethatinthiscasethesystemisgainlimited(duetothelowhetero-
dynefrequency)andnotsensornoiselimitedandthattheclosedloopnoiseisdominatedby
residual frequency fluctuations and not phasemeter noise or path length fluctuations. The
orange curve shows a projection of the measured displacement noise (including the dummy

| 2 PRE-STABILIZATION |     |     |     |     | 23  |
| ------------------- | --- | --- | --- | --- | --- |
108

Master Laser
Error Point 1
| 107 |     |     | Error Point 2 |     |     |
| --- | --- | --- | ------------- | --- | --- |
Free Running Master
Closed Loop Master
106
105
104
]zH√/zH[ DSA
103
102
101
100
10−1
10−2
| 10−4 | 10−2 | 100 | 102 | 104 |     |
| ---- | ---- | --- | --- | --- | --- |
Frequency [Hz]
Figure14: Closedloopfrequencynoise(bluetrace)assuminga50cmpathlengthmismatch
for Mach-Zehnder pre-stabilization.
test masses which are mounted on metallic mounts), assuming a path length mismatch of
| 38cm following the relationship: |     |     |     |     |     |
| -------------------------------- | --- | --- | --- | --- | --- |
c
|     | δν(f)     | = Φ               | (f). |     | (16) |
| --- | --------- | ----------------- | ---- | --- | ---- |
|     | (cid:102) | 2π∆L (cid:101)F−R |      |     |      |
The orange curve is indicative of the performance that could be achieved if the loop
gain was increased. The current loop gain is sufficient to reach the LTP requirement.

2 PRE-STABILIZATION 24
|     | 106 |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- |
)zH(trqs/zH
]2/1−zH[ DSL ycneuqerF 105
104
LTP req = 28 kHz/sqrt(Hz)
Beatnote "LTP" with "iodine−stabilized"
LTP phase noise scaled to frequency noise via pathlength mismatch
103

|     | 10−4 | 10−3 | 10−2 | 10−1 | 100 | 101 |
| --- | ---- | ---- | ---- | ---- | --- | --- |
Frequency [Hz]
Figure 15: Laser frequency stability of the LTP optical bench engineering model measured
with an iodine-stabilized NPRO reference and the projected performance.
| 2.5.9 Performance |     | Improvement | Options |     |     |     |
| ----------------- | --- | ----------- | ------- | --- | --- | --- |
TheperformanceprojectionofFigure16(orangecurve)wasobtainedusingtheLTPoptical
bench engineering model and LTP phasemeter (with a heterodyne frequency of approxi-
mately 1.6kHz, which limits the achievable loop gain). The optical path included the
| dummy test | masses | using metallic mounts. |     |     |     |     |
| ---------- | ------ | ---------------------- | --- | --- | --- | --- |
For a given path length/phasemeter performance the sensor noise and thus closed loop
performance level of the technique can be improved by increasing the path length mis-
match of the Mach-Zehnder. The path length mismatch used in this analysis (50cm) could
| potentially | be increased. |     |     |     |     |     |
| ----------- | ------------- | --- | --- | --- | --- | --- |
It may be possible to use a fixed heterodyne frequency which may allow optimization
| of the phasemeter | performance | for | this heterodyne | frequency. |     |     |
| ----------------- | ----------- | --- | --------------- | ---------- | --- | --- |
| 2.5.10            | Summary     |     |                 |            |     |     |
The proposed LTP-style unequal arm length Mach-Zehnder frequency stabilization has the
| following | requirements | and characteristics: |     |     |     |     |
| --------- | ------------ | -------------------- | --- | --- | --- | --- |

2 PRE-STABILIZATION 25
108
107
106
105
104
103
102
10-4 10-3 10-2 0.1 1 10
]zH√/zH[
esion
ycneuqerF
Free-running (direct measurement)
Free-running (projection)
LTP set-up (projection)
Beatnote LTP-laser (bb) with Iodine
LTP Requirement = 28 kHz/√Hz
1 kHz/√Hz
30 Hz/√Hz
Frequency [Hz]
Figure 16: Measured LTP performance and projected sensor noise floor. The system meets
the LTP requirement, however the system is not sensor noise limited. The performance
couldbesignificantlyimprovedbyincreasingtheloopgain. Theorangecurveisanestimate
of the sensor noise floor.
• Several extra components (of the type that will be implemented in any case: mirrors,
beam-splitters, photodiodes and phasemeter channels) are needed to implement an
addtional interferometer;
• Subtractingthereferencephasemeteroutputfromthefrequencyinterferometerphaseme-
ter output makes the master laser controller design independent of the phase-lock
bandwidth of the slave laser;
• Extrapolation of phasemeter performance to frequencies above 1Hz leads to worse
than free-running laser frequency (above approx. 10Hz for typical NPRO frequency
noise) performance limit if a large bandwidth is used to stabilize the master laser.
Therefore limiting the bandwidth is desirable;
• The target laser frequency can be tuned by subtracting a phase offset from the error
signal before feeding it to the servo. A split feedback arrangement, where the (ap-
propriately scaled) signal for frequency tuning is fed directly into the laser frequency
input, appears to be feasible to overcome the bandwidth restriction that is desirable

3 ARM LOCKING 26
due to the assumed high frequency phasemeter performance;
• Although the predicted performance may not be as good as that of a rigid cavity,
the technique has some significant advantages. For example, the error signal is im-
mediately available for any operating point (no lock acquisition procedure needed),
and minimal additional hardware is required compared to other tunable frequency
references.
3 Arm Locking
Arm locking is the second stabilization technique in the LISA frequency noise plan. Arm
lockinghasdevelopedsignificantlysincetheinitialarmlockingproposalbySheardet.al [14].
Much of the risk associated with the unusual control system has been retired by hardware
demonstrations [15, 16, 17, 18], simulations [19] and theoretical investigations [20]. Dual
arm locking [21], the current baseline for in the LISA design, builds on the proposal of
Enhanced arm locking [22]. This scheme uses combinations of phase measurements from
two arms to increase the frequency of the first null of the sensor from 1/τ ≈ 30 mHz to
1/(2∆τ) > 2 Hz, where ∆τ is the 1/2 the difference in light travel round trip times of the
twoarmsused(wedefinetheaverageroundtriptimeasτ¯). Movingthefirstnulltooutside
the LISA band allows a more aggressive controller design below 2 Hz and eliminates, from
the LISA science band, noise amplification due to the nulls.
Recent studies undertaken by members of the FCST have since extended the under-
standing of how arm locking would operate in LISA, the expected performance, and the
issues that need to be addressed. This chapter gives an overview and reports issues asso-
ciated with laser frequency pulling due to Doppler frequency error, noise limits, and the
expected performance in LISA. Although the single and dual arm locking configurations
areintroduced,theperformanceiscalculatedusingamodifieddualarmlocking,ahybridof
common and dual arm locking sensors, which delivers the frequency pulling characteristics
and low-frequency noise coupling of common arm locking, but retains the control system
advantages of dual arm locking.
3.1 Measurement Architecture for Arm Locking
Time-Delay Interferometry will be implemented in post processing by forming linear com-
binations of five low bandwidth (∼3 Hz) phase measurements on each optical bench (with
two optical benches per spacecraft) [23] with delays determined by inter-spacecraft rang-
ing. These phase measurements are (1) inter-spacecraft measurement, (2) the backlink
measurement, (3) the proof mass to optical bench measurement, (4) and (5), the beatnotes
of the upper-upper and lower-lower clock sidebands. To form the displacement measure-
ment, TDI will use the strap-down architecture [24], which combines the inter-spacecraft
measurements, the proof mass to optical bench, and the backlink measurement to remove

| 3 ARM | LOCKING |     |     |     |     |     |     |     |     | 27  |
| ----- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
spacecraft motion. Clock noise in the measurement can be removed using the beatnote of
| clock | sidebands | [25, | 26, | 27, 28, | 29]. |     |     |     |     |     |
| ----- | --------- | ---- | --- | ------- | ---- | --- | --- | --- | --- | --- |
Unlike TDI, arm locking requires high bandwidth signals (∼ 20kHz), in real time,
and has significantly less stringent noise requirements than the LISA science measure-
ment. Given the relaxed noise requirements, we assume that arm locking will operate with
the most simple measurement architecture - using only the inter-spacecraft phase mea-
surements. An outcome of this simple measurement architecture is both clock noise and
spacecraft motion will be present in the phase measurements used for arm locking.
| 3.2 | Frequency |     | Noise | After | Arm | Locking |     |     |     |     |
| --- | --------- | --- | ----- | ----- | --- | ------- | --- | --- | --- | --- |
To/from Spacecraft 2
|     |     |     |     |     |     | ~ 5 x 109 m |     |     | A31 |     |
| --- | --- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- |
G
|     |     |     |     | −   |     |     |     |            | 3   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | --- |
|     |     |     |     | +   |     |     |     | Phasemeter |     |     |
Phasemeter
|     |     |     | Laser 1 |      |     |     | τ   |     | LASER |     |
| --- | --- | --- | ------- | ---- | --- | --- | --- | --- | ----- | --- |
|     |     | G   |         |      |     |     | 13  |     | φ     |     |
|     |     |     |         | Σ    |     |     |     |     | L3    |     |
|     |     | 1   | −       |      |     |     |     | − + |       |     |
|     | B1  |     |         | + O1 |     |     |     |     |       |     |
τ
|     |      |     |       |     |     | +   | 31  |     | +   |     |
| --- | ---- | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
|     | Arm  |     | LASER |     |     | −   |     |     | −   |     |
Σ
|     |     |     |     | φ   |     |     |     | O3  |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Locking
|     |     |     |     | L1  |     |     |     |     | Laser 3 |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- |
Sensor
Spacecraft 3
|     | A12 | A13 |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Phasemeter
Spacecraft 1
Figure 17: Schematic of arm locking control loop. Laser frequency noise is represented by
φ , with j representing the number of the local spacecraft. The clock noise, shot noise,
Lj
| and spacecraft |     | motion | are | not shown. |     |     |     |     |     |     |
| -------------- | --- | ------ | --- | ---------- | --- | --- | --- | --- | --- | --- |
Figure17showaschematicofthearmlockingcontrolsystem. Thephasemeasurements
that enter the arm locking sensor on the central spacecraft (points A12 and A13) are
|     |     |     |     | (cid:20) | (cid:21) | (cid:20) | (cid:21) |     |      |      |
| --- | --- | --- | --- | -------- | -------- | -------- | -------- | --- | ---- | ---- |
|     |     |     |     | φ        |          | P        | (ω)      |     |      |      |
|     |     | Φ   | =   | A13      | ≈        | φ        | 13 +N    | +N  | +N . | (17) |
|     |     | A1  |     | φ        |          | L1 P     | (ω)      | S   | C X  |      |
|     |     |     |     | A12      |          |          | 12       |     |      |      |
where φ and φ represent the phase measured on the central spacecraft in the 13
|     | A13 |     | A12 |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
arm and 12 arm respectively, φ is the laser phase noise of the laser on the central
L1
spacecraft, and P (ω) and P (ω) are the frequency responses of the 13 arm and 12 arm
|     |     | 13  |     | 12  |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
respectively. The vectors N ,N , and N contain shot noise, clock noise, and spacecraft
|     |     |     |     | S   | C   | X   |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

| 3 ARM | LOCKING |     |     |     |     |     |     |     |     |     |     | 28  |
| ----- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
jitter noise [30], discussed in section 3.5. If the lasers on the far spacecraft are phased
locked to the incoming light with high gain, P (ω) and P (ω) can be well approximated
|     |     |     |     |     |     | 13  |     |     | 12  |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
by [30]
|     |     | P   | (ω) ≈ | 1−e−i2ωτ13, |     | P   | (ω) ≈ | 1−e−i2ωτ12. |     |     |     | (18) |
| --- | --- | --- | ----- | ----------- | --- | --- | ----- | ----------- | --- | --- | --- | ---- |
|     |     | 13  |       |             |     | 12  |       |             |     |     |     |      |
where τ and τ are the one-way light propagation delays in the respective arms.
|     | 13  | 12  |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
The signals in Φ can be combined using the using the signal mapping vector, S ,
|     |     | A1  |     |     |     |     |     |     |     |     |     | k   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
where k = S for single arm locking, k = + for common arm locking, and k = D for dual
arm locking. The signal mapping vectors and frequency responses are given in table 4.
The open loop noise at the output of the arm locking sensor (point B1 in Figure 17) is
simply φ | = S Φ . The frequency noise at laser output with the arm locking control
|             | B1 k   | k A1 |           |     |      |      |      |       |     |      |     |      |
| ----------- | ------ | ---- | --------- | --- | ---- | ---- | ---- | ----- | --- | ---- | --- | ---- |
| loop closed | (point | O1   | in Figure | 17) | is   |      |      |       |     |      |     |      |
|             |        |      |           |     | G    | (ω)φ | |    |       |     |      |     |      |
|             |        | φ    | | =       | φ   | −    | 1    | B1 k | ,     |     |      |     | (19) |
|             |        | O1   | k         | L1  |      |      |      |       |     |      |     |      |
|             |        |      |           |     | 1+G  | (ω)P | (ω)  |       |     |      |     |      |
|             |        |      |           |     |      | 1    | k    |       |     |      |     |      |
|             |        |      |           |     | φ    |      |      | G (ω) |     |      |     |      |
|             |        |      | =         |     | L1   |      | −    | 1     |     | S N, |     | (20) |
|             |        |      |           | 1+G | (ω)P | (ω)  | 1+G  | (ω)P  | (ω) | k    |     |      |
|             |        |      |           |     | 1    | k    |      | 1     | k   |      |     |      |
where G (ω) is the gain of the arm locking controller and P (ω) is the frequency response
|            | 1       |     |     |     |     |     |     |     | k   |     |     |     |
| ---------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| of the kth | sensor. |     |     |     |     |     |     |     |     |     |     |     |
Table 4: The signal mapping vector and frequency response of different arm locking con-
figurations. Here τ is the one way light travel time of the ijth arm, τ¯ is the average round
ij
trip time of the two arms, and E(ω) is an filter used to combine the common and difference
sensors, given in [30]. The parameters H (ω) and H (ω) are defined in equation 24.
|               |     |        |            |           |     | +    |           | −     |                     |           |     |     |
| ------------- | --- | ------ | ---------- | --------- | --- | ---- | --------- | ----- | ------------------- | --------- | --- | --- |
| Configuration |     | Signal | Mapping    |           |     |      | Frequency |       | Response            |           |     |     |
| Single        |     | =      | (cid:2) 1, | 0 (cid:3) |     |      | P         | (ω) = | 2isin(τ             | ω)e−iωτij |     |     |
|               |     | S S    |            |           |     |      | S         |       |                     | ij        |     |     |
|               |     |        | (cid:2)    | (cid:3)   |     |      |           |       |                     |           |     |     |
| Common        |     | S =    | 1,         | 1         |     |      | P         | (ω) = | 2(1−cos(∆τω)e−iωτ¯) |           |     |     |
|               |     | +      |            |           |     |      | +         |       |                     |           |     |     |
|               |     |        | (cid:2)    | (cid:3)   |     |      |           |       |                     |           |     |     |
| Difference    |     | S =    | 1,         | −1        |     |      | P         | (ω) = | −2isin(∆τω)e−iωτ¯   |           |     |     |
|               |     | −      |            |           |     |      | −         |       |                     |           |     |     |
|               |     |        | (cid:104)  |           |     |      | (cid:105) |       |                     |           |     |     |
| Dual          |     | S =    | 1−         | E(ω),     | 1+  | E(ω) | P         | (ω) = | P (ω)−              | E(ω)P     | (ω) |     |
|               |     | D      |            |           |     |      | D         |       | +                   |           | −   |     |
|               |     |        |            | iω∆τ      |     | iω∆τ |           |       |                     | iω∆τ      |     |     |
(cid:20)
|              |      |      | H   | (ω)−H   |     | (ω),     |     |     |     |            |      |     |
| ------------ | ---- | ---- | --- | ------- | --- | -------- | --- | --- | --- | ---------- | ---- | --- |
|              |      |      |     | +       | −   |          |     |     |     |            |      |     |
| Modified     | dual | =    |     |         |     |          | P   | (ω) | = P | (ω)H (ω)−P | (ω)H | (ω) |
|              |      | S M  |     |         |     | (cid:21) | M   |     | +   | +          | −    | −   |
|              |      |      | H   | (ω)+H   |     | (ω)      |     |     |     |            |      |     |
|              |      |      |     | +       | −   |          |     |     |     |            |      |     |
| 3.3 Modified |      | Dual | Arm | Locking |     |          |     |     |     |            |      |     |
A combination of common and dual arm locking sensors can be used to retain the control
system advantages of dual arm locking and minimize frequency pulling and low frequency

| 3 ARM | LOCKING |     |     |     |     |     |     |     |     |     |     | 29  |
| ----- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
noise. This modified dual arm locking sensor is designed so that the common arm sensor
dominates below the first null of the arm (f < 1/τ¯) and the dual sensor dominates above
this frequency [30]. The components of the modified sensor are plotted in Figure 18. The
| frequency | response | of  | the | sensor | is         |                    |           |           |                    |           |     |      |
| --------- | -------- | --- | --- | ------ | ---------- | ------------------ | --------- | --------- | ------------------ | --------- | --- | ---- |
|           |          |     | P   | (ω)    | = F        | (ω)P               | (ω)+F     | (ω)P      | (ω),               |           |     | (21) |
|           |          |     |     | M      |            | C                  | +         | D         | D                  |           |     |      |
|           |          |     |     |        | (cid:124)  | (cid:123)(cid:122) | (cid:125) | (cid:124) | (cid:123)(cid:122) | (cid:125) |     |      |
|           |          |     |     |        | CommonPart |                    |           | DualPart  |                    |           |     |      |
where the functions F (ω) and F (ω) are filters designed to smooth the crossover from
|            |     |      | C       |        | D   |     |       |      |       |       |     |      |
| ---------- | --- | ---- | ------- | ------ | --- | --- | ----- | ---- | ----- | ----- | --- | ---- |
| the common | to  | dual | sensors | given  | by  |     |       |      |       |       |     |      |
|            |     |      | g       | g (s+z | )   |     |       |      | g g   | g s4  |     |      |
|            | F   | (ω)  | =       | a b    | b , | F   | (ω) = |      | c     | d e   | ,   | (22) |
|            | C   |      |         |        |     | D   |       |      |       |       |     |      |
|            |     |      |         | s(s+p  | )   |     |       | (s+p | )(s+p | )(s+p | )2  |      |
|            |     |      |         |        | b   |     |       |      | c     | d     | e   |      |
with the parameters given in table 5. Equation 21 can be rewritten as a function of the
0
edutingaM 10
|     |     |     |     | F (ω)P |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
(ω)
|     |     |     |     | C      | +   |     |     |     |     |     |     |     |
| --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
|     |     |     |     | F (ω)P | (ω) |     |     |     |     |     |     |     |
|     |     |     |     | D      | D   |     |     |     |     |     |     |     |
10 −2
|     |     | 10  | −4  | 10 −3 |     | 10 −2 |     | 10 −1 | 10  | 0   | 10 1 |     |
| --- | --- | --- | --- | ----- | --- | ----- | --- | ----- | --- | --- | ---- | --- |
Frequency [Hz]
300
]seerged[ esahP
200
100
0
−100
|     |     |     | −4  | −3  |     | −2  |     | −1  |     | 0   | 1   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     |     | 10  |     | 10  |     | 10  |     | 10  | 10  |     | 10  |     |
Frequency [Hz]
Figure 18: Common and dual components of the modified dual arm locking sensor. The
| combination | of             | these | gives   | the modified |     | dual | arm locking |      | sensor. |      |     |      |
| ----------- | -------------- | ----- | ------- | ------------ | --- | ---- | ----------- | ---- | ------- | ---- | --- | ---- |
| common      | and difference |       | sensors |              |     |      |             |      |         |      |     |      |
|             |                |       |         | P (ω)        | = P | (ω)H | (ω)−P       | (ω)H |         | (ω), |     | (23) |
|             |                |       |         | M            |     | +    | +           | −    | −       |      |     |      |
with
E(ω)
|     |     | H   | (ω) = | F (ω)+F |     | (ω), | H (ω) | =   |      | F   | (ω). | (24) |
| --- | --- | --- | ----- | ------- | --- | ---- | ----- | --- | ---- | --- | ---- | ---- |
|     |     | +   |       | C       | D   |      | −     |     | iω∆τ | D   |      |      |

| 3 ARM LOCKING |     |     |     |     |     |     |     |     |     | 30  |
| ------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
100
edutingaM
|     | 10−1 |     | S&S DAL Sensor |     |     |     |     |     |     |     |
| --- | ---- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- |
MDAL Sensor
10−2
|     | 10−4 |     | 10−3 |     | 10−2 | 10−1 |     | 100 |     | 101 |
| --- | ---- | --- | ---- | --- | ---- | ---- | --- | --- | --- | --- |
Frequency [Hz]
100
]seerged[ esahP
50
0
−50
−100
|     | 10−4 |     | 10−3 |     | 10−2 | 10−1 |     | 100 |     | 101 |
| --- | ---- | --- | ---- | --- | ---- | ---- | --- | --- | --- | --- |
Frequency [Hz]
Figure 19: Bode plot of the modified dual arm locking sensor (grey curve) and the Sutton
| and Shaddock | [21] (S&S) |     | dual arm | locking | sensor | (blue | curve). |     |     |     |
| ------------ | ---------- | --- | -------- | ------- | ------ | ----- | ------- | --- | --- | --- |
The frequency response of the modified dual arm locking sensor, shown in Figure 19,
is similar to the dual arm locking sensor, with an almost flat response below the first null
| with a magnitude | of        | 2.    |               |     |          |               |     |         |         |        |
| ---------------- | --------- | ----- | ------------- | --- | -------- | ------------- | --- | ------- | ------- | ------ |
|                  | Table     | 5:    | Parameters    | of  | modified | dual          | arm | locking | filters |        |
|                  | Filter    | zeros | (radians/s)   |     | Poles    | (radians/s)   |     |         | Gain    |        |
|                  | F (ω)     |       |               |     | p        | = 0           |     |         | g =     | (τ¯)−1 |
|                  | C         |       |               |     | a        |               |     |         | a       |        |
|                  |           | z     | = 2π×5/(13τ¯) |     | p        | = 2π×5/(2τ¯)  |     |         | g =     | p /z   |
|                  |           | b     |               |     | b        |               |     |         | b       | b b    |
|                  | F (ω)     |       | 0             |     | p        | = 7/(5τ¯)     |     |         | g =     | 1      |
|                  | D         |       |               |     | c        |               |     |         | c       |        |
|                  |           |       | 0             |     | p        | = 11/(20τ¯)   |     |         | g =     | 1      |
|                  |           |       |               |     | d        |               |     |         | d       |        |
|                  |           |       | 0             |     | p        | = 2π×1/(90τ¯) |     |         | g =     | 1      |
|                  |           |       |               |     | e        |               |     |         | e       |        |
| 3.4 Laser        | Frequency |       | Pulling       |     |          |               |     |         |         |        |
The relative velocities of the spacecraft cause a Doppler shift of up to 18 MHz [32]. For
arm locking to operate stably, this round trip Doppler frequency must be estimated and
subtracted in the phase measurements used in the arm locking sensor. In the limit of

| 3 ARM | LOCKING |     |     |     |     |     |     |     | 31  |
| ----- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
a high gain DC coupled arm locking control system, an error in the estimated Doppler
frequency is compensated for by changing the local laser frequency to maintain the desired
beat note frequency. In single arm locking, this frequency change will appear on the light
returning from the distant spacecraft 33 s later, necessitating a further change by the local
laser frequency to maintain the desired beat note frequency. The closed loop master laser
frequency, ν , will be changed by the error in the Doppler frequency, ν , each round
|     | CL  |     |     |     |     |     |     | DE  |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
trip, or an average rate of δνCL = ν c Hz/s. For example, if the Doppler frequency
|     |     |     | δt  | DE2L |     |     |     |     |     |
| --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- |
can be estimated to 100 kHz, the laser frequency will be forced to change by 1 GHz in 4
days. Such large pulling of the laser frequency is undesirable, as it could drive the master
laser through a mode-hop region, compromising instrument sensitivity. The other lasers
in the constellation are also at risk of being pulled into a mode-hop region as they will be
locked to the master laser frequency. Additionally, ramping of laser frequency combined
with scattered light sources can couple noise into the science band, see Section 4.7.
Frequency pulling can be considered in two regimes: 1) in steady state operation, and
2) at lock acquisition. At lock acquisition, the laser frequency can be pulled significantly
by an error in the initial Doppler frequency estimate and also in the time derivatives of
| the Doppler | frequency. |              | We see two | solutions: |                 |     |               |       |     |
| ----------- | ---------- | ------------ | ---------- | ---------- | --------------- | --- | ------------- | ----- | --- |
| • Add       | high       | pass filters | to the     | arm        | locking control |     | loop to limit | this. |     |
Have a DC coupled controller with an additional control loop operating at low fre-
•
quencies to limit the amplitude of the controller signal at these frequencies [31].
While we present the first solution here, the second, active solution may have precision
advantages in implementation and details can be found in reference [31].
We expect the arm locking control system will operate as follows: before arm locking
is engaged, measurements of the Doppler frequency and the Doppler rate (the first time
derivative of the Doppler frequency) will be made (Appendix A. of reference [30]) and
subtracted from the phasemeter measurement. After the control loop is closed, the error
in the Doppler frequency measurement will cause the laser frequency to ramp at a rate
proportional to the product of the error and the step response of the controller. Whilst
locked, the Doppler frequency estimate will not need to be updated. The arm locking
control loop will be unlocked and re-locked periodically to perform mission tasks, such as
to change the heterodyne frequencies [32]. At these times the Doppler frequency and its
time derivatives will be known very accurately (as many weeks or months of data can be
averaged to measure it) and the impulse to laser frequency will be much smaller than in
| the first     | time arm | locking   | is engaged. |     |     |     |     |     |     |
| ------------- | -------- | --------- | ----------- | --- | --- | --- | --- | --- | --- |
| 3.4.1 Pulling |          | in Steady | State       |     |     |     |     |     |     |
The laser frequency pulling in modified dual arm locking arises due to both the common,
| ν = | ν   | + ν | , and differential |     | errors, | ν   | = ν | ν in the | Doppler |
| --- | --- | --- | ------------------ | --- | ------- | --- | --- | -------- | ------- |
−
| DE+ | DE12 | DE13 |     |     |     | DE− | DE12 | DE13 |     |
| --- | ---- | ---- | --- | --- | --- | --- | ---- | ---- | --- |

| 3 ARM | LOCKING |     |     |     |     |     |     |     |     | 32  |
| ----- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Phasemeter
ν
DE12
+
|     |     | ν   | ν    |       |     |     |     |         |     |     |
| --- | --- | --- | ---- | ----- | --- | --- | --- | ------- | --- | --- |
|     |     |     | + CL |       | +   |     | +   |         |     |     |
|     |     | OL  | Σ    | P (ω) |     | Σ   |     | Σ H (ω) |     |     |
|     |     |     |      | 12    |     |     |     | +       |     |     |
+
−
|     |     | lauD deifidoM |     | P (ω) | +   |     |     |     |     |     |
| --- | --- | ------------- | --- | ----- | --- | --- | --- | --- | --- | --- |
Σ
13
|     |     |     |     |     |     | +    |     | −      | +   |     |
| --- | --- | --- | --- | --- | --- | ---- | --- | ------ | --- | --- |
|     |     |     |     |     |     | ν    | +   |        | −   |     |
|     |     |     |     |     |     | DE13 |     | Σ H(ω) | Σ   |     |
-
Phasemeter
Controller
G(ω)
1
|     |     |     |     | G*(ω) | 1/2 |     |     |     |     |     |
| --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- |
1
Figure 20: Block diagram of the modified arm locking control system showing where the
| Doppler    | frequency |               | errors, ν | , ν       | enter | the control | loop. |     |     |      |
| ---------- | --------- | ------------- | --------- | --------- | ----- | ----------- | ----- | --- | --- | ---- |
|            |           |               |           | DE12 DE13 |       |             |       |     |     |      |
| frequency. |           | The frequency | responses | are       |       |             |       |     |     |      |
|            |           |               |           | ν         |       | −G (ω)H     | (ω)   |     |     |      |
|            |           |               | Y(±)(ω)   | CL        | | M   | 1           | ±     |     |     |      |
|            |           |               |           | =         | =     |             |       | ,   |     | (25) |
|            |           |               | M         | ν         |       | 1+G (ω)P    |       | (ω) |     |      |
|            |           |               |           | DE±       |       | 1           | M     |     |     |      |
where the ‘+’ is used for the common path and the ‘−’ for the difference path. Figure 20
is a block diagram showing where the Doppler error enters the modified dual arm locking
sensor-atthephasemeter,beforethesignalsarecombinedtocreatethearmlockingsensor.
The laser frequency pulling in steady state for modified dual arm locking is
|     |     |     | ν (t) | = y(+)(t)∗∆ | (t)+y(−)(t)∗∆ |     |     | (t), |     | (26) |
| --- | --- | --- | ----- | ----------- | ------------- | --- | --- | ---- | --- | ---- |
|     |     |     | CL    | D           | +             | D   |     | −    |     |      |
where ∆ (t) is the differential Doppler shift of the two arms used and y(+)(t) and y(−)(t)
|         | −       |         |            |     |         |          |     |               | M   | M   |
| ------- | ------- | ------- | ---------- | --- | ------- | -------- | --- | ------------- | --- | --- |
|         |         |         |            |     | Y(+)(ω) | Y(−)(ω), |     |               |     |     |
| are the | inverse | Laplace | transforms | of  |         | and      |     | respectively. |     |     |
|         |         |         |            |     | M       |          | M   |               |     |     |
The laser frequency pulling in steady state is shown in Figure 21 with the controller
detailed in section 3.6 is very modest, less than 8 MHz peak to peak whilst operating
in steady state. The pulling is dominated by the common Doppler shift. The pulling is
independent of the laser frequency noise as no Doppler frequency estimates are used, and
will be an insignificant change compared to the laser frequency drift over this period.
| 3.4.2 | Pulling | at  | Lock Acquisition |     |     |     |     |     |     |     |
| ----- | ------- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- |
In addition to the error in Doppler frequency associated with the initial estimate of the
commonDopplerfrequency,ν ,theerrorwillevolveintimeduetothechangesinDoppler
0+

| 3 ARM | LOCKING |     |     |     |     |     |     |     |     | 33  |
| ----- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|       |         | 4   |     |     |     |     |     |     |     |     |
MDAL − steady state common part
MDAL − steady state diff part
2
]zHM[ gnilluP
0
−2
−4
|     |     | 100 | 200 | 300 |     | 400 500 |     | 600 700 | 800 |     |
| --- | --- | --- | --- | --- | --- | ------- | --- | ------- | --- | --- |
Time [days]
Figure 21: The laser frequency pulling when arm locking is engaged. The pulling arrises
because the changing Doppler frequencies. The component due to the common Doppler
shift dominates.
frequency2. Thus, the first and second time derivatives of the Doppler frequency, labeled
γ (t), and α (t), need to be accounted for. The common Doppler frequency error in the
| +           | +   |     |     |         |          |               |          |                    |     |      |
| ----------- | --- | --- | --- | ------- | -------- | ------------- | -------- | ------------------ | --- | ---- |
| time domain | is  |     |     |         |          |               |          |                    |     |      |
|             |     |     |     |         |          | t             | t        | t(cid:48)          |     |      |
|             |     |     |     |         | (cid:90) |               | (cid:90) | (cid:90)           |     |      |
|             |     | ν   | (t) | = ν     | +        | γ (t)dt+      |          | α (t)dt(cid:48)dt+ |     |      |
|             |     | DE+ |     | 0+      |          | +             |          | +                  |     |      |
|             |     |     |     |         | 0        |               | 0        | 0                  |     |      |
|             |     |     |     | (Higher |          | order terms), |          |                    |     | (27) |
HigherordertimederivativesofthecommonDopplerfrequencyerrorareneglectedbecause
| they are | sufficiently | small. |     |     |     |     |     |     |     |     |
| -------- | ------------ | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
The design of the arm locking controller is such that the transients will decay over a
period of a few days. Over this period the terms γ (t),α (t) will change little and for
|     |     |     |     |     |     |     | +   | +   |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
simplicity we shall approximate these terms as constants equal to their initial errors. The
| Doppler | error at | lock acquisition |     | is  | then |       |     |     |     |      |
| ------- | -------- | ---------------- | --- | --- | ---- | ----- | --- | --- | --- | ---- |
|         |          |                  |     |     |      |       | α   | t2  |     |      |
|         |          |                  | ν   | (t) | ν    | +γ t+ | 0+  | ,   |     | (28) |
≈
|     |     |     | DE+ |     | 0+  | 0+  | 2   |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
with the initial errors in the Doppler rate, change in the Doppler rate given by γ and
0+
| α . In | the frequency | domain, |     | the | Doppler | error | at lock | acquisition | is  |     |
| ------ | ------------- | ------- | --- | --- | ------- | ----- | ------- | ----------- | --- | --- |
0+
|     |     |     |     |     |     | γ   | α   |     |     |      |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- |
|     |     |     |     |     |     | 0+  | 0+. |     |     |      |
|     |     |     |     | ν   | ≈ ν | + − |     |     |     | (29) |
|     |     |     |     | DE+ | 0+  | iω  | 2ω2 |     |     |      |
2The errors in the differential Doppler frequency can be neglected for modified dual arm locking [30]

| 3 ARM | LOCKING |     |     |     |     |     |     |     |     |     |     | 34  |
| ----- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
The frequency responses to the different terms in equation 29 can be found using equa-
| tion | 25. The | frequency |     | responses |     | are |         |          |      |     |     |      |
| ---- | ------- | --------- | --- | --------- | --- | --- | ------- | -------- | ---- | --- | --- | ---- |
|      |         |           |     |           |     |     | −G      | (ω)H (ω) |      |     |     |      |
|      |         |           |     | V(+)(ω)   |     | =   | 1       | +        | ,    |     |     | (30) |
|      |         |           |     |           |     |     | 1+G     | (ω)P     | (ω)  |     |     |      |
|      |         |           |     |           |     |     |         | 1 M      |      |     |     |      |
|      |         |           |     |           |     |     | −G      | (ω)H     | (ω)  |     |     |      |
|      |         |           |     | G(+)(ω)   |     | =   |         | 1        | +    | ,   |     | (31) |
|      |         |           |     |           |     |     | iω(1+G  | (ω)P     | (ω)) |     |     |      |
|      |         |           |     |           |     |     |         | 1        | M    |     |     |      |
|      |         |           |     |           |     |     | G       | (ω)H     | (ω)  |     |     |      |
|      |         |           |     | A(+)(ω)   |     | =   |         | 1 +      |      | .   |     | (32) |
|      |         |           |     |           |     |     | 2ω2(1+G | (ω)P     | (ω)) |     |     |      |
|      |         |           |     |           |     |     |         | 1        | M    |     |     |      |
Frequency pulling during lock acquisition is determined by the step response of the
control system. The step response follows from the closed-loop control system ν (s)
CL
| according | to  |     |     |     |     |     |     |     |     |     |     |     |
| --------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
(cid:18)ν (s)(cid:19)
|     |     |     |     |     | ν    | (t) = | L−1 | CL  | ,   |     |     | (33) |
| --- | --- | --- | --- | --- | ---- | ----- | --- | --- | --- | --- | --- | ---- |
|     |     |     |     |     | step |       |     | s   |     |     |     |      |
where s = iω and L−1 is the inverse Laplace transform operator. Step responses from
the error in the three Doppler derivatives, equations 30-32, are plotted in Figure 22, for
both free-running and pre-stabilized lasers. The maximum pulling including errors in all
the derivatives of ν is 460, 90, and 4 MHz, for the respective cases of free-running,
0+
Mach-Zehnder pre-stabilized, and Fabry-Perot cavity pre-stabilized lasers. These plots
have been made assuming 200 s of averaging for the Doppler estimates and show that since
the Doppler frequency estimates are better for pre-stabilized lasers, the pulling is smaller.
Further reduction of pulling can be achieved simply by increasing the Doppler frequency
measurement time. In the case of free-running laser noise, the estimates of γ and α
0+ 0+
have an error larger than the maximum value determined by the orbital motion. Thus we
do not use the laser measurement of these quantities; rather, we assume them to be zero.
With pre-stabilization the error in the measurement of α is larger than its maximum
0+
| value | and thus | we     | assume | it       | to be | zero. |        |          |        |       |       |      |
| ----- | -------- | ------ | ------ | -------- | ----- | ----- | ------ | -------- | ------ | ----- | ----- | ---- |
| 3.5   | Noise    | Limits |        |          |       |       |        |          |        |       |       |      |
| For   | modified | dual   | arm    | locking, | the   | noise | at the | laser    | output | is    |       |      |
|       |          |        |        | φ        |       |       | G      | (ω)      |        |       |       |      |
|       | φ        | | =    |        | L1       |       | −     | 1      |          | S      | [N +N | +N ], | (34) |
|       | O1       | M      | 1+P    | (ω)G     | (ω)   | 1+P   |        | (ω)G (ω) | M      | S     | C X   |      |
|       |          |        |        | M        | 1     |       | M      | 1        |        |       |       |      |
The vectors containing the shot noise, clock noise, and spacecraft motion are given by
|     |     |     |     |          |      |     |          | (cid:34) |     |       | (cid:35) |     |
| --- | --- | --- | --- | -------- | ---- | --- | -------- | -------- | --- | ----- | -------- | --- |
|     |     |     |     | (cid:20) | φ +φ |     | (cid:21) | ∆12(y    |     | (f)+y | (f))     |     |
|     |     |     |     |          |      |     |          |          | 1   |       | 2        |     |
|     |     |     | N   | =        | S12  | S21 | ,N       | = 2πf    |     |       | ,        |     |
|     |     |     | S   |          | φ +φ |     | C        | ∆13(y    |     | (f)+y | (f))     |     |
|     |     |     |     |          | S13  | S31 |          |          | 1   |       | 3        |     |
2πf
|     |     |     |     | (cid:20) | φ (cid:0) | 1 + e − | i 2 ω τ | (cid:1) + 2 φ | (cid:21) |     |     |      |
| --- | --- | --- | --- | -------- | --------- | ------- | ------- | ------------- | -------- | --- | --- | ---- |
|     |     |     |     |          | X 1 2     |         | 1 2     | X             | 2 1      |     |     |      |
|     |     |     | N   | =        | (cid:0)   |         |         | (cid:1)       | .        |     |     | (35) |
|     |     |     | X   |          | φ         | 1 + e − | i 2 ω τ | + 2 φ         |          |     |     |      |
|     |     |     |     |          | X 1 3     |         | 1 3     | X             | 3 1      |     |     |      |

| 3 ARM LOCKING |     |                                        |     |     |     | 35    |
| ------------- | --- | -------------------------------------- | --- | --- | --- | ----- |
|               |     |                                        |     |     |     | v (t) |
|               | 300 | M-dual arm locking: Free running laser |     |     |     | +     |
]zHM[ gnilluP
|     | 200 |     |     |     |     | g (t) |
| --- | --- | --- | --- | --- | --- | ----- |
+
|     |     |     |     |     |     | a (t) |
| --- | --- | --- | --- | --- | --- | ----- |
|     | 100 |     |     |     |     | +     |
0
−100

|     | 0 2 | 4 6 | 8 10 | 12 14 | 16 18 | 20  |
| --- | --- | --- | ---- | ----- | ----- | --- |
Time [days]
|     | 80  |                                         |     |     |     | v (t) |
| --- | --- | --------------------------------------- | --- | --- | --- | ----- |
|     |     | M-dual arm locking: MZ Prestabilization |     |     |     | +     |
]zHM[ gnilluP
|     | 60  |     |     |     |     | g (t) |
| --- | --- | --- | --- | --- | --- | ----- |
+
|     | 40  |     |     |     |     | a (t) |
| --- | --- | --- | --- | --- | --- | ----- |
+
20
0
−20
|     | 0 2 | 4 6 | 8 10 | 12 14 | 16 18 | 20  |
| --- | --- | --- | ---- | ----- | ----- | --- |
Time [days]
|     |               |                                         |     |     |     | v (t)   |
| --- | ------------- | --------------------------------------- | --- | --- | --- | ------- |
|     | 3             | M-dual arm locking: FP Prestabilization |     |     |     | +       |
|     | ]zHM[ gnilluP |                                         |     |     |     | g (t)   |
|     | 2             |                                         |     |     |     | +       |
|     | 1             |                                         |     |     |     | a + (t) |
0
−1
|     | 0 2 | 4 6 | 8 10 | 12 14 | 16 18 | 20  |
| --- | --- | --- | ---- | ----- | ----- | --- |
Time [days]
Figure 22: The step responses of different drivers of Doppler frequency error for modified
dual arm locking. The upper, middle, and lower plots assume free-running laser noise,
Mach-Zehndertypepre-stabilization, andFabry-Perotcavitypre-stabilzation, respectively,
| with the Doppler | frequency | estimates | averaged | for 200 s. |     |     |
| ---------------- | --------- | --------- | -------- | ---------- | --- | --- |

3 ARM LOCKING 36
3.5.1 Performance Assuming Free-running Laser Noise
Figure 23 shows the noise budget of modified dual arm locking (plotted using equation 34)
withfree-runninglasernoise, anarmlengthmismatchof2∆τ = 0.51s, andtheparameters
in table 6. The total noise (dashed black curve) is a quadrature sum of shot noise (red
curve), spacecraft motion (green curve), the clock noise (blue curve) and laser frequency
noise (cyan curve). For this arm length mismatch the laser frequency noise is the limiting
noise source (the system is gain limited) with the other system noise sources well below
the laser frequency noise. Clock noise is the largest other noise source below 20 mHz and
spacecraftmotionrepresentsanoiselimitatfrequenciesabovethis. Notethatclocknoiseis
linearlydependentontheheterodynefrequencyateachphasemeterandthisplotwasmade
with the worst combination of heterodyne frequencies that can occur for dual arm locking:
a maximum difference in Doppler shifts between the two arms, ∆ −∆ = 29 MHz. In
13 12
the science band, shot noise is always smaller than the both clock and spacecraft motion,
though it dominates above band as clock noise and spacecraft motion roll off.
6
10
4
10
2 10
0
10
−2
10
−4
10
−4 −3 −2 −1 0 1
10 10 10 10 10 10
Frequency[Hz]
]zHtr/zH[
esioN
Free running laser
TDI Capability
Total, frequency
Clock
S/C motion Shot
Figure 23: The noise budget of modified dual arm locking with arm length mismatch of
∆τ = 0.51s. The performance was calculated with free-running laser noise as an initial
condition.
Even without any form of laser pre-stabilization arm locking will meet the TDI capa-
bility across the entire LISA science band. At the most sensitive frequency of LISA, 3 mHz
the frequency noise is a factor of 5 below the TDI capability. If there is not a failure of one
inter-spacecraft laser link, the dual arm locking central spacecraft can be switched when
the arm length mismatch becomes small, and arm locking alone has sufficient performance

| 3 ARM   | LOCKING |            |                  |     |     |     | 37  |
| ------- | ------- | ---------- | ---------------- | --- | --- | --- | --- |
| to meet | the TDI | capability | for the mission. |     |     |     |     |
The variation of the modified dual arm locking noise floor due to the changing arm
length mismatch can be seen in Figure 24. This shows the noise sources at 3 mHz over the
firsttwoyearsoftheLISAmissionassumingonlytwoofthethreeLISAarmsareavailable.
In this case, the noise floor at 3 mHz is below the TDI capability for the vast majority of
the time and breaches the TDI capability for only short periods, twice per year. It also
provides some indication of how infrequently and how short a time dual arm locking can
not meet the TDI capability in case of a critical failure of one arm. The noise performance
is insufficient to meet the TDI capability for approximately 1/2 an hour, twice per year.
|     | 4   |                         |     |     | 104 |       |     |
| --- | --- | ----------------------- | --- | --- | --- | ----- | --- |
| 10  |     |                         |     |     |     |       |     |
|     |     | TDI Capability at 3 mHz |     |     | zH  | Clock |     |
m
|                          | 2   |     |       |     |  3      |                |     |
| ------------------------ | --- | --- | ----- | --- | ------- | -------------- | --- |
| 10                       |     |     |       |     |  ta     |                |     |
| zHm 3 ta ]zHtr/zH[ esioN |     |     |       |     |  ]zH103 |                |     |
|                          |     |     |       |     | tr/zH   | TDI Capability |     |
|                          | 0   |     |       |     | [ e     |                |     |
| 10                       |     |     | Clock |     | sio     |                |     |
N
S/C motion
102
|     |     |     | S/C motion |     | 0 1 | 2 3 | 4 5 |
| --- | --- | --- | ---------- | --- | --- | --- | --- |
−2
| 10  |     |         |         |     | Time [Hours] + (459 days) |     |     |
| --- | --- | ------- | ------- | --- | ------------------------- | --- | --- |
|     | −4  |         | Shot    |     |                           |     |     |
| 10  |     |         |         |     |                           |     |     |
|     |     | 100 200 | 300 400 | 500 | 600 700                   |     |     |
Time [Days]
Figure 24: The noise sources of arm locking measured at 3 mHz over the first two years
of the LISA mission. This plot assumes only two of the three LISA arms are available,
preventing the central spacecraft from being switched at small arm length mismatch. The
heterodyne frequency assumed for the clock noise curve here is pessimistic, as we have
assumed the worst case that occurs in the mission (∆ −∆ = 29 MHz ) for the duration
|     |     |     |     | 12  | 13  |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- |
of this plot. The heterodyne frequency over the mission lifetime depends on the Doppler
| shift, which | we have | neglected | for simplicity. |     |     |     |     |
| ------------ | ------- | --------- | --------------- | --- | --- | --- | --- |
| 3.6 The      | Arm     | Locking   | Controller      |     |     |     |     |
Thearmlockingcontrollerisdesignedforthemodifieddualarmlockingsensors. Compared
to a standard phase-locking control loop, the arm locking control loop has two additional
| design constraints. |     | These | are: |     |     |     |     |
| ------------------- | --- | ----- | ---- | --- | --- | --- | --- |
1. The controller should have appropriate low frequency filtering to limit the laser fre-
| quency | pulling. |     |     |     |     |     |     |
| ------ | -------- | --- | --- | --- | --- | --- | --- |
2. The controller must allow for the nulls in the sensor and the additional phase delay
associated with them. The nulls in the dual arm locking sensor occur at frequencies

| 3 ARM        | LOCKING    |            |         |            |     |              |           |          |         | 38  |
| ------------ | ---------- | ---------- | ------- | ---------- | --- | ------------ | --------- | -------- | ------- | --- |
|              |            | Table      | 6: LISA | parameters |     | and          | amplitude | of noise | sources |     |
| Parameter    |            |            |         | Symbol     |     | Value        |           |          | Units   |     |
| Average      |            | arm length |         |            | L¯  | 5×109        |           |          | m       |     |
| Differential |            | arm        | length  |            | ∆L  | ≤ 76,500,000 |           |          | m       |     |
| Laser        | wavelength |            |         |            | λ   | 1064         |           |          | nm      |     |
| Doppler      |            | shift arm  | 13      |            | ∆   | 15           |           |          | MHz     |     |
13
| Doppler |     | shift arm | 12  |     | ∆   | -14 |     |     | MHz |     |
| ------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
12
|              |     |     |       |     |      |            |     | √   | √     |     |
| ------------ | --- | --- | ----- | --- | ---- | ---------- | --- | --- | ----- | --- |
| Fluctuations |     | of  | clock |     | y(f) | 2.4×10−12/ |     | f   | 1/ Hz |     |
√
| Shot | noise |     |     |     | φ   | 10  |     |     | µcycles/ | Hz  |
| ---- | ----- | --- | --- | --- | --- | --- | --- | --- | -------- | --- |
Sij
|            |     |        |     |     |     |      | (cid:112)1+(f/0.3Hz)4 |     |               | √   |
| ---------- | --- | ------ | --- | --- | --- | ---- | --------------------- | --- | ------------- | --- |
| Spacecraft |     | motion |     |     | φ   | 2.5× |                       |     | 10−3· cycles/ | Hz  |
Xij
√
| TDI | capability |     |     | ν   | (f) | 300×(1+(3 |     | mHz/f)2) | Hz/ Hz |     |
| --- | ---------- | --- | --- | --- | --- | --------- | --- | -------- | ------ | --- |
TDI
| above |     | 2 Hz. |     |     |     |     |     |     |     |     |
| ----- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
These additional constraints limit the achievable gain in the LISA science band and neces-
sitate careful design to ensure loop stability. Although the controller is designed for the
maximum arm length mismatch, it will operate stably for smaller arm length mismatch.
| 3.6.1 | Controller |     | Overview |     |     |     |     |     |     |     |
| ----- | ---------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
AblockdiagramofthecontrollerarchitectureisshowninFigure25. Thecontrollerconsists
of five stages. Stage 1 is the very low frequency part of the controller and comprises three
zero-pole pairs to form unity gain high pass filters at 0.8 µHz in series. Stage 2 sets the
lowerunitygainfrequencyandhasazeroatDCandapoleat210µHz. Thislowfrequency
filtering is adopted to limit laser frequency pulling that arises at lock acquisition and in
steady state. Stage 3 is a lead stage, which has five zero-pole stages in series to roll up
the gain steeply between the lower unity gain frequency and the low frequency part of the
controller. Stage 4 consists of two poles in series and provides the transition between the
low frequency gain and the shallow slope high frequency part of the controller. Stage 5
is the shallow sloped part of the controller. It consists of nine poles in parallel, with the
gain for each pole chosen to achieve the required slope of approximately f−0.66 a slope
optimized to maximize the gain while maintaining > 30 degree phase margin at the unity
| gain frequencies. |          | The                   | frequency |                     | response | of the     | controller | is given | by       |          |
| ----------------- | -------- | --------------------- | --------- | ------------------- | -------- | ---------- | ---------- | -------- | -------- | -------- |
|                   |          |                       |           |                     |          |            | (cid:32)   |          |          | (cid:33) |
|                   | (cid:18) | g s (cid:19)3(cid:18) | g         | s (cid:19)(cid:18)g | (s+z     | )(cid:19)5 |            | g        | 9        | g        |
|                   |          | 1                     |           | 2                   | 3        | 3          |            | 4        | (cid:88) | 5k       |
| G∗(ω)             | =        |                       |           |                     |          |            |            |          | +        | , (36)   |
| 1                 |          | s+p                   | s+p       |                     | s+p      |            | (s+p       | )(s+p    | ) s+p    |          |
|                   |          | 1                     |           | 2                   |          | 3          |            | 41       | 42       | 5k       |
k=1

| 3 ARM | LOCKING |         |     |     |         |     |         |       |     | 39  |
| ----- | ------- | ------- | --- | --- | ------- | --- | ------- | ----- | --- | --- |
|       |         | Stage 2 |     |     | Stage 3 |     | Stage 4 |       |     |     |
|       |         |         |     |     |         |     | p       | p     | g   |     |
|       |         | z       | p   | g   | z       | p g |         | 41 42 | 4   |     |
|       |         | 2       | 2   | 2   | 3       | 3 3 |         |       |     |     |
|       |         |         |     |     | z       | p g |         |       |     |     |
|       |         |         |     |     | 3       | 3 3 |         |       |     |     |
|       |         |         |     |     |         |     |         | p g   |     |     |
|       |         | Stage 1 |     |     |         |     |         | 51 51 |     |     |
+
|     |     |     |     |     | z   | p g |     |       |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | --- |
|     |     |     | p   | g   | 3   | 3 3 |     |       |     |     |
|     |     | z   |     |     |     |     |     | p g   |     |     |
|     |     | 1   | 1   | 1   |     |     |     | 52 52 |     |     |
.
|     |     |     |     |     | z   | p g |         | .     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------- | ----- | --- | --- |
|     |     | z   | p   | g   | 3   | 3 3 |         | .     |     |     |
|     |     | 1   | 1   | 1   |     |     |         |       |     |     |
|     |     |     |     |     |     |     |         | p g   |     |     |
|     |     |     |     |     | z   | p g |         | 59 59 |     |     |
|     |     | z   | p   | g   | 3   | 3 3 |         |       |     |     |
|     |     | 1   | 1   | 1   |     |     | Stage 5 |       |     |     |
Controller
Figure 25: Block diagram of the arm locking controller. The controller is built from five
stages: stage 1 consist of three very low frequency high pass filters, stage 2, defines the
lower unity gain frequency; stage 3, rolls up the gain below the LISA science band; stage
4 has two poles in parallel to effectively transition between stage 3 and stage 5; stage 5
has 9 poles in parallel, with gains individually chosen to generate a slope of approximately
f−0.66.
| with values | of  | the zeros, | poles, | and | gains listed | in table | 73. |     |     |     |
| ----------- | --- | ---------- | ------ | --- | ------------ | -------- | --- | --- | --- | --- |
The assumption of delays in the control system are shown in table 8. The open loop
gain of the control system with the modified dual arm locking sensor is given by
|     |     | G   | (ω) | = G (ω)P | (ω)e−iω(τact+τpm+τtrans+τps). |     |     |     |     | (37) |
| --- | --- | --- | --- | -------- | ----------------------------- | --- | --- | --- | --- | ---- |
|     |     |     | L   | 1        | M                             |     |     |     |     |      |
TheBodeplotofG (ω)isplottedinFigure26. Notethatinthisplotwehaveassumedthe
L
phase delays of the pre-stabilization control loop can also be removed and thus set τ = 0.
ps
Thus, when we discuss system options in section II the same arm locking controller can be
| used with | and | without | pre-stabilization. |     |     |     |     |     |     |     |
| --------- | --- | ------- | ------------------ | --- | --- | --- | --- | --- | --- | --- |
The open loop phase looks somewhat deceptive. At high frequencies it appears that
the open loop phase crosses 180 degrees before 1 kHz, making the 14.9 kHz bandwidth
control loop unstable. In fact, the total phase at the unity gain points is always greater
than -150 degrees which is indicated by the red solid curve, which is given by
180
|          | θ     | = ∠G∗(ω)× |          |     | +θ        | +360f(τ | +τ  | +τ  | ),    | (38) |
| -------- | ----- | --------- | -------- | --- | --------- | ------- | --- | --- | ----- | ---- |
|          | UG    |           | 1        | π   | sensor|UG |         | act | pm  | trans |      |
| which is | valid | for f     | 1/(2∆τ). |     |           |         |     |     |       |      |
≥
3An additional low pass filter in series with the controller is generally required to roll off the loop gain
| at the resonance |     | frequency | of the | laser | PZT actuator | (near 100 | kHz) |     |     |     |
| ---------------- | --- | --------- | ------ | ----- | ------------ | --------- | ---- | --- | --- | --- |

3 ARM LOCKING 40
4
10
2 10
0
10
−2
10
−6 −4 −2 0 2 4
10 10 10 10 10 10
Frequency [Hz]
edutingaM
300
200
100
0
−100
−200 −6 −4 −2 0 2 4
10 10 10 10 10 10
Frequency [Hz]
]seerged[
esahP
Open Loop Magnitude
Gain Requirement
Open Loop Phase
Phase at unity gain
-150 degrees
Figure 26: Open loop frequency response, G (ω), of modified dual arm locking. Also
L
shown in the magnitude plot is the gain required to meet the TDI capability, assuming no
pre-stabilization. In the phase plot, the red curve indicates the total phase of the control
loop at unity gain (given by equation 38). The arm length mismatch is assumed to be
2∆τ = 0.51s.

| 3   | ARM | LOCKING |          |            |            |         |            | 41  |
| --- | --- | ------- | -------- | ---------- | ---------- | ------- | ---------- | --- |
|     |     |         | Table 7: | Parameters | of the arm | locking | controller |     |
Stage zeros (radians/s) Poles (radians/s) Gain (radians/radian)
|     | 1   | z = | 0            |     | p = 2π×8×10−7   |     | g =   | 1      |
| --- | --- | --- | ------------ | --- | --------------- | --- | ----- | ------ |
|     |     | 1   |              |     | 1               |     | 1     |        |
|     | 2   | z = | 0            |     | p = 2π×210×10−6 |     | g =   | 0.95/f |
|     |     | 2   |              |     | 2               |     | 2     | ac     |
|     | 3   | z = | 2π×36.6×10−6 |     | p = 2π×185×10−6 |     | 4 g = | p /z   |
|     |     | 3   |              |     | 3               |     | 3     | 3 3    |
|     | 4   |     |              |     | p = 2π×3×10−3   |     |       |        |
41
|     |     |     |     |     | p = 2π×238×10−3 |     | g = | p p        |
| --- | --- | --- | --- | --- | --------------- | --- | --- | ---------- |
|     |     |     |     |     | 42              |     | 4   | 41 42      |
|     | 5   |     |     |     | p = 2π×3×10−3   |     | g   | = 1.3×10−3 |
|     |     |     |     |     | 51              |     | 51  |            |
|     |     |     |     |     | p = 2π×3×10−2   |     | g   | = 3.7×10−3 |
|     |     |     |     |     | 52              |     | 52  |            |
|     |     |     |     |     | p = 2π×3×10−1   |     | g   | = 4.2×10−3 |
|     |     |     |     |     | 53              |     | 53  |            |
|     |     |     |     |     | p = 2π×3        |     | g   | = 16×10−3  |
|     |     |     |     |     | 54              |     | 54  |            |
|     |     |     |     |     | p = 2π×3×101    |     | g   | = 30×10−3  |
|     |     |     |     |     | 55              |     | 55  |            |
|     |     |     |     |     | p = 2π×3×102    |     | g   | = 69×10−3  |
|     |     |     |     |     | 56              |     | 56  |            |
|     |     |     |     |     | p = 2π×3×103    |     | g   | = 0.11     |
|     |     |     |     |     | 57              |     | 57  |            |
|     |     |     |     |     | p = 2π×3×104    |     | g   | = 0.33     |
|     |     |     |     |     | 58              |     | 58  |            |
|     |     |     |     |     | p = 2π×3×105    |     | g   | = 0.70     |
|     |     |     |     |     | 59              |     | 59  |            |
ThedisturbancesuppressionfunctionisshowninFigure27. Alsoplottedistherequired
suppression to meet the TDI capability. Note that the amplification at the nulls is always
less than a factor of 2 except near the final unity gain frequency, near 15 kHz, where the
| amplitude |     | increases | to 5. |     |     |     |     |     |
| --------- | --- | --------- | ----- | --- | --- | --- | --- | --- |
3.7 Summary
Our understanding of arm locking has matured significantly in the last year. We have:
• Adetailedanalysisofarmlockingwhichincludesmanyoftheorbitaleffectsexpected
|     | on LISA. |     |     |     |     |     |     |     |
| --- | -------- | --- | --- | --- | --- | --- | --- | --- |
• Understanding of laser frequency pulling and two methods to limit to an acceptable
level.
• A noise analysis includes the expected dominant noise sources in arm locking; clock
|     | noise, | spacecraft | motion, | and | shot noise. |     |     |     |
| --- | ------ | ---------- | ------- | --- | ----------- | --- | --- | --- |
• A new sensor design for the dual arm locking sensor that uses a combination of the
common and dual arm sensor at frequencies below 1/τ¯ and the dual arm locking
sensor frequencies above 1/τ¯ to retain the control system advantages of dual arm
locking while inheriting the frequency pulling characteristics and low frequency noise
|     | performance |     | of common | arm | locking. |     |     |     |
| --- | ----------- | --- | --------- | --- | -------- | --- | --- | --- |

| 3 ARM LOCKING |        |           |        |         |          |          |          |            | 42   |
| ------------- | ------ | --------- | ------ | ------- | -------- | -------- | -------- | ---------- | ---- |
|               |        | Table     | 8: Arm | locking | system   | delays   |          |            |      |
| Type of Delay |        | Symbol    |        | Delay   |          |          | Notes    |            |      |
|               |        |           |        |         | (cid:16) | (cid:17) |          |            |      |
| Arm locking   | sensor | θ         |        | −arccos | 1        |          | Phase at | unity gain | [30] |
|               |        | sensor|UG |        |         | |2G∗(ω)| |          |          |            |      |
1
| Actuator | delay | τ   |     |     | 5µs |     | PZT delay | (4µs | measured) |
| -------- | ----- | --- | --- | --- | --- | --- | --------- | ---- | --------- |
act
| Phasemeter |     | τ   |     |     | 2µs |     | DACs have | 1µs delay |     |
| ---------- | --- | --- | --- | --- | --- | --- | --------- | --------- | --- |
pm
| Transponding | S/C | τ   |     | (2π30kHz)−1s |     |     | 30kHz UGF | assumed5 |     |
| ------------ | --- | --- | --- | ------------ | --- | --- | --------- | -------- | --- |
trans
| Pre-stabilization |     | τ   |     | (2π30kHz)−1s |     |     | 30kHz UGF | assumed |     |
| ----------------- | --- | --- | --- | ------------ | --- | --- | --------- | ------- | --- |
ps
1
10
10 0
−1
10
edutingaM 10 −2
−3
10
−4
10
−5
|     |     | 10  |     |     |     | Required Suppression |     |     |     |
| --- | --- | --- | --- | --- | --- | -------------------- | --- | --- | --- |
Suppression function
−6
10
|     |     | −8 −6 |     | −4 −2 | 0   | 2   | 4   | 6   |     |
| --- | --- | ----- | --- | ----- | --- | --- | --- | --- | --- |
|     |     | 10 10 | 10  | 10    | 10  | 10  | 10  | 10  |     |
Frequency [Hz]
Figure 27: Plot of the disturbance sensitivity, S (ω) = 1/(1+G (ω)) and the required
|     |     |     |     |     | D   |     |     | L   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
suppression to meet the TDI capability without pre-stabilization. Plotted with 2∆τ =
0.55s.

| 4 TIME-DELAY |     | INTERFEROMETRY |     |     |     |     |     |     |     |     | 43  |
| ------------ | --- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
• A detailed controller designed to maximize gain in the science band, minimize fre-
quencypulling, butstillmaintainaphasemarginofgreaterthan30degreestoensure
stability. The control bandwidth (∼ 15 kHz) is 10 times higher than previously ex-
|     | pected     | possible. |                |     |     |     |     |     |     |     |     |
| --- | ---------- | --------- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4   | Time-Delay |           | Interferometry |     |     |     |     |     |     |     |     |
The final step in frequency noise suppression is a post-processing technique called Time-
Delay Interferometry (TDI) [33]. TDI removes laser frequency noise by forming linear
combinations of the phase measurements with different delays. TDI can be understood as
a way to synthesize an interferometer that has equal arm lengths. To achieve this, phase
measurements recorded locally at each spacecraft are time shifted using high performance
interpolation algorithms and recombined in post-processing. These same linear combina-
tions maintain the gravitational wave signal, as it is primarily contained in the difference
| of the | arms | while the | laser noise | is common |     | to the | arms. |     |     |     |     |
| ------ | ---- | --------- | ----------- | --------- | --- | ------ | ----- | --- | --- | --- | --- |
The performance of TDI can be characterized by a suppression factor. Here we define
the suppression factor to be the ratio of laser frequency noise to the frequency noise re-
maining in the TDI output. This suppression factor is frequency dependent and may be
limited by several effects. Six categories of these effects are listed Table 9 along with an
| estimate | of the     | suppression   | factor      | limit     | due          | to each    | effect.         |             |         |        |     |
| -------- | ---------- | ------------- | ----------- | --------- | ------------ | ---------- | --------------- | ----------- | ------- | ------ | --- |
|          |            | Table         | 9: Effects  | that      | limit        | the        | TDI suppression |             | factor. |        |     |
|          |            | Effect        |             |           | Assumption   |            |                 | Suppression |         | Factor |     |
|          |            | Ranging       | Error       |           | 1 m ranging  |            | error           | 2.4×107×(1  |         | Hz/f)  |     |
|          | Algorithm  |               | limitations | Velocity  | correcting   |            | TDI             | 2×109×(1    |         | Hz/f)  |     |
|          |            | Interpolation |             |           | 21 s kernel, |            | 3 S/s           | 3.2×109×(1  |         | Hz/f)2 |     |
|          | Analog     | Chain         | Errors      |           | Measurement  |            |                 | 5×107×(1    |         | Hz/f)  |     |
|          | Phasemeter |               | DSP         | TRL       | 4            | Phasemeter |                 |             | 1010×(1 | Hz/f)2 |     |
|          | Scattered  |               | Light       | Amplitude |              | 2×10−5     |                 | 1.5×1013×(1 |         | Hz/f)  |     |
| 4.1      | Ranging    | Limited       | Performance |           |              |            |                 |             |         |        |     |
In this section we determine the suppression factor of TDI due to ranging error. This
calculation is based on the LISA technical note TDI Capabilities and Frequency Noise
[34].
Requirements
Time-DelayInterferometryprocessingaffectsnotjustlaserfrequencynoisebutallother
noise sources and the gravitational wave signal. We need to consider this response when

| 4 TIME-DELAY |     |     | INTERFEROMETRY |     |     |     |     |     |     |     | 44  |
| ------------ | --- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- |
determining the requirements on laser frequency noise suppression. For example, it is not
sufficient to require that the laser frequency noise after TDI is less than the shot noise level
before TDI. Instead we require that the laser frequency noise after TDI is less than the
shot noise after TDI. The frequency noise allocation post TDI, φ , can be written as
ln|TDI
| a fraction |     | of shot | noise. |        |      |      |       |     |     |     |      |
| ---------- | --- | ------- | ------ | ------ | ---- | ---- | ----- | --- | --- | --- | ---- |
|            |     |         |        | φ      | = KT | (f)φ |       |     |     |     | (39) |
|            |     |         |        | ln|TDI |      | sn   | sn|PR |     |     |     |      |
where K is the fraction of the shot noise level allocated to residual laser frequency noise,
T (f) is the frequency response of shot noise into the TDI output, and φ is the sum
| sn      |       |     |              |       |                       |     |       |     | sn|PR |     |     |
| ------- | ----- | --- | ------------ | ----- | --------------------- | --- | ----- | --- | ----- | --- | --- |
| of shot | noise | and | acceleration | noise | at the photoreceiver, |     | given | by  |       |     |     |
(cid:112)1+(3mHz/f)4
|       |      |     |                   | 7.5pm× |     |     |         | √   |     |     |      |
| ----- | ---- | --- | ----------------- | ------ | --- | --- | ------- | --- | --- | --- | ---- |
|       |      |     | φ                 | =      |     |     | cycles/ | Hz. |     |     | (40) |
|       |      |     | sn|PR             |        | λ   |     |         |     |     |     |      |
| where | λ is | the | laser wavelength. |        |     |     |         |     |     |     |      |
The allowable laser frequency noise pre-TDI is found by dividing the allocation (equa-
tion 39) by the frequency response for frequency noise, T (f), and converting from phase
ln
to frequency.
|     |     |     |     |        | (cid:18)2πf(cid:19) | T (f) |       |     |     |     |      |
| --- | --- | --- | --- | ------ | ------------------- | ----- | ----- | --- | --- | --- | ---- |
|     |     |     |     | ν      | =                   | sn    | Kx    | .   |     |     | (41) |
|     |     |     |     | ln|LAS | λ                   | T (f) | sn|PR |     |     |     |      |
ln
To get a feel for the numbers we can substitute numbers in for the laser noise allocation
x = Kx and ranging errors. If we assume the TDI combination X [33] (the
| ln|PR |     | sn|PR |     |     |     |     |     |     |     | √   |     |
| ----- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Michelson interferometer combination), with ∆L = 1 m error and x = 1 pm/ Hz we
ln|PR
find
|     |     |     |        |       | √       | (cid:18)1m(cid:19) | (cid:18) | x      | (cid:19) |     |      |
| --- | --- | --- | ------ | ----- | ------- | ------------------ | -------- | ------ | -------- | --- | ---- |
|     |     |     | ν      | = 141 | Hz/ Hz× |                    | ×        | ln|P √ | R .      |     | (42) |
|     |     |     | ln|LAS |       |         | ∆L                 |          |        |          |     |      |
|     |     |     |        |       |         |                    | 1        | pm/    | Hz       |     |      |
where we have assumed the worst case of frequency noise coupling, which occurs with
a differential ranging error coupled with matched arm lengths. Equation 42 shows the
suppression of frequency noise by TDI depends linearly on the accuracy of the arm length
knowledge or ranging error. A TDI suppression factor of 2.4×107 ×(1 Hz/f) is possible
| with | 1 m | ranging | error. |     |     |     |     |     |     |     |     |
| ---- | --- | ------- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
The frequency responses in equation 41 are specific to the TDI combination chosen.
The frequency response of shot noise into the (first generation) TDI combination X is
|     |     |     |       | √ (cid:113)                          |     |     |     |     |     |     |      |
| --- | --- | --- | ----- | ------------------------------------ | --- | --- | --- | --- | --- | --- | ---- |
|     |     |     | T (f) | = 2 (1−e−iω2L2E/c)2+(1−e−iω2L1E/c)2, |     |     |     |     |     |     | (43) |
sn
whereL ,L aretheestimatedlengthsofthetwoarmsgivenbyL = L +∆L ,L =
|     | 1E  | 2E  |     |     |     |     |     |     | 1E 1 | 1   | 2E  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- |
L +∆L , with L and L denoting the actual arm lengths of the two LISA arms and ∆L
| 2   | 2   |     | 1   | 2   |     |     |     |     |     |     | 1   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

| 4 TIME-DELAY |     |     | INTERFEROMETRY |     |     |     |     |     |     | 45  |
| ------------ | --- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- |
and ∆L denoting the ranging error for the respective arms. The frequency response of
2
| laser frequency |     | noise | for  | the TDI combination |     | X        | is   |                  |          |      |
| --------------- | --- | ----- | ---- | ------------------- | --- | -------- | ---- | ---------------- | -------- | ---- |
|                 |     |       |      | (cid:16)            |     | (cid:17) |      | (cid:16)         | (cid:17) |      |
|                 | T   | (f)   | = T  | (f) 1−e−iω2L2E/c    |     |          | −T   | (f) 1−e−iω2L1E/c | ,        | (44) |
|                 | ln  |       | arm1 |                     |     |          | arm2 |                  |          |      |
where T (f) and T (f) are the frequency responses of the arms 1 and 2, given by
|     | arm1 |      | arm2 |                |     |      |                    |     |     |      |
| --- | ---- | ---- | ---- | -------------- | --- | ---- | ------------------ | --- | --- | ---- |
|     |      | T    | (f)  | = 1−e−iω2L1/c, |     | T    | (f) = 1−e−iω2L2/c. |     |     | (45) |
|     |      | arm1 |      |                |     | arm2 |                    |     |     |      |
The frequency responses of laser frequency noise and shot noise are different because they
φ
|LAS
|     |     |     |     | Arm 1 FR |     |     | Arm 2 FR |     |     |     |
| --- | --- | --- | --- | -------- | --- | --- | -------- | --- | --- | --- |
|     |     |     | φ   |          |     |     |          | φ   |     |     |
|     |     |     | sn1 | Σ+       |     |     | Σ+       |     |     |     |
sn2
OPTICAL
ELECTRONIC
|     |     |     |     | Arm 2 FR |     |     | Arm 1 FR |     |     |     |
| --- | --- | --- | --- | -------- | --- | --- | -------- | --- | --- | --- |
|     |     |     |     | Estimate |     |     | Estimate |     |     |     |
Σ
|     |     |     |     |     | +   |     | −   |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
φ
|TDI
Figure 28: Block diagram representation of TDI showing where the laser frequency noise,
φ and the shot noise, φ enter the signal chain. The frequency responses (FR) of the
| ln       |         |     |          | sn         |       |         |     |     |     |     |
| -------- | ------- | --- | -------- | ---------- | ----- | ------- | --- | --- | --- | --- |
| arms are | applied | in  | the post | processing | stage | of TDI. |     |     |     |     |
enter the signal chain at different locations: laser frequency noise enters at the laser, shot
noise enters at the photoreceiver. This is shown schematically in Figure 28 for the case of
the TDI combination X. For simplicity it is assumed that the lasers are perfectly phase-
locked to one master laser in the central spacecraft. The electronic processing part of the
diagram depicts the formation of the TDI combinations performed on ground.

| 4 TIME-DELAY | INTERFEROMETRY |     |     | 46  |
| ------------ | -------------- | --- | --- | --- |
The frequency noise requirement calculated for 2nd generation TDI is the same as 1st
| generation TDI | [34].  |     |     |     |
| -------------- | ------ | --- | --- | --- |
| 4.2 Ranging    | System |     |     |     |
TDI relies on interspacecraft distance tracking with resolution on the order of meters as
described in section 4.1. The LISA interferometry system will provide onboard ranging
measurements and data communication by applying low-index phase modulation onto all
laserlinks. Toachievetherequireddistanceaccuracy,apseudo-randomnoise(PRN)canbe
phase modulated onto the carrier of the remote laser and the travel time can be measured
via the correlation of the local and incoming PRN code. To obtain the phase signal of the
laser beam the beatnote coming from the photodetectors on the optical benches will be
processed in a phase measurement system (PMS). Once the interference has been acquired
(this constitutes the core processing of the phasemeter), the PRN can be tracked in back-
end processing using the fast residual phase error as input signal. This section is based on
| Technical Note   | LI-AEI-TN-3013b | [35].      |     |     |
| ---------------- | --------------- | ---------- | --- | --- |
| 4.2.1 Interfaces | with the        | Phasemeter |     |     |
The core processing of the PMS is based on a digital phase-locked loop (DPLL) [36] archi-
tecture. It is required to track the Doppler-shifted carrier (frequency range between 2 to
√
18MHz) and to measure the phase of the beat note at microcycle/ Hz phase precision.
Therangingcapabilitiesarebasedonadelay-lockedloop(DLL)[37]architecture. Itisused
to track the received PRN code and therefore the estimation of the time delay between
PRN sequences can be obtained as well as the data transmitted. To focus on ranging
capabilities it is assumed that the core processing of the phasemeter keeps the incoming
toneinclosedloopoperationandaPRNsequenceencodedwithdatahavebeenmodulated
| onto the incoming | carrier. |     |     |     |
| ----------------- | -------- | --- | --- | --- |
The ranging system has to be integrated in or very close to the PMS. The input signal
of the DLL is a high rate phase component obtained as residual of the in-phase (I) sampled
signal. Figure 29 shows the schematic of one PMS channel and the proposed integration
with the DLL. There may be a low-pass filter before to the DLL to minimize out-of-band
interferencesandadditionalnoise. Theoutputoftherangingsystemisaregulartime-series
| of time-stamps    | to be processed | by the onboard | computer. |     |
| ----------------- | --------------- | -------------- | --------- | --- |
| 4.2.2 Correlation | Properties      | of PRN         | Codes     |     |
There are a total of six laser beams exchanged between the LISA satellites, and therefore a
PRN code has been designed for each one of them. In the LISA topology, each laser is used
simultaneouslyindifferentinterferometricmeasurements, sothatitalsohasdifferentcodes
modulatedontoitsphase. Themaindesigndriverforthecodeisthataftertheinterference

4 TIME-DELAY INTERFEROMETRY 47
Figure 29: General PMS block diagram. FPGA: Field programmable gate array, ADC:
Analog to digital converter, DAC: Digital to analog converter, LPF: Low pass filter, NCO:
Numerically controlled oscillator, DLL: Delay-locked loop, DIOB: Digital input/output
board, EPP: Enhanced parallel port.
betweenanygiventwolasers, abeatnotecantrackasinglePRNcodeseparatelyfromeach
otherandwithoutincurringsignificantmutualinterferencebetweenpseudo-sequences. The
set of six PRN sequences implemented shown in Figure 30 have even length (for efficient
use in a FPGA processor) and have been obtained by means of numerical optimization.
Note that only when the cross-correlation is made by the same PRN code with the same
delay, does a peak appear in the correlation (see Figure 31). This way, the correlation peak
serves as a timestamp if the start of the PRN is synchronized with the clock of the remote
spacecraft.
Selected cross-correlations of 6 possible pseudo-random bit codes Autocorrelation of 6 pseudo-random bit codes
1 1
0.8 0.8
0.6 0.6
0.4 0.4
0.2 0.2
0 0
-0.2 -0.2
-400 -200 0 200 400 -400 -200 0 200 400
Figure 30: Cross-correlation (left) and auto-correlation (right) between a possible set of
different PRN combinations

| 4 TIME-DELAY | INTERFEROMETRY |     |     |     |     | 48  |
| ------------ | -------------- | --- | --- | --- | --- | --- |
Figure 31: Autocorrelation at different code shifts and zoom at zero shift.
| 4.2.3 Tracking | Architecture |     |     |     |     |     |
| -------------- | ------------ | --- | --- | --- | --- | --- |
Figure 32 shows a general block diagram of the current implementation of the code track-
ing part of the DLL. Sampling frequency at 50MHz. PRN length 1024 chips at F =
c
| F = 50MHz |              |      |            | F =          | 50MHz         |     |
| --------- | ------------ | ---- | ---------- | ------------ | ------------- | --- |
| s         | = 1.5625MHz. | Data | encoded at | F = s        | = 97.65625kHz |     |
| 32samples |              |      |            | d 512samples |               |     |
• The loop filter is updated every integration time and implemented as a first order
| IIR. | filter: |                         |     |     |                |      |
| ---- | ------- | ----------------------- | --- | --- | -------------- | ---- |
|      |         | τ[n] = τ[n−1]+gain(E−L) |     | → y | = y +α(cid:15) | (46) |
|      |         |                         |     | i   | i−1 i          |      |
• Thecodegeneratorisimplementedusingoneindexgeneratorandthreelookuptable:
| On-time | p(t−τ), | early p(t−τ | +Tc/2) and | late p(t−τ | −Tc/2). |     |
| ------- | ------- | ----------- | ---------- | ---------- | ------- | --- |

| 4 TIME-DELAY | INTERFEROMETRY |     |     |     | 49  |
| ------------ | -------------- | --- | --- | --- | --- |
Data bit rate
Fs
t = Integration
|     |            | t = T data |            | time |     |
| --- | ---------- | ---------- | ---------- | ---- | --- |
|     | Integrate  |            | Integrate  |      |     |
|     | and        |            | abs        | and  |     |
|     | dump       |            |            | dump |     |
Remote PRN
 ylraE
sampled at Fs E
|     |     | Fs  |     | Data bit rate |     |
| --- | --- | --- | --- | ------------- | --- |
Loop
| p(t - τ) |     |     |     | filter |     |
| -------- | --- | --- | --- | ------ | --- |
L
|     |     | Integrate  |     | Integrate  |     |
| --- | --- | ---------- | --- | ---------- | --- |
|     |     | and        | abs | and        |     |
t = T
|     |     | dump | data | dump t= Integration |     |
| --- | --- | ---- | ---- | ------------------- | --- |
etaL
 )2/cT + τ - t(p time
 )2/cT - τ - t(p
Local PRN code
generated at Fs
Fs
Figure 32: General schematic of the tracking architecture of DLL implementation.

| 4     | TIME-DELAY |         | INTERFEROMETRY |     |             |     |     |     |     |     | 50  |
| ----- | ---------- | ------- | -------------- | --- | ----------- | --- | --- | --- | --- | --- | --- |
| 4.2.4 |            | Ranging | Accuracy       |     | Limitations |     |     |     |     |     |     |
The DLL scheme shown in Figure 32 was implemented in a C-simulation in order to study
the influence of different noise sources and design parameters in the final ranging accuracy
| for | LISA.   | The   | effects | under   | investigation | are:      |     |     |     |     |     |
| --- | ------- | ----- | ------- | ------- | ------------- | --------- | --- | --- | --- | --- | --- |
|     | 1. Shot | noise | and     | limited | phasemeter    | accuracy. |     |     |     |     |     |
2. Presence of data encoded with a period shorter than a PRN sequence. (e.g. PRN
|     |        | 1024 |         |     |     | 1   |        |     |     |     |     |
| --- | ------ | ---- | ------- | --- | --- | --- | ------ | --- | --- | --- | --- |
|     | length |      | = 655µs | and | T   | = = | 10µs). |     |     |     |     |
d
|     |                |     | F           |     |           | F   |     |     |     |     |     |
| --- | -------------- | --- | ----------- | --- | --------- | --- | --- | --- | --- | --- | --- |
|     |                |     | c           |     |           | d   |     |     |     |     |     |
|     | 3. Presence    |     | of a second | PRN | sequence. |     |     |     |     |     |     |
|     | 4. Integration |     | time.       |     |           |     |     |     |     |     |     |
Current results show that the system is capable of acquisition and tracking of the delay
in the presence of these noise sources. The obtained instantaneous ranging precision in the
order of 3 to 4 meters appears to be limited by the combination of data encoding and the
presence of a second PRN sequence. The current implementation delivers measurements
at kilohertz data rate, whereas TDI requires them at hertz rate, so that the resulting low
| rate | ranging | accuracy |     | can be | improved | by  | post-processing. |     |     |     |     |
| ---- | ------- | -------- | --- | ------ | -------- | --- | ---------------- | --- | --- | --- | --- |
Table10summarizestherangingaccuracyobtainedaftersimulationwithcombinations
ofthethreedifferentnoisesourcesandtwopossibleintegrationtimes. Notethattheranging
accuracy is limited by the presence of data when the integration time is a full PRN length.
Ifashorterintegrationtimeisimplemented,therangingaccuracyislimitedbythepresence
| of  | a second | PRN   | encoded     | in   | the input | signal. |      |             |             |      |     |
| --- | -------- | ----- | ----------- | ---- | --------- | ------- | ---- | ----------- | ----------- | ---- | --- |
|     | Shot     | noise | Integration |      | 2nd       | PRN     | Data | rms ranging | Measurement |      |     |
|     |          |       |             | time |           |         |      | noise       |             | rate |     |
µrad
|     | 4   | √   |     | 1024 |     | No  | No  | 0.11 meters |     | 1.5kHz |     |
| --- | --- | --- | --- | ---- | --- | --- | --- | ----------- | --- | ------ | --- |
Hz
|     | 4   | µrad |     | 1024 |     | Yes | No  | 0.39 meters |     | 1.5kHz |     |
| --- | --- | ---- | --- | ---- | --- | --- | --- | ----------- | --- | ------ | --- |
√
Hz
|     | 4   | µrad |     | 1024 |     | No  | Yes | 2.68 meters |     | 1.5kHz |     |
| --- | --- | ---- | --- | ---- | --- | --- | --- | ----------- | --- | ------ | --- |
√
Hz
|     | 56  | µrad √ |     | 1024 |     | Yes | Yes | 3.48 meters |     | 1.5kHz |     |
| --- | --- | ------ | --- | ---- | --- | --- | --- | ----------- | --- | ------ | --- |
Hz
|     | 56  | µrad |     | 256 |     | No  | No  | 2.95 meters |     | 6kHz |     |
| --- | --- | ---- | --- | --- | --- | --- | --- | ----------- | --- | ---- | --- |
√
Hz
|     | 56  | µrad |     | 256 |     | Yes | No  | 5.21 meters |     | 6kHz |     |
| --- | --- | ---- | --- | --- | --- | --- | --- | ----------- | --- | ---- | --- |
√
Hz
|     | 56  | µrad √ |     | 256 |     | No  | Yes | 4,27 meters |     | 6kHz |     |
| --- | --- | ------ | --- | --- | --- | --- | --- | ----------- | --- | ---- | --- |
Hz
|     | 56  | µrad |     | 256 |     | Yes | Yes | 5.78 meters |     | 6kHz |     |
| --- | --- | ---- | --- | --- | --- | --- | --- | ----------- | --- | ---- | --- |
√
Hz
Table 10: Preliminary result of the ranging accuracy for combinations of three noise
| sources |     | and two | possible | integration |     | times |     |     |     |     |     |
| ------- | --- | ------- | -------- | ----------- | --- | ----- | --- | --- | --- | --- | --- |

| 4 TIME-DELAY | INTERFEROMETRY |     |     |     | 51  |
| ------------ | -------------- | --- | --- | --- | --- |
Future investigations will include simulations with time-varying delays, accuracy esti-
mations after longer integration times and the hardware implementation of the presented
| design with       | optical | signals.    |         |     |     |
| ----------------- | ------- | ----------- | ------- | --- | --- |
| 4.2.5 Performance |         | Improvement | Options |     |     |
Thesepreliminaryresultssupportrangingaccuracyofseveralmeters. Oneofthedominant
errorsiscontaminationbythelocal(outgoing)PRNcodeimposedonthelocaloscillator. It
is predicted that this error can be removed by also tracking the outgoing code, determining
the cross correlation between the two codes, then subtracting this deterministic error from
the measurement. The tracking of the second code would require an extra DLL channel
in the phasemeter. Solving for the cross correlation and correcting the error could be
performed on the ground. We estimate that a tenfold reduction in this error should be
achievable.
Another limitation to ranging accuracy is the presence of data on the PRN code. A
similarcorrectionschememaybeemployedtoreducethiserror. However,itmaybesimpler
to turn off data encoding for a few seconds whenever an accurate ranging measurement is
| needed. Simulations |     | are ongoing | to investigate | these issues. |     |
| ------------------- | --- | ----------- | -------------- | ------------- | --- |
| 4.3 Algorithm       |     | Errors      |                |               |     |
The displacement sensitivity of an interferometer with a single arm of length L is limited
| by fluctuations | in the | laser frequency | ν by, |     |     |
| --------------- | ------ | --------------- | ----- | --- | --- |
L˜
ν˜
(47)
≈
|     |     |     | L   | ν   |     |
| --- | --- | --- | --- | --- | --- |
For an interferometer where two arms are differenced (e.g. a Michelson), we can replace
the arm length L by the arm length mismatch ∆L in Eq. 47. As mentioned above, TDI
effectively synthesizes a two arm interferometer configuration with (near) equal length
arms. First generation TDI provides an equal arm length in the presence of a static arm
length mismatch. However, the original TDI combinations will not in general produce
equal arm interferometers in the presence of spacecraft relative motion [38]. Although each
beam of the virtual two arm interferometer samples all interferometer lengths, they do
so at slightly different times. Second Generation TDI corrects for velocity mismatch by
sampling all the lengths a second time but with reversed order. This resampling averages
out errors due to constant spacecraft velocity, leaving arm length errors due to acceleration
mismatches and higher order derivatives. For the predicted LISA orbits it is expected that
the Second Generation TDI combinations have equal length arms to better than 1 cm.
Extrapolating from the results of Section 4.1 we estimate a maximum suppression factor
| of order 2×109×(1 |     | Hz/f). |     |     |     |
| ----------------- | --- | ------ | --- | --- | --- |

| 4 TIME-DELAY |             | INTERFEROMETRY |             |     |         |     |     | 52  |
| ------------ | ----------- | -------------- | ----------- | --- | ------- | --- | --- | --- |
| 4.3.1        | Performance |                | Improvement |     | Options |     |     |     |
The arm length mismatch due to the acceleration of the spacecraft is negligibly small
compared to the expected ranging errors. However if needed, acceleration correcting TDI
combinationscouldbeused. Themainpenaltyassociatedwiththesealgorithmsisdoubling
of the start-up time needed to ensure that data is available with the appropriate delays
| (up to 16×L/C |     | for the | Michelson | combinations). |     |     |     |     |
| ------------- | --- | ------- | --------- | -------------- | --- | --- | --- | --- |
4.4 Interpolation
TDI requires the phase measurements to be combined with precise delays. The phase mea-
surements are made at a constant rate triggered by a local clock. Although the phasemeter
samplesthephotodetectoroutputat50MS/sthephasemeasurementsaredecimatedtothe
relatively low sample rate of approximately 3 S/s. Phase measurements are made available
at intermediate times by interpolating between samples [39]. Error in this interpolation
| process | will limit | the | suppression | of  | laser frequency | noise by | TDI. |     |
| ------- | ---------- | --- | ----------- | --- | --------------- | -------- | ---- | --- |
Interpolation is achieved through fractional delay filtering. The interpolation error
is determined by the frequency response of the digital filter. The filter kernel (impulse
response) is typically a sinc function multiplied by a window to minimise spectral leakage.
A longer filter kernel allows for more accurate interpolation at the expense of data loss
at the beginning and end of a science run. Figure 33 shows the interpolation error as a
| function | of kernel | length | for | a range | of filter | kernel windows. |     |     |
| -------- | --------- | ------ | --- | ------- | --------- | --------------- | --- | --- |
Increasing the phase measurement sampling rate significantly improves performance
for a given kernel duration as it allows for a larger filter transition band. The trade-
off between sample rate and kernel length are explored in [40]; there it was shown that
sampling a band-limited signal at 3 Hz is acceptable for LISA assuming a laser frequency
√
noise of 30 Hz/ Hz . Below we consider further improving the interpolation performance
to accommodate free-running laser noise. We assume the free-running laser has a noise
| spectrum          | of  |     |         |       |              |              |     |      |
| ----------------- | --- | --- | ------- | ----- | ------------ | ------------ | --- | ---- |
|                   |     |     |         |       |              | √ 1 Hz       |     |      |
|                   |     |     |         | ν˜ =  | 10 kHz/      | Hz×          |     | (48) |
|                   |     |     |         | L     |              | f            |     |      |
| which corresponds |     | to  | a phase | noise | in the phase | measurements | of: |      |
|                   |     |     | φ˜      | ν˜    |              |              |     |      |
|                   |     |     |         | = 2   | L            |              |     | (49) |
|                   |     |     | L       | 2πf2  |              |              |     |      |
(cid:18)1 Hz(cid:19)2
√
|     |     |     |     | 3.2×103 | cycles/ | Hz× |     | (50) |
| --- | --- | --- | --- | ------- | ------- | --- | --- | ---- |
(cid:39)
f
The factor of 2 in the numerator accounts for the transfer function of an arm peaking
φ˜
at 2 with phase-locked lasers. If the requirement for the measurement of phase is =
|     | √   |     |     |     |     |     |     | M   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
10−6 cycles/ Hz. The maximum allowable fractional error added by interpolation is then:

4 TIME-DELAY INTERFEROMETRY 53
100
10−1
10−2
10−3
10−4
10−5
10−6
10−7
10−8
10−9
10−10
10−11
10−12
100 101 102
Kernel length N
!
rorre
noitalopretnI
3 Hz Sampling Rate
1/N
Truncated−sinc
Blackman
Lagrange
Blackman3
Blackman4
Figure 33: A comparison of interpolation error versus kernel length for for windowed-sinc
functions with different window.
φ˜ (cid:18) f (cid:19)2
(cid:15) = M = 3.1×10−10× (51)
φ˜ 1 Hz
L
ThisfractionalerrorisplottedinFigure34. AlsoshowninFigure34,istheinterpolation
error from a filter with a 63 point kernel using a Blackman4 window and 3 S/s sampling
rate. Note that the laser frequency noise increases at low frequencies but the interpolation
error improves faster, so the 1 Hz error drives the filter design. With this kernel, 21 s of
data is unusuable at the start and end of each segment. This dead time could be decreased
by increasing the sampling rate if desired.
The frequency noise suppression factor can be found by inverting equation 51 to give
3.2×109×(1 Hz/f)2.
4.4.1 Testbed Results Using Interpolation
The LISA Interferometry Testbed at JPL [29] uses interpolation to time shift the phase
measurements before combining them into the TDI combination α. The testbed has two
optical benches on which phase measurements are made with respect to two independent
clocks. The relative drift of the clocks introduces an offset to the sample times of the
phase measurement made at each bench. This offset is corrected by using interpolation to
resample the measurements at the required times. Figure 35 shows that the dominant time

| 4 TIME-DELAY |     | INTERFEROMETRY |     |     |     |     |     | 54  |
| ------------ | --- | -------------- | --- | --- | --- | --- | --- | --- |
Error in 1 Hz passband, sampled @ 3 Hz
|     |     | 100 |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
Error requirement free−running laser
10−1
Blackman(63)4
10−2
10−3
10−4
10−5
|     |     | | s 10−6 |     |     |     |     |     |     |
| --- | --- | -------- | --- | --- | --- | --- | --- | --- |
f/D f ! 2 ie − H|
10−7
10−8
Max error in 1 Hz passband = 2.27781e−10
10−9
10−10
10−11
10−12
10−13
10−14
10−15
10−16

|     |     | 10−3 |     | 10−2 |     | 10−1 | 100 |     |
| --- | --- | ---- | --- | ---- | --- | ---- | --- | --- |
Frequency (Hz)
√
Figure 34: Error in the interpolation filter assuming a free-running laser of 10 kHz/f Hz.
| A 63 point | (21 | seconds) Blackman4 |     | filter achieves  | the | required | error.            |     |
| ---------- | --- | ------------------ | --- | ---------------- | --- | -------- | ----------------- | --- |
|            |     | 4                  |     |                  |     |          | 3                 |     |
|            |     | 3                  |     |                  |     |          | 2                 |     |
|            |     | ]sm[ tesffo emit   |     | (i) clock offset |     |          | ]sµ [ tesffo emiT |     |
|            |     | 2                  |     |                  |     |          | 1                 |     |
(ii) detrended clock offset
|     |     | 1   |     |      |      |      | 0    |     |
| --- | --- | --- | --- | ---- | ---- | ---- | ---- | --- |
|     |     | 0   |     |      |      |      | -1   |     |
|     |     | 0   | 500 | 1000 | 1500 | 2000 | 2500 |     |
time [s]
Figure 35: (i) Relative clock offset and (ii) detrended relative clock offset in the JPL LISA
Interferometry Testbed. These offsets were inferred from optical transfer of clock noise,
i.e. the sideband-sideband beat notes of 8 GHz phase modulation sidebands. In LISA the
| clock offsets | will | be extracted | from | the ranging | measurements. |     |     |     |
| ------------- | ---- | ------------ | ---- | ----------- | ------------- | --- | --- | --- |

4 TIME-DELAY INTERFEROMETRY 55
offset is a linear drift arising from a frequency offset of the two clocks. However, the µs
level random clock fluctuations must also be accounted for when determining the correct
time shift.
104
Raw phasemeter output 102
100
Alpha, before interpolation
10-2
10-4 Interferometer noise
Alpha,
after interpolation
10-6
10−2 10−1 100
Frequency [Hz]
]zH√/selcyc[
esahP
5x107
suppression
Figure 36: Experimental results from JPL LISA testbed with two independent spacecraft
and clocks. The measured difference between the two clocks is shown in Figure 35.
Figure 36 shows the root power spectral density (RPSD) of the phase at different
points in the signal processing chain. The upper trace shows the laser phase noise in a
single phase measurement (raw phasemeter output). Each phase measurement contains
√
approximately 30 Hz Hz of relative frequency noise imposed by intentionally adding noise
to phase-locking. If the phase measurements are combined to form the α combination
without interpolation then the laser frequency noise is only partially cancelled (labeled
“alpha, before interpolation”). In this plot, the phase error due clock noise has been
subtracted by incorporating the sideband-sideband beat note phase measurements into α.
What remains is the residual laser noise due to incorrect delays. The bottom trace shows
the noise in α after time shifting the phase measurements using interpolation. The laser
frequency noise is suppressed by more than seven orders of magnitude at 3 mHz. In this
test, the observable suppression was limited by the noise floor of the testbed.

4 TIME-DELAY INTERFEROMETRY 56
4.4.2 Performance Improvement Options
The interpolation error vanishes quickly as the kernel length is increased. The cost is a
longerdeadtimeatthebeginningandendofeachsciencerun. Increasingthe(over)sampling
rate also helps to substantially reduce the interpolation error at the cost of increased data
rate to ground. It may be possible to have the best of both worlds by using a short kernel
and fast sample rate at the beginning (and end) of a run to reduce dead time, then revert-
ing to a longer kernel and lower sampling rate to save on data costs for the majority of
science operations. There is little motivation to move to this more complicated approach
given the currently estimated performance of interpolation.
It is possible that the current formulation of interpolation requirements is overly con-
servative. In particular, it may be permissible to place a requirement only on the difference
ofthetransferfunctionsofanytwophasemeters, ratherthanonthetransferfunctionitself.
The transfer functions will be very closely matched as the filters are implemented digitally
using identical kernels. The transfer functions will vary because of the different sampling
rates used by the clock’s on each spacecraft. As the more conservative requirement can be
met fairly easily with little or no impact on flight hardware design we have deferred further
examination of this issues.
4.5 Analog Chain
We consider the sensitivity to laser frequency noise of the analog electronics chain, which
consists of a photoreceiver, adjustable-gain preamplifier, and anti-alias filter (Figure 37).
To evaluate the performance of the subsystem, phase error at the output of the chain is
ADC
Adjustable gain Antialias
Fixed gain preamplifier filter
photoreceiver
Figure 37: The analog electronics chain is within the green box. The input of the chain
is a light beam from the beamsplitter, and the output is the electrical voltage delivered to
the ADC.
estimated in the presence of frequency noise in the input optical beam. Two mechanisms
relatinganalogelectronicstofrequencynoiseareconsidered: dispersion,aphasedelayeffect
thatcandegradetheaccuracyofrangingneededforTDI,andnonlinearity(“fidelityerror”).
We do not consider here noise terms that are associated with analog electronics that are
unrelatedtofrequencynoise,includingelectronicnoiseattheheterodynefrequency(NEP);

| 4 TIME-DELAY | INTERFEROMETRY |     |     |     |     | 57  |
| ------------ | -------------- | --- | --- | --- | --- | --- |
phase noise at the gravitational wave signal frequency (including temperature sensitivity
of cables); suppression of timing ADC phase noise by pilot tone; suppression of intensity
noise at heterodyne frequency by subtraction of anti-phased beamsplitter outputs.
| 4.5.1 Key   | Parameters | and Assumptions |     |     |     |     |
| ----------- | ---------- | --------------- | --- | --- | --- | --- |
| Phase slope | and range  | error           |     |     |     |     |
Theanalogelectronicschainintroducesagroupdelayτ betweentheinputlightandthe
e
output signal. The group delay is related to the phase by τ = dΦ/df. Here Φ(f) (in units
e
ofcycles)hastheconventionalmeaningofphasedifferencebetweeninputandoutputofthe
electronicschain; weareconcernedwiththeresponseneartheheterodynesignalfrequency,
2MHz < f < 18MHz. Group delay is a mechanism for converting frequency noise ν˜(f )
|     | h   |     |     |     |     | s   |
| --- | --- | --- | --- | --- | --- | --- |
Φ˜(f
in the signal band, f < 1Hz, to phase noise in the signal band: ) = τ ν˜(f ). This
|     | s   |     |     |     | s e | s   |
| --- | --- | --- | --- | --- | --- | --- |
conversion appears to place a tight constraint on the allowed group delay for a given level
|     |     |     | Φ˜(f |     |     | √   |
| --- | --- | --- | ---- | --- | --- | --- |
of frequency noise. For example, requiring ) from group delay to be < 1µcycle/ Hz
√ s
in the presence of ν˜(f ) = 300Hz/ Hz would seem to require τ < 3ns throughout the
|     | s   |     |     | e   |     |     |
| --- | --- | --- | --- | --- | --- | --- |
range of heterodyne frequencies, a demanding requirement. With some attention paid to
the method used for measuring range, however, the allowed group delay can be relaxed by
| orders of | magnitude. |     |     |     |     |     |
| --------- | ---------- | --- | --- | --- | --- | --- |
The requirement on group delay is relaxed by arranging the range measurement to be
common with the science phase measurement. The baseline plan calls for using the same
electronicschainforrangingandsciencephase—thatis, theelectronicsshowninFigure37.
If the science measurement is made at the same frequency as the range measurement, both
see the same τ , and group delay introduces no error. The key determiner of error due to
e
analog electronics delay is the sideband deviation of the ranging measurement.
Dispersion Dispersion is defined as the slope of the group delay vs. frequency curve:
D(f) = dτ /df = d2Φ/df2. Limited bandwidth in the analog chain results in dispersion,
e
which in turn results in τ(f ) (cid:54)= τ(f ), where f and f are the frequencies used for ranging
|     |     | 1   | 2 1 | 2   |     |     |
| --- | --- | --- | --- | --- | --- | --- |
an science measurements. For example, model the chain as n cascaded simple low-pass
filters, each of characteristic frequency f . The transfer function of this model is
0
|     |     |      | (cid:18) 1 | (cid:19)n |     |      |
| --- | --- | ---- | ---------- | --------- | --- | ---- |
|     |     | T(f) | =          | .         |     | (52) |
1+if/f
0
| This transfer | function | has group delay | of  |     |     |     |
| ------------- | -------- | --------------- | --- | --- | --- | --- |
|               |          |                 | n f |     |     |     |
0
|     |     |     | τ(f) = | .   |     | (53) |
| --- | --- | --- | ------ | --- | --- | ---- |
2πf2+f2
0
As a conservative extreme, assume low-bandwidth electronics: n = 3, f = 20MHz,
(worst-case heterodyne frequency), f = 40MHz (minimum acceptable bandwidth). The
0
value of ∆f, the frequency difference between range and science phase measurements,
depends on the ranging method. In the baseline method, pseudo-random sidebands are

| 4 TIME-DELAY |     | INTERFEROMETRY |     |     |     |     | 58  |
| ------------ | --- | -------------- | --- | --- | --- | --- | --- |
imposed, with sideband deviation ∆f = 1MHz. If the sidebands are unbalanced or if only
one of the upper and lower sidebands is used for ranging, the resulting range error is
dτ
|              |      |              | ∆τ =      | ∆f = | 191ps,       | (cid:15) = 6cm. | (54) |
| ------------ | ---- | ------------ | --------- | ---- | ------------ | --------------- | ---- |
|              |      |              | e         | df   |              | r               |      |
| The baseline | plan | has balanced | sidebands |      | for ranging, | in which case   |      |
1d2τ
|     |     |     | ∆τ = | (∆f)2 | = 1.0ps, | (cid:15) = 0.3mm. | (55) |
| --- | --- | --- | ---- | ----- | -------- | ----------------- | ---- |
|     |     |     | e 2  | df2   |          | r                 |      |
Ifimplicitranging[41]with1Hztoneisusedinsteadofthebaselinedesign,then∆f = 1Hz,
and (cid:15) due to dispersion would 60nm, negligible by several orders of magnitude compared
r
| to other limitations |     | to ranging | such | as signal-to-noise |     | ratio. |     |
| -------------------- | --- | ---------- | ---- | ------------------ | --- | ------ | --- |
Nonlinearity Nonlinear effects in analog electronics, or fidelity errors, are difficult
to characterize analytically and are best measured experimentally. As an extreme test,
the single-bench interferometer testbed at JPL was operated with free-running lasers (Fig-
ure 38). The testbed was originally designed to have the slave laser phase-locked to the
Figure 38: Single bench testbed. The feedback to the lower laser is broken, leaving both
lasers free-running.
master laser via the “back link” interferometer. For the nonlinearity test, the feedback to

| 4 TIME-DELAY | INTERFEROMETRY |     | 59  |
| ------------ | -------------- | --- | --- |
the nominal slave laser was disconnected, leaving both lasers free-running and independent
of one another. As a result, the individual Sagnac signals, Φ and Φ were very large; as
√ 1 2
showninFigure39, Φ (f ) 5×103cycles/ Hz×(1Hz/f)2. Aftertime-shiftingtoform
≈
|     | 1,2 | s   |     |
| --- | --- | --- | --- |
Figure 39: Noise of various signals in single-bench experiment with unlocked lasers.
the α TDI combination, the noise level is suppressed by approximately 5×107×(1 Hz/f).
| 4.5.2 Reference | Performance |     |     |
| --------------- | ----------- | --- | --- |
Figure 40 shows a transfer-function measurement of a prototype quadrant photoreceiver.
The overall variation in phase (Φ[deg]) is a result of the limited bandwidth of the front-
end electronics The total variation in τ is less than 7ns, and the maximum variation
e
over 1MHz is ∆τ = 3ns. This is much larger than the model estimates of Section 4.5.1,
and is believed to arise from fluctuations in the measurement of reference phase, derived
from an independent photoreceiver. As a measurement upper limit, the worst-case ranging
method—1MHz, unbalanced ranging sidebands—would introduce the same sensitivity to
| frequency noise | as a ranging | error of 1m. |     |
| --------------- | ------------ | ------------ | --- |

| 4 TIME-DELAY |     | INTERFEROMETRY |     |     |     |     |     | 60  |
| ------------ | --- | -------------- | --- | --- | --- | --- | --- | --- |
Figure 40: Measurement of phase response Φ(f), and corresponding group delay τ =
dΦ/df and dispersion D = dτ/df, for frequencies spanning the range of LISA heterodyne
frequencies.
| 4.5.3 Performance |     |     | Improvement |     | Options |     |     |     |
| ----------------- | --- | --- | ----------- | --- | ------- | --- | --- | --- |
Design and testing of photoreceivers will continue, with the objective of demonstrating
the expected lower level of dispersion. Concurrently, the implicit ranging technique will
be investigated as a method that makes the LISA science measurement almost completely
| insensitive    | to dispersion. |     |         |        |            |     |     |     |
| -------------- | -------------- | --- | ------- | ------ | ---------- | --- | --- | --- |
| 4.6 Phasemeter |                |     | Digital | Signal | Processing |     |     |     |
Non-linearity of the phasemeter digital signal processing can limit the suppression factor
of TDI. A measurement of the TRL 4 phasemeter’s linearity was made by measuring
three digital data streams representing beatnotes between three independent lasers. This
linearity test is actually a test of the superposition principle, commonly stated as f(a)+
f(b) = f(a+b). For our purposes a, b and (a+b) are the true phases of the heterodyne
signals and f(x) is the result of the phase measurement of heterodyne signal with phase x.
| In our case, | we  | use a slightly |                      | modified | superposition: |     |     |      |
| ------------ | --- | -------------- | -------------------- | -------- | -------------- | --- | --- | ---- |
|              |     |                | f(a−b)+f(b−c)−f(a−c) |          |                |     | = 0 | (56) |
This relationship is symmetric in the sense that each of the three terms has the same
RMS noise level (assuming a, b, and c do also). The measurement also more closely
simulates the LISA arrangement, where each heterodyne signal phase is the difference of
| two laser | phases. | The | equivalent | optical | setup | is shown | in Figure 41. |     |
| --------- | ------- | --- | ---------- | ------- | ----- | -------- | ------------- | --- |

4 TIME-DELAY INTERFEROMETRY 61
Figure 41: Block diagram of equivalent optical set up for digital tests of phasemeter lin-
earity.
The test was conducted using a digital signal generator, implemented on a separate
FPGA. The digital signal generator generates three signals with phase correlations satisfy-
ing equation 56 to isolate the non-linearity of the digital signal processing. The individual
√
heterodyne signals’ phase noise spectra were approximately 104 cycles/ Hz ×(1 Hz/f)2.
Each phase measurement produced what appears to be uncorrelated, random noise. When
the three phase difference outputs are combined appropriately, the noise should add to
zero; any residual noise is attributed to non-linearity in the phasemeter. Figure 42 shows
√
that the residual noise root power spectral density of the 3 channel sum is 2 µcycle/ Hz
(limited by the known, internal quantization noise of the breadboard phasemeter). This
test demonstrates that the phasemeter DSP does not limit the TDI suppression factor at
the level of 1010×(1 Hz/f2).
4.7 Scattered Light
Scatteredlightisanothersourceoffrequencynoiseinducednon-linearity. Weconsiderlight
from a particular interferometer beam leaving that beam, travelling some different optical
path, and then rejoining that same beam. The stray or scattered beam must end up well
aligned with the main beam if it is to have any effect on the interferometric measurement.
To determine the effect of this scattered light on the LISA phase measurements we start
by considering an optical beam of amplitude 1. To this beam we add a small amount of
extra light of amplitude a (a << 1) as shown in the phasor diagram of Figure 43.
This light is of the same frequency as the original beam but has travelled a different
distance, so that its phase with respect to the original beam is φ . We can then calculate
s

4 TIME-DELAY INTERFEROMETRY 62
9
10
8
10
7
10
6
10
5
10
4
10
3
10
2
10
1
10
0
10
−1
10
−2
10
−3
10
−4
10
−5
10
−6
10
−2 −1 0 1
10 10 10 10
Frequency [Hz]
]zH!/selcyc[
esahP
Noise
Free running laser
0−1+2
Figure 42: Phasemeter DSP linearity test using three correlated noise sources.
φ
Error a a sinφ
φ s
1 s
Figure 43: Phasor diagram illustrating the phase error caused by scattered light.

| 4 TIME-DELAY |       | INTERFEROMETRY |           |     |        |          |          | 63   |
| ------------ | ----- | -------------- | --------- | --- | ------ | -------- | -------- | ---- |
| the phase    | error | this will      | introduce |     | to the | original | beam as: |      |
|              |       |                |           |     | φ      | =        | asinφ    | (57) |
|              |       |                |           |     | Error  |          | s        |      |
or equivalently
|     |     |     |     |       |     | aλ   | √       |      |
| --- | --- | --- | --- | ----- | --- | ---- | ------- | ---- |
|     |     |     |     | x     | =   | sinφ | [m/ Hz] | (58) |
|     |     |     |     | Error |     | 2π   | s       |      |
Ifthephaseofthescatteredlightisvaryingwithtimethenthiswillproduceatimevarying
| phase, | or displacement, |     | error | as calculated |     | below. |     |     |
| ------ | ---------------- | --- | ----- | ------------- | --- | ------ | --- | --- |
The relative phase of scattered light depends on the laser frequency and the extra path
| length | of the scattered |     | light | d.  |          |     |       |      |
| ------ | ---------------- | --- | ----- | --- | -------- | --- | ----- | ---- |
|        |                  |     |       | φ   | = 2πνd/c |     | [rad] | (59) |
s
| The phase | change | of  | the scattered |     | light | is, |       |      |
| --------- | ------ | --- | ------------- | --- | ----- | --- | ----- | ---- |
|           |        |     |               |     | ∂φ    |     | ∂φ    |      |
|           |        |     |               | ∆φ  | =     | s∆ν | + s∆d | (60) |
|           |        |     |               |     | s     | ∂ν  | ∂d    |      |
The first term is the phase change due to laser frequency changes and the second term is
the phase change due to changes in path length to the scattering source. In the context of
laser frequency noise cancellation we are interested only in the first term and the second
term is neglected for the remainder of this analysis; for a complete treatment of both terms
| see [42]. | From | Eq. 59 | we can | see, |     |     |     |     |
| --------- | ---- | ------ | ------ | ---- | --- | --- | --- | --- |
(cid:20)rad(cid:21)
∂φ
|     |     |     |     |     | s = 2πd/c |     |     | (61) |
| --- | --- | --- | --- | --- | --------- | --- | --- | ---- |
|     |     |     |     | ∂ν  |           |     | Hz  |      |
and so,
2πd
|     |     |     |     | ∆φ  | =   | ∆ν  | [rad] | (62) |
| --- | --- | --- | --- | --- | --- | --- | ----- | ---- |
s
c
For scattered light that has traveled and extra path length of d then, even if this length is
stable, a change of laser frequency will change the relative phase of the main and scattered
light beams.
We can consider two cases (i) the change in φ is small (<< 1) and (ii) the change in
s
| φ is large | compared |     | to a cycle | (>> | 1). |     |     |     |
| ---------- | -------- | --- | ---------- | --- | --- | --- | --- | --- |
s
| Case 1: | For ∆φ | <<  | 1 we | can approximate |     | Eq. | 57 to, |     |
| ------- | ------ | --- | ---- | --------------- | --- | --- | ------ | --- |
s
|     |     |     |     |     | φ     |     | aφ  |     |
| --- | --- | --- | --- | --- | ----- | --- | --- | --- |
|     |     |     |     |     | Error | ≈   | s   |     |
ad
|     |     |     |     |     | ∆φ  |     | 2π ∆ν | (63) |
| --- | --- | --- | --- | --- | --- | --- | ----- | ---- |
≈
|     |     |     |     |     | Error |     | c   |     |
| --- | --- | --- | --- | --- | ----- | --- | --- | --- |

4 TIME-DELAY INTERFEROMETRY 64
This small angle approximation gives the worst case phase error due to scattered light (the
slopeofsineismaximumatzero). Forastationaryscatteringpoint,thisassumptionimplies
that ∆ν << 2πc/d (e.g. ∆ν << 300 MHz for d = 1 m). This is a good approximation for
Fourier frequencies in the LISA band (even the free-running laser noise is expected to be
√
≈ 10 MHz/ Hz at 1 mHz).
The limit to the suppression factor due to scattered light can be found by converting
the laser frequency noise phase noise ∆φ = ∆ν/f [rad].
ν
∆φ c
ν ∼ (64)
∆φ adf
Error
Using pessimistic estimates of scattered light [42] we assume the a < 2e−5 and d = 1 m
we arrive at a suppression factor 1.5×1013×(1 Hz/f).
Case 2: At frequencies well below the LISA band the laser frequency drift could be
significantly larger and we could expect ∆φ >> 1. Long term drift of the laser frequency
s
coupled with the periodic nonlinearity of the scattering error (Eq. 57) will upconvert
low frequency laser noise to produce an error at frequencies within the LISA band. To
avoid this, we should ensure that the laser does not drift through one scattering “fringe”
faster than say, 10,000 seconds. The scattered finge is c/d Hz. so we must ensure that
δ(∆ν)/δt < c/d/104 or a frequency drift of less than 300 kHz/s. This leaves substantial
margin over the worst case frequency drift caused by Doppler knowledge error and arm
locking of around 5 kHz/s (assuming a 600 kHz common arm Doppler knowledge error).
4.8 Summary
Comparing all known effects it is apparent that errors in the ranging/timing limits the
TDI frequency noise suppression. With 1 m ranging and 1 pm allocation a laser frequency
noise 141 Hz/rt(Hz) could be tolerated.

65
Part II
| Frequency |     | Noise |     | Suppression |     |     |     |     | System |     |     |     |
| --------- | --- | ----- | --- | ----------- | --- | --- | --- | --- | ------ | --- | --- | --- |
Options
This section describes how the individual frequency noise suppression techniques are com-
bined into systems capable of meeting LISA’s frequency noise requirement. We consider
| four combinations |     | of techniques |     | listed | in Table | 11. |     |     |     |     |     |     |
| ----------------- | --- | ------------- | --- | ------ | -------- | --- | --- | --- | --- | --- | --- | --- |
Table 11: Summary of system options performance. The margin for systems including arm
locking depends on the arm length mismatch. Values for margin assume a Time-Delay
| Interferometry | performance |             | limited | by    | 1 m    | ranging | error.  |     |           |     |      |         |
| -------------- | ----------- | ----------- | ------- | ----- | ------ | ------- | ------- | --- | --------- | --- | ---- | ------- |
|                |             |             |         |       | Margin | at 3    | mHz     |     | Margin    |     | at 1 | Hz      |
| Suppression    | System      |             |         |       |        |         |         |     |           |     |      |         |
|                |             |             |         | ∆τ =  | 0.51   | s ∆τ    | = 0.026 | s   | ∆τ = 0.51 | s   | ∆τ = | 0.026 s |
| Fixed cavity   |             |             |         |       |        | 10      |         |     |           | 10  |      |         |
| Arm locking    | only        |             |         |       | 5      |         | 5       |     | 1.8       |     |      | 2.4     |
| Cavity &       | arm locking |             |         | 16000 |        |         | 800     |     | 1500      |     |      | 2000    |
| Mach-Zehnder   | &           | arm locking |         | 13000 |        |         | 800     |     | 54        |     |      | 75      |
In all options, one laser is designated as the master laser and all other active lasers
in the constellation are phase-locked to the master with appropriate frequency offsets.
The residual phase-locking error is assumed to be negligible compared to the laser phase
noise after stabilization. The lasers are assumed to have a free-running frequency noise
| characterized | by a | linear | spectral | density  | of  | approximately, |            |     |     |     |     |      |
| ------------- | ---- | ------ | -------- | -------- | --- | -------------- | ---------- | --- | --- | --- | --- | ---- |
|               |      |        |          |          | √   | (cid:18)1      | Hz(cid:19) |     |     |     |     |      |
|               |      |        | ∆ν       | = 30kHz/ |     | Hz·            |            |     |     |     |     | (65) |
f
TDI is common to all designs. The allocated equivalent single-link path length noise to
|     |     |     |     |     |     |     |     |     | √   | (cid:113) |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --------- | --- | --- |
residual laser frequency noise (post-TDI) is assumed to be 2pm/ Hz· 1+(3mHz/f)4,
the value in the Requirements Flowdown Document. This allocation is converted to a
pre-TDI frequency noise allocation using Eq. 42 (Section 4), which assumes that the TDI
supression factor is dominated by 1 m ranging errors. This allocation implies a laser
| frequency | noise stability |     | allocation | described |     | by, |     |     |     |     |     |     |
| --------- | --------------- | --- | ---------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
(cid:20)1m(cid:21)
|     |     |      |          | √   |     |     | (cid:113)   |     |     |     |     |      |
| --- | --- | ---- | -------- | --- | --- | --- | ----------- | --- | --- | --- | --- | ---- |
|     |     | ν    | = 282Hz/ |     | Hz· |     | 1+(3mHzf)4. |     |     |     |     | (66) |
|     |     | stab |          |     |     |     | ·           |     |     |     |     |      |
∆L
For options using arm locking, we assume that modified dual arm locking is used, as
| described | in section | 3.3. |     |     |     |     |     |     |     |     |     |     |
| --------- | ---------- | ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

5 FIXED CAVITY 66
5 Fixed Cavity
The master laser is locked to a fixed Fabry-Perot cavity of moderate finesse using the
Pound-Drever-Hall (PDH) technique. One option for the optical and electronic interfaces
between the relevant subsystems are shown in Figure 44.
5.1 Design Summary
Laser Frequency
Stabilization Subsystem
Phase Measurement
Laser Subsystem
Subsystem
Optical Bench
Subsystem
Electronic Interface Optical Interface
Figure 44: Subsystem interface diagram for Fixed Cavity Stabilization
The optical interface between the Laser Subsystem and the Frequency Stabilization
Subsystem is unmodulated light delivered by an optical fiber. The PDH sidebands are
imposedbyaphasemodulatorcontainedwithinthelaserfrequencystabilizationsubsystem.
The Frequency Stabilization Subsystem contains a waveguide modulator, optical cavity
and photoreceiver. In this diagram it is assumed that the Phase Measurement Subsystem
implements the demodulation of the PDH error signal and feedback controller, however
this functionality could instead be included in the Frequency Stabilization Subsystem.
The electrical interface between the Frequency Stabilization Subsystem and the Phase
Measurement Subsystem is an analog electronic signal from the PDH photoreceiver. The
laserfrequencycontroloperatesintwodistinctmodes: pre-stabilizationandphase-locking.
Only one mode is active at any time and there is no interaction between these control
loops. Not shown is the frequency distribution subsystem and its interfaces with the Laser
Frequency Subsystem, the Phase Measurement Subsystem and the Laser Subsystem.
The cavity’s control system parameters are summarized in Table 12. The noise floor
is set at a level that is consistent with measurements made in several laboratories. The
unity gain frequency was chosen to be near the intersection of the cavity noise floor with
the free-running laser noise to avoid adding noise at high frequencies. With a controller
slope of 1/f or steeper, the open-loop gain is sufficient to reach the cavity noise floor at
all frequencies below the unity gain frequency, making the exact details of the controller
immaterial.

| 6 ARM | LOCKING |       | ONLY      |           |        |            |               | 67  |
| ----- | ------- | ----- | --------- | --------- | ------ | ---------- | ------------- | --- |
|       |         | Table | 12:       | Parameter | sumary | for cavity | stabilization |     |
|       |         |       | Parameter |           |        |            | Value         |     |
√
(cid:112)1+(3mHz/f)4
|     |     | Cavity | Noise | Floor     | 30Hz/ | Hz· |        |     |
| --- | --- | ------ | ----- | --------- | ----- | --- | ------ | --- |
|     |     | Unity  | Gain  | Frequency |       |     | 1.8kHz |     |
∼
5.2 Performance
The frequency noise of the cavity-stabilized laser is shown in Figure 45 compared to the
free-running laser and the TDI capability for 1 m ranging. The frequency stability is
determined by the noise floor of the cavity (sensing). This plot shows that with 1 m
ranging accuracy, cavity stabilization would meet the frequency noise allocation with a
| margin of | approximately |     | 10  | across | the LISA signal | band. |     |     |
| --------- | ------------- | --- | --- | ------ | --------------- | ----- | --- | --- |
106

104
]zHtr/zH[ esioN
TDI Capability
102
Fixed cavity
100
10−2
|     |     |     | 10−4 | 10−3 | 10−2 | 10−1 | 100 101 |     |
| --- | --- | --- | ---- | ---- | ---- | ---- | ------- | --- |
Frequency[Hz]
Figure 45: Frequency noise after cavity stabilization compared to the TDI capability (fre-
| quency noise | requirement) |     | assuming |     | 1 m ranging | accuracy. |     |     |
| ------------ | ------------ | --- | -------- | --- | ----------- | --------- | --- | --- |
| 6 Arm        | Locking      |     | Only     |     |             |           |     |     |
In this option the master laser is frequency stabilized using modified dual arm locking with
no pre-stabilization.

| 7 ARM | LOCKING | WITH | TUNABLE | CAVITY | PRE-STABILIZATION |     |     | 68  |
| ----- | ------- | ---- | ------- | ------ | ----------------- | --- | --- | --- |
Phase Measurement
Laser Subsystem
Subsystem
Optical Bench
Subsystem
|     |                |               | Electronic interface |         |     | Optical interface |              |     |
| --- | -------------- | ------------- | -------------------- | ------- | --- | ----------------- | ------------ | --- |
|     | Figure         | 46: Subsystem | interface            | diagram | for | Arm Locking       | only option. |     |
| 6.1 | Design Summary |               |                      |         |     |                   |              |     |
A block diagram of the interfaces between key subsystems is shown in Figure 46. The laser
frequency control operates in two distinct modes: phase-locking and arm locking. Not
shown is the frequency distribution subsystem and its interfaces with the Phase Measure-
ment Subsystem and the Laser Subsystem. The Optical Bench Subsystem in this option is
unchanged from the Fixed Cavity case. In the Phase Measurement Subsystem the Fixed
Cavity demodulation and frequency controller is removed and a modified dual arm locking
controller is needed. The controller and sensor transfer function for modified dual arm
| locking | is described | in detail   | in Section | 3.          |          |         |             |     |
| ------- | ------------ | ----------- | ---------- | ----------- | -------- | ------- | ----------- | --- |
|         | Table        | 13: Summary | of         | arm locking | control  | system  | parameters. |     |
|         |              | Parameter   |            |             | value    |         |             |     |
|         |              | Sensor      |            | Modified    | Dual Arm | Locking | [30]        |     |
|         |              | gain @      | 3mHz       |             | 87,000   |         |             |     |
|         |              | lower       | UGF        |             | 4.8µHz   |         |             |     |
|         |              | upper       | UGF        |             | 14.7kHz  |         |             |     |
6.2 Performance
The frequency noise after arm locking is shown in Figure 47, along with the TDI capability
assuming 1 m ranging accuracy. This design meets the requirements with the possible
exception of the extreme low-end of the LISA band (less than 0.1 mHz). Note that this
spectra was achieved assuming the worst case (minimum) arm-length difference, ∆τ =
0.026s.
| 7 Arm | Locking | with | Tunable |     | Cavity | Pre-stabilization |     |     |
| ----- | ------- | ---- | ------- | --- | ------ | ----------------- | --- | --- |
The master laser is stabilized to a fixed reference cavity with an adjustable frequency offset
provided by offset sideband locking. The master laser is further stabilized by generating

7 ARM LOCKING WITH TUNABLE CAVITY PRE-STABILIZATION 69
106
104
102
100
10−2
10−4 10−3 10−2 10−1 100 101
Frequency[Hz]
]zHtr/zH[
esioN
TDI Capability
Modified Dual Arm Locking
(no prestabilization)
Figure 47: Laser frequency noise after stabilization by modified dual arm locking with no
pre-stabilization. Arm length mismatch of ∆τ = 0.026s
an arm locking error signal, filtering it through a controller, and feeding it back to both
the sideband offset and the laser frequency actuators.
7.1 Design Summary
The optical interface between the Laser Subsystem and the Frequency Stabilization Sub-
system is unmodulated light delivered by an optical fiber. The sidebands are imposed by a
phase modulator contained within the laser frequency stabilization subsystem. The signal
used to drive the phase modulator must have an adjustable center frequency with a tuning
range greater than approximately 10 MHz to accommodate the frequency pulling of arm
locking. This sinusoidal signal is also phase modulated at a frequency of approximately
5 MHz to produce the PDH sidebands. The Frequency Stabilization Subsystem contains
a waveguide modulator, optical cavity, photoreceiver and a voltage controlled oscillator
(VCO) or numerically controlled oscillator (NCO) used to adjust the offset frequency for
the sideband modulation. Once again it is assumed that the Phase Measurement Subsys-
temimplementsthedemodulationofthePDHerrorsignalandfeedbackcontroller,however
this functionality could also be included in the Frequency Stabilization Subsystem. The
electrical signal from the Frequency Stabilization Subsystem to the Phase Measurement
Subsystem is an analog electronic signal from the PDH photoreceiver. The signal from the
Phase Measurement Subsystem to the Frequency Stabilization Subsystem is a correction
signal (analog or digital) to adjust the frequency of the VCO/NCO. The usual interfaces
to the frequency distribution subsystem are not shown.

7 ARM LOCKING WITH TUNABLE CAVITY PRE-STABILIZATION 70
Laser Frequency
Stabilization Subsystem
Phase Measurement
Laser Subsystem
Subsystem
Optical Bench
Subsystem
Electronic interface Optical interface
Figure 48: Subsystem interface diagram for Cavity and Arm Locking option.
Pre-stabilization with arm locking is nested control system. The performance of such
a system depends on the details of how the signals are combined. As shown in Figure 49,
the laser is pre-stabilized to the cavity. An additional error signal from arm locking is
incorporatedattwopoints. Thearmlockingfeedbacksignalisusedtoadjustthefrequency
of the light entering the cavity (point A in Figure 49). This is achieved by changing the
modulation frequency used to produce the resonant sideband. The arm locking feedback
signal is also added to the PDH correction signal and fed back to the laser frequency
actuator (point B in Figure 49). This second correction point allows the arm locking
control system to be optimized independently of the bandwidth of the cavity stabilization
control loop.
ν ν
FR stab
ν
corr
G
AL
G
cav
noitautca
ycneuqerf
resaL
htaP
kcabdeeF
ytivaC
lacitpO
htaP
kcabdeeF
gnikcoL
mrA
A
B
Figure 49: Nested feedback loops for arm locking with a fixed cavity
We can express the stabilized laser frequency ν in terms of the free-running laser
stab

| 8 ARM     | LOCKING  | WITH | MACH-ZEHNDER  |      |            | PRE-STABILIZATION |      |     | 71   |
| --------- | -------- | ---- | ------------- | ---- | ---------- | ----------------- | ---- | --- | ---- |
| frequency | noise, ν | and  | the frequency |      | correction |                   | ν .  |     |      |
|           |          | FR   |               |      |            |                   | corr |     |      |
|           |          |      |               | ν    | = ν        | −ν                |      |     | (67) |
|           |          |      |               | stab |            | FR                | corr |     |      |
ν is made up of contributions from both the arm locking and PDH error signals.
corr
|     |     |     | ν    | = ν  | (G  | +G  | G      | +G ) | (68) |
| --- | --- | --- | ---- | ---- | --- | --- | ------ | ---- | ---- |
|     |     |     | corr | stab | cav |     | AL cav | AL   |      |
where G and G are the total open loop gains of the cavity and arm locking control
cav AL
systems respectively. Rearranging to solve for the noise suppression we get,
|     |     |     | ν    |          |     | 1                |     |          |      |
| --- | --- | --- | ---- | -------- | --- | ---------------- | --- | -------- | ---- |
|     |     |     | stab | =        |     |                  |     |          | (69) |
|     |     |     | ν    | 1+G      |     | +G               | G   | +G       |      |
|     |     |     | FR   |          | cav | AL               | cav | AL       |      |
|     |     |     |      | (cid:18) | 1   | (cid:19)(cid:18) | 1   | (cid:19) |      |
|     |     |     |      | =        |     |                  |     |          | (70) |
|     |     |     |      |          | 1+G |                  | 1+G |          |      |
|     |     |     |      |          | cav |                  |     | AL       |      |
From Equation 70 we can see that the total frequency noise suppression is the product of
| the noise | suppression | of  | the individual |     | loops. |     |     |     |     |
| --------- | ----------- | --- | -------------- | --- | ------ | --- | --- | --- | --- |
7.2 Performance
The frequency noise after cavity pre-stabilization and arm locking is shown in Figure 50.
ThisdesignmeetsrequirementsforTDI1mrangingaccuracywithamarginofgreaterthan
800 across the LISA band. The hump in the noise floor near 3mHz is due to clock noise
coupling into the arm locking sensor and is only present for small arm-length differences.
| 8 Arm | Locking |     | with | Mach-Zehnder |     |     |     | Pre-stabilization |     |
| ----- | ------- | --- | ---- | ------------ | --- | --- | --- | ----------------- | --- |
In this configuration the master laser is stabilized to a Mach-Zehnder interferometer as
describedinSection2.5. Themasterlaserisfurtherstabilizedbygeneratinganarmlocking
error signal, filtering it through a controller, and feeding it back to offset the Mach-Zender
lock point. This is achieved by adjusting the phase of the numerically oscillator used to
demodulate the Mach-Zehnder heterodyne signal. The arm locking correction is also fed
| back to    | the laser | frequency | directly | as  | discussed | below. |     |     |     |
| ---------- | --------- | --------- | -------- | --- | --------- | ------ | --- | --- | --- |
| 8.1 Design | Summary   |           |          |     |           |        |     |     |     |
The optical bench subsystem is modified to include the extra interference path needed to
producethearmlengthmismatchedMach-Zehnder. AnextrachannelisaddedtothePhase
Measurement Subsystem to determine the phase of this heterodyne signal. As described
in Section 2.5, the phase of this signal depends on the master laser frequency relative to
the Mach-Zehnder arm length difference. The Phase Measurement Subsystem would also

| 8 ARM LOCKING | WITH MACH-ZEHNDER |     | PRE-STABILIZATION | 72  |
| ------------- | ----------------- | --- | ----------------- | --- |
106

104
]zHtr/zH[ esioN
TDI Capability
102
Modified Dual Arm Locking
|     | 100 | with Cavity pre-stabilization |     |     |
| --- | --- | ----------------------------- | --- | --- |
10−2

|     | 10−4 | 10−3 10−2 | 10−1 100 101 |     |
| --- | ---- | --------- | ------------ | --- |
Frequency[Hz]
Figure 50: Laser frequency noise after stabilization by modified dual arm locking with
| cavity pre-stabilization. | Arm length | mismatch | of ∆τ = 0.026s |     |
| ------------------------- | ---------- | -------- | -------------- | --- |
Phase Measurement
Laser Subsystem
Subsystem
Optical Bench
Subsystem
|     | Electronic interface |     | Optical interface |     |
| --- | -------------------- | --- | ----------------- | --- |
Figure 51: Subsystem interface diagram for Mach-Zehnder and Arm Locking option.

8 ARM LOCKING WITH MACH-ZEHNDER PRE-STABILIZATION 73
ν ν
FR stab
ν
corr
G
AL
G
MZ
noitautca
ycneuqerf
resaL
htaP
kcabdeeF
rednheZ-hcaM
htaP
kcabdeeF
gnikcoL
mrA
A
B
Figure 52: Nested feedback loops for arm locking with Mach-Zehnder stabilization
include a pre-stabilization controller, needing only minimal modifications from the usual
phase-locking controller.
TheMach-ZehnderandarmlockingstabilizationsystemsarecombinedasshowninFig-
ure 52. Following the derivation in the previous section, the closed loop noise suppression
of laser frequency noise is given by,
ν (cid:18) 1 (cid:19)(cid:18) 1 (cid:19)
stab = . (71)
ν 1+G 1+G
FR MZ AL
If we include sensor noise in both the Mach-Zehnder and arm locking control loops, we
arrive at the total closed loop frequency noise of,
ν N G 1 N G
ν = FR − MZ MZ − AL AL . (72)
stab (1+G )(1+G ) (1+G )(1+G ) (1+G )
MZ AL MZ AL AL
This shows that the Mach-Zehnder closed-loop sensor noise, N G /(1+G ) is sup-
MZ MZ MZ
pressed by the arm locking gain, (1+G ). The arm locking sensor noise N is directly
AL AL
imposed on the stabilized laser frequency.
The Mach-Zehnder frequency stabilization properties are summarized in Table 14. A
pathlengthdifferenceof50cmisassumedforthefrequencyreferenceinterferometer, which
sets both the frequency discriminant and tuning coefficient for the loop. The error point
noise, a combination of path length noise and phase measurement noise, is set at an equiv-
√
alent path length noise of 1pm/ Hz with a roll-up below 2mHz.
The arm locking controller is summarized in Table 7. With a unity gain frequency of
20Hz,theMach-Zehnderpre-stabilizationshouldbereadoutnoiselimitedatallfrequencies
√
in the LISA science band, yielding a level of 800 Hz/ Hz prior to arm locking.

| 8 ARM | LOCKING |       | WITH MACH-ZEHNDER |         |           | PRE-STABILIZATION |                        |                   | 74  |
| ----- | ------- | ----- | ----------------- | ------- | --------- | ----------------- | ---------------------- | ----------------- | --- |
|       | Table   | 14:   | Parameters        | assumed |           | for Mach-Zehnder  |                        | pre-stabilization |     |
|       |         |       | Parameter         |         |           |                   | Value                  |                   |     |
|       |         | Path  | length difference |         |           |                   | 50cm                   |                   |     |
|       |         |       |                   |         |           |                   | √ (cid:112)1+(2mHz/f)4 |                   |     |
|       |         | Error | point             | noise   | (1µcycle/ |                   | Hz)·                   |                   |     |
|       |         | Unity | Gain Frequency    |         |           |                   | ∼ 20Hz                 |                   |     |
8.2 Performance
Figure 53 shows the frequency noise after Mach-Zehnder pre-stabilization and arm locking.
This design meets requirements with a margin greater than 50 at 1 Hz and 800 at 3 mHz.
The hump in the arm locking noise floor near 4mHz is due to clock noise coupling into the
arm locking sensor and is only present for small arm-length differences.
106

104
]zHtr/zH[ esioN
TDI Capability
102
100
Modified Dual Arm Locking
with Mach-Zehnder pre-stabilization
10−2

|     |     |     | 10−4 | 10−3 | 10−2 |     | 10−1 | 100 101 |     |
| --- | --- | --- | ---- | ---- | ---- | --- | ---- | ------- | --- |
Frequency[Hz]
Figure 53: Laser frequency noise after stabilization by modified dual arm locking with
| Mach-Zehnder |     | pre-stabilization. |     | Arm | length | mismatch | of  | ∆τ = 0.026s |     |
| ------------ | --- | ------------------ | --- | --- | ------ | -------- | --- | ----------- | --- |

| REFERENCES |     |     |     |     |     |     |     |     |     | 75  |
| ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
References
[1] Seigman A., Lasers, University Science Books, Sausalito, CA, (1986).
| [2] Pound | R.V.,   |            |         |           |               |     |              |     | Oscillators, | Rev. Sci. |
| --------- | ------- | ---------- | ------- | --------- | ------------- | --- | ------------ | --- | ------------ | --------- |
|           |         | Electronic |         | Frequency | Stabilization |     | of Microwave |     |              |           |
| Instr.    | 17(11): | 490-505,   | (1946). |           |               |     |              |     |              |           |
[3] Drever R.W.P., Hall J.L., Kowalski F.L., Hough J., Ford G.M., Munley A.J., and
| Ward       | H.,      |                 |         |                      |     |               |           |            | Resonator,     | App.     |
| ---------- | -------- | --------------- | ------- | -------------------- | --- | ------------- | --------- | ---------- | -------------- | -------- |
|            |          | Laser Phase     | and     | Frequency            |     | Stabilization | Using     | an Optical |                |          |
| Phys.      | B 31(2): | 97-105,         | (1983). |                      |     |               |           |            |                |          |
| [4] Black  | E.,      |                 |         |                      |     |               |           |            | Stabilization, | Am.      |
|            |          | An Introduction |         | to Pound-Drever-Hall |     |               | Laser     | Frequency  |                |          |
| J. Phys    | 69(1):   | 490-505,        | (2001). |                      |     |               |           |            |                |          |
| [5] Bender | P.L.,    | Danzmann        |         | K. and               | the | LISA Study    | Team,     |            |                |          |
|            |          |                 |         |                      |     |               |           | Laser      | interferometer | space    |
|            |          |                 |         |                      |     |               |           | Report,    | Doc.           | MPQ 233, |
| antenna    | for      | the detection   |         | of gravitational     |     | waves         | Pre-Phase | A          |                |          |
(1998).
[6] Alnis J., Matveev A., Kolachevsky N., Udem Th., and H¨ansch T. W.,
Subhertz
| linewidth |     | diode lasers, | Phys. | Rev. | A,  | 77, 053809, | (2008). |     |     |     |
| --------- | --- | ------------- | ----- | ---- | --- | ----------- | ------- | --- | --- | --- |
[7] Thorpe J.I., Numata K., Livas J., Laser Frequency Stabilization and Control through
|        |          |         |     |         |          | Opt. | Ex. 16(20):15980-15990, |     | (2008). |     |
| ------ | -------- | ------- | --- | ------- | -------- | ---- | ----------------------- | --- | ------- | --- |
| offset | sideband | locking | to  | optical | cavities |      |                         |     |         |     |
[8] de Vine G. and Shaddock D.A., Ongoing investigations at the Jet Propulsion Labora-
| tory, | Pasadena, | CA, | 2008. |     |     |     |     |     |     |     |
| ----- | --------- | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
[9] Leonhardt V. and Camp J., Space interferometry application of laser frequency stabi-
| lization | with | molecular | iodine, | App. | Opt. | 45, | 4142, (2006). |     |     |     |
| -------- | ---- | --------- | ------- | ---- | ---- | --- | ------------- | --- | --- | --- |
[10] BjorklundG.C.,Frequency-modulationspectroscopy: anewmethodformeasuringweak
| absorptions  |       | and dispersions, |     | Opt. | Lett. | 5, 15, | (1979). |     |     |     |
| ------------ | ----- | ---------------- | --- | ---- | ----- | ------ | ------- | --- | --- | --- |
| [11] Shirley | J.H., |                  |     |      |       |        |         |     |     |     |
Modulation transfer processes in optical heterodyne saturation spec-
| troscopy, |     | Opt. Lett. | 7, 537, | (1982). |     |     |     |     |     |     |
| --------- | --- | ---------- | ------- | ------- | --- | --- | --- | --- | --- | --- |
[12] Heinzel G., Braxmaier C., Schilling R., Rudiger A., Robertson D., te Plate M., Wand
V., Arai K., Johann U., and Danzmann K.,, “Interferometry for the LISA technology
package (LTP) aboard SMART-2”, Class. Quantum Grav. 20, S153–S161 (2003).
[13] Heinzel G., Wand V., Garcia A., Jennrich O., Braxmaier C., Robertson D., Middleton
K., Hoyland D., Rudiger A., Schilling R., Johann U., and Danzmann K., “The LTP
interferometer and phasemeter”, Class. Quantum Grav. 21, S581–S587 (2004).
[14] SheardB.S., GrayM.B., McClellandD.E., andShaddockD.A., PhysicsLettersA320,
9 (2003).

| REFERENCES |     |     |     |     |     |     |     |     |     | 76  |
| ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
[15] Marin A.F.G., Heinzel G., Schilling R., Wand V., Cervantes F.G., Steier F., Jennrich
O., Weidner A., and Danzman K., Class. Quantum Grav. 22 , p. S235. (2005)
[16] Thorpe J.I. and Mueller G., Physics Letters A 199-204 (2005)
342
[17] Sheard B.S., Gray M.B., and McClelland D.E., Applied Optics, 8491-8499 (2006).
45
[18] Wand V., Yu Y., Mitryk S., Sweeney D., Preston A., Tanner D., Mueller G., Thorpe
| J.I.           | , and Livas           | J.,      | J. of        | Phys: | Conference |                 | Series, 154 | 012024,         | (2009).    |           |
| -------------- | --------------------- | -------- | ------------ | ----- | ---------- | --------------- | ----------- | --------------- | ---------- | --------- |
| [19] Sylvestre | J.,                   | Phys.    | Rev.         | D 70, | 102002     | (2004).         |             |                 |            |           |
| [20] Tinto     | M., Rakhmanov         |          | M.,          |       |            |                 |             |                 |            |           |
|                |                       |          |              | On    | the        | laser frequency |             | stabilization   | by locking | to a LISA |
| arm,           | arXiv:gr-qc/0408076v1 |          |              |       | (2004).    |                 |             |                 |            |           |
| [21] Sutton    | A., and               | Shaddock |              | D.A., | Phys.      | Rev.            | D 78,       | 082001, (2008). |            |           |
| [22] Herz      | M., Opt.              | Eng.     | (Bellingham, |       | Wash.),    |                 | 44, 090505, | (2005).         |            |           |
[23] Tinto M., Shaddock D.A., Sylvestre J., and Armstrong J.W., Phys. Rev. D (2003).
67
[24] Heinzel G., Braxmaier C., Danzmann K., Gath P., Hough J., Jennrich O., Johann
U., Rudiger A., Sallusti M., and Schulte H., Classical and Quantum Gravity, 23,
| S119-S124 | (2006) |     |     |     |     |     |     |     |     |     |
| --------- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
[25] Tinto M., Estabrook F.B., and Armstrong J.W., Phys. Rev. D 65, 082003 (2002).
[26] Tinto M., Estabrook F.B., and Armstrong J.W., Phys. Rev. D 69, 082001 (2004).
[27] Hellings R.W., Giampieri G., Maleki L., Tinto M., Danzmann K., Hough J., and
| Robertson     | D.,   | Optics | Comm. |     | 124    | 313-320 | (1996). |     |     |     |
| ------------- | ----- | ------ | ----- | --- | ------ | ------- | ------- | --- | --- | --- |
| [28] Hellings | R.W., | Phys.  | Rev.  | D   | 022002 | (2001)  |         |     |     |     |
64
[29] de Vine G., Shaddock D.A., Spero R.E., Ware B., McKenzie K., and Klipstein W., in
| preparation |     | (2009) |     |     |     |     |     |     |     |     |
| ----------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
[30] McKenzie K., Spero R.E., and Shaddock D.A., The performance of arm locking in
|     | , Submitted |     | to Phys. | Rev. | D   |     |     |     |     |     |
| --- | ----------- | --- | -------- | ---- | --- | --- | --- | --- | --- | --- |
LISA
[31] Gath P., Arm Locking Configurations, LISA performance engineering technical note,
| LPE-ASD-TN-0005 |     |     | (2009). |     |     |     |     |     |     |     |
| --------------- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
[32] Gath P., Payload Control Systems, LISA mission formulation technical note, LISA-
| ASD-TN-2004 |     | (2006). |     |     |     |     |     |     |     |     |
| ----------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
[33] Tinto M. and Armstrong J.W., Cancellation of laser noise in an unequal-arm inter-
ferometer detector of gravitational radiation Phys. Rev. D 59, 102003, (1999).

REFERENCES 77
[34] McKenzie K. and Shaddock D.A., TDI Capabilities and Frequency Noise Require-
| ments,               | LISA | Tech. Note | LIMAS-2008-001 |      | (2008).         |     |     |
| -------------------- | ---- | ---------- | -------------- | ---- | --------------- | --- | --- |
| [35] LI-AEI-TN-3013b |      | AEI        | Technical      | Note | in preparation. |     |     |
[36] Shaddock D.A., Ware B., Halverson P., Spero R.E., Klipstein W., Overview of the
|      |            | AIP | Conf Proc. |     | 654-60, | (2006). |     |
| ---- | ---------- | --- | ---------- | --- | ------- | ------- | --- |
| LISA | Phasemeter |     |            | 873 |         |         |     |
[37] Misra P. and Enge P. (2nd Ed) Global positioning system, signals, measurements, and
| performance, |     | Ganga-Jamura | Press, | (2001). |     |     |     |
| ------------ | --- | ------------ | ------ | ------- | --- | --- | --- |
[38] Cornish N.J. and Hellings R.W., Class. Quantum Grav. 20, p 4851-4860 (2003)
[39] Shaddock D.A., Ware B., Spero R.E., and Vallisneri M., Postprocessed time-delay
|                |     | LISA, | Phys | Rev D, | 70, 081101, | (2004). |     |
| -------------- | --- | ----- | ---- | ------ | ----------- | ------- | --- |
| interferometry |     | for   |      |        |             |         |     |
[40] Shaddock D.A. and Ware B.Data rates and interpolation error, JPL Technical Note
| LIMAS      | 2005-001 | (2005)     |             |     |          |             |                    |
| ---------- | -------- | ---------- | ----------- | --- | -------- | ----------- | ------------------ |
| [41] Spero | R.E.,    | et al      |             |     |          | 8th Edoardo | Amaldi Conference, |
|            |          | Range      | measurement |     | for LISA |             |                    |
| Columbia   |          | University | June (2009) |     |          |             |                    |
[42] Robertson D. and Ward H. Light, Technical Note L2-UGL-TN-3001 Version
Scattered
| 1.0 | January, | (2009). |     |     |     |     |     |
| --- | -------- | ------- | --- | --- | --- | --- | --- |