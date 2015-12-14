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
#include "sink_impl.h"

//my includes
#include <fstream>
#include <iostream>

namespace gr {
  namespace inets {

    sink::sptr
    sink::make(const char *filename)
    {
      return gnuradio::get_initial_sptr
        (new sink_impl(filename));
    }

    /*
     * The private constructor
     */
    sink_impl::sink_impl(const char *file_name)
      : gr::sync_block("sink",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(0, 0, 0))
    {
        filename = file_name;
        overwrite = true;

        f.open(filename.c_str(), std::fstream::out | std::fstream::trunc);
        if(!f.is_open()) {
            std::cout << "Could not open file " << filename << std::endl;
        }
        std::cout << "file was opened for writing" << std::endl;
    }

    /*
     * Our virtual destructor.
     */
    sink_impl::~sink_impl()
    {
    }

    int
    sink_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const gr_complex *in = (const gr_complex *) input_items[0];

        std::vector<tag_t> tags;
        std::vector<tag_t>::iterator it;

        get_tags_in_window(tags, 0, 0, noutput_items);

        uint64_t offset = nitems_read(0);

        for(int i=0; i<noutput_items; i++) {
            for(it=tags.begin(); it!=tags.end(); it++) {
                if(tags.size()<=0)
                    break;
                if(it->offset == offset) {
                    f << "tag " << it->offset << " "
                        << ((pmt::is_symbol(it->srcid)) ? pmt::symbol_to_string(it->srcid) : std::string("n/a")) << " "
                        << pmt::symbol_to_string(it->key) << " "
                        << it->value << std::endl;

                    tags.erase(it);
                } else {
                    break;
                }
            }
            f << "stream " << in[i].real() << " " << in[i].imag() << std::endl;
            offset++;
        }

        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace inets */
} /* namespace gr */
