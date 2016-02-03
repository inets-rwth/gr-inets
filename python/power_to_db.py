#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2016 <+YOU OR YOUR COMPANY+>.
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
import math
import pmt

class power_to_db(gr.basic_block):
    """
    docstring for block power_to_db
    """
    def __init__(self):
        gr.basic_block.__init__(self,
            name="power_to_db",
            in_sig=[],
            out_sig=[])

        #register message ports
        self.message_port_register_in(pmt.string_to_symbol("in"))
        self.message_port_register_out(pmt.string_to_symbol("out"))
        self.set_msg_handler(pmt.string_to_symbol("in"), self.msg_handler)


    def msg_handler(self, p):

        length = pmt.length(p)

        for i in range(0,length):
           element = pmt.nth(i, p)

           key = pmt.nth(0, element)
           value = pmt.nth(1, element)

           if str(key) == "power":
               output = pmt.f32vector_elements(value)[0]


               output = -10 * math.log(output, 10)           
               output = pmt.make_f32vector(1, output)

               if i==0:
                   outpmt = pmt.list1(pmt.list2(pmt.string_to_symbol(str(key) + "_dB"), output))
               else:
                   outpmt = pmt.list_add(outpmt, pmt.list2(pmt.string_to_symbol(str(key) + "_dB"), output))



           output = pmt.nth(1, element)

           if i==0:
               outpmt = pmt.list1(pmt.list2(key, output))
           else:
               outpmt = pmt.list_add(outpmt, pmt.list2(key, output))

       
        self.message_port_pub(pmt.string_to_symbol("out"), outpmt)
