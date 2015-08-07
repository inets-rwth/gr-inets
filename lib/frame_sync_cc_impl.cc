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
#include <boost/assign/list_of.hpp>
#include <gnuradio/io_signature.h>
#include "frame_sync_cc_impl.h"

#define M_PI 3.14159265358979323846

using namespace std;
using namespace boost::assign; // bring 'operator+=()' into scope

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
              gr::io_signature::makev(4, 4, boost::assign::list_of(sizeof(gr_complex))(sizeof(gr_complex))(sizeof(unsigned char))(sizeof(float)))),
        _threshold(threshold), _len_tag_key(len_tag_key),
        _state(STATE_DETECT),  _diff(1,0), _preamble(preamble)
    {
        _len_preamble = _preamble.size();
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
        float *f_offset_out = (float*) output_items[3];

        // Do <+signal processing+>
        int num_f_offset_prod = 0;
        int consumed_items = 0;
        int produced_items = 0;
        int i, j; 
        int preamble_items_left = 0;
        gr_complex sum = 0;

        for(i = 0; i < noutput_items - _len_preamble; i++) {

            trig_out[i] = 0;

            sum = 0;
            for(j = 1; j < _len_preamble; j++) {
                sum += std::conj(_preamble[j]) * in[i + j] * std::conj(in[i + j - 1]) * _preamble[j - 1];
                //sum += std::conj(in[i + j]) * in[i + j + (_len_preamble / 2)];   
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
                if((noutput_items - _len_preamble - i) >= (_len_preamble)) {
                    _state = STATE_PROCESS_PREAMBLE;
                    preamble_items_left = _len_preamble;                                            
                } else {
                    break;
                }
            }

            if(_state == STATE_PROCESS_PREAMBLE) {
                
                if(preamble_items_left == _len_preamble) {
                    
                    _d_f = calculate_fd(&in[i],&_preamble[0], _len_preamble / 2, _len_preamble);
                   
                     _d_phi = std::arg(_preamble[_len_preamble - 1] / ((1.0f/std::abs(in[i + (_len_preamble - 1)])) * in[i + (_len_preamble - 1) ]));
                    
                    f_offset_out[num_f_offset_prod] = _d_f;
                    num_f_offset_prod++;
                }

                consumed_items++;
                produced_items++;
                preamble_items_left--;
                                                    
                if(preamble_items_left == 0) {
                    _state = STATE_SET_TRIGGER;
                    continue;
                }                           
            }
            
            if(_state == STATE_SET_TRIGGER) {
                trig_out[i] = 1;
                add_item_tag(0, nitems_written(0) + i, pmt::intern("fd"), pmt::from_float(_d_f));          
                add_item_tag(0, nitems_written(0) + i, pmt::intern("phi"), pmt::from_float(_d_phi));
                 _state = STATE_DETECT;
                consumed_items++;
                produced_items++;
            }

        }
         
        for(i = 0; i < produced_items; i++) {
            out[i] = in[i];
        }

        consume_each(consumed_items); 
        produce(0, produced_items);
        produce(1, produced_items);
        produce(2, produced_items);
        produce(3, num_f_offset_prod);                 
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

        double sum = 0;
        //std::complex<double> sum = 0;
        for(int i = 1; i <= N; i++) {
            double w = (3.0f * ((float)(L0 - i) * (float)(L0 - i + 1) - (float)N * (float)(L0 - N))) / w_div;
            double c1 = std::arg(calculate_R(i, z, L0));
            double c2 = std::arg(calculate_R(i - 1, z, L0));
            double c3 = c1 - c2;
            c3 = wrap_phase(c3);
            //TODO wrap c3 to [-pi,pi)
            sum += w * c3;
            //sum += calculate_R(i, z, L0);
        }
        delete[] z; 
        return ((float)sum / (2.0f * M_PI));
        //return (std::arg(sum) / (M_PI * (N + 1.0)));
    }
    
    std::complex<double> frame_sync_cc_impl::calculate_R(int m, const std::complex<double>* z, int L0)
    {
        std::complex<double> sum = 0;
        for(int i = m; i < L0; i++) {
            float x = std::arg(z[i]) - std::arg(z[i - m]);
            std::complex<float> x2 = std::polar(1.0f, x);
            //std::complex<double> x = z[i] * std::conj(z[i - m]);
            sum += x2;
        }
        return ((1.0/(double)(L0 - m)) * sum); 
    }



  } /* namespace inets */
} /* namespace gr */

