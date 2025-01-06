
from elements.biquad_module import Biquad
import matplotlib.pyplot as plt
import numpy as np

import random, re

def ntrp(x,xa,xb,ya,yb):
  return (x-xa) * (yb-ya) / (xb-xa) + ya

sample_rate = 40000.0

cf = 2000
dev = 140
start_f = cf - dev
end_f = cf + dev
modi = 0

pll_integral = 0
old_ref = 0
pll_cf = 2000
pll_loop_gain = .05
ref_sig = 0

invsqr2 = 1.0 / np.sqrt(2.0)

loop_lowpass = Biquad(Biquad.LOWPASS,100,sample_rate,invsqr2)

output_lowpass = Biquad(Biquad.LOWPASS,10,sample_rate,invsqr2)

lock_lowpass = Biquad(Biquad.LOWPASS,10,sample_rate,invsqr2)

fa = []
da = []
db = []
dc = []

noise_level = 1

dur = 4

for n in range(int(sample_rate * dur)):
  t = n / sample_rate
  
  # BEGIN test signal block
  sweep_freq = ntrp(t,0,dur,start_f,end_f)
  fa.append(sweep_freq)
  modi += (sweep_freq-cf) / (cf * sample_rate)
  test_sig = np.cos(2 * np.pi * cf * (t + modi))
  noise = random.random() * 2 - 1
  test_sig += noise * noise_level
  # END test signal block
  
  # BEGIN PLL block
  pll_loop_control = test_sig * ref_sig * pll_loop_gain # phase detector
  pll_loop_control = loop_lowpass(pll_loop_control) # loop low-pass filter
  output = output_lowpass(pll_loop_control) # output low-pass filter
  pll_integral += pll_loop_control / sample_rate # FM integral
  ref_sig = np.cos(2 * np.pi * pll_cf * (t + pll_integral)) # reference signal
  quad_ref = (ref_sig-old_ref) * sample_rate / (2 * np.pi * pll_cf) # quadrature reference
  old_ref = ref_sig
  pll_lock = lock_lowpass(-quad_ref * test_sig) # lock sensor
  logic_lock = (0,1)[pll_lock > 0.1] # logical lock
  # END PLL block
  
  da.append(output * 32)
  db.append(pll_lock * 2)
  dc.append(logic_lock)

plt.plot(fa,da, label='PLL transfer function')
plt.plot(fa,db, label='Quadrature detector')
plt.plot(fa,dc, label='Lock Indicator')
plt.legend(loc='lower right')
plt.setp(plt.gca().get_legend().get_texts(),fontsize=9)
plt.grid(True)
plt.ylim(-1.2,1.2)
plt.gcf().set_size_inches(5,3.75)

plt.savefig('pll.png')

plt.show()
