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
            static sptr make(float alpha, float th_low_db, int num_samp_idle_det);

            virtual void reset() = 0;
            virtual void set_alpha(float a) = 0;
            virtual double get_pow_data() = 0;
            virtual double get_pow() = 0;
            virtual int get_last_sample_count() = 0;

        };
    } // namespace inets
} // namespace gr

#endif /* INCLUDED_INETS_RSSI_H */

