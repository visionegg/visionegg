#!/usr/bin/env python
#
# The Vision Egg: MouseTargetServer
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""Handle mouse-controlled small targets (server-side)"""

import VisionEgg, string
import VisionEgg.ParameterTypes as ve_types

import sys, os, math
import VisionEgg.Core
import VisionEgg.FlowControl
import VisionEgg.MoreStimuli
import VisionEgg.PyroHelpers
import Pyro.core
import pygame, pygame.locals

from VisionEgg.PyroApps.MouseTargetGUI import MouseTargetMetaParameters

# Variables to store the mouse position
mouse_position = (320.0, 240.0)
last_mouse_position = (0.0,0.0)

# target size global variables
target_w = 50.0
target_h = 10.0

# key state global variables
up = 0
down = 0
left = 0
right = 0

def keydown(event):
    global up, down, left, right
    if event.key == pygame.locals.K_UP:
        up = 1
    elif event.key == pygame.locals.K_DOWN:
        down = 1
    elif event.key == pygame.locals.K_RIGHT:
        right = 1
    elif event.key == pygame.locals.K_LEFT:
        left = 1

def keyup(event):
    global up, down, left, right
    if event.key == pygame.locals.K_UP:
        up = 0
    elif event.key == pygame.locals.K_DOWN:
        down = 0
    elif event.key == pygame.locals.K_RIGHT:
        right = 0
    elif event.key == pygame.locals.K_LEFT:
        left = 0

handle_event_callbacks = [(pygame.locals.KEYDOWN, keydown),
                          (pygame.locals.KEYUP, keyup)]

class MouseTargetExperimentMetaController( Pyro.core.ObjBase ):
    def __init__(self,screen,presentation,stimuli):
        global screen_global
        screen_global = screen
        # get stimulus
        assert( stimuli[0][0] == '2d_overlay')
        target = stimuli[0][1]

        Pyro.core.ObjBase.__init__(self)
        self.meta_params = MouseTargetMetaParameters()
        if not isinstance(screen,VisionEgg.Core.Screen):
            raise ValueError("Expecting instance of VisionEgg.Core.Screen")
        if not isinstance(presentation,VisionEgg.FlowControl.Presentation):
            raise ValueError("Expecting instance of VisionEgg.FlowControl.Presentation")
        if not isinstance(target,VisionEgg.MoreStimuli.Target2D):
            raise ValueError("Expecting instance of VisionEgg.MoreStimuli.Target2D")

        self.screen = screen
        self.p = presentation
        self.stim = target

        self.p.add_controller(target,'position', TargetPositionController())
        self.p.add_controller(target,'size', VisionEgg.FlowControl.FunctionController(during_go_func=get_target_size,
                                                                between_go_func=get_target_size) )
        self.p.add_controller(target,'orientation', TargetOrientationController() )
        self.mouse_position_controller = MousePositionController()
        self.p.add_controller(None,None,self.mouse_position_controller)
        self.orig_event_handlers = self.p.parameters.handle_event_callbacks
        self.p.parameters.handle_event_callbacks = handle_event_callbacks

        self.update() # set stimulus parameters to initial defaults

    def __del__(self):
        self.p.parameters.handle_event_callbacks = self.orig_event_handlers
        self.p.remove_controller(None,None,self.mouse_position_controller)
        self.p.remove_controller(self.stim,'position')
        self.p.remove_controller(self.stim,'size')
        self.p.remove_controller(self.stim,'orientation')

    def get_parameters(self):
        return self.meta_params

    def set_parameters(self, new_parameters):
        if isinstance(new_parameters, MouseTargetMetaParameters):
            self.meta_params = new_parameters
        else:
            raise ValueError("Argument to set_parameters must be instance of MouseTargetMetaParameters")
        self.update()

    def update(self):
        stim_params = self.stim.parameters # shorthand
        meta_params = self.meta_params # shorthand

        # colors
        stim_params.color = meta_params.color
        self.screen.parameters.bgcolor = meta_params.bgcolor

    def go(self):
        pass
        #self.p.parameters.enter_go_loop = 1

    def quit_server(self):
        self.p.parameters.quit = 1

def get_meta_controller_class():
    return MouseTargetExperimentMetaController

def make_stimuli():
    stimulus = VisionEgg.MoreStimuli.Target2D(anchor='center')
    return [('2d_overlay',stimulus)]

def get_meta_controller_stimkey():
    return "mouse_target_server"

########################
#  Define controllers  #
########################

class MousePositionController( VisionEgg.FlowControl.Controller ):
    def __init__(self):
        global mouse_position
        VisionEgg.FlowControl.Controller.__init__(self,
                            return_type=ve_types.get_type(None),
                            eval_frequency=VisionEgg.FlowControl.Controller.EVERY_FRAME)
        self.between_go_eval = self.during_go_eval

    def during_go_eval(self,t=None):
        # Convert pygame mouse position to OpenGL position
        global mouse_position, last_mouse_position, screen_global
        just_current_pos = mouse_position
        (x,y) = pygame.mouse.get_pos()
        y = screen_global.size[1]-y
        mouse_position = (x,y)
        if just_current_pos != mouse_position:
            last_mouse_position = just_current_pos
        return None

class TargetPositionController( VisionEgg.FlowControl.Controller ):
    def __init__(self):
        global mouse_position
        VisionEgg.FlowControl.Controller.__init__(self,
                            return_type=ve_types.Sequence2(ve_types.Real),
                            eval_frequency=VisionEgg.FlowControl.Controller.EVERY_FRAME)
        self.between_go_eval = self.during_go_eval

    def during_go_eval(self,t=None):
        global mouse_position
        return mouse_position

def cross_product(b,c):
    """Cross product between vectors, represented as tuples of length 3."""
    det_i = b[1]*c[2] - b[2]*c[1]
    det_j = b[0]*c[2] - b[2]*c[0]
    det_k = b[0]*c[1] - b[1]*c[0]
    return (det_i,-det_j,det_k)

def mag(b):
    """Magnitude of a vector."""
    return b[0]**2.0 + b[1]**2.0 + b[2]**2.0

class TargetOrientationController( VisionEgg.FlowControl.Controller ):
    def __init__(self):
        VisionEgg.FlowControl.Controller.__init__(self,
                            return_type=ve_types.Real,
                            eval_frequency=VisionEgg.FlowControl.Controller.EVERY_FRAME)
        self.c = (0.0,0.0,1.0)
        self.last_orientation = 0.0
        self.between_go_eval = self.during_go_eval

    def during_go_eval(self):
        global mouse_position, last_mouse_position

        b = (float(last_mouse_position[0]-mouse_position[0]),
             float(last_mouse_position[1]-mouse_position[1]),
             0.0)

        if mag(b) > 1.0: # Must mouse 1 pixel before changing orientation (supposed to reject noise)
            # find cross product b x c. assume b and c are 3-vecs, b has
            # 3rd component 0.
            orientation_vector = cross_product(b,self.c)
            self.last_orientation = math.atan2(orientation_vector[1],orientation_vector[0])/math.pi*180.0
        return self.last_orientation

def get_target_size(t=None):
    global target_w, target_h
    global up, down, left, right

    amount = 0.02

    if up:
        target_w = target_w+(amount*target_w)
    elif down:
        target_w = target_w-(amount*target_w)
    elif right:
        target_h = target_h+(amount*target_h)
    elif left:
        target_h = target_h-(amount*target_h)
    target_w = max(target_w,0.0)
    target_h = max(target_h,0.0)

    return (target_w, target_h)

# Don't do anything unless this script is being run
if __name__ == '__main__':

    pyro_server = VisionEgg.PyroHelpers.PyroServer()

    screen = VisionEgg.Core.Screen.create_default()

    # get Vision Egg stimulus ready to go
    stimuli = make_stimuli()
    stimulus = stimuli[0][1]
    viewport = VisionEgg.Core.Viewport(screen=screen,stimuli=[stimulus])
    p = VisionEgg.FlowControl.Presentation(viewports=[viewport])

    # now hand over control of grating and mask to FlatGratingExperimentMetaController
    meta_controller = MouseTargetExperimentMetaController(screen,p,stimuli)
    pyro_server.connect(meta_controller,get_meta_controller_stimkey())

    # get listener controller and register it
    p.add_controller(None,None, pyro_server.create_listener_controller())

    # enter endless loop
    p.run_forever()
