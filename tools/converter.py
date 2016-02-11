import serial
import argparse
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
        if not self.ser.isOpen():
            print 'ALERT: Serial port not open'

        self.run_input_thread = True
        self.input_thread = threading.Thread(target=self.monitor_input)
        self.input_thread.daemon = True
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

        print 'TX ON?'
        print self.get_tx_on()
        print 'RX ON?'
        print self.get_rx_on()
        print 'TX FREQ?'
        print self.get_tx_freq()
        print 'RX FREQ?'
        print self.get_rx_freq()
        print 'TX GAIN?'
        print self.get_tx_gain()

        print '#####################################'

    def get_tx_gain(self):
        self.send_command('CONV:TXPS?')
        return self.curr_ans

    def set_tx_gain(self, gain_str):
        self.send_command('CONV:TXPS ' + gain_str)

    def set_tx_freq(self, freq):
        hex_str = self.get_freq_hex_string(freq)
        print 'freq hex string = ' + hex_str
        self.send_command('SYNT:TXFR '+hex_str)

    def set_rx_freq(self, freq):
        hex_str = self.get_freq_hex_string(freq)
        print 'freq hex string = ' + hex_str
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

    def get_rx_on(self):
        self.send_command('CONV:RXON?')
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
        self.operation_in_progress = True
        self.ser.write(command+'\r\n')
        while self.operation_in_progress:
            time.sleep(1)

    def monitor_input(self):
        curr_line = ''
        while self.run_input_thread and self.ser.isOpen():
            try:
                curr_byte = self.ser.read(1)
                if curr_byte != '':
                    if curr_byte != '\n' and curr_byte != '\r':
                        curr_line += str(curr_byte)
                    else:
                        #print 'got eol'
                        if self.operation_in_progress:
                            if curr_line == 'NACK':
                                print 'ERROR: NACK'
                                self.ser.close()
                                break
                            self.operation_in_progress = False
                            self.curr_ans = curr_line
                            curr_line = ""
                else:
                    time.sleep(0.1)
            except:
                break

if __name__ == '__main__':
    pars = argparse.ArgumentParser()
    pars.add_argument('mode', help='set, list')
    pars.add_argument('-com', help='com port')
    pars.add_argument('-tx_lo', type=float)
    pars.add_argument('-rx_lo', type=float)
    pars.add_argument('-tx_gain')

    args = pars.parse_args()

    com_port = '/dev/ttyACM0'
    if args.com != None:
        com_port = args.com

    if args.mode == 'show':
        cc = converter(com_port)
        cc.open()
        cc.print_info()
        cc.close()

    if args.mode == 'set':
        cc = converter(com_port)
        cc.open()
        cc.set_tx_on(False)
        cc.set_rx_on(False)

        if args.tx_lo != None:
            cc.set_tx_freq(args.tx_lo)
            cc.set_tx_on(True)
        if args.rx_lo != None:
            cc.set_rx_freq(args.rx_lo)
            cc.set_rx_on(True)
        if args.tx_gain != None:
            print 'Setting Tx Gain = ' + str(args.tx_gain)
            cc.set_tx_gain(args.tx_gain)

        cc.store()
        cc.close()

