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
#include "variable_rotator_impl.h"

namespace gr {
  namespace inets {

    variable_rotator::sptr
    variable_rotator::make(int num_delay)
    {
      return gnuradio::get_initial_sptr
        (new variable_rotator_impl(num_delay));
    }

    /*
     * The private constructor
     */
    variable_rotator_impl::variable_rotator_impl(int num_delay)
      : gr::sync_block("variable_rotator",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex)))
    {
       set_num_delay(num_delay);
    }

    /*
     * Our virtual destructor.
     */
    variable_rotator_impl::~variable_rotator_impl()
    {
    }

    void variable_rotator_impl::set_num_delay(int n)
    {
      _num_delay = n;
    }

    int
    variable_rotator_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const gr_complex *in = (const gr_complex *) input_items[0];
        gr_complex *out = (gr_complex *) output_items[0];

        // Do <+signal processing+>
        std::vector<tag_t> tags;
        get_tags_in_window(tags, 0, 0, 1, pmt::intern("fd"));
        float df = 0;
        if(tags.size() != 0) {
          df = pmt::to_float(tags[0].value);
          _rot.set_phase_incr(exp(gr_complex(0, df * -2.0f * M_PI)));
        } else {
          std::cout << "Missing tag at element number 0." << std::endl;
        }
        tags.clear();
        get_tags_in_window(tags, 0, 0, 1, pmt::intern("phi"));
        if(tags.size() != 0)
        {
          _rot.set_phase(exp(gr_complex(0, pmt::to_float(tags[0].value) + df * -2.0f * M_PI * _num_delay )));  
        } else {
          std::cout << "Missing tag at element number 0." << std::endl;
        }
        _rot.rotateN(out, in, noutput_items);
        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace inets */
} /* namespace gr */

