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


#ifndef INCLUDED_INETS_SIMPLE_FRAMER_BB_H
#define INCLUDED_INETS_SIMPLE_FRAMER_BB_H

#include <inets/api.h>
#include <gnuradio/tagged_stream_block.h>

namespace gr {
  namespace inets {

    /*!
     * \brief <+description of block+>
     * \ingroup inets
     *
     */
    class INETS_API simple_framer_bb : virtual public gr::tagged_stream_block
    {
     public:
      typedef boost::shared_ptr<simple_framer_bb> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of inets::simple_framer_cc.
       *
       * To avoid accidental use of raw pointers, inets::simple_framer_cc's
       * constructor is in a private implementation
       * class. inets::simple_framer_cc::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::string& len_tag_key="packet_len");
    };

  } // namespace inets
} // namespace gr

#endif /* INCLUDED_INETS_SIMPLE_FRAMER_BB_H */

