import numpy as np
import matplotlib.pyplot as plt

class PLL:
    def __init__(self, ref_frequency, vco_frequency, loop_gain=0.1, damping_factor=0.707, filter_bandwidth=100):
        # Reference frequency and initial VCO frequency
        self.ref_frequency = ref_frequency
        self.vco_frequency = vco_frequency
        self.loop_gain = loop_gain
        self.damping_factor = damping_factor
        self.filter_bandwidth = filter_bandwidth
        
        # PLL internal state
        self.phase_error = 0
        self.filtered_error = 0
        self.vco_phase = 0

    def phase_detector(self, ref_phase, vco_phase):
        """Calculate the phase difference between reference and VCO signals."""
        return np.sin(ref_phase - vco_phase)

    def loop_filter(self, phase_error):
        """Simple low-pass filter for smoothing the phase error signal."""
        alpha = self.filter_bandwidth / (self.filter_bandwidth + 1)
        self.filtered_error = alpha * phase_error + (1 - alpha) * self.filtered_error
        return self.filtered_error

    def vco(self, control_signal, dt):
        """Simulate the VCO, adjusting its frequency based on the control signal."""
        self.vco_frequency += self.loop_gain * control_signal
        self.vco_phase += 2 * np.pi * self.vco_frequency * dt
        return self.vco_phase

    def lock_to_signal(self, input_signal, time):
        """Run the PLL to lock onto an input signal."""
        output_signal = []
        for t in time:
            # Reference signal phase
            ref_phase = 2 * np.pi * self.ref_frequency * t
            
            # Phase detection
            phase_error = self.phase_detector(ref_phase, self.vco_phase)
            
            # Filter the phase error
            control_signal = self.loop_filter(phase_error)
            
            # Update the VCO based on filtered error
            vco_phase = self.vco(control_signal, time[1] - time[0])
            
            # Output the VCO signal
            output_signal.append(np.sin(vco_phase))
        
        return np.array(output_signal)

    def plot_output_signal(self, output_signal, time):
        """Plot the PLL output signal and reference signal for comparison."""
        ref_signal = np.sin(2 * np.pi * self.ref_frequency * time)
        
        plt.figure(figsize=(12, 6))
        plt.plot(time, ref_signal, label="Reference Signal")
        plt.plot(time, output_signal, label="PLL Output Signal")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.title("PLL Output vs. Reference Signal")
        plt.legend()
        plt.grid()
        plt.show()


# Usage Example
time = np.linspace(0, 1, 1000)  # 1 second duration
pll = PLL(ref_frequency=50, vco_frequency=45)  # 50 Hz ref freq, 45 Hz initial VCO freq
output_signal = pll.lock_to_signal(None, time)
pll.plot_output_signal(output_signal, time)
