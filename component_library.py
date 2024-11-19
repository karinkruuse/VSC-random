import numpy as np
import matplotlib.pyplot as plt


"""Time base stuff"""
def mixer(signal1, signal2):
    return signal1*signal2

def photodetector(laser1, laser2):
    signal = laser1 + laser2
    I = np.real(signal)**2 + np.imag(signal)**2
    return I

def delay_line(signal, delay):
    return signal

def PLL(signal):
    return signal

"""Spectral stuff"""
def LP_filter(signal, f_cutoff):
    filtered_signal = f_cutoff/(signal + f_cutoff)
    return filtered_signal