import serial
import sys

class converter_control:
    def __init__(self):
        print 'Enter Serial Port Name'
        self.serial_port_name = sys.stdin.readline()
        print 'Opening Serial Port', self.serial_port_name
        self.serial_port = serial.Serial(port=self.serial_port_name,
             baudrate=921600,
             bytesize=serial.EIGHTBITS,
             parity=serial.PARITY_NONE,
             stopbits=STOPBITS_ONE)

    def print_info(self)
        self.serial_port.write('VERS?')
        self.controller_version = ser.readline()
        self.serial_port.write('CONV:VERS?')
        self.converter_version = ser.readline()
        print 'Controller version = ' + self.controller_version + " Converter version = " + self.converter_version

    def configure(self, freq)
        print 'Enter desired freq.'
        

if __name__ == '__main__':
    cc = converter_control()
    cc.print_info()
