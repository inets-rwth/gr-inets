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
import re
import pmt

class source(gr.sync_block):

    """
    docstring for block source
    """
    def __init__(self, filename):
        gr.sync_block.__init__(self,
            name="source",
            in_sig=None,
            out_sig=[numpy.complex64])

        self.filename=filename
        self.f = open(self.filename, "r")

    #files are in the following format:
    #tag <offset> <source> <key> <value>
    #stream <real> <imag>
    #tags for offset i always precede stream data for offset i

    def work(self, input_items, output_items):

        #print "Block work function called: ", len(output_items[0])

        out = output_items[0]

        #print "Need to generate ", len(out), " items"


        i=0
        while i<len(out):
            line = self.f.readline()
            line.rstrip()
            #print "Read the following line: ", line
            ss = re.split(" ", line)

            out[i] = i
            #print "Starting loop iteration ",i,"/",len(out)
            if(ss[0]=="stream"):
                real = ss[1]
                imag = ss[2].replace('\n', '')
                #print "complex number(",real,",",imag,")"
                #out[i] = complex(float(real), float(imag))
                out[i] = numpy.complex(float(real), float(imag))
                out[i] = numpy.complex64(out[i])
                #print out[i]
                #out[i] = numpy.complex64(float(real) + float(imag)*j)
                #print "generated item ", i, " of ", len(out)
                i=i+1

            elif(ss[0] == "tag"):
                #offset,source,key,value1,value2 = ss[1:]
                offset = ss[1]
                source = ss[2]
                key = ss[3]
                value1 = ss[4]
                #print "tag information: ",offset, source, key, value


                #we have a tuple here (this is specific to the toolbox 
                #it looks like this now
                #ss[4]:  {0
                #ss[5]:  0.131072}
                if(value1[0] == '{'):
                    value2 = ss[5]

                    value1 = long(value1[1:])
                    value2 = float(value2[:-2])

                    #print "ss[4]: ", ss[4]
                    #print "ss[5]: ", ss[5]
                    
                    #print "value1: ", value1
                    #print "value2: ", value2
                    _value = pmt.make_tuple(
                            pmt.from_long(value1),
                            pmt.from_float(value2)
                            )
                else:
                    value1 = value1[:-1]
                    counter=0
                    #for i in value1:
                        #print counter, ": ", i
                        #counter=counter+1
                    #print "value1: ", value1
                    value1 = long(value1)
                    #print "value1: ", value1
                    _value = pmt.from_long(value1)


                
                #add tag to stream
                self.add_item_tag(0,                 # output
                        int(offset),                 # offset
                        pmt.string_to_symbol(key),   # key
                        _value,   # value
                        pmt.string_to_symbol(source) # source
                        )

            #break

            ##out[:] = 1+2j



        #print "returning a length of ",len(output_items[0])
        return len(output_items[0])






