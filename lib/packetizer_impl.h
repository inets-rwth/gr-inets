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

#ifndef INCLUDED_INETS_PACKETIZER_IMPL_H
#define INCLUDED_INETS_PACKETIZER_IMPL_H

#include <inets/packetizer.h>
#include <gnuradio/digital/packet_header_default.h>

namespace gr {
  namespace inets {

    class packetizer_impl : public packetizer
    {
      private:
        gr::digital::packet_header_default::sptr _header_generator;
        std::vector< unsigned char > _random;
        std::vector< unsigned char > _preamble;
        std::vector< unsigned char > _preamble_packed;
        int _padding;
        double _last_tx_time;
        double _bps;
        static const unsigned char _random_array[128];
      public:
        packetizer_impl(const std::vector< unsigned char > &preamble, int padding, double bps);
        ~packetizer_impl();
        void receive(pmt::pmt_t msg);
    };

  } // namespace inets
} // namespace gr

#endif /* INCLUDED_INETS_PACKETIZER_IMPL_H */

