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
#include "timing_recovery_cc_impl.h"

namespace gr {
  namespace inets {

    timing_recovery_cc::sptr
    timing_recovery_cc::make(int sps)
    {
      return gnuradio::get_initial_sptr
        (new timing_recovery_cc_impl(sps));
    }

    /*
     * The private constructor
     */
    timing_recovery_cc_impl::timing_recovery_cc_impl(int sps)
      : gr::sync_decimator("timing_recovery_cc",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex)), sps), _sps(sps)
    {
        set_output_multiple(32*_sps);
    }

    /*
     * Our virtual destructor.
     */
    timing_recovery_cc_impl::~timing_recovery_cc_impl()
    {
    }

    int
    timing_recovery_cc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const gr_complex *in = (const gr_complex *) input_items[0];
        gr_complex *out = (gr_complex *) output_items[0];
	
        std::cout << "[timing recovery] noutput_items = " << noutput_items << std::endl;	

        // Do <+signal processing+>
	int i, j, opt_delay;
        double energy = 0, max_energy = -1;
	int output_count = 0;

        for(j = 0; j < _sps; j++) {
	    energy = 0;
	    for(i = j; i < (noutput_items * _sps); i += _sps) {
	        energy += std::pow(std::abs(in[i]), 2);		
	    }
	    if(energy > max_energy) {
                max_energy = energy;
                opt_delay = j;
            }
        }
	int index = 0;
        for(j = opt_delay; j < (noutput_items * _sps); j += _sps) {
            out[index] = in[j];
            index++;
            output_count++;
        }

        // Tell runtime system how many output items we produced.
        std::cout << "Produced "<< output_count << " samples. Opt delay = " << opt_delay << std::endl;
        return noutput_items;
    }

  } /* namespace inets */
} /* namespace gr */

