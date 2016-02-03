import serial
import threading
import time
import sys

class control:
    def __init__(self, com_port_name):
        self.curr_pos = 0
        self.com_port = com_port_name
        self.serial_port = serial.Serial()
        self.serial_port.baudrate = 19200
        self.serial_port.port = self.com_port
        self.serial_port.bytesize = serial.EIGHTBITS
        self.serial_port.parity = serial.PARITY_NONE
        self.serial_port.stopbits = serial.STOPBITS_ONE
        self.serial_port.timeout = 0
        self.operation_in_progress = False

    def open(self):
        self.serial_port.open()
        self.run_input_thread = True
        self.input_thread = threading.Thread(target=self.monitor_input)
        self.input_thread.start()

    def close(self):
        while self.operation_in_progress:
            time.sleep(1)
        print 'closing connection'
        self.serial_port.close()
        self.run_input_thread = False
        if self.input_thread.isAlive():
            print 'joining thread'
            self.input_thread.join()
            print 'thread exited'

    def move_to(self, pos_deg):
        diff = pos_deg - self.curr_pos
        self.curr_pos = pos_deg
        self.operation_in_progress = True
        if diff == 0:
            return
        print "moving: " + str(int(diff))
        self.serial_port.write(str(int(diff))+"\r\n")
        #while self.operation_in_progress:
            #time.sleep(0.1)

    def monitor_input(self):
        curr_line = ''
        while self.run_input_thread and self.serial_port.isOpen():
            try:
                 curr_byte = self.serial_port.read()
                 if curr_byte != '':
                     if curr_byte != '\n' and curr_byte != '\r':
                         curr_line += str(curr_byte)
                     if curr_byte == '\r':
                         print curr_line
                         if curr_line == 'done':
                             self.operation_in_progress = False
                         curr_line = ""
            except:
                self.operation_in_progress = False
                break

        print 'exiting input thread'

if __name__ == "__main__":
    pos = sys.argv[1]

    con = control("/dev/ttyACM0")
    con.open()
    con.move_to(int(pos))
    con.close()

