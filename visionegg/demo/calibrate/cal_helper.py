#!/usr/bin/env python

from VisionEgg.PyroHelpers import *
from VisionEgg.Core import *

# Get the controllers

client = PyroClient()

color_controller = client.get('color_controller')
go_controller = client.get('go_controller')
duration_controller = client.get('duration_controller')

class SignalBuilder:
    def __init__(self):
        self.done_time = 0.0
        self.time_vector = []
        self.sig_vector = []
        
    def add_sync_signal(self):
        """Create square wave signal to line up times."""
        # On
        self.time_vector.append( self.done_time )
        self.sig_vector.append( 1.0 )

        self.done_time = self.done_time + 1.0

        # Off
        self.time_vector.append( self.done_time )
        self.sig_vector.append( 0.0 )
        
        self.done_time = self.done_time + 1.0

        # On
        self.time_vector.append( self.done_time )
        self.sig_vector.append( 1.0 )

        self.done_time = self.done_time + 1.0

        # Off
        self.time_vector.append( self.done_time )
        self.sig_vector.append( 0.0 )

        self.done_time = self.done_time + 1.0

    def add_test_points(self,points,seconds_per_point=0.5):
        for i in range(len(points)):
            self.time_vector.append( self.done_time )
            self.sig_vector.append( points[i] )
            
            self.done_time = self.done_time + seconds_per_point

    def run(self):
        """Run the stimulus."""

        print "#Time\tOpenGL color"
        for i in range(len(self.time_vector)):
            print "%f\t%f"%(self.time_vector[i],self.sig_vector[i])
        print "%f\t%f"%(self.done_time,self.sig_vector[-1])
        
        # This is the trickiest part of the whole thing:
        # Building an exec string from a vector.

        my_str = """
if t > %s:
    raise ValueError("t beyond signal duration.")
if t < 0:
    x=(0.5,1.,1.,0.) # test value
else:
    i = %d-1
    while 1:
        if t >= %s[i]:
            break
        i = i - 1
    val = %s[i]
    x=(val,val,val,0.0)
"""%(
        repr(self.done_time),len(self.time_vector),repr(self.time_vector),repr(self.sig_vector))

        #print "Sending the following code to the server:-------------"
        #print my_str
        #print "------------------------------------------------------"

        duration_controller.set_during_go_value((self.done_time,'seconds'))
        duration_controller.evaluate_now()

        color_controller.set_during_go_exec_string(my_str)
        color_controller.evaluate_now()
        color_controller._test_self(1)

        go_controller.set_during_go_value(0)
        go_controller.set_between_go_value(1)
        go_controller.set_eval_frequency(Controller.ONCE)

