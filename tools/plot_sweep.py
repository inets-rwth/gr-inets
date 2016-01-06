import matplotlib.pyplot as plt
import numpy as np
from numpy import genfromtxt

data = np.genfromtxt('RSSI.csv', delimiter=',', skip_header=1)
p_rx_max = dict()
for i in range(0, len(data)):
  if data[i,0] not in p_rx_max:
    p_rx_max[data[i,0]] = data[i,2]
  else:
    if p_rx_max[data[i,0]] < data[i,2]:
      p_rx_max[data[i,0]] = data[i,2]

plt.subplot(polar=True)

for key in p_rx_max:
  plt.plot((key / 360.0) * 2.0 * np.pi,p_rx_max[key],'bo')


plt.show()
