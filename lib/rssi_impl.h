/* -*- c++ -*- */

#ifndef INCLUDED_INETS_RSSI_IMPL_H
#define INCLUDED_INETS_RSSI_IMPL_H

#include <inets/rssi.h>

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

     public:
      rssi_impl(float alpha);
      ~rssi_impl();
      void start_rssi_meas();
      void stop_rssi_meas(int RXangle, int TXangle);

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace inets
} // namespace gr

#endif /* INCLUDED_INETS_RSSI_IMPL_H */

