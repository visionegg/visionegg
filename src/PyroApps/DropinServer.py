import VisionEgg, string


import sys, os, math
import VisionEgg.Core
import VisionEgg.FlowControl
import VisionEgg.Textures
import VisionEgg.SphereMap
import VisionEgg.PyroHelpers
import Pyro.core

from VisionEgg.PyroApps.ScreenPositionServer import ScreenPositionMetaController
from VisionEgg.PyroApps.ScreenPositionGUI import ScreenPositionParameters
from VisionEgg.PyroApps.DropinGUI import DropinMetaParameters

class DropinMetaController( Pyro.core.ObjBase ):
    def __init__(self,screen,presentation,stimuli):
        
        # get the instance of Stimulus that was created
        #assert( stimuli[0][0] == '3d_perspective_with_set_viewport_callback' )
        #grid = stimuli[0][1]
        Pyro.core.ObjBase.__init__(self)
        self.meta_params = DropinMetaParameters()
        #self.stim = stimuli
        #if not isinstance(screen,VisionEgg.Core.Screen):
        #    raise ValueError("Expecting instance of VisionEgg.Core.Screen")
        #if not isinstance(presentation,VisionEgg.FlowControl.Presentation):
        #    raise ValueError("Expecting instance of VisionEgg.FlowControl.Presentation")
        #if not isinstance(grid,VisionEgg.SphereMap.AzElGrid):
        #    raise ValueError("Expecting instance of VisionEgg.SphereMap.SphereMap")
        self.p = presentation
        #self.stim = grid

        #screen.parameters.bgcolor = (1.0, 1.0, 1.0, 0.0)

    def get_parameters(self):
        #print self.x
        return self.meta_params

    def set_parameters(self, new_parameters):
        self.meta_params = new_parameters
        self.update()
        
    def update(self):
        pass
        #print len(self.meta_params.float_names)
        #print self.meta_params.float_names[0]
        #print self.meta_params.float_names[1]
        #self.p.parameters.go_duration = ( 0.0, 'seconds')

    def go(self):
        self.p.parameters.enter_go_loop = 1

    def quit_server(self):
        self.p.parameters.quit = 1

  

def get_meta_controller_class():
    return DropinMetaController

def make_stimuli():
    pass
    #stimulus = VisionEgg.SphereMap.AzElGrid()
    #def set_az_el_grid_viewport(viewport):
    #    stimulus.parameters.my_viewport = viewport
    #return [('3d_perspective_with_set_viewport_callback',stimulus,set_az_el_grid_viewport)] # return ordered list of tuples

def get_meta_controller_stimkey():
    return "dropin_server"
