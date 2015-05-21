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
              gr::io_signature::make(1, 1, sizeof(gr_complex))),
		_threshold(threshold), _len_preamble(16), _len_tag_key(len_tag_key),
		_state(STATE_DETECT), _last_phase(0)
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

        // Do <+signal processing+>
		gr_complex sum = 0;
		int consumed_items = 0;
		int produced_items = 0;
		int i, j;
		for(i = 0; i < noutput_items; i++) {
			
			if(_state == STATE_DETECT) {			
				sum = 0;
				for(j = 0; j < 13; j++) {
					sum += std::conj(_preamble[j]) * in[i + j];
				}
				
				if(std::abs(sum) > _threshold) {
		//			std::cout << "thresh met: " << std::abs(sum) << std::endl;
					float last_phi = 0;
				    _delta_phi = 0;
					_phi = 0;	
					float add = 0;
					bool round = false;
					for(j = 0; j < 13; j++) {
 		//				std::cout << "preamble["<< j <<"]: " << in[i + j] << std::endl;
						float curr_phi = std::arg(in[i + j]);
 
						if(curr_phi < 0) {
							curr_phi += 2 * M_PI;
						}

						curr_phi = curr_phi - std::arg(_preamble[j]);
						
						if(curr_phi < 0) {
							curr_phi += 2 * M_PI;
						}

						if(j == 0) {
							_phi = curr_phi;
						}
						
						//std::cout << "curr_phi: " << curr_phi << " last_phi: " << last_phi << " add: " << add << std::endl;
						if(j > 0)
						{
							if((curr_phi - last_phi) > M_PI) {
								 last_phi += 2 * M_PI;
							}
							if((curr_phi - last_phi) < -1.0*M_PI) {
								curr_phi += 2 * M_PI;
							}	
							
							//std::cout << "curr: " << curr_phi << " last: "<< last_phi << " delta_phi:" << _delta_phi << std::endl;
							_delta_phi += curr_phi - last_phi;  
							//std::cout << "new delta_phi: " << _delta_phi << std::endl;
						}

						last_phi = curr_phi;
					}

					_delta_phi /= 12;
					//std::cout << "freq offset: "<<_delta_phi<<std::endl;

					message_port_pub(pmt::string_to_symbol("phase"), pmt::from_float(0));
					
					_state = STATE_PREAMBLE;
					_last_phase = 0;
					
					consumed_items += i - consumed_items; 
				} else {
					consumed_items++;
				}
			}
			
			if(_state == STATE_PREAMBLE) {
				if(ninput_items[0] - i >= _len_preamble) {
					for(j = i; j < i+13; j++) {
						
				    }

					i += _len_preamble;
					consumed_items += _len_preamble;
					_state = STATE_PAYLOAD;
				} else {
					break;
				}
			}

			if(_state == STATE_PAYLOAD) {
				if(ninput_items[0] - i >= 1024 && noutput_items >= 1024) {
					for(j = 0; j < 1024; j++) {
						//std::cout << "correcting by: " << std::exp(-1.0f * (float)j * std::complex<float>(0, 1) * _delta_phi) << std::endl;
						//out[j + produced_items] = in[i + j] * 
							//std::exp(((-1.0f * (float)(j + _len_preamble)  * _delta_phi) -  _phi) * std::complex<float>(0, 1));
					
						out[j + produced_items] = in[i + j] * 
							std::exp(( -1.0f *  _phi ) * std::complex<float>(0, 1));
					}
					//memcpy(out + produced_items, in + i, sizeof(gr_complex)*1024);

					add_item_tag(0, nitems_written(0) + produced_items,
						pmt::string_to_symbol(_len_tag_key), pmt::from_long(1024));
					
					i += 1024;					
					produced_items += 1024;
					consumed_items += 1024;
					_state = STATE_DETECT;
				} else {
					break;
				}

			}
		}
		
		consume_each(consumed_items); 
		produce(0, produced_items);
		return WORK_CALLED_PRODUCE;
    }

  } /* namespace inets */
} /* namespace gr */

