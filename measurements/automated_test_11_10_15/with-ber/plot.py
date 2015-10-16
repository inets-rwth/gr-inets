import matplotlib
import os
import numpy as np
from numpy import genfromtxt
import matplotlib.pyplot as plt
import scipy.special

#for complex input signals: 10log(2) = 3
# (E_b / N_0)(dB)  = SNR(dB) + 10*log(1.5*T_sym/T_samp) - 10log(k)
   
qpsk_data = genfromtxt('per_stats_log_qpsk.csv', delimiter=',', skip_header=1)
bpsk_data = genfromtxt('per_stats_log_bpsk.csv', delimiter=',', skip_header=1)
bpsk_data_theory = []
qpsk_data_theory = []

for snr in bpsk_data[:,1]:
    bpsk_data_theory.append(0.5*scipy.special.erfc(np.sqrt(0.5*np.power(10,0.1*(snr+6-0)))))

for snr in qpsk_data[:,1]:
    qpsk_data_theory.append(0.5*scipy.special.erfc(np.sqrt(0.5*np.power(10,0.1*(snr+6-3)))))

plt.semilogy(bpsk_data[:,1], bpsk_data[:, 3], 'bo', ms=8.0)
plt.semilogy(bpsk_data[:,1], bpsk_data_theory, 'bx', ms=8.0)

plt.semilogy(qpsk_data[:,1], qpsk_data[:, 3], 'ro', ms=8.0)
plt.semilogy(qpsk_data[:,1], qpsk_data_theory, 'rx', ms=8.0)

plt.xlabel('SNR [dB]', fontsize=16)
plt.ylabel('BER', fontsize=16)
plt.legend(['BPSK', 'BPSK Theor.', 'QPSK', 'QPSK Theor.'],'lower left')
plt.grid(True)
plt.hold(True)

plt.savefig('ber_snr.pdf', dpi=3600, bbox_inches='tight')
