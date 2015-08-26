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
import numpy
import time
import Queue
from gnuradio import gr
import pmt
import threading
import control

class rrrm(gr.basic_block):
    """
    docstring for block rrrm
    """
    STATE_RUN = 0
    STATE_WAIT_FOR_CHANNEL_SWITCH = 1

    PACKET_TYPE_DATA = 0
    PACKET_TYPE_SWITCH = 1
    PACKET_TYPE_SWITCH_ACCEPT = 2
    PACKET_TYPE_SWITCH_REJECT = 3

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
        self.state = self.STATE_RUN
        self.curr_channel_id = 0
        self.thread_lock = threading.Lock()        
        self.antenna_control = control.control("/dev/ttyACM0")
        self.antenna_control.open()

    def handle_app_message(self, msg_pmt):  
        with self.thread_lock:
            if self.state == self.STATE_RUN:
                print 'RRRM: App message. Run state. Forwarding message'
                self.send_data_message(msg_pmt)
        
            if self.state == self.STATE_WAIT_FOR_CHANNEL_SWITCH:
                print 'RRRM: App message. Switch state. Buffering message'
                self.app_queue.put(msg_pmt)
    
    def handle_radar_message(self, msg_pmt):
        with self.thread_lock:
            #msg_str = self.get_data_str_from_pmt(msg_pmt)
            #if msg_pmt == "ALERT": #come up with proper protocol here....
            print 'RRRM: radar alert. Initiating switch'
            self.state = self.STATE_WAIT_FOR_CHANNEL_SWITCH
            #calculate new path
            self.curr_channel_id = self.curr_channel_id + 1 
            self.send_switch_command(self.curr_channel_id)

    def send_switch_command(self, new_channel_id):
        packet_str = chr(self.PACKET_TYPE_SWITCH)
        packet_str = packet_str + chr(new_channel_id)
        send_pmt = self.get_pmt_from_data_str(packet_str)  
        self.message_port_pub(pmt.intern('to_ll'), send_pmt) 

    def send_switch_accept(self):
        packet_str = chr(self.PACKET_TYPE_SWITCH_ACCEPT)
        send_pmt = self.get_pmt_from_data_str(packet_str)  
        self.message_port_pub(pmt.intern('to_ll'), send_pmt) 

    def send_switch_reject(self):
        packet_str = chr(self.PACKET_TYPE_SWITCH_REJECT)
        send_pmt = self.get_pmt_from_data_str(packet_str)  
        self.message_port_pub(pmt.intern('to_ll'), send_pmt) 

    def send_data_message(self, msg_pmt): 
        msg_str = self.get_data_str_from_pmt(msg_pmt)
        msg_str = chr(self.PACKET_TYPE_DATA) + msg_str
        send_pmt = self.get_pmt_from_data_str(msg_str)
        self.message_port_pub(pmt.intern('to_ll'), send_pmt)

    def handle_ll_message(self, msg_pmt):
        with self.thread_lock:
            msg_str = self.get_data_str_from_pmt(msg_pmt)
            msg_type, msg_data = self.parse_rrrm_message(msg_str)
            if msg_type == self.PACKET_TYPE_DATA:
                print 'RRRM: forwarding incoming data packet'
                send_pmt = self.get_pmt_from_data_str(msg_data)
                self.message_port_pub(pmt.intern('to_app'), send_pmt)
            if msg_type == self.PACKET_TYPE_SWITCH:
                channel_id = ord(msg_data[0])
                print 'RRRM: Processing channel switch to ',channel_id
                self.antenna_control.move_to(90)
                self.send_switch_accept()
                self.state = self.STATE_WAIT_FOR_CHANNEL_SWITCH
            if msg_type == self.PACKET_TYPE_SWITCH_ACCEPT:
                print 'RRRM: Switch accept'
                #reposition antenna, start sending ping messages ???
                self.antenna_control.move_to(90)
                while not self.app_queue.empty():
                    self.send_data_message(self.app_queue.get())

                self.state = self.STATE_RUN
            
                    

    def parse_rrrm_message(self, message_str):
        message_type = ord(message_str[0])
        message_data = message_str[1:]
        return (message_type, message_data)        

    ################ PMT helper functions #####################
    def get_data_str_from_pmt(self, msg_pmt):
        meta = pmt.to_python(pmt.car(msg_pmt))
        msg = pmt.cdr(msg_pmt)
        msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])
        return msg_str

    def get_pmt_from_data_str(self, msg_str):
        send_pmt = pmt.make_u8vector(len(msg_str), ord(' '))
        for i in range(len(msg_str)):
            pmt.u8vector_set(send_pmt, i, ord(msg_str[i]))
        
        send_pmt = pmt.cons(pmt.PMT_NIL, send_pmt)
        return send_pmt

        
