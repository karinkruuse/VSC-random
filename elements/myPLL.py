import numpy as np

import scipy.signal as signal
import matplotlib.pyplot as plt


class PLL:
    def __init__(self, Kp, Ki, Kd, sample_rate, tuning_parameter=1.0, cutoff_frequency=0.1):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.sample_rate = sample_rate
        self.phase_error = 0
        self.integral = 0
        self.previous_v_out = 0
        self.tuning_parameter = tuning_parameter
        self.cutoff_frequency = cutoff_frequency

        self.a1 = 1 / (1 + cutoff_frequency / sample_rate)
        self.b0 = cutoff_frequency / sample_rate / (1 + cutoff_frequency / sample_rate)
    
    def __phase_detector(self, v_in):
        return self.previous_v_out * v_in
    

    def __low_pass_filter(self, v_in):
        return self.a1 * self.previous_v_out + self.b0 * v_in

    def update(self, v_in):
        phase_error = self.__phase_detector(v_in)
        self.integral += phase_error
        v_out = self.Kp * phase_error + self.Ki * self.integral + self.Kd * (phase_error - self.previous_v_out)
        self.previous_v_out = v_out
        return v_out

    def set_tuning_parameter(self, tuning_parameter):
        self.tuning_parameter = tuning_parameter

    def get_tuning_parameter(self):
        return self.tuning_parameter

    def set_cutoff_frequency(self, cutoff_frequency):
        self.cutoff_frequency = cutoff_frequency

    def get_cutoff_frequency(self):
        return self.cutoff_frequency