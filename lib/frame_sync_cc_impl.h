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

#ifndef INCLUDED_INETS_FRAME_SYNC_CC_IMPL_H
#define INCLUDED_INETS_FRAME_SYNC_CC_IMPL_H

#include <inets/frame_sync_cc.h>

namespace gr {
  namespace inets {

    class frame_sync_cc_impl : public frame_sync_cc
    {
     private:
		gr_complex _preamble[13]; //13 bit Barker code
		float _threshold;
		int _len_preamble;
		std::string _len_tag_key;

     public:
      frame_sync_cc_impl(float threshold, const std::string &len_tag_key);
      ~frame_sync_cc_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace inets
} // namespace gr

#endif /* INCLUDED_INETS_FRAME_SYNC_CC_IMPL_H */

