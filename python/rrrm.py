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

class rrrm(gr.basic_block):
    """
    docstring for block rrrm
    """
    STATE_RUN = 0
    STATE_WAIT_FOR_CHANNEL_SWITCH = 1

    def __init__(self):
        gr.basic_block.__init__(self,
            name="rrrm",
            in_sig=[],
            out_sig=[])

	self.message_port_register_in(pmt.intern('from_app'))
        self.message_port_register_out(pmt.intern('to_app'))
	self.message_port_register_in(pmt.intern('from_radar'))
        self.message_port_register_in(pmt.intern('from_ll'))
        self.message_port_register_out(pmt.intern('to_ll'))
        self.message_port_register_out(pmt.intern('to_antenna'))
        self.set_msg_handler(pmt.intern('from_app'), self.handle_app_message)
        self.set_msg_handler(pmt.intern('from_ll'), self.handle_ll_message)
        self.set_msg_handler(pmt.intern('from_radar'), self.handle_radar_message)
        self.app_queue = Queue.Queue()
        self.state = STATE_RUN


    def handle_app_message(self, msg_pmt):	
	if self.state == STATE_RUN:
	    self.message_port_pub(pmt.intern('to_ll'), msg_pmt)
	
	if self.state == STATE_WAIT_FOR_CHANNEL_SWITCH:
	    self.app_queue.put(msg_pmt)
	

    def handle_radar_message(self, msg_pmt):


    def handle_ll_message(self, msg_pmt):



