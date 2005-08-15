#!/usr/bin/env python
"""Convert 3D position to 2D position"""

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, FunctionController
from VisionEgg.Text import *
from VisionEgg.Textures import *

screen = get_default_screen()
screen.parameters.bgcolor = 0.0, 0.0, 0.0 # background black

l = -0.1
r = 0.5
t = 0.3
b = 0
z = 0

vertices = [(l,b,z),
            (r,b,z),
            (l,t,z),
            (r,t,z)]

# Get a texture
filename = os.path.join(VisionEgg.config.VISIONEGG_SYSTEM_DIR,"data","visionegg.bmp")
texture = Texture(filename)

rect = TextureStimulus3D(texture=texture,
                         lowerleft=vertices[0],
                         lowerright=vertices[1],
                         upperleft=vertices[2],
                         upperright=vertices[3],
                         )

viewport2D = Viewport(screen=screen)
camera_matrix = ModelView()

def update(t):
    new_camera_matrix = ModelView()
    new_camera_matrix.stateless_translate(0,0,-1)
    new_camera_matrix.stateless_rotate(36.0*t,0.0,1.0,0)
    camera_matrix.parameters.matrix = new_camera_matrix.get_matrix()
    eye_coords = camera_matrix.apply_to_vertices( vertices )
    for i in range(len(vertex_labels)):
        text = vertex_labels[i]
        eye_coord_vertex = eye_coords[i]
        window_coords = viewport3D.eye_2_window(eye_coord_vertex) # eye to window
        text.parameters.text='<- %.1f, %.1f'%(window_coords[0],window_coords[1])
        text.parameters.position = window_coords[0],window_coords[1]

viewport3D = Viewport(
    screen=screen,
    projection=SimplePerspectiveProjection(fov_x=90.0),
    camera_matrix=camera_matrix,
    stimuli=[rect])
    
vertex_labels = []
for vertex in vertices:
    vertex_labels.append(
        Text(text='temporary text',
             anchor='left',
             )
        )

other_text = []
other_text.append(
    Text(text='Pixel positions (x,y) calculated from 3D coordinates',
         position=(screen.size[0]/2,screen.size[1]),
         anchor='top',
         )
    )

other_text.append(
    Text(text='----> x',
         position=(10,10),
         anchor='left',
         )
    )

other_text.append(
    Text(text='----> y',
         angle=90.0,
         position=(10,10),
         anchor='left',
         )
    )

viewport2D.parameters.stimuli = vertex_labels + other_text

p = Presentation(go_duration=(10.0,'seconds'),viewports=[viewport3D,viewport2D])
p.add_controller(None, None, FunctionController(during_go_func=update))
p.go()
