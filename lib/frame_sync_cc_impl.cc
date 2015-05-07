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
	 * Needed to make preamble len a multiple of 8.
	 * Otherwise the gnuradio blocks packed_to_unpacked and unpacked_to_packed don't work
	 * beacuse the payload will not be byte aligned.	
     */
    frame_sync_cc_impl::frame_sync_cc_impl(float threshold, const std::string &len_tag_key)
      : gr::block("frame_sync_cc",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex))),
		_threshold(threshold), _len_preamble(16), _len_tag_key(len_tag_key),
		_state(STATE_DETECT)
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
		
		//Preamble could have first sample only in our inputbuffer
		//therfore we need 12 samples as look ahead
		//set_history(13);
		set_tag_propagation_policy(TPP_DONT);
		set_output_multiple(1024);
	}

    /*
     * Our virtual destructor.
     */
    frame_sync_cc_impl::~frame_sync_cc_impl()
    {
    }

	void frame_sync_cc_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
	{
		switch(_state) {
			case STATE_DETECT:
				ninput_items_required[0] = noutput_items;
				break;
			case STATE_PREAMBLE:
				ninput_items_required[0] = _len_preamble;
				break;
			case STATE_PAYLOAD:
				ninput_items_required[0] = 1024;
				break;
			default:
				break;
		}
			
	}

    int
    frame_sync_cc_impl::general_work(int noutput_items,
			  gr_vector_int &ninput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const gr_complex *in = (const gr_complex *) input_items[0];
        gr_complex *out = (gr_complex *) output_items[0];		

		std::cout << "call! ninput: "<< ninput_items[0] << "noutput: " << noutput_items << std::endl; 

        // Do <+signal processing+>
		gr_complex sum = 0;
		int consumed_items = 0;
		int items_produced = 0;
		int i, j;
		for(i = 0; i < noutput_items; i++) {
		
			if(_state == STATE_DETECT) {			
				//std::cout << "DETECT" << std::endl;
				sum = 0;
				for(j = 0; j < 13; j++) {
					sum += std::conj(_preamble[j]) * in[i + j];
				}
				
				if(std::abs(sum) > _threshold) {
					//Frame detected
					//resolve phse
					float phi = std::arg(sum);
					std::cout << "Found! curr corr: " << 
						std::abs(sum) <<  " curr phase: " << phi << std::endl;	
					
					_state = STATE_PREAMBLE;
					std::cout << "consuming " << i - consumed_items << " items" << std::endl;
					consumed_items = i; 
				}
			}
			
			if(_state == STATE_PREAMBLE) {
				std::cout << "PREAMBLE" << std::endl;
				if(ninput_items[0] - i >= _len_preamble) {
					
					for(j = i; j < i+13; j++) {
						
				    }

					i+=_len_preamble;
					consumed_items += _len_preamble;
					_state = STATE_PAYLOAD;

					std::cout << "consuming " << _len_preamble  << " items. Total: " << consumed_items << std::endl; 
				} else {
				
					std::cout << "not enough items in buffer" << std::endl; 
					break;
				}
			}

			if(_state == STATE_PAYLOAD) {
				std::cout << "PAYLOAD" << std::endl;
				if(ninput_items[0] - i >= 1024 && noutput_items >= 1024) {
					
					memcpy(out + items_produced, in + i, sizeof(gr_complex)*1024);
					i += 1024;

					std::cout << "adding tag at: " << (nitems_written(0) + items_produced) << std::endl;
					add_item_tag(0, nitems_written(0) + items_produced,
						pmt::string_to_symbol(_len_tag_key), pmt::from_long(1024));
					
					items_produced += 1024;
					consumed_items += 1024;
					_state = STATE_DETECT;

					std::cout << "consuming " << "1024" << " items. Total: " << consumed_items << std::endl; 
				} else {
		
					std::cout << "not enough items in buffer" << std::endl; 
					
					break;
				}

			}
		}
		
		//No preamble in whole buffer
		if(_state == STATE_DETECT) {
			consume_each(noutput_items);
		} else {
			consume_each(consumed_items);
		}
 
        // Tell runtime system how many output items we produced.
        std::cout << noutput_items <<  " items processed" << std::endl; 
		if(items_produced>0) {
			produce(0, items_produced);
			return WORK_CALLED_PRODUCE;
		} else {
			return 0;
		}
    }

  } /* namespace inets */
} /* namespace gr */

