#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: BT_Capture
# GNU Radio version: 3.9.5.0

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import soapy


class BT_Capture(gr.top_block):

    def __init__(self, center_frequency, sample_rate, filename):
        gr.top_block.__init__(self, "BT_Capture", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.sample_rate = sample_rate
        self.center_frequency = center_frequency

        ##################################################
        # Blocks
        ##################################################
        self.soapy_hackrf_source_0 = None
        dev = 'driver=hackrf'
        stream_args = ''
        tune_args = ['']
        settings = ['']

        self.soapy_hackrf_source_0 = soapy.source(dev, "fc32", 1, '',
                                                  stream_args, tune_args, settings)
        self.soapy_hackrf_source_0.set_sample_rate(0, sample_rate)
        self.soapy_hackrf_source_0.set_bandwidth(0, 2e6)
        self.soapy_hackrf_source_0.set_frequency(0, center_frequency)
        self.soapy_hackrf_source_0.set_gain(0, 'AMP', False)
        self.soapy_hackrf_source_0.set_gain(0, 'LNA', min(max(20, 0.0), 40.0))
        self.soapy_hackrf_source_0.set_gain(0, 'VGA', min(max(20, 0.0), 62.0))
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex * 1, filename, False)
        self.blocks_file_sink_0.set_unbuffered(False)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.soapy_hackrf_source_0, 0), (self.blocks_file_sink_0, 0))

    def get_sample_rate(self):
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.soapy_hackrf_source_0.set_sample_rate(0, self.sample_rate)

    def get_center_frequency(self):
        return self.center_frequency

    def set_center_frequency(self, center_frequency):
        self.center_frequency = center_frequency
        self.soapy_hackrf_source_0.set_frequency(0, self.center_frequency)


def main(top_block_cls=BT_Capture, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
