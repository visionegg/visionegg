#!/usr/bin/env python
"""Convert 3D position to 2D position"""

import VisionEgg
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
filename = os.path.join(VisionEgg.config.VISIONEGG_SYSTEM_DIR,"data","visionegg.png")
texture = Texture(filename)

rect = TextureStimulus3D(texture=texture,
                         lowerleft=vertices[0],
                         lowerright=vertices[1],
                         upperleft=vertices[2],
                         upperright=vertices[3],
                         )

viewport2D = Viewport(screen=screen)
projection2D = viewport2D.parameters.projection

# This gets updated in the function below
projection3D = SimplePerspectiveProjection(fov_x=90.0)

def update(t):
    projection = SimplePerspectiveProjection(fov_x=90.0)
    projection.translate(0,0,-1)
    projection.rotate(36.0*t,0.0,1.0,0)
    projection3D.parameters.matrix = projection.get_matrix()
    for i in range(len(vertex_labels)):
        vertex = vertices[i]
        text = vertex_labels[i]
        window_coords = viewport3D.eye_2_window(vertex)
        text.parameters.text='<- %.1f, %.1f'%(window_coords[0],window_coords[1])
        text.parameters.position = window_coords[0],window_coords[1]

viewport3D = Viewport(screen=screen,
              projection=projection3D,
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
