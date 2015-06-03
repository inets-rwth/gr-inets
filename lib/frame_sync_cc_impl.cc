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
# define M_PI           3.14159265358979323846
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
              gr::io_signature::make3(3, 3, sizeof(gr_complex), sizeof(gr_complex) ,sizeof(unsigned char))),
		_threshold(threshold), _len_preamble(40), _len_tag_key(len_tag_key),
		_state(STATE_DETECT), _last_phase(0), _phi(0), _diff(0,0)
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
		int i,j;		
		for(i = 0;i < 2; i++) {
			for(j = 0; j < 13; j++) {
				_preamble[(i + 1) * 13 + j] = _preamble[j];
			} 
		}
		//Preamble could have first sample only in our inputbuffer
		//therfore we need 12 samples as look ahead
		//set_history(13);
		set_tag_propagation_policy(TPP_DONT);
		set_output_multiple(1024);
		message_port_register_out(pmt::string_to_symbol("phase"));
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
		gr_complex *corr_out = (gr_complex *) output_items[1];
		unsigned char *trig_out = (unsigned char *) output_items[2];
        // Do <+signal processing+>
		
		memset(trig_out, 0, noutput_items * sizeof(gr_complex));
		
//		std::cout << "call: noutput: " << noutput_items << std::endl;		
		
		gr_complex sum = 0;
		
		int consumed_items = 0;
		int produced_items = 0;
		
		int i, j;
		
		int preamble_items_left = 0;

		for(i = 0; i < noutput_items - _len_preamble; i++) {
			
			sum = 0;
			for(j = 0; j < 39; j++) {
				sum += std::conj(_preamble[j]) * in[i + j];
			}

			corr_out[i] = sum;
			
			if(_state == STATE_DETECT) {			

				if(std::abs(sum) > _threshold) {
					_state = STATE_PREAMBLE;
				} else {
					consumed_items++;
					produced_items++;
				}

			}
			
			if(_state == STATE_PREAMBLE) { 
				if((noutput_items - i) > (2 * _len_preamble + 1)) {
					_state = STATE_PROCESS_PREAMBLE;
					preamble_items_left = _len_preamble;
				
				} else {
					std::cout << "not enough samples" << std::endl; 
					break;
				}
			}

			if(_state == STATE_PROCESS_PREAMBLE) {

				if(preamble_items_left == _len_preamble) {
					//resolve phase ambiguity
					_diff = _preamble[0] / in[i];
					_phi = std::arg(_diff);
					std::cout << "preamble[0] = " << _preamble[0] << " rec = " << in[i] << std::endl;
					std::cout << "arg preamble[0] = " << std::arg(_preamble[0]) << " arg rec = " << std::arg(in[i]) << std::endl;
					
					std::cout << "phase difference = " << _phi << std::endl;
				}

				consumed_items++;
				produced_items++;
				preamble_items_left--;
				
				if(preamble_items_left == 0) {
					_state = STATE_DETECT;
					trig_out[i + 1] = 1; 
				}				
			}

		}

//		std::cout << "consumed: " << consumed_items << "produced: " << produced_items << std::endl;
		
		for(i = 0; i < produced_items; i++) {
			out[i] = in[i] * _diff;
		}

//		memcpy(out, in, produced_items * sizeof(gr_complex));
		
		consume_each(consumed_items); 
		produce(0, produced_items);
		produce(1, produced_items);
		produce(2, produced_items);
	
	
		return WORK_CALLED_PRODUCE;
    }

  } /* namespace inets */
} /* namespace gr */

