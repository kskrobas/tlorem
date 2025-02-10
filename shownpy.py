

import numpy as np
import matplotlib.pyplot as plt

from skued import gaussian
from skued import baseline_dwt


import pywt


plt.style.use('default')


s, signal = np.load("A11.npy")

s,signal=s[:2500],signal[:2500]
#sn=s[:200]

#####
baseline = baseline_dwt(signal, level = 6, max_iter = 150, 
                        wavelet = 'db20')

#####

plt.plot(s,baseline,'-r',label='baeline')
plt.plot(s,signal,'-b',label='origin')
plt.plot(s,signal-baseline,'-g',label='signal-background')
#plt.ylim([0,25])
#plt.xlim([500,1000])
plt.legend()