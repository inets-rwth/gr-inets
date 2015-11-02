import socket
import time

IP_TRANSCEIVER = '127.0.0.1'
PORT_TRANSCEIVER = 52002

class radar_client:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.sock.connect((IP_TRANSCEIVER, PORT_TRANSCEIVER))

    def warn(self, direction):
        self.sock.sendto("ALERT "+str(direction),(IP_TRANSCEIVER, PORT_TRANSCEIVER))

    def close(self):
        pass#self.sock.close()


if __name__ == "__main__":
    rad = radar_client()
#    while True:
    rad.warn(20) #20 deg -> left
    time.sleep(20)

    rad.close()
