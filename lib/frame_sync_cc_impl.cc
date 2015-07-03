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
#include <boost/assign/std/vector.hpp> // for 'operator+=()'
#include <boost/assert.hpp>
using namespace std;
using namespace boost::assign; // bring 'operator+=()' into scope
#include <gnuradio/io_signature.h>
#include "frame_sync_cc_impl.h"
# define M_PI           3.14159265358979323846
namespace gr {
  namespace inets {

    frame_sync_cc::sptr
    frame_sync_cc::make(const std::vector<gr_complex> &preamble, float threshold, const std::string &len_tag_key)
    {
      return gnuradio::get_initial_sptr
        (new frame_sync_cc_impl(preamble, threshold, len_tag_key));
    }

    /*
     * The private constructor
	 * Needed to make preamble len a multiple of 8.
	 * Otherwise the gnuradio blocks packed_to_unpacked and unpacked_to_packed don't work
	 * beacuse the payload will not be byte aligned.	
     */
    frame_sync_cc_impl::frame_sync_cc_impl(const std::vector<gr_complex> &preamble, float threshold, const std::string &len_tag_key)
      : gr::block("frame_sync_cc",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make3(3, 3, sizeof(gr_complex), sizeof(gr_complex) ,sizeof(unsigned char))),
			_threshold(threshold), _len_tag_key(len_tag_key),
			_state(STATE_DETECT),  _diff(1,0), _preamble(preamble)
    {

      _len_preamble = _preamble.size();
      /*
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
      */
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

      ninput_items_required[0] = noutput_items;
      return;
			switch(_state) {
				case STATE_DETECT:
					ninput_items_required[0] = noutput_items;
					break;
				case STATE_PREAMBLE:
					ninput_items_required[0] = noutput_items;
					break;
				case STATE_PAYLOAD:
					ninput_items_required[0] = noutput_items;
					break;
        case STATE_PROCESS_PREAMBLE:
          ninput_items_required[0] = noutput_items;
          break;
        case STATE_SET_TRIGGER:
          ninput_items_required[0] = noutput_items;
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
		
				//memset(trig_out, 0, noutput_items * sizeof(unsigned char));
		
				//std::cout << "frame_sync: state = " << _state << " noutput: " << noutput_items << std::endl;		
	      //std::cout << "looping from 0 to " << noutput_items - 38 - 1 << std::endl;	
				gr_complex sum = 0;
				int consumed_items = 0;
				int produced_items = 0;
				
				int i, j;
				
				int preamble_items_left = 0;

				for(i = 0; i < noutput_items - _len_preamble; i++) {
					trig_out[i] = 0;
					sum = 0;
					for(j = 0; j < _len_preamble / 2; j++) {
					 //sum += std::conj(_preamble[j]) * in[i + j];
					 sum += std::conj(in[i + j]) * in[i + j + (_len_preamble / 2)];   
          }
					corr_out[i] = sum;
					
					if(_state == STATE_DETECT) {			

						if(std::abs(sum) > _threshold) {
							_state = STATE_PREAMBLE;
						  //std::cout << "preamble detected. i = " << i << std::endl;
            } else {
							consumed_items++;
							produced_items++;
						}

					}
					
					if(_state == STATE_PREAMBLE) { 
						if((noutput_items - _len_preamble - i) >= (_len_preamble)) {
							_state = STATE_PROCESS_PREAMBLE;
							preamble_items_left = _len_preamble;						
						} else {
							//std::cout << "############# WARNING: Not enough samples in input buffer  ############" << std::endl; 
							break;
						}
					}

					if(_state == STATE_PROCESS_PREAMBLE) {

						if(preamble_items_left == _len_preamble) {
							//resolve phase ambiguity
							//_diff = _preamble[0] / in[i];
							//_diff = (1 / std::abs(_diff)) * _diff;
							//_d_phi = std::arg(_diff);
							
              
              
              //std::cout << "preamble[0] = " << _preamble[0] << " received = " << in[i] << std::endl;
							//std::cout << "arg preamble[0] = " << std::arg(_preamble[0]) << " arg rec = " << std::arg(in[i]) << std::endl;					
							//std::cout << "complex correction term (i = " << i << " ): " << 
              //    _diff << " abs = " << std::abs(_diff) << " arg = " << std::arg(_diff) << std::endl;
							//std::cout << "phase difference = " << _phi << std::endl;
						  _d_f = calculate_fd(&in[i],&_preamble[0], _len_preamble / 2, _len_preamble);
              std::cout << "calculated fd to fd = " << _d_f << std::endl;
            }

						consumed_items++;
						produced_items++;
						preamble_items_left--;
						
						if(preamble_items_left == 0) {
							//correct preamble
              gr_complex* preamble_corr = new gr_complex[_len_preamble];
              gr_complex d_phi = 0;
              gr_complex d_phi_sum = 0;
              for(int k = 0; k < _len_preamble; k++){
                preamble_corr[k] = in[i + k - (_len_preamble - 1)] * std::polar(1.0f, (float)(k * _d_f * -2.0f * M_PI)); 
                d_phi = _preamble[k] / preamble_corr[k];
                d_phi = (1 / std::abs(d_phi)) * d_phi;
                d_phi_sum += d_phi;
              } 
              _d_phi = std::arg(d_phi_sum / (float)_len_preamble);
              _state = STATE_SET_TRIGGER;
						  continue;
            }				
					}

          if(_state == STATE_SET_TRIGGER) {
            trig_out[i] = 1;
            //std::cout << "setting trigger at i = " << i << std::endl;
            add_item_tag(0, nitems_written(0) + i, pmt::intern("fd"), pmt::from_float(_d_f));          
            add_item_tag(0, nitems_written(0) + i, pmt::intern("phi"), pmt::from_float(_d_phi));
             _state = STATE_DETECT;
            consumed_items++;
            produced_items++;
          }

				}
				/*
        float corr = 0;
        for(i = 0; i < produced_items; i++) {
          corr = -2.0f * M_PI * _d_f * i;// + _last_corr;
          corr = wrap_phase(corr);
          out[i] = in[i] * std::polar(1.0f, corr);
				}
        _last_corr = -2.0f * M_PI * _d_f * produced_items + _last_corr; 
        std::cout << "last corr = " << _last_corr << " corr = " << corr << std::endl;	
       //memcpy(out, in, produced_items * sizeof(gr_complex));
        //std::cout << "producing " << produced_items << " consuming " << consumed_items << std::endl;
				
        */
        for(i = 0; i < produced_items; i++) {
          out[i] = in[i];
				}
        consume_each(consumed_items); 
				produce(0, produced_items);
				produce(1, produced_items);
				produce(2, produced_items);
			
			
				return WORK_CALLED_PRODUCE;
    }

    float frame_sync_cc_impl::wrap_phase(float phi)
    {
      while(phi > 2.0f * M_PI) {
        phi -= 2.0f * M_PI;
      }
      while(phi < -2.0f * M_PI) {
        phi += 2.0f * M_PI;
      }
      
      if(phi > M_PI) {
        phi = -(2.0f * M_PI - phi);
      }

      if(phi <= -M_PI) {
        phi = 2.0f * M_PI + phi;
      }

      return phi;
    }


    float frame_sync_cc_impl::calculate_fd(const gr_complex* x,const gr_complex* c, int N, int L0)
    {

      double w_div =(float)N * (4.0f * (float)N * (float)N - 6.0f * (float)N * (float)L0 + 3.0f * (float)L0 * (float)L0 - 1.0f);
      //z(k) = x(k) * conj(c(k))   
      std::complex<double>* z = new std::complex<double>[L0];
      for(int i = 0; i < L0; i++) {
        z[i] = (1 / std::abs(x[i])) * x[i] * std::conj(c[i]);
      }

      //double sum = 0;
      std::complex<double> sum = 0;
      for(int i = 1; i <= N; i++) {
        //double w = (3.0f * ((float)(L0 - i) * (float)(L0 - i + 1) - (float)N * (float)(L0 - N))) / w_div;
        //double c1 = std::arg(calculate_R(i, z, L0));
        //double c2 = std::arg(calculate_R(i - 1, z, L0));
        //double c3 = c1 - c2;
        //c3 = wrap_phase(c3);
        //TODO wrap c3 to [-pi,pi)
        //sum += w * c3;
        sum += calculate_R(i, z, L0);
      }
      delete[] z; 
      //return sum / (2.0f * M_PI);
      return (std::arg(sum) / (M_PI * (N + 1.0)));

    }
    
    std::complex<double> frame_sync_cc_impl::calculate_R(int m, const std::complex<double>* z, int L0)
    {
      std::complex<double> sum = 0;
      for(int i = m; i < L0; i++) {
        //float x = std::arg(z[i]) - std::arg(z[i - m]);
        //std::complex<float> x2 = std::polar(1.0f, x);
        std::complex<double> x = z[i] * std::conj(z[i - m]);
        sum += x;
      }
      return ((1.0/(double)(L0 - m)) * sum); 
    }



  } /* namespace inets */
} /* namespace gr */

