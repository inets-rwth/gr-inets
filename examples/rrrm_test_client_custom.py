#!/usr/bin/env python2

# GNU Radio Python Flow Graph
# Title: RRRM Test Client
# Author: Julian Arnold
# Generated: Thu Mar 17 11:26:52 2016
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import gr, blocks
from gnuradio import qtgui
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from inets_radio import inets_radio
from optparse import OptionParser
import gnuradio
import inets
import numpy
import sip
import time

import threading

from distutils.version import StrictVersion
class rrrm_test_client(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "RRRM Test Client")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("RRRM Test Client")
        try:
             self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
             pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "rrrm_test_client")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.sps = sps = 4
        self.range_rx_gain = range_rx_gain = 10
        self.range_mu = range_mu = 0.6
        self.threshold = threshold = 40
        self.samp_rate = samp_rate = 4e6
        self.rx_gain = rx_gain = range_rx_gain

        self.rrc = rrc = firdes.root_raised_cosine(1.0, sps, 1, 0.5, 11*sps)

        self.qpsk_mod = qpsk_mod = gnuradio.digital.constellation_qpsk().base()
        self.mu = mu = range_mu
        self.diff_preamble_128 = diff_preamble_128 = [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0,0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0,0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1,1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0][0:128]
        self.bpsk_mod = bpsk_mod = gnuradio.digital.constellation_bpsk().base()

        ##################################################
        # Blocks
        ##################################################
        self.tab = Qt.QTabWidget()
        self.tab_widget_0 = Qt.QWidget()
        self.tab_layout_0 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tab_widget_0)
        self.tab_grid_layout_0 = Qt.QGridLayout()
        self.tab_layout_0.addLayout(self.tab_grid_layout_0)
        self.tab.addTab(self.tab_widget_0, "TX")
        self.tab_widget_1 = Qt.QWidget()
        self.tab_layout_1 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tab_widget_1)
        self.tab_grid_layout_1 = Qt.QGridLayout()
        self.tab_layout_1.addLayout(self.tab_grid_layout_1)
        self.tab.addTab(self.tab_widget_1, "RX")
        self.tab_widget_2 = Qt.QWidget()
        self.tab_layout_2 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tab_widget_2)
        self.tab_grid_layout_2 = Qt.QGridLayout()
        self.tab_layout_2.addLayout(self.tab_grid_layout_2)
        self.tab.addTab(self.tab_widget_2, "Demod")
        self.top_layout.addWidget(self.tab)
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("addr=192.168.10.2", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_center_freq(2e9, 0)
        self.uhd_usrp_source_0.set_gain(rx_gain, 0)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
        	",".join(("addr=192.168.10.2", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        	"packet_len",
        )
        self.uhd_usrp_sink_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0.set_center_freq(1.5e9, 0)
        self.uhd_usrp_sink_0.set_gain(0, 0)
        self._range_rx_gain_range = Range(0, 60, 1, 10, 200)
        self._range_rx_gain_win = RangeWidget(self._range_rx_gain_range, self.set_range_rx_gain, "Rx Gain", "counter_slider", float)
        self.top_grid_layout.addWidget(self._range_rx_gain_win, 1,0,1,1)
        self._range_mu_range = Range(0, 1, 0.01, 0.6, 200)
        self._range_mu_win = RangeWidget(self._range_mu_range, self.set_range_mu, "BB Derotation Gain", "counter_slider", float)
        self.top_grid_layout.addWidget(self._range_mu_win, 2,0,1,1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
        	20000, #size
        	samp_rate / 4, #samp_rate
        	"RX Signal", #name
        	2 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(0, 80)

        self.qtgui_time_sink_x_0.set_y_label("Magnitude", "")

        self.qtgui_time_sink_x_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_NORM, qtgui.TRIG_SLOPE_POS, 20, 0, 1, "")
        self.qtgui_time_sink_x_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)

        if not False:
          self.qtgui_time_sink_x_0.disable_legend()

        labels = ["RX Signal", "Correlation", "", "", "",
                  "", "", "", "", ""]
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in xrange(2):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.tab_layout_1.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_const_sink_x_0_0 = qtgui.const_sink_c(
        	1024, #size
        	"Payload", #name
        	1 #number of inputs
        )
        self.qtgui_const_sink_x_0_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0_0.set_y_axis(-2, 2)
        self.qtgui_const_sink_x_0_0.set_x_axis(-2, 2)
        self.qtgui_const_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0_0.enable_grid(True)

        if not True:
          self.qtgui_const_sink_x_0_0.disable_legend()

        labels = ["", "", "", "", "",
                  "", "", "", "", ""]
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "red", "red", "red",
                  "red", "red", "red", "red", "red"]
        styles = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0_0.pyqwidget(), Qt.QWidget)
        self.tab_layout_2.addWidget(self._qtgui_const_sink_x_0_0_win)
        self.inets_stop_and_wait_arq_0 = inets.stop_and_wait_arq(0.2, 500, False, 100000)
        self.inets_rrrm_0 = inets.rrrm(1, [-166,-229,-63])
        self.inets_radio_0 = inets_radio(
            constellation=qpsk_mod,
            matched_filter_coeff=rrc,
            mu=mu,
            preamble=diff_preamble_128,
            samp_rate=samp_rate,
            sps=sps,
            threshold=threshold,
        )
        self.inets_per_logger_0 = inets.per_logger()
        self.fir_filter_xxx_0 = filter.fir_filter_fff(64, (gnuradio.filter.firdes.low_pass(1,4e6,4e6/64.0,100e3)))
        self.fir_filter_xxx_0.declare_sample_delay(0)
        self.blocks_socket_pdu_1 = blocks.socket_pdu("UDP_SERVER", "localhost", "52002", 10000, False)
        self.blocks_socket_pdu_0 = blocks.socket_pdu("UDP_SERVER", "localhost", "52001", 10000, False)
        self.blocks_null_sink_0_1 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_char*1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((1, ))
        #self.blocks_message_debug_0 = blocks.message_debug()
        self.blocks_file_meta_sink_0 = blocks.file_meta_sink(gr.sizeof_float*1, "rrrm_test_client_rx_data.dat", samp_rate, 1.0/64.0, blocks.GR_FILE_FLOAT, False, 1000000, "", True)
        self.blocks_file_meta_sink_0.set_unbuffered(False)
        self.blocks_complex_to_mag_0_0_0 = blocks.complex_to_mag(1)
        self.blocks_complex_to_mag_0_0 = blocks.complex_to_mag(1)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_socket_pdu_0, 'pdus'), (self.inets_stop_and_wait_arq_0, 'from_app'))
        self.msg_connect((self.blocks_socket_pdu_1, 'pdus'), (self.inets_rrrm_0, 'radar_in'))
        self.msg_connect((self.inets_radio_0, 'out'), (self.inets_per_logger_0, 'payload_in'))
        self.msg_connect((self.inets_radio_0, 'snr'), (self.inets_per_logger_0, 'snr_in'))
        self.msg_connect((self.inets_radio_0, 'out'), (self.inets_rrrm_0, 'rrrm_in'))
        self.msg_connect((self.inets_radio_0, 'snr'), (self.inets_stop_and_wait_arq_0, 'snr'))
        self.msg_connect((self.inets_rrrm_0, 'rrrm_out'), (self.inets_radio_0, 'in'))
        self.msg_connect((self.inets_rrrm_0, 'payload_out'), (self.inets_stop_and_wait_arq_0, 'from_phy'))
        #self.msg_connect((self.inets_stop_and_wait_arq_0, 'to_app'), (self.blocks_message_debug_0, 'print'))
        self.msg_connect((self.inets_stop_and_wait_arq_0, 'to_phy'), (self.inets_rrrm_0, 'payload_in'))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.qtgui_time_sink_x_0, 1))
        self.connect((self.blocks_complex_to_mag_0_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_complex_to_mag_0_0_0, 0), (self.fir_filter_xxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_complex_to_mag_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.inets_radio_0, 0))
        self.connect((self.fir_filter_xxx_0, 0), (self.blocks_file_meta_sink_0, 0))
        self.connect((self.inets_radio_0, 2), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.inets_radio_0, 1), (self.blocks_complex_to_mag_0_0, 0))
        self.connect((self.inets_radio_0, 5), (self.blocks_null_sink_0, 0))
        self.connect((self.inets_radio_0, 6), (self.blocks_null_sink_0_0, 0))
        self.connect((self.inets_radio_0, 4), (self.blocks_null_sink_0_1, 0))
        self.connect((self.inets_radio_0, 3), (self.qtgui_const_sink_x_0_0, 0))
        self.connect((self.inets_radio_0, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "rrrm_test_client")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.inets_radio_0.set_sps(self.sps)

    def get_range_rx_gain(self):
        return self.range_rx_gain

    def set_range_rx_gain(self, range_rx_gain):
        self.range_rx_gain = range_rx_gain
        self.set_rx_gain(self.range_rx_gain)

    def get_range_mu(self):
        return self.range_mu

    def set_range_mu(self, range_mu):
        self.range_mu = range_mu
        self.set_mu(self.range_mu)

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold
        self.inets_radio_0.set_threshold(self.threshold)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.inets_radio_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate / 4)
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.uhd_usrp_source_0.set_gain(self.rx_gain, 0)

    def get_rrc(self):
        return self.rrc

    def set_rrc(self, rrc):
        self.rrc = rrc
        self.inets_radio_0.set_matched_filter_coeff(self.rrc)

    def get_qpsk_mod(self):
        return self.qpsk_mod

    def set_qpsk_mod(self, qpsk_mod):
        self.qpsk_mod = qpsk_mod
        self.inets_radio_0.set_constellation(self.qpsk_mod)

    def get_mu(self):
        return self.mu

    def set_mu(self, mu):
        self.mu = mu
        self.inets_radio_0.set_mu(self.mu)

    def get_diff_preamble_128(self):
        return self.diff_preamble_128

    def set_diff_preamble_128(self, diff_preamble_128):
        self.diff_preamble_128 = diff_preamble_128
        self.inets_radio_0.set_preamble(self.diff_preamble_128)

    def get_bpsk_mod(self):
        return self.bpsk_mod

    def set_bpsk_mod(self, bpsk_mod):
        self.bpsk_mod = bpsk_mod

class rrrm_test:
    def __init__(self, top_block, qapp):
        self.tb = top_block
        self.log = open('/home/inets/Documents/Log/rrrm_test_client_log.txt','w+')
        self.qapp = qapp

    def block(self):
        self.tb.blocks_multiply_const_vxx_0.set_k((0,))
        self.log.write("Block;" + "{:.5f}".format(time.time()) + ";\r\n")
        self.log.flush()

    def unblock(self):
        self.tb.blocks_multiply_const_vxx_0.set_k((1,))
        self.log.write("Un-Block;" + "{:.5f}".format(time.time()) + ";\r\n")
        self.log.flush()

    def run_test(self):
        time.sleep(2)
        self.block()
        time.sleep(2)
        self.unblock()
        time.sleep(2)
        tb.stop()
        tb.wait()
        qapp.quit()

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    if(StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0")):
        Qt.QApplication.setGraphicsSystem(gr.prefs().get_string('qtgui','style','raster'))
    qapp = Qt.QApplication(sys.argv)
    tb = rrrm_test_client()
    tb.start()
    my_test = rrrm_test(tb, qapp)
    per_thread = threading.Thread(target=my_test.run_test)
    per_thread.start()
    tb.show()
    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()
    tb = None #to clean up Qt widgets
