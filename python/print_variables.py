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

class print_variables(gr.basic_block):
    """
    docstring for block print_variables
    """
    def __init__(self, names, values):
        gr.basic_block.__init__(self,
            name="print_variables",
            in_sig=[],
            out_sig=[])

        if len(names) != len(values):
            print "Error: lengths do not match"
        else:
            print "#################################"
            print "Summary of variables:"
            for i in range(0, len(names)):
                print "variable ", names[i], ": ", values[i]
            print "#################################"

