/* -*- c++ -*- */

#define INETS_API
#define DIGITAL_API
%include "gnuradio.i"			// the common stuff
//load generated python docstrings
%include "inets_swig_doc.i"

%{
#include "gnuradio/digital/constellation.h"
#include "inets/frame_sync_cc.h"
#include "inets/timing_recovery_cc.h"
#include "inets/packetizer.h"
#include "inets/variable_rotator.h"
#include "inets/baseband_derotation.h"
#include "inets/rssi.h"
%}
%include "gnuradio/digital/constellation.h"


%include "inets/frame_sync_cc.h"
GR_SWIG_BLOCK_MAGIC2(inets, frame_sync_cc);
%include "inets/timing_recovery_cc.h"
GR_SWIG_BLOCK_MAGIC2(inets, timing_recovery_cc);
%include "inets/packetizer.h"
GR_SWIG_BLOCK_MAGIC2(inets, packetizer);
%include "inets/variable_rotator.h"
GR_SWIG_BLOCK_MAGIC2(inets, variable_rotator);
%include "inets/baseband_derotation.h"
GR_SWIG_BLOCK_MAGIC2(inets, baseband_derotation);
%include "inets/rssi.h"
GR_SWIG_BLOCK_MAGIC2(inets, rssi);
