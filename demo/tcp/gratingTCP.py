#!/usr/bin/env python
"""Sinusoidal grating under network control."""

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, \
     ConstantController, EvalStringController, \
     EVERY_FRAME, TIME_SEC_ABSOLUTE
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

# See if user wants to adjust default parameters
if VisionEgg.config.VISIONEGG_GUI_INIT:
    import VisionEgg.GUI # Could import in beginning, but no need if not using GUI
    window = VisionEgg.GUI.GraphicsConfigurationWindow()
    window.mainloop() # All this does is adjust VisionEgg.config
    if not window.clicked_ok:
            sys.exit() # User wants to quit

# Should do dialog here to ask for hostname and port
tcp_server = TCPServer(hostname=hostname,port=port,single_socket_but_reconnect_ok=1,confirm_address_with_gui=1)
if tcp_server.server_socket is None: # User wants to quit
    sys.exit()
tcp_listener = tcp_server.create_listener_once_connected()

# Initialize OpenGL graphics screen.
# We don't want to use VisionEgg.get_default_screen() here because we've already
# shown the graphics configuration window.
screen = Screen(size=(VisionEgg.config.VISIONEGG_SCREEN_W,
                      VisionEgg.config.VISIONEGG_SCREEN_H),
                fullscreen=VisionEgg.config.VISIONEGG_FULLSCREEN,
                preferred_bpp=VisionEgg.config.VISIONEGG_PREFERRED_BPP,
                bgcolor=(0.5,0.5,0.5,0.0),
                maxpriority=VisionEgg.config.VISIONEGG_MAXPRIORITY)

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
    initial_controller=EvalStringController(during_go_eval_string="0.0",
                                            between_go_eval_string="fmod(t_abs,360.0/5.0)*5.0",
                                            eval_frequency=EVERY_FRAME,
                                            temporal_variables=TIME_SEC_ABSOLUTE)
    )
num_samples_controller = tcp_listener.create_tcp_controller(
    tcp_name="num_samples",
    initial_controller=ConstantController(during_go_value=512,
                                          return_type=ve_types.UnsignedInteger),
    require_type=ve_types.UnsignedInteger,
    )
bit_depth_controller = tcp_listener.create_tcp_controller(
    tcp_name="bit_depth",
    initial_controller=ConstantController(during_go_value=8,
                                          return_type=ve_types.UnsignedInteger),
    require_type=ve_types.UnsignedInteger,
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
stimulus = SinGrating2D(anchor='center')

# Create a viewport (with default pixel coordinate system)
# with stimulus
viewport = Viewport( screen=screen, stimuli=[stimulus] )

# Create an instance of the Presentation class
p = Presentation(viewports=[viewport],check_events=1)

# Register the controller functions, connecting them with the parameters they control
p.add_controller(None,None, tcp_listener) # Actually listens to the TCP socket
p.add_controller(stimulus,'on', on_controller)
p.add_controller(stimulus,'contrast', contrast_controller)
p.add_controller(stimulus,'position', center_controller)
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
