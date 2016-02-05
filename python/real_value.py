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
import pmt
import os
import time

class real_value(gr.basic_block):
    """
    docstring for block real_value
    """
    def __init__(self):
        gr.basic_block.__init__(self,
            name="real_value",
            in_sig=[],
            out_sig=[])


        #register message ports
        self.message_port_register_in(pmt.string_to_symbol("in"))
        self.message_port_register_out(pmt.string_to_symbol("out"))
        self.set_msg_handler(pmt.string_to_symbol("in"), self.msg_handler)

    def msg_handler(self, p):
        #os.system("pwd")
        #time.sleep(1)
        fd = open("real_range", "r")

        s = fd.readline()
        fd.close()

        s = float(s)

        p = pmt.list_add(p, pmt.list2(pmt.string_to_symbol("real_range"), pmt.make_f32vector(1, s)))

        if(s>-500.0):
            self.message_port_pub(pmt.string_to_symbol("out"), p)
    
