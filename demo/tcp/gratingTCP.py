#!/usr/bin/env python
"""Sinusoidal grating under network control."""

from VisionEgg.Core import *
from VisionEgg.Gratings import *
from VisionEgg.TCPController import *
import sys

# Vision Egg server name and port
hostname = ''
port = 5000

# Allow command line to override defaults
if len(sys.argv) == 2:
    try:
        port = int(sys.argv[1])
    except ValueError:
        hostname = sys.argv[1]
elif len(sys.argv) == 3:
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    
tcp_server = TCPServer(hostname=hostname,port=port,single_socket_but_reconnect_ok=1)
tcp_listener = tcp_server.create_listener_once_connected()

# Initialize OpenGL graphics screen.
screen = get_default_screen()

tcp_listener.send_raw_text("Screen size = %s\n"%(screen.size,))

# Create controllers for all variables of a sine wave grating
on_controller = tcp_listener.create_tcp_controller(
    tcp_name="on",
    initial_controller=ConstantController(during_go_value=1)
    )
contrast_controller = tcp_listener.create_tcp_controller(
    tcp_name="contrast",
    initial_controller=ConstantController(during_go_value=1.0)
    )
center_controller = tcp_listener.create_tcp_controller(
    tcp_name="center",
    initial_controller=ConstantController((screen.size[0]/2.0,screen.size[1]/2.0))
    )
size_controller = tcp_listener.create_tcp_controller(
    tcp_name="size",
    initial_controller=ConstantController(during_go_value=(300.0,300.0))
    )
spatial_freq_controller = tcp_listener.create_tcp_controller(
    tcp_name="sf",
    initial_controller=ConstantController(during_go_value=15.0/640.0)
    )
temporal_freq_controller = tcp_listener.create_tcp_controller(
    tcp_name="tf",
    initial_controller=ConstantController(during_go_value=5.0)
    )
phase_controller = tcp_listener.create_tcp_controller(
    tcp_name="phase",
    initial_controller=ConstantController(during_go_value=0.0)
    )
orientation_controller = tcp_listener.create_tcp_controller(
    tcp_name="orient",
    initial_controller=ConstantController(during_go_value=0.0)
    )
num_samples_controller = tcp_listener.create_tcp_controller(
    tcp_name="num_samples",
    initial_controller=ConstantController(during_go_value=512)
    )
bit_depth_controller = tcp_listener.create_tcp_controller(
    tcp_name="bit_depth",
    initial_controller=ConstantController(during_go_value=8)
    )
go_duration_controller = tcp_listener.create_tcp_controller(
    tcp_name="go_duration",
    initial_controller=ConstantController(during_go_value=(10,'seconds'))
    )
go_controller = tcp_listener.create_tcp_controller(
    tcp_name="go",
    initial_controller=ConstantController(during_go_value=0)
    )

# Create the instance SinGrating with appropriate parameters
stimulus = SinGrating2D()

# Create a viewport (with default pixel coordinate system)
# with stimulus
viewport = Viewport( screen=screen, stimuli=[stimulus] )

# Create an instance of the Presentation class
p = Presentation(viewports=[viewport],check_events=1)

# Register the controller functions, connecting them with the parameters they control
p.add_controller(None,None, tcp_listener) # Actually listens to the TCP socket
p.add_controller(stimulus,'on', on_controller)
p.add_controller(stimulus,'contrast', contrast_controller)
p.add_controller(stimulus,'center', center_controller)
p.add_controller(stimulus,'size', size_controller)
p.add_controller(stimulus,'spatial_freq', spatial_freq_controller)
p.add_controller(stimulus,'temporal_freq_hz', temporal_freq_controller)
p.add_controller(stimulus,'phase_at_t0', phase_controller)
p.add_controller(stimulus,'orientation', orientation_controller)
p.add_controller(stimulus,'num_samples', num_samples_controller)
p.add_controller(stimulus,'bit_depth', bit_depth_controller)
p.add_controller(p,'go_duration', go_duration_controller)
p.add_controller(p,'enter_go_loop', go_controller)

# Go!
p.run_forever()
