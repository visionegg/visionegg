"""VisionEgg Core Library
"""

# Copyright (c) 2001, 2002 Andrew Straw.  Distributed under the terms
# of the GNU General Public License (GPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

from VisionEgg import *                         # Vision Egg package
import PlatformDependent                        # platform dependent Vision Egg C code

import pygame                                   # pygame handles OpenGL window setup
import pygame.locals
			                        # from PyOpenGL:
from OpenGL.GL import *                         #   main package
from OpenGL.GLU import *                        #   utility routines

from Numeric import * 				# Numeric Python package
from MLab import *                              # Matlab function imitation from Numeric Python

############# What function do we use to swap the buffers? #########
swap_buffers = pygame.display.flip

####################################################################
#
#        Screen
#
####################################################################

class Screen:
    """Contains one or more viewports.

    Currently only one screen is supported, but hopefully multiple
    screens will be supported in the future.
    """

    def __init__(self,
                 size=(config.VISIONEGG_SCREEN_W,
                       config.VISIONEGG_SCREEN_H),
                 fullscreen=config.VISIONEGG_FULLSCREEN,
                 preferred_bpp=config.VISIONEGG_PREFERRED_BPP,
                 bgcolor=config.VISIONEGG_SCREEN_BGCOLOR,
                 maxpriority=config.VISIONEGG_MAXPRIORITY):
        self.size = size
        self.fullscreen = fullscreen 

        PlatformDependent.sync_swap_with_vbl(failure_ok = 0)

        pygame.display.init()
        if hasattr(pygame.display,"gl_set_attribute"):
            pygame.display.gl_set_attribute(pygame.locals.GL_ALPHA_SIZE,8)
        else:
            print "WARNING: Could not request alpha in framebuffer because you have an old version of pygame."
        pygame.display.set_caption("Vision Egg")
        flags = pygame.locals.OPENGL | pygame.locals.DOUBLEBUF
        if self.fullscreen:
            flags = flags | pygame.locals.FULLSCREEN

        # Choose an appropriate framebuffer pixel representation
        try_bpps = [32,24,0] # bits per pixel (32 = 8 bits red, 8 green, 8 blue, 8 alpha, 0 = any)
        try_bpps.insert(0,preferred_bpp) # try the preferred size first

        # SDL, and therefore pygame, has problems on linux when trying
        # to acheive a 32 bpp depth, at least on any of the (nVidia)
        # setups I've tried.  This is a real killer when trying to use
        # alpha in the framebuffer.
        
        # I workaround this by modifying "display.c" in the pygame
        # sourcecode where I've added
        # "SDL_GL_SetAttribute(SDL_GL_ALPHA_SIZE, 8);" before
        # "SDL_SetVideoMode(w, h, depth, flags);"

        # Until this is fixed in SDL and pygame, the following
        # special case for linux must stay. :(
        
        if sys.platform=='linux2': 
            try:
                while 1:
                    try_bpps.remove(32)
            except:
                pass
        
        found_mode = 0
        for bpp in try_bpps:
            modeList = pygame.display.list_modes( bpp, flags )
            if modeList == -1: # equal to -1 if any resolution will work
                found_mode = 1
            else:
                if len(modeList) == 0: # any resolution is OK
                    found_mode = 1
                else:
                    if self.size in modeList:
                        found_mode = 1
                    else:
                        self.size = modeList[0]
                        print "WARNING: Using %dx%d video mode instead of requested size."%(self.size[0],self.size[1])
            if found_mode: # found the color depth to tell pygame
                try_bpp = bpp 
                break
        if found_mode == 0:
            print "WARNING: Could not find acceptable video mode! Trying anyway with bpp=0..."
            try_bpp = 0 # At least try something!

        print "Initializing graphics at %d x %d ( %d bpp )."%(self.size[0],self.size[1],try_bpp)
        try:
            pygame.display.set_mode(self.size, flags, try_bpp )
        except pygame.error, x:
            print "FATAL VISION EGG ERROR:",x
            sys.exit(1)

        self.bpp = pygame.display.Info().bitsize
        print "Video system reports %d bpp"%self.bpp
        if self.bpp < try_bpp:
            print "************ VISION EGG WARNING ***************"
            print "Video system reports %d bits per pixel, while your"%try_bpp
            print "program requested %d.  (Try setting your video"%self.bpp
            print "drivers to 32 bpp, sometimes called TrueColor.)"
        self.cursor_visible_func = pygame.mouse.set_visible

        # Check previously made OpenGL assumptions
        check_gl_assumptions()
        
        if self.fullscreen:
            self.cursor_visible_func(0)

        self.parameters = Parameters()
        self.parameters.bgcolor = bgcolor

        # Attempt to set maximum priority
        # (This may not be the best place in the code to do it,
        # because it's an application-level thing, not a screen-level
        # thing, but it fits reasonably well here for now.)
        if maxpriority: 
            PlatformDependent.set_realtime()

    def clear(self):
        c = self.parameters.bgcolor # Shorthand
        glClearColor(c[0],c[1],c[2],c[3])
        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)

    def make_current(self):
        """Makes screen active for drawing.

        Can not be implemented until multiple screens are possible."""
        pass

    def __del__(self):
        """Make sure mouse is visible after screen closed."""
        self.cursor_visible_func(1)
        
