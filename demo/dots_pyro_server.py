#!/usr/bin/env python
"""User-defined mainloop while listening for commands over network

This example implements a mainloop directly within this short script
in addition to starting a Pyro server which listens for commands on
the network.

NOTE THAT USING PYRO IN THIS WAY A SECURITY RISK - PLEASE ONLY RUN
BEHIND A FIREWALL. AN ATTACKER COULD PROBABLY EXECUTE ARBITRARY PYTHON
COMMANDS ON YOUR COMPUTER WHEN RUNNING THIS SERVER.
"""

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

import VisionEgg.Core
import pygame
import pygame.locals
import VisionEgg.Text
import VisionEgg.Dots
import Pyro.core

Pyro.config.PYRO_MULTITHREADED = 0
Pyro.config.PYRO_TRACELEVEL = 3
Pyro.config.PYRO_USER_TRACELEVEL = 3
Pyro.config.PYRO_DETAILED_TRACEBACK = 1
Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

class DotServer(Pyro.core.ObjBase):
    def post_init(self,screen,pyro_daemon):
        self.pyro_daemon = pyro_daemon
        
        screen.parameters.bgcolor = (0.0,0.0,0.0) # black (RGB)
        self.dots = VisionEgg.Dots.DotArea2D(
            position                = ( screen.size[0]/2.0, screen.size[1]/2.0 ),
            size                    = ( 300.0 , 300.0 ),
            signal_fraction         = 0.1,
            signal_direction_deg    = 180.0,
            velocity_pixels_per_sec = 10.0,
            dot_lifespan_sec        = 5.0,
            dot_size                = 3.0,
            num_dots                = 100)
        text = VisionEgg.Text.Text(
            text = "Vision Egg dot_simple_loop demo.",
            position = (screen.size[0]/2,2),
            anchor = 'bottom',
            color = (1.0,1.0,1.0))
        
        self.screen = screen
        self.viewport = VisionEgg.Core.Viewport( screen=screen, stimuli=[self.dots,text] )
        self.frame_timer = VisionEgg.Core.FrameTimer()
        self.quit_now = False

    def set_signal_fraction(self,f):
        self.dots.set(signal_fraction=f)

    def quit(self):
        self.quit_now = True

    def mainloop(self):
        pyro_timeout = 0.0 # just check for any already events present
        while not self.quit_now:
            
            for event in pygame.event.get():
                if event.type in (pygame.locals.QUIT,
                                  pygame.locals.KEYDOWN,
                                  pygame.locals.MOUSEBUTTONDOWN):
                    self.quit_now = True
            self.pyro_daemon.handleRequests(pyro_timeout)
            
            self.screen.clear()
            self.viewport.draw()
            VisionEgg.Core.swap_buffers()
            self.frame_timer.tick()
            
        self.frame_timer.log_histogram()

def main():
    screen = VisionEgg.Core.get_default_screen()
    
    Pyro.core.initServer(banner=0)
    hostname = 'localhost'
    port = 4321
    daemon = Pyro.core.Daemon(host=hostname,port=port)
    dot_server_instance = DotServer()
    dot_server_instance.post_init(screen,daemon)
    URI=daemon.connect(dot_server_instance,'DotServer')
    dot_server_instance.mainloop()

if __name__=='__main__':
    main()
