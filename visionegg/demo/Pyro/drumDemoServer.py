#!/usr/bin/env python

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.PyroHelpers import *
from VisionEgg.GUI import *
from VisionEgg.Textures import *

default_max_speed = 1000.0

pyro_server = PyroServer()

screen = get_default_screen()

try:
    texture = TextureFromFile("orig.bmp")
except:
    texture = Texture(size=(256,32))

perspective_proj = SimplePerspectiveProjection(fov_x=98.0)
ortho_proj = OrthographicProjection(right=screen.size[0],top=screen.size[1])
ortho_proj.translate(screen.size[0]/2-texture.orig.size[0]/2,screen.size[1]/2-texture.orig.size[1]/2,0) # Draw flat texture in middle of viewport
viewport = Viewport(screen,(0,0),screen.size,perspective_proj)

drum = SpinningDrum(texture=texture,flat_projection=ortho_proj)
drum.init_gl()
fixation_spot = FixationSpot()
fixation_spot.init_gl()

viewport.add_stimulus(drum)
viewport.add_stimulus(fixation_spot)

p = Presentation(viewports=[viewport])

################# make controllers
# fixation spot toggle
fixation_spot_on_controller = ConstantPyroController(1) # on during stimulus, off otherwise
pyro_server.connect(fixation_spot_on_controller,'fixation_spot_on_controller')
p.add_transitional_controller(fixation_spot.parameters,'on',fixation_spot_on_controller.eval)

# drum on toggle
drum_on_controller = BiStatePyroController(1,0) # on during stimulus, off otherwise
pyro_server.connect(drum_on_controller,'drum_on_controller')
p.add_transitional_controller(drum.parameters,'on',drum_on_controller.eval)

# duration constant
duration_controller = ConstantPyroController((10.0,'seconds'))
pyro_server.connect(duration_controller,'duration_controller')
p.add_transitional_controller(p.parameters,'duration',duration_controller.eval)

# angular position eval string
angle_controller = EvalStringPyroController('%f*cos(t)'%default_max_speed)
pyro_server.connect(angle_controller,'angle_controller')
p.add_realtime_time_controller(drum.parameters,'angle',angle_controller.eval)

# contrast eval string
contrast_controller = EvalStringPyroController('1.0')
pyro_server.connect(contrast_controller,'contrast_controller')
p.add_realtime_time_controller(drum.parameters,'contrast',contrast_controller.eval)

# projection controller --  allows remote object to set the projection
projection_controller = LocalDictPyroController({'perspective_proj':perspective_proj,
                                                 'ortho_proj':ortho_proj})
pyro_server.connect(projection_controller,'projection_controller')
p.add_transitional_controller(viewport.parameters,'projection',projection_controller.eval)

# drum flat/cylinder controller
drum_flat_controller = ConstantPyroController(0)
pyro_server.connect(drum_flat_controller,'drum_flat_controller')
p.add_transitional_controller(drum.parameters,'flat',drum_flat_controller.eval)

# linear interpolation controller
interpolation_controller = ConstantPyroController(1)
pyro_server.connect(interpolation_controller,'interpolation_controller')
p.add_transitional_controller(drum.parameters,'texture_scale_linear_interp',interpolation_controller.eval)

# texture clamp controller
texture_repeat_controller = ConstantPyroController(0)
pyro_server.connect(texture_repeat_controller,'texture_repeat_controller')
p.add_transitional_controller(drum.parameters,'texture_repeat',texture_repeat_controller.eval)

################### done with controllers

# initialize graphics to between presentations state
p.between_presentations() 

# register the go function and serve it with pyro
go_object = PyroGoClass( go_func = p.go,
                         quit_func = pyro_server.quit_mainloop )
pyro_server.connect(go_object,'go_object')

# wait for commands and do them!
pyro_server.mainloop(idle_func=p.between_presentations,time_out=0.001) # try to idle every msec
