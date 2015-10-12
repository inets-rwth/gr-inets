import matplotlib
import os
import numpy as np
from numpy import genfromtxt
import matplotlib.pyplot as plt


snr = []
per = []
meas_points = []

curr_file = 'per_stats_log.csv'
data = genfromtxt(curr_file, delimiter=',', skip_header=1)
data2 = genfromtxt('per_stats_log_bpsk.csv', delimiter=',', skip_header=1)

#mean_ber = np.mean(data[:,2])
#mean_per = np.mean(data[:,3])
#snr.append(mean_snr)
#ber.append(mean_ber) 
           
#meas_points.append([mean_snr,mean_ber,mean_per])

#meas_points.sort(key=lambda point: point[1])
#data = np.array(meas_points)

#plt.figure(figsize=(128, 128))

plt.plot(data[:,1], data[:,2], 'ro', lw=20.0, ms=8.0)
plt.xlabel('SNR [dB]', fontsize=16)
plt.ylabel('PER', fontsize=16)
plt.title('PER vs SNR Measurement', fontsize=18)
plt.grid(True)
plt.hold(True)
plt.plot(data2[:,1], data2[:,2], 'bo', lw=20.0, ms=8.0)
#plt.show()
plt.savefig('test.svg', dpi=3600, bbox_inches='tight')
