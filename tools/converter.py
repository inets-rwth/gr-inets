import serial
import sys
import threading
import time

class converter:

    LO_STEP = 250e3

    def __init__(self, com):
        self.com_port = com
        self.ser = serial.Serial()
        self.ser.baudrate = 921600 
        self.ser.port = self.com_port
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 0
        self.operation_in_progress = False
        self.curr_ans = ''

    def open(self):
        self.ser.open()
        self.run_input_thread = True
        self.input_thread = threading.Thread(target=self.monitor_input)
        self.input_thread.daemon = False
        self.input_thread.start()

    def close(self):
        while self.operation_in_progress:
            time.sleep(1)
        print 'closing connection'
        self.ser.close()
        self.run_input_thread = False
        if self.input_thread.isAlive():
            print 'joining thread'
            self.input_thread.join()
            print 'thread exited'


    def print_info(self):
        print '############### Info ################'
        self.send_command('CONV:VERS?')
        self.send_command('VERS?')
        
        print self.get_tx_on()
        print self.get_rx_on()
        print self.get_tx_freq()
        print self.get_rx_freq()

        print '#####################################\r\n'


    def set_tx_freq(self, freq):
        hex_str = self.get_freq_hex_string(freq)
        self.send_command('SYNT:TXFR '+hex_str)

    def set_rx_freq(self, freq):
        hex_str = self.get_freq_hex_string(freq)
        self.send_command('SYNT:RXFR '+hex_str)

    def get_tx_freq(self):
        self.send_command('SYNT:TXFR?')
        return self.get_freq_from_hex(self.curr_ans) / 1e9

    def get_rx_freq(self):
        self.send_command('SYNT:RXFR?')
        return self.get_freq_from_hex(self.curr_ans) / 1e9

    def get_tx_on(self):
        self.send_command('CONV:TXON?')
        if self.curr_ans == 'ON':
            return True
        if self.curr_ans == 'OFF':
            return False

    def set_rx_on(self, on):
        if on:
            self.send_command('CONV:RXON ON')
            self.send_command('SYNT:RXON ON')
        else:
            self.send_command('CONV:RXON OFF')
            self.send_command('SYNT:RXON OFF')

    def set_tx_on(self, on):
        if on:
            self.send_command('CONV:TXON ON')
            self.send_command('SYNT:TXON ON')
        else:
            self.send_command('CONV:TXON OFF')
            self.send_command('SYNT:TXON OFF')

    def get_tx_on(self):
        self.send_command('CONV:TXON?')
        if self.curr_ans == 'ON':
            return True
        if self.curr_ans == 'OFF':
            return False

    def get_rx_on(self):
        self.send_command('CONV:RXON?')
        if self.curr_ans == 'ON':
            return True
        if self.curr_ans == 'OFF':
            return False

    def store(self):
        self.send_command('CONV:STOR')
        self.send_command('SYNT:STOR')

    def get_freq_hex_string(self, freq):
        num_steps =  freq // self.LO_STEP
        actual_freq = num_steps * self.LO_STEP
        print 'actual freq = ' + str(actual_freq)
        hex_string = hex(int(num_steps))
        hex_string = hex_string[2:] # remove '0x' prefix

        if len(hex_string) == 5:
            hex_string = '0' + hex_string
        
        return hex_string

    def get_freq_from_hex(self, hex_str):
        hex_str = hex_str.replace(" ","")
        num = int(hex_str, 16)
        num = num * self.LO_STEP
        return int(num)

    def send_command(self, command): 
        print 'command: ' + command
        self.operation_in_progress = True
        self.ser.write(command+'\r\n')
        while self.operation_in_progress:
            time.sleep(1)

    def monitor_input(self):
        curr_line = ''
        while self.run_input_thread and self.ser.isOpen():
            try:    
                 curr_byte = self.ser.read()
                 if curr_byte != '':
                     if curr_byte != '\n' and curr_byte != '\r':
                         curr_line += str(curr_byte)
                     if curr_byte == '\r':
                         print curr_line
                         self.operation_in_progress = False
                         self.curr_ans = curr_line
                         curr_line = ""
            except:
                break

        print 'exiting input thread'


if __name__ == '__main__':
    cc = converter('/dev/ttyACM0')
    cc.open()

    cc.print_info()
#   cc.set_tx_freq(77e9)
#   cc.set_rx_freq(87e9)
#   cc.set_tx_on(True)
#   cc.set_rx_on(True)
#   cc.store()

    cc.close()
