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

class calibrate(gr.basic_block):
    """
    docstring for block calibrate
    """
    def __init__(self, val):
        gr.basic_block.__init__(self,
            name="calibrate",
            in_sig=[],
            out_sig=[])
        self.val = val
        self.minimum = val
        self.maximum = val + 2*numpy.pi

        #register message ports
        self.message_port_register_in(pmt.string_to_symbol("in"))
        self.message_port_register_out(pmt.string_to_symbol("out"))
        self.set_msg_handler(pmt.string_to_symbol("in"), self.msg_handler)
        self.last_val = 0
        self.subtract = 0

    def set_val(self, val):
        self.val = val

    def cal(self, cal):
        if cal==1: #do the calibration here
            #self.minimum = self.val
            #self.maximum = self.val + 2*numpy.pi

            self.subtract = self.last_val - self.val
            
            print "self.subtract: ", self.subtract
            #print "self.minimum: ", self.minimum
            #print "self.maximum: ", self.maximum

    def msg_handler(self, p):


        length = pmt.length(p)
        

        #iterate over all elements
        for i in range(0,length):
           element = pmt.nth(i, p)

           key = pmt.nth(0, element)
           value = pmt.nth(1, element)


            #when we found the phase key
           if str(key) == 'phase':
                #extract value from pmt
                #print "-------------------------------"
                #print "value = ", value
                #print "self.subtract = ", self.subtract
                value = pmt.f32vector_elements(value)[0]
                self.last_val = value

                value = value - self.subtract
                while value < -numpy.pi:
                    value = value + numpy.pi
                while value > numpy.pi:
                    value = value - numpy.pi


                #put it in the right interval
                #while value < self.minimum:
                    #value = value + 2*numpy.pi
                #while value > self.maximum:
                    #value = value - 2*numpy.pi

                #print "resulting phase = ", value

                outvalue = pmt.make_f32vector(1, value)
                output = pmt.list2(pmt.string_to_symbol(str(key)), outvalue)
                #output = pmt.list_add(outpmt, pmt.list2(pmt.string_to_symbol(str(key)), output))
                #print "-------------------------------"
                #print "if path, output = ", output

           else:
                output = element
                #print "else path, output = ", output


           #output = pmt.nth(1, element)

           if i==0:
               outpmt = pmt.list1(output)
           else:
               outpmt = pmt.list_add(outpmt, output)


        self.message_port_pub(pmt.string_to_symbol("out"), outpmt)







