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
#include "frame_sync_cc_impl.h"

namespace gr {
  namespace inets {

    frame_sync_cc::sptr
    frame_sync_cc::make(float threshold, const std::string &len_tag_key)
    {
      return gnuradio::get_initial_sptr
        (new frame_sync_cc_impl(threshold, len_tag_key));
    }

    /*
     * The private constructor
     */
    frame_sync_cc_impl::frame_sync_cc_impl(float threshold, const std::string &len_tag_key)
      : gr::sync_block("frame_sync_cc",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex))),
		_threshold(threshold), _len_preamble(13), _len_tag_key(len_tag_key)
    {
		_preamble[0] = gr_complex(-1, 0);
		_preamble[1] = gr_complex(-1, 0);
		_preamble[2] = gr_complex(-1, 0);
		_preamble[3] = gr_complex(-1, 0);
		_preamble[4] = gr_complex(-1, 0);
		_preamble[5] = gr_complex(1, 0);
		_preamble[6] = gr_complex(1, 0);
		_preamble[7] = gr_complex(-1, 0);
		_preamble[8] = gr_complex(-1, 0);
		_preamble[9] = gr_complex(1, 0);
		_preamble[10] = gr_complex(-1, 0);
		_preamble[11] = gr_complex(1, 0);
		_preamble[12] = gr_complex(-1, 0);
	}

    /*
     * Our virtual destructor.
     */
    frame_sync_cc_impl::~frame_sync_cc_impl()
    {
    }

    int
    frame_sync_cc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const gr_complex *in = (const gr_complex *) input_items[0];
        gr_complex *out = (gr_complex *) output_items[0];

        // Do <+signal processing+>
		gr_complex sum = 0;
		int i, j;
		for(i = 0; i < noutput_items - _len_preamble; i++) {
			for(j = 0; j < _len_preamble; j++) {
				sum += std::conj(_preamble[j]) * in[i + j];
			}
			
			if(std::abs(sum) > _threshold) {
				//Frame detected
				//resolve phse
				float phi = std::arg(sum);
				std::cout << "curr phase: " << phi << std::endl;	
			}
		} 
        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace inets */
} /* namespace gr */

