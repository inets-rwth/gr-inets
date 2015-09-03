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


#ifndef INCLUDED_INETS_FRAME_SYNC_CC_H
#define INCLUDED_INETS_FRAME_SYNC_CC_H

#include <inets/api.h>
#include <gnuradio/sync_block.h>
#include <gnuradio/digital/constellation.h>

namespace gr {
  namespace inets {

    /*!
     * \brief <+description of block+>
     * \ingroup inets
     *
     */
    class INETS_API frame_sync_cc : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<frame_sync_cc> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of inets::frame_sync_cc.
       *
       * To avoid accidental use of raw pointers, inets::frame_sync_cc's
       * constructor is in a private implementation
       * class. inets::frame_sync_cc::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::vector<int> &preamble, gr::digital::constellation_sptr constellation, float threshold, const std::string &len_tag_key = "packet_len");

      virtual void set_constellation(gr::digital::constellation_sptr constellation) = 0;
    
    };

  } // namespace inets
} // namespace gr

#endif /* INCLUDED_INETS_FRAME_SYNC_CC_H */

