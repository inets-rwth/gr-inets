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
    self.wait_for_frag = False    
    self.last_frag_index = 0
    self.packet_buffer = ''
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
      print '#######################################################'
      print '################## ERROR: Bad CRC #####################'
      print '#######################################################'
      return
    if ok:
      #print 'CRC check OK'
      frag_byte = ord(packet[0])  
      frag_index = frag_byte >> 2
      #print 'Fragmentation byte: ', frag_byte 
      if frag_byte & 0x01 == 1 :
        #print "got packet fragment. Index = %d. Last index = %d" % (frag_index, self.last_frag_index)
        self.last_frag_index = frag_index
        if frag_byte & 0x02 == 0 :
          self.wait_for_frag = True
          #strip fragmentation control and append payload
          self.packet_buffer += packet[1:] 
          return
        else:
          #last part of fragmented packet
          #print 'got last fragment of packet. Index = ', frag_index
          self.wait_for_frag = False
          
          self.packet_buffer += packet[1:]
          packet = self.packet_buffer
          self.packet_buffer = ''
      else:
        #packet is not fragmented at all.
        #just strip off frag byte and hand it off
        packet = packet[1:]
        self.wait_for_frag = False

      if not self.wait_for_frag:
        # Create an empty PMT (contains only spaces):
        send_pmt = pmt.make_u8vector(len(packet), ord(' '))
        # Copy all characters to the u8vector:
        for i in range(len(packet)):
          pmt.u8vector_set(send_pmt, i, ord(packet[i]))
        # Send the message:
        self.message_port_pub(pmt.intern('out'),
          pmt.cons(pmt.PMT_NIL, send_pmt))

