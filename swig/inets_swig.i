/* -*- c++ -*- */

#define INETS_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "inets_swig_doc.i"

%{
#include "inets/simple_framer_cc.h"
#include "inets/simple_framer_bb.h"
#include "inets/frame_sync_cc.h"
#include "inets/timing_recovery_cc.h"
#include "inets/packetizer.h"
%}


%include "inets/simple_framer_cc.h"
GR_SWIG_BLOCK_MAGIC2(inets, simple_framer_cc);
%include "inets/simple_framer_bb.h"
GR_SWIG_BLOCK_MAGIC2(inets, simple_framer_bb);
%include "inets/frame_sync_cc.h"
GR_SWIG_BLOCK_MAGIC2(inets, frame_sync_cc);
%include "inets/timing_recovery_cc.h"
GR_SWIG_BLOCK_MAGIC2(inets, timing_recovery_cc);
%include "inets/packetizer.h"
GR_SWIG_BLOCK_MAGIC2(inets, packetizer);
