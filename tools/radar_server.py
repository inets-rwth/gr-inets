import socket
import time

IP_TRANSCEIVER = '127.0.0.1'
PORT_TRANSCEIVER = 52003

class radar_client:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((IP_TRANSCEIVER, PORT_TRANSCEIVER))

    def warn(self, link_id):
        self.sock.send("ALERT "+str(link_id))

    def close(self):
        self.sock.close()


if __name__ == "__main__":
    rad = radar_client()
    while True:
        rad.warn(0)
        time.sleep(20)
    
    rad.close()
