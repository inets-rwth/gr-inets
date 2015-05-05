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
#include "simple_framer_bb_impl.h"

namespace gr {
  namespace inets {

    simple_framer_bb::sptr
    simple_framer_bb::make(const std::string& len_tag_key)
    {
      return gnuradio::get_initial_sptr
        (new simple_framer_bb_impl(len_tag_key));
    }

    /*
     * The private constructor
     */
    simple_framer_bb_impl::simple_framer_bb_impl(const std::string& len_tag_key)
      : gr::tagged_stream_block("simple_framer_bb",
              gr::io_signature::make(1, 1, sizeof(unsigned char)),
              gr::io_signature::make(1, 1, sizeof(unsigned char)),
	      len_tag_key)
    {
		preamble[0] = 0;
		preamble[1] = 0;
		preamble[2] = 0;
		preamble[3] = 0;
		preamble[4] = 0;
		preamble[5] = 1;
		preamble[6] = 1;
		preamble[7] = 0;
		preamble[8] = 0;
		preamble[9] = 1;
		preamble[10] = 0;
		preamble[11] = 1;
		preamble[12] = 0;

		set_tag_propagation_policy(TPP_DONT);
    }

    /*
     * Our virtual destructor.
     */
    simple_framer_bb_impl::~simple_framer_bb_impl()
    {
    }

    int
    simple_framer_bb_impl::calculate_output_stream_length(const gr_vector_int &ninput_items)
    {
      int noutput_items = ninput_items[0] + 2;
      return noutput_items;
    }

    int
    simple_framer_bb_impl::work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
		std::cout << "noutput_items: "<<noutput_items<<std::endl;
		std::cout << "ninput_items: "<<ninput_items[0]<<std::endl;
	
        const unsigned char *in = (const unsigned char *) input_items[0];
        unsigned char  *out = (unsigned char *) output_items[0];
		
        // Do <+signal processing+>
		int i;
		for(i = 0; i < 13; i++) {
			//pack bits
			out[i/8] |= (preamble[i] << i);
		}
		
		std::cout << "noutput_items: "<<noutput_items<<std::endl;
		std::cout << "ninput_items: "<<ninput_items[0]<<std::endl;
		memcpy(out + 2, in, ninput_items[0]);
       
		// Tell runtime system how many output items we produced.
        return ninput_items[0] + (13/8) + 1;
    }

  } /* namespace inets */
} /* namespace gr */

