#!/usr/bin/env python
"""gamma.py -- display a series of luminances on a display.

Unfortunately, the luminance sampling equipment I have is incapable of
precise timing, so I've added these "sync signals", which let me align
the traces in time after the calibration has been performed.
"""

from cal_helper import *

points = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]

sig_builder = SignalBuilder()

sig_builder.add_sync_signal()
sig_builder.add_test_points(points=points,seconds_per_point=0.5)
sig_builder.add_sync_signal()

sig_builder.run()
