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


class message_print(gr.basic_block):
    """
    docstring for block message_print
    """
    def __init__(self, key, filename):
        gr.basic_block.__init__(self,
            name="message_print",
            in_sig=[],
            out_sig=[])


        self.key = key
        self.filename=filename
        self.counter=0

        #delete the contents of the file
        self.fdout = open(filename, "w")
        self.fdout.close()
        
        if key != "all":
            if filename != "":
                self.fdout = open(filename, "w")
                for i in self.key:
                    self.fdout.write(i + ",")
                self.fdout.write("\n")
            self.fdout.close()

        #register message ports
        self.message_port_register_in(pmt.string_to_symbol("in"))
        self.set_msg_handler(pmt.string_to_symbol("in"), self.msg_handler)


    def msg_handler(self, p):

        if self.filename != "":
            self.fdout = open(self.filename, "a")

        length = pmt.length(p)

        if self.key == "all":
            #if all keys are printed, they need however be printed once above
            if self.counter == 0:
                for i in range(0, length):
                    element = pmt.nth(i, p)
                    current_key = str(pmt.nth(0, element))
                    self.fdout.write(current_key + ",")
                self.fdout.write("\n")
                self.counter=1

            #print all
            for i in range(0, length):
                element = pmt.nth(i, p)
                current_key = str(pmt.nth(0, element))
                current_value = pmt.nth(1, element)

                if current_key=="rx_time":
                    self.fdout.write("[" + str(pmt.tuple_ref(current_value, 0)) + "|" + str(pmt.tuple_ref(current_value, 1)) + "],")
                else:
                    self.fdout.write(str(pmt.f32vector_elements(current_value)[0]) + ",")

        else:
            #print all values that correspond to keys
            for key in self.key:
                for i in range(0, length):
                    element = pmt.nth(i, p)
                    current_key = str(pmt.nth(0, element))
                    current_value = pmt.nth(1, element)

                    if current_key == key:
                        if key=="rx_time":
                            self.fdout.write("[" + str(pmt.tuple_ref(current_value, 0)) + "|" + str(pmt.tuple_ref(current_value, 1)) + "],")
                        else:
                            self.fdout.write(str(pmt.f32vector_elements(current_value)[0]) + ",")

        self.fdout.write("\n")
        self.fdout.close()
















