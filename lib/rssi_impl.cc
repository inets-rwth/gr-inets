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
              gr::io_signature::make(1, 1, sizeof(float)),
              gr::io_signature::make(0, 0, 0)),
              d_rssi_avg(0),
              d_rssi_max(0),
              d_num_of_samples(0),
              d_accumulated_powers(0),
              d_active(false)
    {}

    /*
     * Our virtual destructor.
     */
    rssi_impl::~rssi_impl()
    {
    }

    void rssi_impl::start_rssi_meas()
    {
        d_rssi_avg = 0;
        d_rssi_max = 0;
        d_num_of_samples = 0;
        d_accumulated_powers = 0;
        d_active = true;
        std::cout << "RSSI measurement started\n";
    }

    void rssi_impl::stop_rssi_meas(int RXangle, int TXangle)
    {
        d_active = false;
        d_rssi_avg = d_accumulated_powers / d_num_of_samples;

        std::ofstream myfile;
	    myfile.open("/home/inets/Documents/Log/RSSI.csv", std::ios::app);

        myfile.seekp(0, std::ios::end);  
        if(myfile.tellp() == 0)
        {    
            myfile << "RXangle,TXangle,RSSI_avg,RSSI_max,Num_of_Samples\n";
        }

		myfile << RXangle << "," << TXangle << "," << d_rssi_avg << "," << d_rssi_max << "," << d_num_of_samples << "\n";
	    myfile.close();
        std::cout << "RSSI measurement done\n";
    }

    int
    rssi_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const float *in = (const float *) input_items[0];

        if(d_active)
        {
            d_num_of_samples += 1;
            d_accumulated_powers += *in;
    
            if(*in > d_rssi_max)
            {
                d_rssi_max = *in;
            }
        }

        return noutput_items;
    }

  } /* namespace inets */
} /* namespace gr */
