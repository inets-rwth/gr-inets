#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2015 <+YOU OR YOUR COMPANY+>.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import string
import csv
import numpy
import time
import Queue
from gnuradio import gr
import pmt
from gnuradio import digital
import threading

class stop_and_wait_arq(gr.basic_block):
    """
    docstring for block stop_and_wait_arq
    """
    STATE_WAIT_FOR_ACK = 0
    STATE_IDLE = 1
    PACKET_TYPE_DATA = 0
    PACKET_TYPE_ACK = 1

    def __init__(self, ack_timeout, max_mtu_size, use_ack, stat_update_interval):
        gr.basic_block.__init__(self,
            name="stop_and_wait_arq",
            in_sig=[],
            out_sig=[])

        self.message_port_register_in(pmt.intern('from_app'))
        self.message_port_register_in(pmt.intern('snr'))
        self.message_port_register_out(pmt.intern('to_app'))
        self.message_port_register_in(pmt.intern('from_phy'))
        self.message_port_register_out(pmt.intern('to_phy'))
        self.set_msg_handler(pmt.intern('from_app'), self.handle_app_message)
        self.set_msg_handler(pmt.intern('from_phy'), self.handle_phy_message)
        self.set_msg_handler(pmt.intern('snr'), self.handle_snr_message)
        self.app_queue = Queue.Queue()
        self.state = self.STATE_IDLE
        self.last_tx_time = 0
        self.last_tx_packet = 0
        self.ack_timeout = ack_timeout #in fractional seconds
        self.max_mtu_size = max_mtu_size
        self.use_ack = use_ack
        self.wait_for_frag = False
        self.packet_buffer = []
        self.last_frag_index = 0
        self.tx_seq_num = 0
        self.thread_lock = threading.Lock()
        self.last_seq_num = -1

        #statistics
        self.total_num_rx_packets = 0
        self.total_num_rx_bits = 0
        self.total_num_rx_bit_errors = 0
        self.total_num_rx_wrong_bits = 0
        self.total_num_rx_bad_packets = 0
        self.total_num_rx_good_packets = 0
        self.snr_log = []
        self.curr_packet_len = 0
        self.curr_packet_seq = 0
        self.last_snr = 0

        self.num_ack_timeouts = 0
        self.num_acks_received = 0
        self.num_data_packets_send = 0

        self.rx_statistics_update_interval = stat_update_interval
        numpy.random.seed(0)
        self.test_data = numpy.random.randint(0, 256, 500)

        self.csv_fields = ['Timestamp', 'TX/RX' , 'Packet Type', 'Packet Length', 'Packet Seq #', 'SNR']
        curr_time = time.strftime("%d.%m.%Y-%H-%M-%S")

        self.log_file_name = '/home/inets/Documents/Log/stop_and_wait_arq_log.csv'

        with open(self.log_file_name,'w') as log_file:
            csv_writer = csv.DictWriter(log_file, fieldnames=self.csv_fields)
            csv_writer.writeheader()

    def handle_snr_message(self, msg):
        snr_pmt = pmt.to_python(msg)
        self.snr_log.append(float(snr_pmt))
        self.last_snr = float(snr_pmt)

    def handle_app_message(self, msg_pmt):
        with self.thread_lock:
          packets_str = self.fragment_packet(msg_pmt)
          for packet_str in packets_str:

            packet_str_total = chr(self.tx_seq_num)

            if self.tx_seq_num < 255:
              self.tx_seq_num = self.tx_seq_num + 1
            else:
              self.tx_seq_num = 0

            packet_str_total += chr(self.PACKET_TYPE_DATA)
            packet_str_total += packet_str

            send_pmt = pmt.make_u8vector(len(packet_str_total), ord(' '))
            for i in range(len(packet_str_total)):
              pmt.u8vector_set(send_pmt, i, ord(packet_str_total[i]))

            send_pmt = pmt.cons(pmt.PMT_NIL, send_pmt)
            self.app_queue.put(send_pmt)
            self.handle_queue()

    def handle_queue(self):
        if self.state == self.STATE_IDLE:
          if self.app_queue.empty() == False:
            self.last_tx_packet = self.app_queue.get()

            msg_str = "".join([chr(x) for x in pmt.u8vector_elements(pmt.cdr(self.last_tx_packet))])
            self.curr_packet_len = len(msg_str[3:])
            self.curr_packet_seq = ord(msg_str[0])

            self.last_tx_time = time.time()
            print '[stop_and_wait] :: Sending packet. Payload len: '+ str(self.curr_packet_len) +' Queue fill level = ', self.app_queue.qsize()

            if self.use_ack:
                self.state = self.STATE_WAIT_FOR_ACK

            self.num_data_packets_send += 1
            self.log_packet("TX", 0, self.curr_packet_len, self.curr_packet_seq, self.last_snr)
            self.message_port_pub(pmt.intern('to_phy'), self.last_tx_packet)

        elif self.state == self.STATE_WAIT_FOR_ACK:
          if (time.time() - self.last_tx_time) > self.ack_timeout:
            #retransmit
            print '[stop_and_wait] :: ACK timeout. Retransmitting'
            self.last_tx_time = time.time()
            self.num_ack_timeouts += 1
            self.num_data_packets_send += 1
            self.log_packet("TX", 0, self.curr_packet_len, self.curr_packet_seq, self.last_snr)
            self.message_port_pub(pmt.intern('to_phy'), self.last_tx_packet)

    def handle_phy_message(self, msg_pmt):
            meta = pmt.to_python(pmt.car(msg_pmt))
            msg = pmt.cdr(msg_pmt)
            msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])

            packet_str = msg_str

            #self.update_rx_statistics(packet_str[3:], self.test_data, True)

            packet_rx_seq_byte = ord(packet_str[0])
            packet_type_byte = ord(packet_str[1])
            packet_frag_byte = ord(packet_str[2])
            packet_str = packet_str[2:]

            drop = False
            if(self.last_seq_num == packet_rx_seq_byte):
                print '[stop_and_wait] :: WARN: duplicate packet. dropping...'
                drop = True

            if((self.last_seq_num + 1) != packet_rx_seq_byte):
                print '[stop_and_wait] :: WARN: out of seq packet'

            print '[stop_and_wait] :: Packet received. seq = ', packet_rx_seq_byte, ' type = ', packet_type_byte

            self.log_packet("RX", packet_type_byte, len(packet_str) - 1, packet_rx_seq_byte, self.last_snr) #remove frag hdr

            self.last_seq_num = packet_rx_seq_byte

            if packet_type_byte == self.PACKET_TYPE_DATA:
                if self.use_ack:
                    #send ACK packet
                    print '[stop_and_wait] :: Sending ACK'
                    ack_pdu = self.generate_ack_packet_pdu(packet_rx_seq_byte)
                    self.message_port_pub(pmt.intern('to_phy'), ack_pdu)

                if not drop:
                    #process fragment
                    self.process_fragment(packet_str)

            elif packet_type_byte == self.PACKET_TYPE_ACK:
                if packet_rx_seq_byte == self.curr_packet_seq:
                    #mark curr packet as transmitted
                    self.state = self.STATE_IDLE
                    self.num_acks_received += 1
                    self.handle_queue()

    def update_rx_statistics(self,  payload_str, test_data, crc_ok):

        if len(payload_str) != len(test_data):
            return

        self.total_num_rx_packets += 1
        self.total_num_rx_bits += len(payload_str) * 8

        num_bit_errors = 0
        if not crc_ok:
            self.total_num_rx_bad_packets += 1
            num_bit_errors = self.calculate_bit_errors(payload_str, test_data)
        else:
            self.total_num_rx_good_packets += 1

        self.total_num_rx_bit_errors += num_bit_errors

        if self.total_num_rx_packets == self.rx_statistics_update_interval:

            ber = self.total_num_rx_bit_errors / float(self.total_num_rx_bits)
            ber_per_bad_packet = 0
            if self.total_num_rx_bad_packets > 0:
                ber_per_bad_packet = self.total_num_rx_bit_errors / float(self.total_num_rx_bad_packets)
            per = self.total_num_rx_bad_packets / float(self.total_num_rx_packets)

            avg_snr = 0
            if self.snr_log > 0:
                snr_avg_len = 0
                for snr in self.snr_log:
                    avg_snr = avg_snr + snr
                    snr_avg_len += 1
                avg_snr = avg_snr / snr_avg_len

            self.write_rx_statistics(ber_per_bad_packet, ber, per, avg_snr)

            self.total_num_rx_packets = 0
            self.total_num_rx_bits = 0
            self.total_num_rx_bit_errors = 0
            self.total_num_rx_wrong_bits = 0
            self.total_num_rx_bad_packets = 0
            self.total_num_rx_good_packets = 0

    def log_packet(self, tx_rx, packet_type, packet_len, seq, snr):
        with open(self.log_file_name, 'a') as log_file:
            csv_writer = csv.DictWriter(log_file, fieldnames=self.csv_fields)
            csv_writer.writerow({'Timestamp' : time.time(),
                    'TX/RX' : tx_rx,
                    'Packet Type' : packet_type,
                    'Packet Length' : packet_len,
                    'Packet Seq #' : seq,
                    'SNR' : snr})

    def write_rx_statistics(self, ber_per_bad_packet, ber, per, snr):
        with open(self.log_file_name, 'a') as log_file:
            csv_writer = csv.DictWriter(log_file, fieldnames=self.csv_fields)
            csv_writer.writerow({'Date' : time.strftime("%d.%m.%Y-%H-%M-%S"),
                    'SNR' : "{0:.2f}".format(snr),
                    '#BER / Bad Packet' : "{0:.2f}".format(ber_per_bad_packet),
                    'BER' : "{0:.8f}".format(ber),
                    'PER' : "{0:.8f}".format(per)})

    def calculate_bit_errors(self, payload_str, test_data):
        data = []
        for x in payload_str:
            data.append(ord(x))

        bit_error_count = 0
        for i in range(0, len(data)):
            count = 0
            mask = 1
            for j in range(0, 8):
                if (data[i] & mask) != (test_data[i] & mask):
                    count += 1
                mask = mask << 1

            bit_error_count += count

        print '# bit errors = ', bit_error_count
        return bit_error_count

    def generate_ack_packet_pdu(self, seq_num):
        packet_str = chr(seq_num)
        packet_str += chr(self.PACKET_TYPE_ACK)
        packet_str += 'aaa'

        send_pmt = pmt.make_u8vector(len(packet_str), ord(' '))

        for i in range(len(packet_str)):
          pmt.u8vector_set(send_pmt, i, ord(packet_str[i]))

        return pmt.cons(pmt.PMT_NIL, send_pmt)

    def process_fragment(self, packet_str):
        frag_byte = ord(packet_str[0])
        frag_index = frag_byte >> 2
        if frag_byte & 0x01 == 1 :
          self.last_frag_index = frag_index
          if frag_byte & 0x02 == 0 :
            self.wait_for_frag = True
            self.packet_buffer += packet_str[1:]
            return
          else:
            self.wait_for_frag = False
            self.packet_buffer += packet_str[1:]
            packet_str = self.packet_buffer
            self.packet_buffer = ''
        else:
          packet_str = packet_str[1:]
          self.wait_for_frag = False
        if not self.wait_for_frag:
          send_pmt = pmt.make_u8vector(len(packet_str), ord(' '))
          for i in range(len(packet_str)):
            pmt.u8vector_set(send_pmt, i, ord(packet_str[i]))
          self.message_port_pub(pmt.intern('to_app'), pmt.cons(pmt.PMT_NIL, send_pmt))

    def fragment_packet(self, msg_pmt):
        meta = pmt.to_python(pmt.car(msg_pmt))
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print "ERROR wrong pmt format"
            return

        msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])
        print '[stop_and_wait] :: App message: Len: '+ str(len(msg_str))

        num_mtus = (len(msg_str) // self.max_mtu_size)
        if len(msg_str) % self.max_mtu_size != 0:
          num_mtus = num_mtus + 1

        mtu_index_start = 0
        mtu_index_end = 0
        last = False
        frag = False
        frag_index = 0

        packet_list = []

        if num_mtus > 1:
          frag = True;

        for i in range(num_mtus):

          if (len(msg_str) - mtu_index_start) > self.max_mtu_size:
            mtu_index_end = mtu_index_start + self.max_mtu_size
          else:
            mtu_index_end = len(msg_str)
            last = True

          fragment_str = msg_str[mtu_index_start:mtu_index_end]

          packet = self.add_frag_hdr(fragment_str, frag, last, i)

          mtu_index_start += self.max_mtu_size

          # Send the message:
          packet_list.append(packet)

        print '[stop_and_wait] :: #Fragments: '+ str(len(packet_list))

        return packet_list

    def add_frag_hdr(self, payload_str, frag, last_frag, frag_index):
        hdr_str = ''
        if not frag:
          hdr_str = '\x00'
        else:
          frag_byte = 0
          if not last_frag:
            frag_byte = 1 | frag_index << 2
          else:
            frag_byte = 3 | frag_index << 2
          hdr_str = chr(frag_byte)

        packet_str = hdr_str + payload_str
        return packet_str

    def get_packet_type(msg_pmt):
        meta = pmt.to_python(pmt.car(msg_pmt))
        msg = pmt.cdr(msg_pmt)
        data = pmt.u8vector_elements(msg)
        packet_type = data[0]


