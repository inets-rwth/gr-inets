/* -*- c++ -*- */
/* 
 * Copyright 2015 <+YOU OR YOUR COMPANY+>.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "packetizer_impl.h"
#include <sys/time.h>
#include <uhd/types/time_spec.hpp>

namespace gr {
  namespace inets {

    const unsigned char packetizer_impl::_random_array[] = {
        91, 136, 224, 144, 124,  33,  38,  17,  66, 161, 144, 212,  43, 141, 207, 58 ,
        13, 221, 169,  88, 118, 144, 155, 176, 112, 229, 212,  74, 235,  25, 130, 207,
        221,  12, 124, 225, 193, 140,   1, 240, 169,  23, 194,  29,  46, 204, 224,  66,
        255, 118,  59,  48, 204,  57, 165,  91, 241,  45,  49, 206,  94, 176, 177,  79,
        243, 176, 240, 152, 103, 133,  62, 255,  83,  31, 172, 226, 129, 155, 181,  30,
        7, 156, 148, 197, 231, 127, 255,  61,   5, 179, 168, 132,  87,  95,  41,  26,
        109, 206, 152,  12, 214,  51, 177, 236, 207,  88,  52, 202, 110, 185, 200, 200,
        74, 105, 211, 188, 137, 160, 126, 101, 170, 189, 141,  22, 206, 232, 199, 209
    };
        
    packetizer::sptr
    packetizer::make(const std::vector<unsigned char> &preamble, int padding, double bps)
    {
      return gnuradio::get_initial_sptr
        (new packetizer_impl(preamble, padding, bps));
    }

    /*
     * The private constructor
     */
    packetizer_impl::packetizer_impl(const std::vector<unsigned char> &preamble, int padding, double bps)
      : gr::block("packetizer",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0)), 
        _header_generator(gr::digital::packet_header_default::make(32, "packet_len", "packet_num", 1)),
        _preamble(preamble), _padding(padding), _last_tx_time(0), _bps(bps)
    {
        _random = std::vector<unsigned char>(_random_array, _random_array + 64);

        message_port_register_in(pmt::mp("payload_in"));
        set_msg_handler(pmt::mp("payload_in"), boost::bind(&packetizer_impl::receive, this, _1 ));
        message_port_register_out(pmt::mp("packet_out"));

        //pack up preamble. Big Endian. MSB first
        for(int i = 0; i < _preamble.size(); i += 8) {
            unsigned char curr_byte = 0;
            for(int j = 0; j < 8; j++) {
                curr_byte += preamble[i + j] << (7 - j);
            }
            _preamble_packed.push_back(curr_byte);
        }
    }

    /*
     * Our virtual destructor.
     */
    packetizer_impl::~packetizer_impl()
    {
    }
    

    void packetizer_impl::receive(pmt::pmt_t msg)
    {

        if(pmt::is_pair(msg)) {

            pmt::pmt_t payload_pmt = pmt::cdr(msg);
            
            if(pmt::is_u8vector(payload_pmt)){
                const std::vector< unsigned char > payload = pmt::u8vector_elements(payload_pmt);
                std::vector< unsigned char > packet;
                
                packet.insert(packet.end(), _random.begin(), _random.begin() + _padding);
                packet.insert(packet.end(), _preamble_packed.begin(), _preamble_packed.end());
    
                unsigned char hdr[32]; 
                _header_generator->header_formatter(payload.size(), hdr, std::vector<tag_t>());
                std::vector<unsigned char> hdr_packed;
                //Big Endian. MSB to lowest position
                for(int i = 0; i < 32; i += 8) {
                    unsigned char curr_byte = 0;
                    for(int j = 0; j < 8; j++) {
                        curr_byte += hdr[i + j] << (7 - j);
                    }
                    hdr_packed.push_back(curr_byte);
                }

                packet.insert(packet.end(), hdr_packed.begin(), hdr_packed.end());
                packet.insert(packet.end(), payload.begin(), payload.end());
                packet.insert(packet.end(), _random.begin(), _random.begin() + _padding);

                static const pmt::pmt_t time_key = pmt::string_to_symbol("tx_time");
                struct timeval t;
                gettimeofday(&t, NULL);
                double tx_time = t.tv_sec + t.tv_usec / 1000000.0;
                double min_time_diff = (1000 * 8.0) / _bps; //Max packet len [bit] / bit rate 
                if((tx_time - _last_tx_time) <= min_time_diff) {
                    tx_time = _last_tx_time + min_time_diff;
                } else {
                    //std::cout << "in time packet" << std::endl;
                }
                //std::cout << "tx time = " << std::fixed << tx_time << std::endl;
                _last_tx_time = tx_time;
                uhd::time_spec_t now = uhd::time_spec_t(tx_time)
                    + uhd::time_spec_t(0.05);

                const pmt::pmt_t time_value = pmt::make_tuple(
                    pmt::from_uint64(now.get_full_secs()),
                    pmt::from_double(now.get_frac_secs())
                );
                pmt::pmt_t out_pmt_vector = pmt::init_u8vector(packet.size(), packet);
                pmt::pmt_t meta = pmt::make_dict();
                meta = pmt::dict_add(meta, pmt::mp("tx_time"), time_value);
                pmt::pmt_t pdu = pmt::cons(meta, out_pmt_vector);

                message_port_pub(pmt::mp("packet_out"), pdu);
            } else { std::cout << "no u8 vector " << std::endl; }

        } else {
            std::cout << "pmt is not a pair" << std::endl;
        }
    }


  } /* namespace inets */
} /* namespace gr */

