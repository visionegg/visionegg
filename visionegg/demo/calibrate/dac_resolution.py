#!/usr/bin/env python
"""daq_resolution.py -- Attempt to locate frame buffer and DAC quanta
"""

import Numeric

adjust_with_n_bits = 12
increment = 1.0/(2**adjust_with_n_bits)
#print increment

expect_n_bits = 10
expected_bit_range = 4 # try and cover this many LSBs of expected bits

start_points = [0.5]

factor_more_points = (2**(adjust_with_n_bits - expect_n_bits))*(2**expected_bit_range)
final_points = []

for i in range(len(start_points)):
    new_points = Numeric.arange(start_points[i]-factor_more_points*increment/2.0,start_points[i]+factor_more_points*increment/2.0,increment)
    for j in range(len(new_points)):
        final_points.append(new_points[j])

#print final_points

from cal_helper import *

sig_builder = SignalBuilder()

sig_builder.add_sync_signal()
sig_builder.add_test_points(points=final_points,seconds_per_point=0.5)
sig_builder.add_sync_signal()

sig_builder.run()
