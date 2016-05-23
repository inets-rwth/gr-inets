/* -*- c++ -*- */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "rssi_impl.h"

#include <stdio.h>
#include <stdlib.h>
#include <iostream>

namespace gr {
  namespace inets {

    rssi::sptr rssi::make(float alpha)
    {
      return gnuradio::get_initial_sptr
        (new rssi_impl(alpha));
    }

    /*
     * The private constructor
     */
    rssi_impl::rssi_impl(float alpha)
        : gr::sync_block("rssi",
            gr::io_signature::make(1, 1, sizeof(std::complex<float>)),
            gr::io_signature::make(2, 2, sizeof(float))),
        d_rssi_avg(0),
        d_num_of_samples(0),
        d_active(false),
        d_alpha(alpha),
        d_beta(1.0 - alpha),
        log_file("/home/inets/Documents/Log/RSSI.csv")
    {
        log_file << "Time;RXangle;TXangle;RSSI;Num_of_Samples;" << std::endl;
    }

    /*
     * Our virtual destructor.
     */
    rssi_impl::~rssi_impl()
    {
        log_file.close();
    }

    void rssi_impl::start_rssi_meas()
    {
        boost::lock_guard<boost::mutex> guard(mtx);
        d_active = true;
        d_avg = 0;
        d_num_of_samples = 0;
    }

    void rssi_impl::store(std::string app_time, int RXangle, int TXangle)
    {

        boost::lock_guard<boost::mutex> guard(mtx);

        d_rssi_avg = d_avg;
        //d_num_of_samples = 0;
        //convert to dB and add correction term to convert to dBm
        //correction term was generated using a tone at 3.0001 GHz
        //with a power of -20.9 dBm. The USRP was set to 3 GHz and 0dB gain.
        //The measured RMS power was -22.25 dB -> 1.35 dB difference
        double input_power_db = 10.0 * std::log10(d_rssi_avg) + 1.35;

        log_file << app_time << ";" << RXangle << ";" << TXangle << ";"
            << input_power_db << ";" << d_num_of_samples << ";" << std::endl;

    }

    void rssi_impl::set_alpha(float a)
    {
        boost::lock_guard<boost::mutex> guard(mtx);
        d_alpha = a;
        d_beta = 1.0f - a;
        std::cout << "Alpha = " << d_alpha << "Beta = " << d_beta << std::endl;
    }

    int rssi_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
        boost::lock_guard<boost::mutex> guard(mtx);
        const std::complex<float> *in = (const std::complex<float> *) input_items[0];
        float *out_avg = (float *) output_items[0];
        float *out = (float *) output_items[1];

        for(int i = 0; i < noutput_items; i++) {
            double mag_sqrd = std::abs(in[i]) * std::abs(in[i]);
            d_avg = d_beta*d_avg + d_alpha*mag_sqrd; //Single pole IIR LP
            out_avg[i] = d_avg;
            out[i] = mag_sqrd;
        }

        d_num_of_samples += noutput_items;
        return noutput_items;
    }

  } /* namespace inets */
} /* namespace gr */
