#!/usr/bin/env python
"""Convert 3D position to 2D position"""

from VisionEgg.Core import *
from VisionEgg.Text import *
from VisionEgg.MoreStimuli import *

screen = get_default_screen()
screen.parameters.bgcolor = 0.0, 0.0, 0.6 # background blue

l = 0
r = 0.5
t = 0.3
b = 0
z = -1

vertices = [(l,b,z),
     (l,t,z),
     (r,t,z),
     (r,b,z)]

rect = Rectangle3D(color=(1.0,0.3,1.0),
                   vertex1=vertices[0],
                   vertex2=vertices[1],
                   vertex3=vertices[2],
                   vertex4=vertices[3],
                   )

viewport2D = Viewport(screen=screen)
projection2D = viewport2D.parameters.projection

# specify whatever projection you want here
projection3D = SimplePerspectiveProjection(fov_x=90.0)
# arbitrary manipulations just to prove point
projection3D.rotate(20.0,0.0,1.0,1.0)
projection3D.translate(-.2,.1,0.02)

viewport3D = Viewport(screen=screen,
              projection=projection3D,
              stimuli=[rect])
    
ortho_stim = []
for vertex in vertices:
    window_coords = viewport3D.eye_2_window(vertex)
    ortho_stim.append(
        Text(text='<- %.1f, %.1f'%(window_coords[0],window_coords[1]),
             position=window_coords[:2],
             anchor='left',
             )
        )
    
ortho_stim.append(
    Text(text='Pixel positions (x,y) calculated from 3D coordinates',
         position=(screen.size[0]/2,screen.size[1]),
         anchor='top',
         )
    )

ortho_stim.append(
    Text(text='----> x',
         position=(10,10),
         anchor='left',
         )
    )

ortho_stim.append(
    Text(text='----> y',
         angle=90.0,
         position=(10,10),
         anchor='left',
         )
    )

viewport2D.parameters.stimuli = ortho_stim

p = Presentation(go_duration=(10.0,'seconds'),viewports=[viewport3D,viewport2D])
p.go()