####################################################################
#
#        Viewport
#
####################################################################

class Viewport:
    """A portion of a screen which shows stimuli.

    A screen may have multiple viewports.  The viewports may be
    overlapping.  """
    def __init__(self,screen,lower_left,size,projection=None):
        self.screen = screen
        self.stimuli = []
        self.parameters = Parameters()
        self.parameters.lower_left = lower_left
        self.parameters.size = size
        if projection is None:
            # Default projection maps object coordinates 1:1 on viewport pixel coordinates
            self.parameters.projection = OrthographicProjection(left=0,right=self.parameters.size[0],
                                                                bottom=0,top=self.parameters.size[1],
                                                                z_clip_near=0.0,
                                                                z_clip_far=1.0)
        else:
            self.parameters.projection = projection

    def add_stimulus(self,stimulus,draw_order=-1):
        """Add a stimulus to the list of those drawn in the viewport

        By default, the stimulus is drawn last, but this behavior
        can be changed with the draw_order argument.
        """
        if draw_order == -1:
            self.stimuli.append(stimulus)
        else:
            self.stimuli.insert(draw_order,stimulus)

    def remove_stimulus(self,stimulus):
        self.stimuli.remove(stimulus)

    def draw(self):
        """Set the viewport and draw stimuli."""
        self.screen.make_current()
        glViewport(self.parameters.lower_left[0],self.parameters.lower_left[1],self.parameters.size[0],self.parameters.size[1])

        self.parameters.projection.set_gl_projection()
        
        for stimulus in self.stimuli:
            stimulus.draw()

####################################################################
#
#        Projection and derived classes
#
####################################################################

