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
#include "baseband_derotation_impl.h"

namespace gr {
  namespace inets {

    baseband_derotation::sptr
    baseband_derotation::make(float mu)
    {
      return gnuradio::get_initial_sptr
        (new baseband_derotation_impl(mu));
    }

    /*
     * The private constructor
     */
    baseband_derotation_impl::baseband_derotation_impl(float mu)
      : gr::sync_block("baseband_derotation",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex))),
      _error(0), _error_last(0), _mu(mu)
    {}

    /*
     * Our virtual destructor.
     */
    baseband_derotation_impl::~baseband_derotation_impl()
    {
    }

    int
    baseband_derotation_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const gr_complex *in = (const gr_complex *) input_items[0];
        gr_complex *out = (gr_complex *) output_items[0];
        _error = 0;
        _error_last = 0;
        // Do <+signal processing+>
        for(int i = 0; i < noutput_items; i++) {
          out[i] = in[i] * std::polar(1.0f, -1.0f * _error);

          float arg = std::arg(out[i]);
          float error = 0;
          if(arg > M_PI / 2 || arg < -M_PI / 2) {
              if(arg < 0) {
                error = arg + 2 * M_PI;
              } else {
                error = arg - 2 * M_PI;
              }
          } else {
            error = arg;
          } 

          _error = _error_last - _mu * error;
          _error_last = _error; 
        }
        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace inets */
} /* namespace gr */

