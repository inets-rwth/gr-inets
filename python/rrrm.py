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
from gnuradio import digital
import pmt
import threading
import control
import threading

class rrrm(gr.basic_block):
    """
    docstring for block rrrm
    """
    STATE_FORWARD_PAYLOAD = 0
    STATE_SWITCH = 1

    PACKET_TYPE_DATA = 0
    PACKET_TYPE_SWITCH = 1
    PACKET_TYPE_SWITCH_ACCEPT = 2
    PACKET_TYPE_SWITCH_REJECT = 3

    def __init__(self, node_id, channel_map):
        gr.basic_block.__init__(self,
            name="rrrm",
            in_sig=[],
            out_sig=[])

        self.message_port_register_in(pmt.intern('payload_in'))
        self.message_port_register_out(pmt.intern('payload_out'))
        self.message_port_register_in(pmt.intern('radar_in'))
        self.message_port_register_in(pmt.intern('rrrm_in'))
        self.message_port_register_out(pmt.intern('rrrm_out'))
        self.message_port_register_out(pmt.intern('antenna_out'))
        self.set_msg_handler(pmt.intern('payload_in'), self.handle_payload_message)
        self.set_msg_handler(pmt.intern('rrrm_in'), self.handle_rrrm_message)
        self.set_msg_handler(pmt.intern('radar_in'), self.handle_radar_message)

        self.channel_map = channel_map
        self.node_id = node_id

        self.state = self.STATE_FORWARD_PAYLOAD
        self.curr_channel_id = 0
        self.next_channel_id = 0
        self.next_channel_pos = 0
        self.thread_lock = threading.Lock()
        self.switch_ack_thread = None
        self.switch_ack_received = False

        try:
            self.antenna_control = control.control("/dev/ttyACM0")
            self.antenna_control.open()
        except:
            print 'could not open serial port'

    def handle_payload_message(self, msg_pmt):
        with self.thread_lock:
            if self.state == self.STATE_FORWARD_PAYLOAD:
                print 'RRRM: payload_in. Run state. Forwarding message'
                self.send_data_message(msg_pmt)

            if self.state == self.STATE_SWITCH:
                print 'RRRM: payload_in. Switch state. Discarding message'

    def handle_radar_message(self, msg_pmt):
        with self.thread_lock:
            print 'RRRM: radar_in'

            if self.state == self.STATE_SWITCH:
                print 'RRRM: WARN: Already in SWITCH state.'
                return

            self.state = self.STATE_SWITCH

            #calculate new path
            if self.curr_channel_id == 0:
                self.next_channel_id = 1
            else:
                self.next_channel_id = 0

            print ('RRRM: Curr chan = '+
                str(self.curr_channel_id)+" next chan = "+str(self.next_channel_id))

            self.next_channel_pos = self.channel_map[self.next_channel_id]
            self.switch_ack_received = False
            self.switch_ack_thread = threading.Thread(target=self.do_wait_for_switch_ack)
            self.switch_ack_thread.daemon = True
            self.switch_ack_thread.start()

    def do_wait_for_switch_ack(self):
        count = 0
        while (self.switch_ack_received == False and count < 3):
            self.send_switch_command(self.next_channel_id)
            time.sleep(0.1)
            count += 1
        print 'RRRM: FATAL: Missing SWITCH ACK'

    def build_link_layer_packet(self, msg_str):
        msg_str = chr(self.node_id) + msg_str
        msg_str = digital.crc.gen_and_append_crc32(msg_str)
        #packet_str_total = digital.packet_utils.whiten(packet_str_total, 0)
        send_pmt = self.get_pmt_from_data_str(msg_str)
        return send_pmt

    def send_switch_command(self, new_channel_id):
        msg_str = chr(self.PACKET_TYPE_SWITCH)
        msg_str = msg_str + chr(new_channel_id)
        send_pmt = self.build_link_layer_packet(msg_str)
        self.message_port_pub(pmt.intern('rrrm_out'), send_pmt)

    def send_switch_accept(self):
        msg_str = chr(self.PACKET_TYPE_SWITCH_ACCEPT)
        send_pmt = self.build_link_layer_packet(msg_str)
        self.message_port_pub(pmt.intern('rrrm_out'), send_pmt)

    def send_switch_reject(self):
        msg_str = chr(self.PACKET_TYPE_SWITCH_REJECT)
        send_pmt = self.build_link_layer_packet(msg_str)
        self.message_port_pub(pmt.intern('rrrm_out'), send_pmt)

    def send_data_message(self, msg_pmt):
        msg_str = self.get_data_str_from_pmt(msg_pmt)
        msg_str = chr(self.PACKET_TYPE_DATA) + msg_str
        send_pmt = self.build_link_layer_packet(msg_str)
        self.message_port_pub(pmt.intern('rrrm_out'), send_pmt)

    def handle_rrrm_message(self, msg_pmt):
        with self.thread_lock:
            print 'RRRM: rrrm_in'

            msg_str = self.get_data_str_from_pmt(msg_pmt)
            ok, node_id, msg_type, msg_data = self.parse_rrrm_message(msg_str)

            if not ok:
                print 'RRRM: Bad CRC'
                return

            print 'RRRM: Message: node_id = ' + str(node_id) + ' type = ' + str(msg_type)

            if node_id == self.node_id:
                print 'RRRM: discarding... '
                return

            if msg_type == self.PACKET_TYPE_DATA:
                send_pmt = self.get_pmt_from_data_str(msg_data)
                self.message_port_pub(pmt.intern('payload_out'), send_pmt)

            if msg_type == self.PACKET_TYPE_SWITCH:

                channel_id = ord(msg_data[0])
                print 'RRRM: SWITCH REQ: ' + str(channel_id)

                if self.antenna_control != None:
                    self.antenna_control.move_to(self.next_channel_pos)

                self.curr_channel_id = self.next_channel_id

                #make sure switch ack reaches other side before turning antenna
                self.send_switch_accept()
                time.sleep(0.01)
                self.send_switch_accept()
                time.sleep(0.01)
                self.send_switch_accept()

                self.state = self.STATE_FORWARD_PAYLOAD

            if msg_type == self.PACKET_TYPE_SWITCH_ACCEPT:

                if self.switch_ack_received == True: #Duplicate ACK, we'll receive 3 ACKs
                    return

                self.switch_ack_received = True
                if (self.switch_ack_thread != None and self.switch_ack_thread.isAlive()):
                    self.switch_ack_thread.join()
                self.switch_ack_thread = None

                if self.antenna_control != None:
                    self.antenna_control.move_to(self.next_channel_pos)

                self.curr_channel_id = self.next_channel_id

                self.state = self.STATE_FORWARD_PAYLOAD

    def parse_link_layer_packet(self, msg_str):
        (ok, msg_str) = digital.crc.check_crc32(msg_str)
        return (ok, msg_str)

    def parse_rrrm_message(self, msg_str):
        ok, msg_str = self.parse_link_layer_packet(msg_str)
        if not ok:
            return (False, None, None, None)
        node_id = ord(msg_str[0])
        msg_type = ord(msg_str[1])
        msg_str = msg_str[2:]
        return (True, node_id, msg_type, msg_str)

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


