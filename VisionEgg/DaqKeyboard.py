# The Vision Egg: DaqKeyboard
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
Data acquisition and triggering over the keyboard.

This module was programmed using information from the web site
http://www.pygame.org/docs/ref/pygame_key.html

"""

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import VisionEgg
import VisionEgg.Core
import VisionEgg.FlowControl
import VisionEgg.ParameterTypes as ve_types
import sys
import pygame

__version__ = VisionEgg.release_name

####################################################################
#
#        KeyboardInput
#
####################################################################

class KeyboardInput:

    def get_pygame_data(self):
        """Get keyboard input (return values are in pygame.locals.* notation)."""
        keys = pygame.key.get_pressed()
        return [k for k, v in enumerate(keys) if v]

    def get_string_data(self):
        """Get keyboard input (return values are converted to keyboard symbols (strings))."""
        pressed = self.get_pygame_data()
        keys_pressed = []
        for k in pressed: # Convert integers to keyboard symbols (strings)
            keys_pressed.append(pygame.key.name(k))
        return keys_pressed

    get_data = get_string_data # Create alias

####################################################################
#
#        KeyboardTriggerInController
#
####################################################################

class KeyboardTriggerInController(VisionEgg.FlowControl.Controller):
    """Use the keyboard to trigger the presentation."""

    def __init__(self,key=pygame.locals.K_1):
        VisionEgg.FlowControl.Controller.__init__(
            self,
            return_type=ve_types.Integer,
            eval_frequency=VisionEgg.FlowControl.Controller.EVERY_FRAME)
        self.key = key

    def during_go_eval(self):
        return 1

    def between_go_eval(self):
        for event in pygame.event.get():
#           if (event.type == pygame.locals.KEYUP) or (event.type == pygame.locals.KEYDOWN):
            if event.type == pygame.locals.KEYDOWN:
                if event.key == self.key:
                    return 1
                else:
                    return 0
