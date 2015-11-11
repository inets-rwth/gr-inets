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

class packetizer_python(gr.basic_block):
  """
  docstring for block packetizer_python
  """
  def __init__(self):
    gr.basic_block.__init__(self, name="packetizer_python", in_sig=[], out_sig=[])
    self.message_port_register_in(pmt.intern('in'))
    self.message_port_register_out(pmt.intern('out'))
    self.set_msg_handler(pmt.intern('in'), self.handle_message)
    #Max MTU size in bytes the PHY is able to handle
    self.max_mtu_size = 250

  def handle_message(self, msg_pmt):
    meta = pmt.to_python(pmt.car(msg_pmt))
    msg = pmt.cdr(msg_pmt)
    if not pmt.is_u8vector(msg):
        print "ERROR wrong pmt format"
        return


    msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])

    num_mtus = (len(msg_str) // self.max_mtu_size)
    if len(msg_str) % self.max_mtu_size != 0:
      num_mtus = num_mtus + 1
      
    #Fragment packet?
    
    mtu_index_start = 0
    mtu_index_end = 0
    last = False
    frag = False
    frag_index = 0
    
    if num_mtus > 1:
      frag = True;
      
    for i in range(num_mtus):
      
      if (len(msg_str) - mtu_index_start) > self.max_mtu_size:
        mtu_index_end = mtu_index_start + self.max_mtu_size
      else:
        mtu_index_end = len(msg_str)
        last = True

      fragment_str = msg_str[mtu_index_start:mtu_index_end]
     
      packet = self.build_packet(fragment_str, frag, last, i)
      
      mtu_index_start += self.max_mtu_size

      # Create an empty PMT (contains only spaces):
      send_pmt = pmt.make_u8vector(len(packet), ord(' '))
      # Copy all characters to the u8vector:
      for i in range(len(packet)):
        pmt.u8vector_set(send_pmt, i, ord(packet[i]))
      # Send the message:
      self.message_port_pub(pmt.intern('out'),
        pmt.cons(pmt.PMT_NIL, send_pmt))

  def build_packet(self, payload_str, frag, last_frag, frag_index): 
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
      #print 'generating frag byte: ', ord(hdr_str)
    packet_str = hdr_str + payload_str
    packet_str = digital.crc.gen_and_append_crc32(packet_str)
    packet_str = digital.packet_utils.whiten(packet_str, 0)
    #print 'building fagment: hdr byte = %d payload len = %d total len = %d' % (ord(hdr_str), len(payload_str) , len(packet_str))
    return packet_str

