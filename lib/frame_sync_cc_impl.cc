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
#include <gnuradio/tags.h>
#include <pmt/pmt.h>
#include "frame_sync_cc_impl.h"
#include <volk/volk.h>
using namespace std;
using namespace boost::assign; // bring 'operator+=()' into scope

namespace gr {
  namespace inets {

    frame_sync_cc::sptr
    frame_sync_cc::make(const std::vector<int> &preamble, gr::digital::constellation_sptr constellation, float threshold, const std::string &len_tag_key)
    {
      return gnuradio::get_initial_sptr
        (new frame_sync_cc_impl(preamble, constellation, threshold, len_tag_key));
    }

    /*
     * The private constructor
     * Needed to make preamble len a multiple of 8.
     * Otherwise the gnuradio blocks packed_to_unpacked and unpacked_to_packed don't work
     * beacuse the payload will not be byte aligned.
     */
    frame_sync_cc_impl::frame_sync_cc_impl(const std::vector<int> &preamble, gr::digital::constellation_sptr constellation, float threshold, const std::string &len_tag_key)
      : gr::block("frame_sync_cc",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::makev(4, 4, boost::assign::list_of(sizeof(gr_complex))(sizeof(gr_complex))(sizeof(unsigned char))(sizeof(float)))),
        _threshold(threshold), _len_tag_key(len_tag_key),
        _state(STATE_DETECT),  _diff(1,0), _preamble(preamble), _constellation(constellation)
    {
        _len_preamble = _preamble.size();
        modulate_preamble();
        _len_preamble = _mod_preamble.size();
        std::cout << "[frame_sync_cc_impl] :: Using preamble of len " << _len_preamble << std::endl;
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

    void frame_sync_cc_impl::set_constellation(gr::digital::constellation_sptr constellation)
    {
        std::cout << "[Frame Sync] setting constellation" << std::endl;
        boost::lock_guard<boost::mutex> guard(_set_lock);
        _constellation = constellation;
        modulate_preamble();
    }

    void frame_sync_cc_impl::modulate_preamble()
    {
        _mod_preamble.clear();
        int bits_per_sym = _constellation->bits_per_symbol();
        //Use Big Endian (MSB first) to be compatible with constellation modulator block
        for(int i = 0; i < _len_preamble; i+= bits_per_sym) {
            int val = 0;
            for(int j = 0; j < bits_per_sym; j++) {
                val += (_preamble[i + ((bits_per_sym - 1) - j)] << j);
            }
            _mod_preamble.push_back(_constellation->points()[val]);
        }
    }

    void frame_sync_cc_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
    {
        ninput_items_required[0] = noutput_items;
        return;
    }

    std::complex<float>* curr_correlation_buffer; // = (gr_complex*)volk_malloc(sizeof(gr_complex)*256, volk_get_alignment());
    std::complex<float>* ab =  (gr_complex*)volk_malloc(sizeof(gr_complex)*256, volk_get_alignment());
    std::complex<float>* ab_conj =(gr_complex*)volk_malloc(sizeof(gr_complex)*256, volk_get_alignment());
    std::complex<float>* cd = (gr_complex*)volk_malloc(sizeof(gr_complex)*256, volk_get_alignment());
    long rx_time = 0;

    int
    frame_sync_cc_impl::general_work(int noutput_items,
                          gr_vector_int &ninput_items,
                          gr_vector_const_void_star &input_items,
                          gr_vector_void_star &output_items)
    {

        boost::lock_guard<boost::mutex> guard(_set_lock);

        const gr_complex *in = (const gr_complex *) input_items[0];
        gr_complex *out = (gr_complex *) output_items[0];
        gr_complex *corr_out = (gr_complex *) output_items[1];
        unsigned char *trig_out = (unsigned char *) output_items[2];
        float *f_offset_out = (float*) output_items[3];
        float preamble_p_sum = 0.0;

        // Do <+signal processing+>
        int num_f_offset_prod = 0;
        int consumed_items = 0;
        int produced_items = 0;
        int i, j;
        int preamble_items_left = 0;
        gr_complex sum = 0;

        //look for tx_time tag
        std::vector<tag_t> tags;
        get_tags_in_window(tags, 0, 0, noutput_items, pmt::intern("rx_time"));
        if(tags.size() > 0) {
            rx_time_full_sec = pmt::to_uint64(pmt::tuple_ref(tags[0].value, 0));
            rx_time_frac_sec = pmt::to_double(pmt::tuple_ref(tags[0].value, 1));
            std::cout << "received rx_time tag. Offset = " << tags[0].offset << " Full Sec = " << rx_time_full_sec << " Frac Sec = " << rx_time_frac_sec << std::endl;
            add_item_tag(0, tags[0].offset, pmt::intern("rx_time"), pmt::make_tuple(pmt::from_uint64(rx_time_full_sec), pmt::from_double(rx_time_frac_sec)));
        }

        for(i = 0; i < noutput_items - _len_preamble; i++) {

            trig_out[i] = 0;

            //Look for preamble. Use differentially encoded preamble for increased detection range
            sum = 0;
            //volk_32fc_x2_conjugate_dot_prod_32fc(&sum, &in[i], &_mod_preamble[0], _len_preamble);
            volk_32fc_x2_multiply_conjugate_32fc(ab, &in[i], &_mod_preamble[0], _len_preamble);
            volk_32fc_conjugate_32fc(ab_conj, ab, _len_preamble);
            volk_32fc_x2_multiply_32fc(cd, &ab[1], ab_conj, _len_preamble - 1);
            curr_correlation_buffer = ab;
            //volk_32fc_x2_multiply_conjugate_32fc(cd, &_mod_buffer[0], &in[i - 1], _len_preamble);

            for(j = 0; j < _len_preamble - 1; j++) {
                //std::complex<float> x = std::conj(_mod_preamble[j]) * in[i + j];
                //curr_correlation_buffer[j] = x;
                //Differential detection for better freq. offset agnostic
                //sum += x * conj(x_prev)
                //if(j >= 1) {
                //    sum += curr_correlation_buffer[j] * std::conj(curr_correlation_buffer[j - 1]);
                //}
                //sum += std::conj(in[i + j]) * in[i + j + (_len_preamble / 2)];
                //sum += std::conj(in[i + j]) * _mod_preamble[j];
                sum += cd[j];
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
                    preamble_p_sum = 0.0;
                    _d_f = calculate_fd(curr_correlation_buffer, &in[i], &_mod_preamble[0], _len_preamble / 2, _len_preamble);
                    //_d_phi = _mod_preamble[_len_preamble - 1] / in[i + (_len_preamble - 1)];
                    f_offset_out[num_f_offset_prod] = _d_f;
                    num_f_offset_prod++;
                    std::complex<float> curr_d_phi(0,0);
                    for(int j = 0; j < (_len_preamble / 4); j++) {
                        std::complex<float> curr_pre_item = in[j + i] * std::polar(1.0f, (float)(-2.0 * M_PI * _d_f * (float)j));
                        curr_d_phi += _mod_preamble[j] / curr_pre_item;
                    }
                    curr_d_phi = curr_d_phi * (1.0f / std::abs(curr_d_phi));
                    _d_phi = curr_d_phi;
                    //_d_phi = std::complex<float>(0,0);
                }

                preamble_p_sum += (in[i] * std::conj(in[i])).real();
                consumed_items++;
                produced_items++;

                preamble_items_left--;

                if(preamble_items_left == 0) {
                    _state = STATE_SET_TRIGGER;
                    float p_rms = std::sqrt( preamble_p_sum / _len_preamble);
                    add_item_tag(0, nitems_written(0) + i + 1, pmt::intern("p_preamble_rms"), pmt::from_float(p_rms));
                    add_item_tag(0, nitems_written(0) + i + 1, pmt::intern("sample_offset"), pmt::from_uint64(nitems_written(0) + i + 1));
                    continue;
                }
            }

            if(_state == STATE_SET_TRIGGER) {
                trig_out[i] = 1;
                add_item_tag(0, nitems_written(0) + i, pmt::intern("fd"), pmt::from_float(_d_f));
                add_item_tag(0, nitems_written(0) + i, pmt::intern("phi"), pmt::from_float(std::arg(_d_phi)));
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

    /*
     * Data aided frequency offset estimation.
     * See Eq. #8 in "Data-Aided Frequency Estimation for Burst Digital Transmission" by Mengali and Morelli
     */
    float frame_sync_cc_impl::calculate_fd(const gr_complex* z, const gr_complex* x,const gr_complex* c, int N, int L0)
    {
        double w_div =(float)N * (4.0f * (float)N * (float)N - 6.0f * (float)N * (float)L0 + 3.0f * (float)L0 * (float)L0 - 1.0f);
        //z(k) = x(k) * conj(c(k))
        //std::complex<double>* z = new std::complex<double>[L0];
        //for(int i = 0; i < L0; i++) {
        //    z[i] = (1 / std::abs(x[i])) * x[i] * std::conj(c[i]);
        //}

        double sum = 0;
        for(int i = 1; i <= N; i++) {
            double w = (3.0f * ((float)(L0 - i) * (float)(L0 - i + 1) - (float)N * (float)(L0 - N))) / w_div;
            double c1 = std::arg(calculate_R(i, z, L0));
            double c2 = std::arg(calculate_R(i - 1, z, L0));
            double c3 = c1 - c2;
            c3 = wrap_phase(c3);
            sum += w * c3;
        }
        return ((float)sum / (2.0f * M_PI));
    }

    std::complex<double> frame_sync_cc_impl::calculate_R(int m, const gr_complex* z, int L0)
    {
        std::complex<double> sum = 0;
        for(int i = m; i < L0; i++) {
            float x = std::arg(z[i]) - std::arg(z[i - m]);
            std::complex<float> x2 = std::polar(1.0f, x);
            sum += x2;
        }
        return ((1.0/(double)(L0 - m)) * sum);
    }

  } /* namespace inets */
} /* namespace gr */

