"""Displays a mouse-controlled target in a custom user loop,
using pyglet (see pyglet.org). Demonstrates pyglet event handling.

In pyglet 1.0b3, a given window might not appear on its associated
physical screen unless set to fullscreen (see VISIONEGG_FULLSCREEN
in VisionEgg.cfg)"""

from __future__ import division

import math
import pyglet.window
import pyglet.window.key as key
import pyglet.window.mouse as mouse
import OpenGL.GL as gl

import VisionEgg.Core
from VisionEgg.MoreStimuli import Target2D
from VisionEgg.Text import Text


class MouseTarget(object):
    """Mouse-controlled target"""
    def __init__(self):
        # Init signals
        self.UP, self.DOWN, self.LEFT, self.RIGHT = False, False, False, False
        self.PLUS, self.MINUS = False, False
        self.LEFTBUTTON, self.RIGHTBUTTON, self.SCROLL = False, False, False
        self.x = 400
        self.y = 300
        self.width = 50
        self.height = 10
        self.sizerate = 2
        self.ori = 0
        self.snapDeg = 18
        self.orirate = 0.5
        self.brightness = 1
        self.brightnessstep = 0.01
        self.antialiase = True
        self.exclusive_mouse = True

    def createstimuli(self):
        """Creates the VisionEgg stimuli objects"""
        self.target = Target2D(anchor='center',
                               anti_aliasing=self.antialiase,
                               color=(self.brightness, self.brightness, self.brightness, 1.0))
        self.tp = self.target.parameters # synonym

        self.tip = Target2D(size=(5, 1),
                            anchor='center',
                            anti_aliasing=self.antialiase,
                            color=(1, 0, 0, 1))
        self.tipp = self.tip.parameters

        ##TODO: switch to pyglet.font
        self.text = Text(position=(0, 6),
                         anchor='left',
                         color=(0, 1, 0, 1),
                         texture_mag_filter=gl.GL_NEAREST,
                         font_size=20)
        self.textp = self.text.parameters

        self.help = Text(text=r'ESC exits, LEFT, RIGHT, UP, DOWN, +/-, mouse buttons, and scroll wheel control bar',
                         position=(400, 300),
                         anchor='center',
                         color=(1, 0, 0, 1),
                         texture_mag_filter=gl.GL_NEAREST,
                         font_size=20)

        # last entry will be topmost layer in viewport
        self.stimuli = (self.target, self.tip, self.text, self.help)

    def get_targetsize(self):
        """Get target width and height"""
        if self.UP:
            self.height += self.sizerate
        elif self.DOWN:
            self.height = max(self.height-self.sizerate, 1)
        if self.RIGHT:
            self.width += self.sizerate
        elif self.LEFT:
            self.width = max(self.width-self.sizerate, 1)

    def get_targetori(self):
        """Get target orientation, make scrolling snap to nearest snapDeg ori step"""
        if self.SCROLL:
            mod = self.ori % self.snapDeg
            if mod:
                if self.SCROLL > 0: # snap up
                    self.ori += -mod + self.SCROLL * self.snapDeg
                else: # snap down
                    self.ori -= mod
            else: # snap up or down by a full snapDeg ori step
                self.ori += self.SCROLL * self.snapDeg
            self.SCROLL = False
        elif self.LEFTBUTTON:
            self.ori += self.orirate
        elif self.RIGHTBUTTON:
            self.ori -= self.orirate
        self.ori = self.ori % 360 # keep it in [0, 360)

    def get_targetbrightness(self):
        """Get target brightness"""
        if self.PLUS:
            self.brightness += self.brightnessstep
        elif self.MINUS:
            self.brightness -= self.brightnessstep
        self.brightness = max(self.brightness, 0) # keep it >= 0
        self.brightness = min(self.brightness, 1) # keep it <= 1

    def updatestimuli(self):
        """Update stimuli"""
        # Update target params
        self.tp.position = self.x, self.y
        self.tp.size = self.width, self.height
        self.tp.orientation = self.ori
        self.tp.color = (self.brightness, self.brightness, self.brightness, 1)
        self.tipp.position = ( self.x + self.width / 2 * math.cos(math.pi / 180 * self.ori),
                               self.y + self.width / 2 * math.sin(math.pi / 180 * self.ori) )
        self.tipp.orientation = self.ori
        # Update text
        self.textp.text = 'x, y = (%d, %d)  |  size = (%d, %d)  |  ori = %5.1f' \
                          % (self.x, self.y, self.width, self.height, self.ori)

    def on_mouse_motion(self, x, y, dx, dy):
        """Update target position"""
        if self.exclusive_mouse:
            # need to use dx/dy when using exclusive_mouse
            self.x += dx
            self.y += dy
            self.x = min(max(self.x, 0), self.wins[0].win.width) # constrain it to the first window
            self.y = min(max(self.y, 0), self.wins[0].win.height)
        else:
            self.x = x
            self.y = y

    def on_key_press(self, symbol, modifiers):
        if symbol == key.UP:
            self.UP = True
        elif symbol == key.DOWN:
            self.DOWN = True
        elif symbol == key.RIGHT:
            self.RIGHT = True
        elif symbol == key.LEFT:
            self.LEFT = True
        elif symbol == key.EQUAL:
            self.PLUS = True
        elif symbol == key.MINUS:
            self.MINUS = True

    def on_key_release(self, symbol, modifiers):
        if symbol == key.UP:
            self.UP = False
        elif symbol == key.DOWN:
            self.DOWN = False
        elif symbol == key.RIGHT:
            self.RIGHT = False
        elif symbol == key.LEFT:
            self.LEFT = False
        elif symbol == key.EQUAL:
            self.PLUS = False
        elif symbol == key.MINUS:
            self.MINUS = False

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.LEFTBUTTON = True
        elif button == mouse.RIGHT:
            self.RIGHTBUTTON = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.LEFTBUTTON = False
        elif button == mouse.RIGHT:
            self.RIGHTBUTTON = False

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.SCROLL = scroll_y / abs(scroll_y) # +ve or -ve scroll click

    def attach_handlers(self):
        for win in self.wins:
            win.win.push_handlers(self.on_mouse_motion)
            win.win.push_handlers(self.on_key_press)
            win.win.push_handlers(self.on_key_release)
            win.win.push_handlers(self.on_mouse_press)
            win.win.push_handlers(self.on_mouse_release)
            win.win.push_handlers(self.on_mouse_scroll)

    def exit(self):
        """Check if any windows have the has_exit attrib set True"""
        quit = False
        for win in self.wins:
            if win.win.has_exit:
                quit = True
        return quit

    def run(self):
        """Run the stimulus"""
        # Init OpenGL graphics windows, one window per requested screen
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        self.screens = display.get_screens()
        self.wins = []
        for screen in self.screens:
            win = VisionEgg.Core.get_default_window(screen=screen)
            win.win.set_exclusive_mouse(self.exclusive_mouse)
            self.wins.append(win)

        # Create VisionEgg stimuli objects, defined by each specific subclass of Experiment
        self.createstimuli()

        # Create viewport(s), all with identical stimuli
        self.viewports = []
        for win in self.wins:
            viewport = VisionEgg.Core.pyglet_Viewport(window=win, stimuli=self.stimuli)
            self.viewports.append(viewport)

        self.attach_handlers()

        # Run the main stimulus loop
        self.main()

        # Close OpenGL graphics windows (necessary when running from Python interpreter)
        for win in self.wins:
            win.close()

    def main(self):
        """Run the main stimulus loop"""
        while not self.exit():

            for win in self.wins:
                win.dispatch_events() # to the event handlers

            self.get_targetsize()
            self.get_targetori()
            self.get_targetbrightness()
            self.updatestimuli()

            for win, viewport in zip(self.wins, self.viewports):
                win.switch_to()
                win.clear()
                viewport.draw()
                win.flip()


if __name__ == '__main__':
    mt = MouseTarget()
    mt.run()
