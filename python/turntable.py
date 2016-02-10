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
import sys
import control

class turntable(gr.basic_block):
    """
    docstring for block turntable
    """

    #i declare the class' variables here
    #angle
    
    def __init__(self, period, serial_port, degrees_per_trigger, stop):
        gr.basic_block.__init__(self,
            name="turntable",
            in_sig = [], # Input signature: 1 float at a time
            out_sig = []) # Output signature: 1 float at a time
        #register message ports
        self.message_port_register_in(pmt.string_to_symbol("in"))
        self.message_port_register_out(pmt.string_to_symbol("out"))
        
        self.set_msg_handler(pmt.string_to_symbol("in"), self.msg_handler)
        self.d_period = period
        self.d_serial_port = serial_port
        self.d_degrees_per_trigger = degrees_per_trigger
        self.d_stop = stop

        #accumulated angle
        self.angle=0

        #count up how many messages received
        self.counter=0

        print "Opening serial port: " + self.d_serial_port
        if self.d_serial_port != "":
            self.ttctrl = control.control(self.d_serial_port)
            self.ttctrl.open()

    def __del__(self):
        if self.d_serial_port != "":
            self.ttctrl.close()

    def msg_handler(self, p):
        self.counter = self.counter + 1
        if self.counter == self.d_period:
            self.counter = 0
            #print "turning ", self.d_degrees_per_trigger, " degrees"
            self.angle += self.d_degrees_per_trigger

            if self.d_serial_port != "":
                self.ttctrl.move_to(self.angle)

            if self.angle > self.d_stop:
                print "Stopping execution now"
                #sys.exit(0)

        ang_key = pmt.string_to_symbol("angle")
        ang_value = pmt.init_f32vector(1, [self.angle])
        ang_pack = pmt.list2(ang_key, ang_value)

        #m = pmt.list1(ang_pack)
        m = pmt.list4(pmt.nth(0, p), pmt.nth(1, p), pmt.nth(2, p), ang_pack)

        #pmt.list_add(m, p)
        self.message_port_pub(pmt.string_to_symbol("out"), m)














