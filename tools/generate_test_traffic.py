import numpy as np
import socket
import time

IP = "127.0.0.1"
PORT = 52001

np.random.seed(0)
payload = np.random.randint(0, 256, 500) #500 byte payload

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print len(payload)


while True:
	num = s.sendto(payload.tostring()[0::8], (IP,PORT))
	print 'send '+str(num)+' bytes'
	time.sleep(2)

