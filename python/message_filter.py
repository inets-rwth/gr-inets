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

class message_filter(gr.basic_block):
    """
    docstring for block message_filter
    """
    #$n, $k, $init, $filter_suffix, $min_suffix, $max_suffix, diff_suffix
    def __init__(self, n, k, init, filter_suffix, min_suffix, max_suffix, diff_suffix):
        gr.basic_block.__init__(self,
            name="message_filter",
            in_sig=[],
            out_sig=[])

        self.n = n
        self.kk = k
        self.init = init
        self.prev_values = []
        self.filter_suffix = filter_suffix
        self.min_suffix = min_suffix
        self.max_suffix = max_suffix
        self.diff_suffix

        if len(self.n) != len(self.kk) or len(self.n) != len(self.init):
            print "Error with parameters"



        #register message ports
        self.message_port_register_in(pmt.string_to_symbol("in"))
        self.message_port_register_out(pmt.string_to_symbol("out"))
        self.set_msg_handler(pmt.string_to_symbol("in"), self.msg_handler)

        for i in range(0, len(self.n)):
            self.prev_values.append(numpy.zeros(self.n[i]))


        print "len self.n: " + str(len(self.n))
        print "len self.kk: " + str(len(self.kk))
        print "len self.init: " + str(len(self.init))
        print "len self.prev_values: " + str(len(self.prev_values))


        print "self.n: ", self.n
        print "self.kk: ", self.kk
        print "self.init: ", self.init
        print "self.prev_values: ", self.prev_values


    def msg_handler(self, p):

        verbose = False

        length = pmt.length(p)
        
        if verbose:
            print "PMT contrains " + str(length) + " key/value pairs"

        for i in range(0,length):
           element = pmt.nth(i, p)

           key = pmt.nth(0, element)
           value = pmt.nth(1, element)

           if verbose:
               print "Key of " + str(i) + "th element: " + str(key)
               print "Value of " + str(i) + "th element: " + str(value)
               print

           found = False
           for j in range(0, len(self.n)):
               if str(key) == self.kk[j]:
                   found = True

                   if verbose:
                       print "found the key " + str(key)

                   #rotate the values, the latest one disappears
                   self.prev_values[j] = numpy.roll(self.prev_values[j], -1)

                   #set the vector accordingly
                   self.prev_values[j][-1] = pmt.f32vector_elements(value)[0]
                   

                   output = sum(self.prev_values[j])/len(self.prev_values[j])
                   output = pmt.make_f32vector(1, output)

                   if i==0:
                       outpmt = pmt.list1(pmt.list2(pmt.string_to_symbol(str(key) + "_filtered"), output))
                   else:
                       outpmt = pmt.list_add(outpmt, pmt.list2(pmt.string_to_symbol(str(key) + "_filtered"), output))



           output = pmt.nth(1, element)

           if i==0:
               outpmt = pmt.list1(pmt.list2(key, output))
           else:
               outpmt = pmt.list_add(outpmt, pmt.list2(key, output))

        if verbose:
            print


        #iterate over all keys
        for i in range(0, len(self.kk)):
            minimum = self.prev_values[i][0]
            maximum = self.prev_values[i][0]
            #iterate over all saved values
            for j in range(0, self.n[i]):
                if self.prev_values[i][j] < minimum:
                    minimum = self.prev_values[i][j]
                if self.prev_values[i][j] > maximum:
                    maximum = self.prev_values[i][j]
        
        #print out a min, diff, max for every key
        difference = maximum-minimum
        outpmt = pmt.list_add(outpmt, pmt.list2(pmt.string_to_symbol("min"), pmt.make_f32vector(1, minimum)))
        outpmt = pmt.list_add(outpmt, pmt.list2(pmt.string_to_symbol("max"), pmt.make_f32vector(1, maximum)))
        outpmt = pmt.list_add(outpmt, pmt.list2(pmt.string_to_symbol("diff"), pmt.make_f32vector(1, difference)))


        self.message_port_pub(pmt.string_to_symbol("out"), outpmt)
    



