/* -*- c++ -*- */

#ifndef INCLUDED_INETS_RSSI_H
#define INCLUDED_INETS_RSSI_H


#include <inets/api.h>
#include <gnuradio/sync_block.h>
#include <string>

namespace gr {
    namespace inets {
        /*!
         * \brief <+description of block+>
         * \ingroup inets
         *
         */
        class INETS_API rssi : virtual public gr::sync_block
        {

            public:
            typedef boost::shared_ptr<rssi> sptr;
            /*!
             * \brief Return a shared_ptr to a new instance of inets::rssi.
             *
             * To avoid accidental use of raw pointers, inets::rssi's
             * constructor is in a private implementation
             * class. inets::rssi::make is the public interface for
             * creating new instances.
             */
            static sptr make(float alpha, float th_low_db);

            virtual void start_rssi_meas() = 0;
            virtual void set_alpha(float a) = 0;
            virtual void store(std::string time, int RXangle = 0, int TXangle = 0) = 0;

        };
    } // namespace inets
} // namespace gr

#endif /* INCLUDED_INETS_RSSI_H */

