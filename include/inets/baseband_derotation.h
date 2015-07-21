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


#ifndef INCLUDED_INETS_BASEBAND_DEROTATION_H
#define INCLUDED_INETS_BASEBAND_DEROTATION_H

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
    class INETS_API baseband_derotation : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<baseband_derotation> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of inets::baseband_derotation.
       *
       * To avoid accidental use of raw pointers, inets::baseband_derotation's
       * constructor is in a private implementation
       * class. inets::baseband_derotation::make is the public interface for
       * creating new instances.
       */
      static sptr make(float mu, gr::digital::constellation_sptr con);
      virtual void set_mu(float mu) = 0;
      virtual float mu() const = 0;

    };

  } // namespace inets
} // namespace gr

#endif /* INCLUDED_INETS_BASEBAND_DEROTATION_H */

