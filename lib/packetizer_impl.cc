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
		
		const unsigned char packetizer_impl::_preamble_array_packed[] = {
			249, 175, 205, 126, 106
		};


    packetizer::sptr
    packetizer::make()
    {
      return gnuradio::get_initial_sptr
        (new packetizer_impl());
    }

    /*
     * The private constructor
     */
    packetizer_impl::packetizer_impl()
      : gr::block("packetizer",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0)), _header_generator(gr::digital::packet_header_default::make(4, "packet_len", "packet_num", 8))
    {
			_random = std::vector<unsigned char>(_random_array, _random_array + 128);
			_preamble = std::vector<unsigned char>(_preamble_array_packed, _preamble_array_packed + 5);

			message_port_register_in(pmt::mp("payload_in"));
			set_msg_handler(pmt::mp("payload_in"), boost::bind(&packetizer_impl::receive, this, _1 ));
			message_port_register_out(pmt::mp("packet_out"));
		}

    /*
     * Our virtual destructor.
     */
    packetizer_impl::~packetizer_impl()
    {
    }

		unsigned char buffer[128];

		void packetizer_impl::receive(pmt::pmt_t msg)
		{

			// pdu is defined as pmt pair
			std::cout << "received payload" <<  std::endl;

			if(pmt::is_pair(msg)) {

				std::cout << "pmt is pair" << std::endl;
				std::cout << "extracting payload" << std::endl;
				pmt::pmt_t payload_pmt = pmt::cdr(msg);
				std::cout << "len: " << pmt::length(payload_pmt) << std::endl;
				
				if(pmt::is_u8vector(payload_pmt)){
					std::cout << "payload is u8 vector" << std::endl;
					const std::vector< unsigned char > payload = pmt::u8vector_elements(payload_pmt);
					std::cout << "std vec len: " << payload.size() << std::endl; 
					std::vector< unsigned char > packet;
					
					std::cout << "adding head" << std::endl; 
					packet.insert(packet.end(), _random.begin(), _random.end());
					std::cout << "adding preamble" << std::endl;
					packet.insert(packet.end(), _preamble.begin(), _preamble.end());
		
					unsigned char hdr[4]; 
					std::cout << "generating header" << std::endl;
					_header_generator->header_formatter(payload.size(), hdr, std::vector<tag_t>());

					std::cout << "adding header" << std::endl;

					packet.insert(packet.end(), hdr, hdr + 4);
					std::cout << "adding payload" << std::endl;
					packet.insert(packet.end(), payload.begin(), payload.end());
					std::cout << "adding tail" << std::endl;
					packet.insert(packet.end(), _random.begin(), _random.end());

					pmt::pmt_t out_pmt_vector = pmt::init_u8vector(packet.size(), packet);
					pmt::pmt_t pdu = pmt::cons(pmt::PMT_NIL, out_pmt_vector);


			std::cout << "sending packet" << std::endl;
		message_port_pub(pmt::mp("packet_out"), pdu);
				} else { std::cout << "no u8 vector " << std::endl; }

			} else {
				std::cout << "pmt is not a pair" << std::endl;
			}
		}


  } /* namespace inets */
} /* namespace gr */

