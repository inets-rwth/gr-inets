/* -*- c++ -*- */

#ifndef INCLUDED_INETS_RSSI_IMPL_H
#define INCLUDED_INETS_RSSI_IMPL_H

#include <boost/thread.hpp>
#include <inets/rssi.h>
#include <fstream>

namespace gr {
  namespace inets {

    class rssi_impl : public rssi
    {
     private:
      float d_rssi_avg;
      int d_num_of_samples;
      bool d_active;
      double d_avg;
      double d_beta;
      double d_alpha;
      boost::mutex mtx;
      std::ofstream log_file;

     public:
      rssi_impl(float alpha);
      ~rssi_impl();
      void start_rssi_meas();
      void store(std::string time, int RXangle = 0, int TXangle = 0);
      void set_alpha(float a);

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace inets
} // namespace gr

#endif /* INCLUDED_INETS_RSSI_IMPL_H */

