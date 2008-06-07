# The Vision Egg: ResponseControl
#
# Author(s): Hubertus Becker <hubertus.becker@uni-tuebingen.de>
# Copyright: (C) 2005 by Hertie Institute for Clinical Brain Research,
#            Department of Cognitive Neurology, University of Tuebingen
# URL:       http://www.hubertus-becker.de/resources/visionegg/
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.

"""
Response control during a presentation is running.

"""

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import logging
import logging.handlers

import VisionEgg
import VisionEgg.Core
import VisionEgg.FlowControl
import VisionEgg.DaqKeyboard
import VisionEgg.ParameterTypes as ve_types
import pygame

__version__ = VisionEgg.release_name

####################################################################
#
#        ResponseController
#
####################################################################

class ResponseController(VisionEgg.FlowControl.Controller):
    """This abstract base class defines the interface to any ResponseController.

    This module provides an interface to collect responses during a
    presentation is running. To interface with real data acquisition devices,
    use a module that subclasses the classes defined here.

    """

    def _reset(self):
        self.responses = []
        self.responses_since_go = []
        self.time_responses_since_go = []
        self.first_responses_since_go = []
        self.time_first_responses_since_go = None
        self.status_first_responses_since_go = False
        self.last_responses_since_go = []
        self.time_last_responses_since_go = None

    def __init__(self, **kw):
        self._reset()

    def get_responses(self):
        """Returns the responses in the current frame."""
        return self.responses

    get_data = get_responses # For backward compatibility

    def get_responses_since_go(self):
        """Returns all responses since the main 'go' loop has been
        started."""
        return self.responses_since_go

    def get_time_responses_since_go(self):
        """Returns the time stamps for all responses since the main 'go'
        loop has been started."""
        return self.time_responses_since_go

    def get_first_response_since_go(self, index=0):
        """Returns the first response since the main 'go' loop has been
        started."""
        if self.first_responses_since_go == []:
            return []
        else:
            return self.first_responses_since_go[index]

    def get_first_responses_since_go(self):
        """Returns the first responses since the main 'go' loop has been
        started."""
        return self.first_responses_since_go

    def get_time_first_response_since_go(self):
        """Returns the time stamp for first responses since the main 'go'
        loop has been started."""
        return self.time_first_responses_since_go

    get_time_first_responses_since_go = get_time_first_response_since_go

    def get_last_response_since_go(self, index=0):
        """Returns the last response since the main 'go' loop has been
        started."""
        if self.last_responses_since_go == []:
            return []
        else:
            return self.last_responses_since_go[index]

    def get_last_responses_since_go(self):
        """Returns the last responses since the main 'go' loop has been
        started."""
        return self.last_responses_since_go

    def get_time_last_response_since_go(self):
        """Returns the time stamp for last response since the main 'go'
        loop has been started."""
        return self.time_last_responses_since_go

    get_time_last_responses_since_go = get_time_last_response_since_go

    def between_go_eval(self):
        """Evaluate between runs of the main 'go' loop.

        Override this method in subclasses."""
        raise RuntimeError("%s: Definition of between_go_eval() in abstract base class ResponseController must be overriden."%(str(self),))

    def during_go_eval(self):
        """Evaluate during the main 'go' loop.

        Override this method in subclasses."""
        raise RuntimeError("%s: Definition of during_go_eval() in abstract base class ResponseController must be overriden."%(str(self),))


####################################################################
#
#        KeyboardResponseController
#
####################################################################

#class KeyboardResponseController(VisionEgg.ReponseController):
class KeyboardResponseController(ResponseController):
    """Use the keyboard to collect responses during a presentation is running."""

    def __init__(self):
        VisionEgg.FlowControl.Controller.__init__(self,
            return_type=ve_types.get_type(None),
            eval_frequency=VisionEgg.FlowControl.Controller.EVERY_FRAME,
            temporal_variables=VisionEgg.FlowControl.Controller.TIME_SEC_SINCE_GO
        )
        self.input = VisionEgg.DaqKeyboard.KeyboardInput()

    def between_go_eval(self):
        return None # Ignore keyboard

    def during_go_eval(self):
        if self.time_sec_since_go <= 0.01: # Reset it every presentation
            self._reset()
#       self.responses = self.input.get_pygame_data()
        self.responses = self.input.get_string_data()
        if len(self.responses) > 0:
            self.responses_since_go.append(self.responses)
            self.time_responses_since_go.append(self.time_sec_since_go)
            if self.status_first_responses_since_go == False:
                self.time_first_responses_since_go = self.time_sec_since_go
                self.first_responses_since_go = self.responses
                self.status_first_responses_since_go = True
            self.time_last_responses_since_go = self.time_sec_since_go
            self.last_responses_since_go = self.responses
        return None
