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

#mean_ber = np.mean(data[:,2])
#mean_per = np.mean(data[:,3])
#snr.append(mean_snr)
#ber.append(mean_ber) 
           
#meas_points.append([mean_snr,mean_ber,mean_per])

#meas_points.sort(key=lambda point: point[1])
#data = np.array(meas_points)

#plt.figure(figsize=(128, 128))

plt.plot(data[:,1], data[:,2], 'ro')
plt.savefig('test.svg', dpi=3600, bbox_inches='tight')
