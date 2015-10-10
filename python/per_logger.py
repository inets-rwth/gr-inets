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

import numpy
from gnuradio import gr
from gnuradio import digital
import pmt
import string
import time
import csv

class per_logger(gr.basic_block):
    """
    docstring for block per_logger
    """
    def __init__(self):
        gr.basic_block.__init__(self,
            name="per_logger",
            in_sig=[],
            out_sig=[])

        self.message_port_register_in(pmt.intern('payload_in'))
        self.set_msg_handler(pmt.intern('payload_in'), self.handle_payload_message)
        self.message_port_register_in(pmt.intern('snr_in'))
        self.set_msg_handler(pmt.intern('snr_in'), self.handle_snr_message)

        self.csv_fields = ['Timestamp', 'OK', 'SNR']
        curr_time = time.strftime("%d.%m.%Y-%H-%M-%S")
        self.log_file_name = '/home/inets/per_log.csv'

        with open(self.log_file_name,'w') as log_file:
            csv_writer = csv.DictWriter(log_file, fieldnames=self.csv_fields)
            csv_writer.writeheader()

        self.log = False
        self.curr_snr = 0
        self.num_rec_packets = 0

        numpy.random.seed(0)
        self.payload = numpy.random.randint(0, 256, 500) #500 byte payload
        print '[per_logger] using payload:'
        print self.payload

    def handle_payload_message(self, msg_pmt):
        if not self.log:
            return

        meta = pmt.to_python(pmt.car(msg_pmt))
        msg = pmt.cdr(msg_pmt)
        print '[per_logger] got message'
        msg_data = pmt.u8vector_elements(msg)
        print msg_data

        msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])

        self.num_rec_packets += 1
        self.avg_snr += self.curr_snr
        ok = True

        if msg_data != self.payload:
            self.num_packet_errors += 1
            print 'Packet error'
            ok = False

        self.log_packet(ok, self.curr_snr)

        if self.num_rec_packets == 1024:
            snr = sefl.avg_snr / self.num_rec_packets
            self.num_rec_packets = 0
            self.avg_snr = 0
            self.log = False

    def log_packet(self, ok, snr):
        with open(self.log_file_name, 'a') as log_file:
            csv_writer = csv.DictWriter(log_file, fieldnames=self.csv_fields)
            csv_writer.writerow({'Timestamp' : time.time(),
                    'OK' : ok,
                    'SNR' : snr})

    def handle_snr_message(self, msg_pmt):
        snr_pmt = pmt.to_python(msg)
        snr = float(snr_pmt)
        self.curr_snr = snr
        self.log = True

