/* -*- c++ -*- */

#ifndef INCLUDED_INETS_RSSI_IMPL_H
#define INCLUDED_INETS_RSSI_IMPL_H

#include <boost/thread.hpp>
#include <inets/rssi.h>
#include <fstream>
namespace gr {
  namespace inets {

    #define POW_WIN_LEN 128


    class rssi_impl : public rssi
    {
     private:
      float d_rssi_avg;
      int d_num_of_samples;
      bool d_active;
      double d_avg;
      double d_beta;
      double d_alpha;
      bool in_pkt;
      int th_low_counter;
      int th_high_counter;
      double pow_win[POW_WIN_LEN];
      int store_counter;
      const int pow_win_len;
      int pow_win_wp;
      double th_low;
      boost::mutex mtx;
      std::ofstream log_file;

     public:
      rssi_impl(float alpha, float th_low_db);
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

