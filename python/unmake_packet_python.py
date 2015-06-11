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
import pmt
import numpy
from gnuradio import gr
from gnuradio import digital

class unmake_packet_python(gr.basic_block):
    """
    docstring for block unmake_packet_python
    """
    def __init__(self):
        gr.basic_block.__init__(self,
            name="unmake_packet_python",
            in_sig=[],
            out_sig=[])
        
        self.message_port_register_in(pmt.intern('in'))
        self.message_port_register_out(pmt.intern('out'))
        self.set_msg_handler(pmt.intern('in'), self.handle_message)
    def handle_message(self, msg_pmt):
        meta = pmt.to_python(pmt.car(msg_pmt))
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
          print "ERROR wrong pmt format"
          return
        msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])
        packet = digital.packet_utils.dewhiten(msg_str, 0)
        (ok, packet) = digital.crc.check_crc32(packet)
        if not ok:
          print '################## ERROR: Bad CRC #####################'

        # Create an empty PMT (contains only spaces):
        send_pmt = pmt.make_u8vector(len(packet), ord(' '))
        # Copy all characters to the u8vector:
        for i in range(len(packet)):
            pmt.u8vector_set(send_pmt, i, ord(packet[i]))
        # Send the message:
        self.message_port_pub(pmt.intern('out'), pmt.cons(pmt.PMT_NIL, send_pmt))


    
