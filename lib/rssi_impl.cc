/* -*- c++ -*- */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "rssi_impl.h"

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <fstream>

namespace gr {
  namespace inets {

    rssi::sptr
      rssi::make()
      {
        return gnuradio::get_initial_sptr
          (new rssi_impl());
      }

    /*
     * The private constructor
     */
    rssi_impl::rssi_impl()
      : gr::sync_block("rssi",
          gr::io_signature::make(1, 1, sizeof(std::complex<float>)),
          gr::io_signature::make(0, 0, 0)),
      d_rssi_avg(0),
      d_num_of_samples(0),
      d_active(false),
      d_alpha(0.001),
      d_beta(1.0-0.001)
    {}

    /*
     * Our virtual destructor.
     */
    rssi_impl::~rssi_impl()
    {
    }

    void rssi_impl::start_rssi_meas()
    {
      d_active = true;
      d_avg = 0;
      d_num_of_samples = 0;
      std::cout << "RSSI measurement started\n";
    }

    void rssi_impl::stop_rssi_meas(int RXangle, int TXangle)
    {
      d_active = false;
      d_rssi_avg = d_avg;

      std::ofstream myfile;
      myfile.open("/home/inets/Documents/Log/RSSI.csv", std::ios::app);

      myfile.seekp(0, std::ios::end);  
      if(myfile.tellp() == 0)
      {    
        myfile << "RXangle,TXangle,RSSI_avg,RSSI_max,Num_of_Samples\n";
      }

      myfile << RXangle << "," << TXangle << ","
        << 10.0 * std::log10(d_rssi_avg) << ","
        << "0.0" << "," << d_num_of_samples << "\n";
      myfile.close();
      std::cout << "RSSI measurement done\n";
    }

    int rssi_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const std::complex<float> *in = (const std::complex<float> *) input_items[0];

      for(int i = 0; i < noutput_items; i++) {
        double mag_sqrd = std::abs(in[i]) * std::abs(in[i]);
        d_avg = d_beta*d_avg + d_alpha*mag_sqrd; //Single pole IIR LP
      }
      d_num_of_samples += noutput_items;
      return noutput_items;
    }

  } /* namespace inets */
} /* namespace gr */