class Projection:
    """Abstract base class to define interface for OpenGL projection matrices"""
    def __init__(self):
        raise RuntimeError("Trying to instantiate an abstract base class.")

    def set_gl_projection(self):
        """Set the OpenGL projection matrix."""
        glMatrixMode(GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        glLoadMatrixf(self.parameters.matrix)

    def push_and_set_gl_projection(self):
        """Set the OpenGL projection matrix, pushing current projection matrix to stack."""
        glMatrixMode(GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        glPushMatrix()
        glLoadMatrixf(self.parameters.matrix)

    def translate(self,x,y,z):
        """Compose a translation and set the OpenGL projection matrix."""
        glMatrixMode(GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        glLoadMatrixf(self.parameters.matrix)
        glTranslatef(x,y,z)
        self.parameters.matrix = glGetFloatv(GL_PROJECTION_MATRIX)

    def stateless_translate(self,x,y,z):
        """Compose a translation without changing OpenGL state."""
        matrix_mode = glGetInteger(GL_MATRIX_MODE)
        glMatrixMode(GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        glPushMatrix()
        glLoadMatrixf(self.parameters.matrix)
        glTranslatef(x,y,z)
        self.parameters.matrix = glGetFloatv(GL_PROJECTION_MATRIX)
        glPopMatrix()
        if matrix_mode is not None:
            glMatrixMode(matrix_mode)

    def rotate(self,angle_degrees,x,y,z):
        """Compose a rotation and set the OpenGL projection matrix."""
        glMatrixMode(GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        glLoadMatrixf(self.parameters.matrix)
        glRotatef(angle_degrees,x,y,z)
        self.parameters.matrix = glGetFloatv(GL_PROJECTION_MATRIX)

    def stateless_rotate(self,angle_degrees,x,y,z):
        """Compose a rotation without changing OpenGL state."""
        matrix_mode = glGetInteger(GL_MATRIX_MODE)
        glMatrixMode(GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        glPushMatrix()
        glLoadMatrixf(self.parameters.matrix)
        glRotatef(angle_degrees,x,y,z)
        self.parameters.matrix = glGetFloatv(GL_PROJECTION_MATRIX)
        glPopMatrix()
        if matrix_mode is not None:
            glMatrixMode(matrix_mode)

class OrthographicProjection(Projection):
    """An orthographic projection"""
    def __init__(self,left=0.0,right=640.0,bottom=0.0,top=480.0,z_clip_near=0.0,z_clip_far=1.0):
        """Create an orthographic projection.

        Defaults to map x eye coordinates in the range [0,640] to clip
        coordinates in the range [0,1] and y eye coordinates [0,480]
        -> [0,1].  In other words, if the viewport is 640 x 480, eye
        coordinates correspond 1:1 with window coordinates."""
        self.parameters = Parameters()
        glMatrixMode(GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        glLoadIdentity() # Clear the projection matrix
        glOrtho(left,right,bottom,top,z_clip_near,z_clip_far) # Let GL create a matrix and compose it
        self.parameters.matrix = glGetFloatv(GL_PROJECTION_MATRIX)

class SimplePerspectiveProjection(Projection):
    """A simplified perspective projection"""
    def __init__(self,fov_x=45.0,z_clip_near = 0.1,z_clip_far=100.0,aspect_ratio=4.0/3.0):
        self.parameters = Parameters()
        fov_y = fov_x / aspect_ratio
        glMatrixMode(GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        glLoadIdentity() # Clear the projection matrix
        gluPerspective(fov_y,aspect_ratio,z_clip_near,z_clip_far) # Let GLU create a matrix and compose it
        self.parameters.matrix = glGetFloatv(GL_PROJECTION_MATRIX)

class PerspectiveProjection(Projection):
    """A perspective projection"""
    def __init__(self,left,right,bottom,top,near,far):
        self.parameters = Parameters()
        glMatrixMode(GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        glLoadIdentity() # Clear the projection matrix
        glFrustrum(left,right,top,bottom,near,far) # Let GL create a matrix and compose it
        self.parameters.matrix = glGetFloatv(GL_PROJECTION_MATRIX)

####################################################################
#
#        Parameters
#
####################################################################

class Parameters:
    """Hold stimulus parameters.

    This abstraction of parameters is useful so that parameters can be
    controlled via any number of means: evaluating a python function,
    acquiring some data with a digital or analog input, etc.

    All parameters (such as contrast, position, etc.) which should be
    modifiable in runtime should be attributes of an instance of this
    class, which serves as a nameholder for just this purpose.

    See the Presentation class for more information about parameters
    and controllers.
    """
    pass

####################################################################
#
#        Stimulus - Base class
#
####################################################################

class Stimulus:
    """Base class for a stimulus.

    Any stimulus element should be a subclass of this Stimulus class.
    The draw() method contains the code executed before every buffer
    swap in order to render the stimulus to the frame buffer.  It
    should execute as quickly as possible.  The init_gl() method must
    be called before the first call to draw() so that any internal
    data, OpenGL display lists, and OpenGL:texture objects can be
    established.
    
    If your experiment displays two spots simultaneously, you could
    create two instances of (a single subclass of) Stimulus, varying
    parameters so each draws at a different location.  Another
    possibility is to create one instance of a subclass that draws two
    spots.  A third possibility is to create a single instance and add
    it to two different viewports.  (Something that will not work
    would be adding the same instance two times to the same viewport.
    It would also get drawn twice, although at exactly the same
    location.)
    
    OpenGL is a 'state machine', meaning that it has internal
    parameters whose values vary and affect how it operates.  Because
    of this inherent uncertainty, there are only limited assumptions
    about the state of OpenGL that an instance of Stimulus should
    expect when its draw() method is called.  Because the Vision Egg
    loops through stimuli this also imposes some rules that a
    well-behaved subclass of Stimulus must follow.
    
    First, the framebuffer will contain the results of any drawing
    operations performed since the last buffer swap by other instances
    of (subclasses of) Stimulus. Therefore, the order in which stimuli
    are added to an instance of Viewport may be important.
    Additionally, if there are overlapping viewports, the order in
    which viewports are added to an instance of Screen may be
    important.

    Second, the projection matrix will be that which was set by the
    viewport. Note that for some stimuli, you will want the stimulus
    to set its own projection.  Most 2D objects should probably define
    their own projection, which will specify where, in relation to the
    viewport, the object is drawn.  3D objects should probably let the
    viewport's default projection be used.   To be well-behaved, if the draw() method alters the
    projection matrix, it must be restored.  The glPushMatrix() and
    glPopMatrix() commands provide an easy way to do this.  (See the
    FixationSpot class for an example.)

    Third, previously established OpenGL display lists and OpenGL
    texture objects will be available.  The method init_gl() is
    provided to establish these things.

    Fourth, there are several OpenGL state variables which are
    commonly set by subclasses of Stimulus, and which cannot be
    assumed to have any particular value at the time draw() is called.
    These state variables are: blending mode and function, texture
    state and environment, the matrix mode (modelview or projection),
    the modelview matrix, depth mode and settings. Therefore, if the
    draw() method depends on specific values for any of these states,
    it must specify its own values to OpenGL.

    Finally, a well-behaved Stimulus subclass resets any OpenGL state
    values other than those listed above to their initial state before
    draw() and init_gl() were called.  In other words, before your
    stimulus changes the state of an OpenGL variable, use
    glGetBoolean, glGetInteger, glGetFloat, or a similar function to 
    query its value and restore it later.
    """
    def __init__(self):
        self.parameters = Parameters()
        
    def draw(self):
    	"""Draw the stimulus.  This method is called every frame.
    
        This method actually performs the OpenGL calls to draw the
        stimulus. In this base class, however, it does nothing."""
        pass
        
    def init_gl(self):
        """Get OpenGL ready to do everything in the draw() method.

        This method typically loads texture objects and creates
        display lists.  In this base class, however, it does nothing."""
        pass

####################################################################
#
#        FixationSpot
#
####################################################################

class FixationSpot(Stimulus):
    def __init__(self,position=(320,240),projection=None):
        """Create a fixation spot.
        
        If no projection is specified, assume the position of the
        fixation spot, which is by default equal to (320,240), is in
        the middle of the viewport.
        """
        self.parameters = Parameters()
        self.parameters.on = 1
        if projection is None:
            # assume spot is in center of viewport
            w,h=(position[0]*2.0,position[1]*2.0)
            self.parameters.projection = OrthographicProjection(right=w,top=h)
        else:
            self.parameters.projection = projection
            
        self.parameters.size = 5.0 # length of side
        self.parameters.color = (1.0,1.0,1.0,1.0)
        self.parameters.position = position

    def init_gl(self):
        pass

    def draw(self):
        if self.parameters.on:
            glDisable(GL_DEPTH_TEST)
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # before we set the projection matrix, push its state
            self.parameters.projection.push_and_set_gl_projection()

            c = self.parameters.color
            glColor(c[0],c[1],c[2],c[3])

            # This could go in a display list to speed it up, but then
            # size wouldn't be dynamically adjustable this way.  Could
            # still use one of the matrices to make it change size.
            size = self.parameters.size/2.0 # self.parameters.size is in pixels
            x,y = self.parameters.position
            x1 = x-size; x2 = x+size
            y1 = y-size; y2 = y+size
            glBegin(GL_QUADS)
            glVertex2f(x1,y1)
            glVertex2f(x2,y1)
            glVertex2f(x2,y2)
            glVertex2f(x1,y2)
            glEnd() # GL_QUADS

            glPopMatrix() # restore projection matrix

####################################################################
#
#        Presentation
#
####################################################################

class Presentation:
    """Handles the timing and coordination of stimulus presentation.

    This class is the key to the real-time operation of the Vision
    Egg. It contains the mainloop, and maintains the association
    between 'controllers' and the parameters they control.  During the
    mainloop, the parameters are updated via function calls to the
    controllers.  A controller can be called once every frame (the
    realtime controllers) or called before and after any stimulus
    presentations (the transitional_controllers).  All controllers are
    called as frequently as possible between stimulus presentations.

    There is no class named Controller that must be subclassed.
    Instead, any function which takes a single argument can be used as
    a controller.  (However, for a controller which can be used from a
    remote computer, see the PyroController class of the PyroHelpers
    module.)

    There are two types of realtime controllers and one transitional
    controller.

    All contollers are passed a negative value when a stimulus is not
    being displayed and a non-negative value when the stimulus is
    being displayed.  realtime_time_controllers are passed the current
    time (in seconds) since the beginning of a stimulus, while
    realtime_frame_controllers are passed the current frame number
    since the beginning of a stimulus.  Immediately prior to drawing
    the first frame of a stimulus presentation, all controllers are
    passed a value of zero.

    The realtime_time and realtime_frame controllers are meant to be
    'realtime', but the term realtime here is a bit hopeful at this
    stage. This is because no OpenGL environment I know of can
    guarantee that a new frame is drawn and the double buffers swapped
    before the monitor's next vertical retrace sync pulse.  Still,
    although one can worry endlessly about this problem, it works.  In
    other words, on a fast computer with a fast graphics card running
    even a pre-emptive multi-tasking operating system (insert name of
    your favorite operating system here), a new frame is drawn before
    every vertical retrace sync pulse.
    """
    
    def __init__(self,viewports=[],duration=(5.0,'seconds')):
        self.parameters = Parameters()
        self.parameters.viewports = viewports
        self.parameters.duration = duration
        self.realtime_time_controllers = []
        self.realtime_frame_controllers = []
        self.transitional_controllers = []
        self.frame_draw_times = []

    def add_realtime_time_controller(self, parameters, name, controller):
        if not isinstance(parameters,Parameters):
            raise ValueError('"%s" is not an instance of %s'%(parameters,Parameters))
        if not hasattr(parameters,name):
            raise AttributeError('"%s" not an attribute of %s'%(name,parameters))
        self.realtime_time_controllers.append((parameters,name,controller))

    def remove_realtime_time_controller(self, parameters, name):
        if not isinstance(parameters,Parameters):
            raise ValueError('"%s" is not an instance of %s'%(parameters,Parameters))
        if not hasattr(parameters,name):
            raise AttributeError('"%s" not an attribute of %s'%(name,parameters))
        i = 0
        while i < len(self.realtime_time_controllers):
            orig_parameters,orig_name,orig_controller = self.realtime_time_controllers[i]
            if orig_parameters == parameters and orig_name == name:
                del self.realtime_time_controllers[i]
            else:
                i = i + 1

    def add_realtime_frame_controller(self, parameters, name, controller):
        if not isinstance(parameters,Parameters):
            raise ValueError('"%s" is not an instance of %s'%(parameters,Parameters))
        if not hasattr(parameters,name):
            raise AttributeError('"%s" not an attribute of %s'%(name,parameters))
        self.realtime_frame_controllers.append((parameters,name,controller))

    def remove_realtime_frame_controller(self, parameters, name):
        if not isinstance(parameters,Parameters):
            raise ValueError('"%s" is not an instance of %s'%(parameters,Parameters))
        if not hasattr(parameters,name):
            raise AttributeError('"%s" not an attribute of %s'%(name,parameters))
        i = 0
        while i < len(self.realtime_frame_controllers):
            orig_parameters,orig_name,orig_controller = self.realtime_frame_controllers[i]
            if orig_parameters == parameters and orig_name == name:
                del self.realtime_frame_controllers[i]
            else:
                i = i + 1

    def add_transitional_controller(self, parameters, name, controller):
        if not isinstance(parameters,Parameters):
            raise ValueError('"%s" is not an instance of %s'%(parameters,Parameters))
        if not hasattr(parameters,name):
            raise AttributeError('"%s" not an attribute of %s'%(name,parameters))
        self.transitional_controllers.append((parameters,name,controller))

    def remove_transitional_controller(self, parameters, name):
        if not isinstance(parameters,Parameters):
            raise ValueError('"%s" is not an instance of %s'%(parameters,Parameters))
        if not hasattr(parameters,name):
            raise AttributeError('"%s" not an attribute of %s'%(name,parameters))
        i = 0
        while i < len(self.transitional_controllers):
            orig_parameters,orig_name,orig_controller = self.transitional_controllers[i]
            if orig_parameters == parameters and orig_name == name:
                del self.transitional_controllers[i]
            else:
                i = i + 1

    def go(self,collect_timing_info=0):
        """Main control loop during stimulus presentation.

        This is the heart of realtime control in the Vision Egg, and
        contains the main loop during a stimulus presentation.

        First, all controllers (realtime and transitional) are called
        and update their parameters for the start of the
        stimulus. Next, data acquisition is readied. Finally, the main
        loop is entered.

        In the main loop, the current stimulus-relative time is
        computed, the realtime controllers are called with this
        information, the screen is cleared, each viewport is drawn to
        the back buffer (while the video card continues painting the
        front buffer on the display), and the buffers are
        swapped. Unfortunately, there is no system independent way to
        synchronize buffer swapping with the vertical retrace period.
        It usually depends on your operating system, your video card,
        and your video drivers.  (This should be remedied in OpenGL 2.)
        """
        # Create a few shorthand notations, which speeds
        # the main loop by not performing name lookup each time.
        duration_value = self.parameters.duration[0]
        duration_units = self.parameters.duration[1]
        viewports = self.parameters.viewports

        # Get list of screens
        screens = []
        for viewport in viewports:
            if viewport.screen not in screens:
                screens.append(viewport.screen)

        # Tell transitional controllers a presentation is starting
        for parameters,name,controller in self.transitional_controllers:
            setattr(parameters,name,controller(0.0))

        # Clear any previous timing info if necessary
        if collect_timing_info:
            self.frame_draw_times = []

        # Still need to add DAQ hooks here...

        # Do the main loop
        start_time_absolute = timing_func()
        current_time = 0.0
        current_frame = 0
        if duration_units == 'seconds':
            current_duration_value = current_time
        elif duration_units == 'frames':
            current_duration_value = current_frame
        else:
            raise RuntimeError("Unknown duration unit '%s'"%duration_units)
        while (current_duration_value < duration_value):
            # Update all the realtime parameters
            for parameters,name,controller in self.realtime_time_controllers:
                setattr(parameters,name,controller(current_time))
            for parameters,name,controller in self.realtime_frame_controllers:
                setattr(parameters,name,controller(current_frame))
            # Clear the screen(s)
            for screen in screens:
                screen.clear()
            # Draw each viewport
            for viewport in viewports:
                viewport.draw()
            # Swap the buffers
            swap_buffers()
            # If wanted, save time this frame was drawn for
            if collect_timing_info:
                self.frame_draw_times.append(current_time)
            # Get the time for the next frame
            current_time_absolute = timing_func()
            current_time = current_time_absolute-start_time_absolute
            current_frame = current_frame + 1
            # Make sure we use the right value to check if we're done
            if duration_units == 'seconds':
                current_duration_value = current_time
            elif duration_units == 'frames':
                current_duration_value = current_frame
            else:
                raise RuntimeError("Unknown duration unit '%s'"%duration_units)

        self.between_presentations() # Call at end of stimulus to reset values

        # Check to see if frame by frame control was desired
        # but OpenGL not syncing to vertical retrace
        if len(self.realtime_frame_controllers) > 0: # Frame by frame control desired
            impossibly_fast_frame_rate = 205.0
            if current_frame / current_time > impossibly_fast_frame_rate: # Let's assume no monitor exceeds 200 Hz
                print
                print "**************************************************************"
                print
                print "PROBABLE VISION EGG ERROR: Frame by frame control desired, but"
                print "average frame rate was %f frames per second-- faster than any"%(current_frame / current_time)
                print "display device (that I know of).  Set your drivers"
                print "to sync buffer swapping to vertical retrace. (platform/driver dependent)"
                print
                print "**************************************************************"
                print
        if collect_timing_info:
            self.print_frame_timing_stats()

    def between_presentations(self):
        """Maintain display while between stimulus presentations.

        This function gets called as often as possible when not
        in the 'go' loop.

        To indicate to the controllers that a stimulus is not in
        progress, instead of passing a positive stimulus-relative
        time, it passes a negative value to the controller.
        Therefore, a controller should assume any negative time value
        means it is between stimulus presentations.

        It would be cleaner to have a separate parameter passed to the
        controller that indicates this status, but because the
        controller code is performance-critical, we'll just make do
        with this.

        Other than the difference in the time passed to the
        controllers, this routine is very similar to the inside of the
        main loop in the go method.
        """
        # For each controller, let it do its thing
        # Pass value of -1.0 to indicate between stimulus status
        #
        # This works by evaluating the function "controller" and
        # putting the results in parameters.name.
        # It's like "parameters.name = controller(-1.0)", but name is
        # a string, so it must be called this way.
        for parameters,name,controller in self.realtime_time_controllers:
            setattr(parameters,name,controller(-1.0))
        for parameters,name,controller in self.realtime_frame_controllers:
            setattr(parameters,name,controller(-1))
        for parameters,name,controller in self.transitional_controllers:
            setattr(parameters,name,controller(-1.0))

        viewports = self.parameters.viewports

        # Get list of screens
        screens = []
        for viewport in viewports:
            if viewport.screen not in screens:
                screens.append(viewport.screen)
            
        # Clear the screen(s)
        for screen in screens:
            screen.clear()
        # Draw each viewport
        for viewport in viewports:
            viewport.draw()
        swap_buffers()

    def export_movie_go(self, frames_per_sec=12.0, filename_suffix=".tif", filename_base="visionegg_movie", path="."):
        """Call this method rather than go() to save a movie of your experiment.
        """
        import Image # Could import this above, but it breaks stuff!
        
        for parameters,name,controller in self.realtime_time_controllers:
            setattr(parameters,name,controller(0.0))
        for parameters,name,controller in self.realtime_frame_controllers:
            setattr(parameters,name,controller(0))
        for parameters,name,controller in self.transitional_controllers:
            setattr(parameters,name,controller(0.0))

        # Create a few shorthand notations, which speeds
        # the main loop by not performing name lookup each time.
        duration_value = self.parameters.duration[0]
        duration_units = self.parameters.duration[1]
        viewports = self.parameters.viewports

        # Get list of screens
        screens = []
        for viewport in viewports:
            if viewport.screen not in screens:
                screens.append(viewport.screen)

        if len(screens) > 1:
            raise EggError("Can only export movie of one screen")

        current_time = 0.0
        current_frame = 0
        image_no = 1
        if duration_units == 'seconds':
            current_duration_value = current_time
        elif duration_units == 'frames':
            current_duration_value = current_frame
        else:
            raise RuntimeError("Unknown duration unit '%s'"%duration_units)
        while (current_duration_value < duration_value):
            # Update all the realtime parameters
            for parameters,name,controller in self.realtime_time_controllers:
                setattr(parameters,name,controller(current_time))
            for parameters,name,controller in self.realtime_frame_controllers:
                setattr(parameters,name,controller(current_frame))
            # Clear the screen(s)
            for screen in screens:
                screen.clear()
            # Draw each viewport
            for viewport in viewports:
                viewport.draw()
            swap_buffers()

            # Now save the contents of the framebuffer
            glPixelStorei(GL_PACK_ALIGNMENT, 1)
            framebuffer = glReadPixels(0,0,screen.size[0],screen.size[1],GL_RGB,GL_UNSIGNED_BYTE)
            fb_image = Image.fromstring('RGB',screen.size,framebuffer)
            fb_image = fb_image.transpose( Image.FLIP_TOP_BOTTOM )
            filename = "%s%04d%s"%(filename_base,image_no,filename_suffix)
            savepath = os.path.join( path, filename )
            print "Saving '%s'"%filename
            fb_image.save( savepath )
            image_no = image_no + 1
            current_time = current_time + 1.0/frames_per_sec
            current_frame = current_frame + 1
            if duration_units == 'seconds':
                current_duration_value = current_time
            elif duration_units == 'frames':
                current_duration_value = current_frame
            else:
                raise RuntimeError("Unknown duration unit '%s'"%duration_units)

    def print_frame_timing_stats(self):
        """Print a histogram of the last recorded frame drawing times.
        """
        if len(self.frame_draw_times) > 1:
            frame_draw_times = array(self.frame_draw_times)
            self.frame_draw_times = [] # clear the list
            frame_draw_times = frame_draw_times[1:] - frame_draw_times[:-1] # get inter-frame interval
            print (len(frame_draw_times)+1), "frames drawn."
            mean_sec = mean(frame_draw_times)
            print "mean frame to frame time:", mean_sec*1.0e6, "(usec), fps: ",1.0/mean_sec, " max:",max(frame_draw_times)*1.0e6
            
            bins = arange(0.0,15.0,1.0) # msec
            bins = bins*1.0e-3 # sec
            print "Frame to frame"
            self.print_hist(frame_draw_times,bins)
            print

    def histogram(self,a, bins):  
        """Create a histogram from data

        This function is taken straight from NumDoc.pdf, the Numeric Python
        documentation."""
        n = searchsorted(sort(a),bins)
        n = concatenate([n, [len(a)]])
        return n[1:]-n[:-1]
        
    def print_hist(self,a, bins):
        """Print a pretty histogram"""
        hist = self.histogram(a,bins)
        lines = 10
        maxhist = float(max(hist))
        h = hist # copy
        hist = hist.astype('f')/maxhist*float(lines) # normalize to 10
        print "Histogram:"
        for line in range(lines):
            val = float(lines)-1.0-float(line)
            print "%6d"%(round(maxhist*val/10.0),),
            q = greater(hist,val)
            for qi in q:
                s = ' '
                if qi:
                    s = '*'
                print "%5s"%(s,),
            print
        print " Time:",
        for bin in bins:
            print "%5.2f"%(bin*1.0e3,),
        print "+",
        print "(msec)"
        print "Total:",
        for hi in h:
            print "%5d"%(hi,),
        print
        
####################################################################
#
#        Error handling and assumption checking
#
####################################################################
    
class EggError(Exception):
    """Created whenever a Vision Egg specific error occurs"""
    def __init__(self,str):
        Exception.__init__(self,str)

gl_assumptions = []

def add_gl_assumption(gl_variable,required_value,failure_string):
    """Save assumptions for later checking once OpenGL context created."""
    gl_assumptions.append((gl_variable,required_value,failure_string))

def check_gl_assumptions():
    """Requires OpenGL context to be created."""
    for gl_variable,required_value,failure_string in gl_assumptions:
        # Code required for each variable to be checked
        if string.upper(gl_variable) == "GL_VENDOR":
            value = string.split(string.lower(glGetString(GL_VENDOR)))[0]
            if value != required_value:
                raise EggError(gl_variable + " not equal " + required_value + ": " + failure_string)
        elif string.upper(gl_variable) == "GL_VERSION":
            value_str = string.split(glGetString(GL_VERSION))[0]
            value_ints = map(int,string.split(value_str,'.'))
            value = float( str(value_ints[0]) + "." + string.join(map(str,value_ints[1:]),''))
            if value < required_value:
                raise EggError(gl_variable + " less than " + str(required_value) + ": " + failure_string)
