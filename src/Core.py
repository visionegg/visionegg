"""VisionEgg Core Library
"""

# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import sys,types,string
import VisionEgg                                # Vision Egg base module (__init__.py)
import PlatformDependent                        # platform dependent Vision Egg C code

import pygame                                   # pygame handles OpenGL window setup
import pygame.locals
			                        # from PyOpenGL:
import OpenGL.GL                                #   main package
import OpenGL.GLU                               #   utility package
gl = OpenGL.GL                                  # shorthand
glu = OpenGL.GLU                                # shorthand

import Numeric  				# Numeric Python package
import MLab                                     # Matlab function imitation from Numeric Python

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'
__all__ = ['Screen','Viewport','Projection','OrthographicProjection',
           'SimplePerspectiveProjection','PerspectiveProjection',
           'Stimulus','FixationSpot','Presentation','EggError']

####################################################################
#
#        Screen
#
####################################################################

class Screen(VisionEgg.ClassWithParameters):
    """An OpenGL window for use by Vision Egg.

    An easy way to make an instance of screen is to use a helper
    function in the VisionEgg.AppHelper class:
    
    >>> import Visionegg.AppHelper
    >>> VisionEgg.AppHelper.get_default_screen()

    Make an instance of this class to create an OpenGL window for the
    Vision Egg to draw in.  For a an instance of Screen to do anything
    useful, it must contain one or more instances of the Viewport
    class and one or more instances of the Stimulus class.

    Only one parameter can be changed in realtime--bgcolor.  The
    screen is cleared with this color on each frame drawn.

    Currently, only one screen is supported by the library with which
    the Vision Egg opens an OpenGL window (pygame/SDL).  However, this
    need not limit display to a single physical display device.
    NVidia's video drivers, for example, allow applications to treat
    two separate monitors as one large array of contiguous pixels.  By
    sizing a window such that it occupies both monitors and creating
    separate viewports for the portion of the window on each monitor,
    a multiple screen effect can be created.  """
    # List of stuff to be improved in this class:
    # Better configurability of number of bits per pixel, including alpha.
    
    parameters_and_defaults = {'bgcolor':VisionEgg.config.VISIONEGG_SCREEN_BGCOLOR}

    def __init__(self,
                 size=(VisionEgg.config.VISIONEGG_SCREEN_W,
                       VisionEgg.config.VISIONEGG_SCREEN_H),
                 fullscreen=VisionEgg.config.VISIONEGG_FULLSCREEN,
                 preferred_bpp=VisionEgg.config.VISIONEGG_PREFERRED_BPP,
                 maxpriority=VisionEgg.config.VISIONEGG_MAXPRIORITY,
                 **kw):
        
        apply(VisionEgg.ClassWithParameters.__init__,(self,),kw)
        
        self.size = size
        self.fullscreen = fullscreen 

        # Attempt to synchronize buffer swapping with vertical sync
        sync_success = PlatformDependent.sync_swap_with_vbl_pre_gl_init()

        # Initialize pygame stuff
        if sys.platform == "darwin": # bug in Mac OS X version of pygame
            pygame.init()
        pygame.display.init()

        # Request alpha in the framebuffer
        if hasattr(pygame.display,"gl_set_attribute"):
            pygame.display.gl_set_attribute(pygame.locals.GL_ALPHA_SIZE,8)
            requested_alpha = 1
        else:
            requested_alpha = 0
            pygame_nag = """Could not request alpha in framebuffer because you need
            pygame release 1.4.9 or greater. This is only of concern
            if you use a stimulus that needs this feature. In that
            case, the stimulus should verify the presence of alpha."""

            message.add(text=pygame_nag,level=Message.NAG)
            
        pygame.display.set_caption("Vision Egg")
        
        flags = pygame.locals.OPENGL | pygame.locals.DOUBLEBUF
        if self.fullscreen:
            flags = flags | pygame.locals.FULLSCREEN

        # Choose an appropriate framebuffer pixel representation
        try_bpps = [32,24,0] # bits per pixel (32 = 8 bits red, 8 green, 8 blue, 8 alpha, 0 = any)
        try_bpps.insert(0,preferred_bpp) # try the preferred size first

        if sys.platform=='linux2':
            # linux (at least nVidia drivers) doesn't like to give a
            # 32 bpp depth.
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

        message.add("Initializing graphics at %d x %d ( %d bpp )."%(self.size[0],self.size[1],try_bpp))

        try:
            pygame.display.set_mode(self.size, flags, try_bpp )
        except pygame.error, x:
            print "FATAL VISION EGG ERROR:",x
            sys.exit(1)

        self.bpp = pygame.display.Info().bitsize
        message.add("Video system reports %d bpp"%self.bpp)
        if self.bpp < try_bpp:
            message.add(
                """Video system reports %d bits per pixel, while your program
                requested %d. Can you adjust your video drivers?"""%(self.bpp,try_bpp),
                level=Message.WARNING)

        # Save the address of these function so they can be called
        # when closing the screen.
        self.cursor_visible_func = pygame.mouse.set_visible
        self.set_dout = PlatformDependent.set_dout

        # Attempt to synchronize buffer swapping with vertical sync again
        if not sync_success:
            if not PlatformDependent.sync_swap_with_vbl_post_gl_init():
                message.add(
                    """Unable to synchronize buffer swapping with vertical
                    retrace. May be possible by manually adjusting video
                    drivers. (Try "Enable Vertical Sync" or similar.)""",
                    level=Message.WARNING)

        # Check previously made OpenGL assumptions now that we have OpenGL window
        check_gl_assumptions()
        
        if self.fullscreen:
            self.cursor_visible_func(0)

        # Attempt to set maximum priority (This may not be the best
        # place in the code to do it because it's an application-level
        # thing, not a screen-level thing, but it fits reasonably well
        # here for now.)
        if maxpriority: 
            PlatformDependent.set_realtime()

    def clear(self):
        """Clear the screen.

        Gets called every frame."""
        c = self.parameters.bgcolor # Shorthand
        gl.glClearColor(c[0],c[1],c[2],c[3])
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

    def make_current(self):
        """Makes screen active for drawing.

        Can not be implemented until multiple screens are possible."""
        pass

    def __del__(self):
        # Make sure the TTL signal is low when screen closed.
        self.set_dout(0)
        # Make sure mouse is visible after screen closed.
        self.cursor_visible_func(1)
        
####################################################################
#
#        Viewport
#
####################################################################

class Viewport(VisionEgg.ClassWithParameters):
    """A portion of a screen which shows stimuli.

    A screen may have multiple viewports.  The viewports may be
    overlapping.

    By default, a viewport has a projection which maps eye coordinates
    to viewport coordinates in 1:1 manner.  In other words, eye
    coordinates specify pixel location in the viewport.

    A different projection is desired for stimuli whose eye
    coordinates it is most convenient not be equal to viewport
    coordinates. In this case, the application must change the
    viewport's projection from the default.  This is typically the
    case for 3D stimuli.    
    """
    parameters_and_defaults = {'lowerleft':(0,0), # tuple of length 2
                               'size':None,       # tuple of length 2, will use screen.size if not specified
                               'projection':None} # instance of VisionEgg.Core.Projection

    def __init__(self,screen,**kw):
        apply(VisionEgg.ClassWithParameters.__init__,(self,),kw)
        
        self.screen = screen
        self.stimuli = []
        if self.parameters.size is None:
            self.parameters.size = self.screen.size
        if self.parameters.projection is None:
            # Default projection maps eye coordinates 1:1 on window (pixel) coordinates
            self.parameters.projection = OrthographicProjection(left=0,right=self.parameters.size[0],
                                                                bottom=0,top=self.parameters.size[1],
                                                                z_clip_near=0.0,
                                                                z_clip_far=1.0)

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
        gl.glViewport(self.parameters.lowerleft[0],self.parameters.lowerleft[1],self.parameters.size[0],self.parameters.size[1])

        self.parameters.projection.set_gl_projection()
        
        for stimulus in self.stimuli:
            stimulus.draw()

####################################################################
#
#        Projection and derived classes
#
####################################################################

class Projection(VisionEgg.ClassWithParameters):
    """Abstract base class to define interface for OpenGL projection matrices"""
    parameters_and_defaults = {'matrix':Numeric.array(
        [[1.0, 0.0, 0.0, 0.0], # 4x4 identity matrix
         [0.0, 1.0, 0.0, 0.0],
         [0.0, 0.0, 1.0, 0.0],
         [0.0, 0.0, 0.0, 1.0]]) }
                               
    def __init__(self,**kw):
        apply(VisionEgg.ClassWithParameters.__init__,(self,),kw)

    def set_gl_projection(self):
        """Set the OpenGL projection matrix."""
        gl.glMatrixMode(gl.GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        gl.glLoadMatrixf(self.parameters.matrix)

    def push_and_set_gl_projection(self):
        """Set the OpenGL projection matrix, pushing current projection matrix to stack."""
        gl.glMatrixMode(gl.GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        gl.glPushMatrix()
        gl.glLoadMatrixf(self.parameters.matrix)

    def translate(self,x,y,z):
        """Compose a translation and set the OpenGL projection matrix."""
        gl.glMatrixMode(gl.GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        gl.glLoadMatrixf(self.parameters.matrix)
        gl.glTranslatef(x,y,z)
        self.parameters.matrix = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)

    def stateless_translate(self,x,y,z):
        """Compose a translation without changing OpenGL state."""
        matrix_mode = gl.glGetInteger(gl.GL_MATRIX_MODE)
        gl.glMatrixMode(gl.GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        gl.glPushMatrix()
        gl.glLoadMatrixf(self.parameters.matrix)
        gl.glTranslatef(x,y,z)
        self.parameters.matrix = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
        gl.glPopMatrix()
        if matrix_mode is not None:
            gl.glMatrixMode(matrix_mode)

    def rotate(self,angle_degrees,x,y,z):
        """Compose a rotation and set the OpenGL projection matrix."""
        gl.glMatrixMode(gl.GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        gl.glLoadMatrixf(self.parameters.matrix)
        gl.glRotatef(angle_degrees,x,y,z)
        self.parameters.matrix = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)

    def stateless_rotate(self,angle_degrees,x,y,z):
        """Compose a rotation without changing OpenGL state."""
        matrix_mode = gl.glGetInteger(gl.GL_MATRIX_MODE)
        gl.glMatrixMode(gl.GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        gl.glPushMatrix()
        gl.glLoadMatrixf(self.parameters.matrix)
        gl.glRotatef(angle_degrees,x,y,z)
        self.parameters.matrix = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
        gl.glPopMatrix()
        if matrix_mode is not None:
            gl.glMatrixMode(matrix_mode)

class OrthographicProjection(Projection):
    """An orthographic projection"""
    def __init__(self,left=0.0,right=640.0,bottom=0.0,top=480.0,z_clip_near=0.0,z_clip_far=1.0):
        """Create an orthographic projection.

        Defaults to map x eye coordinates in the range [0,640] to clip
        coordinates in the range [0,1] and y eye coordinates [0,480]
        -> [0,1].  Therefore, if the viewport is 640 x 480, eye
        coordinates correspond 1:1 with window (pixel) coordinates."""
        gl.glMatrixMode(gl.GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        gl.glLoadIdentity() # Clear the projection matrix
        gl.glOrtho(left,right,bottom,top,z_clip_near,z_clip_far) # Let GL create a matrix and compose it
        matrix = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
        if matrix is None:
            # OpenGL wasn't started
            raise RuntimeError("OpenGL matrix operations can only take place once OpenGL context started.")
        apply(Projection.__init__,(self,),{'matrix':matrix})

class SimplePerspectiveProjection(Projection):
    """A simplified perspective projection"""
    def __init__(self,fov_x=45.0,z_clip_near = 0.1,z_clip_far=100.0,aspect_ratio=4.0/3.0):
        fov_y = fov_x / aspect_ratio
        gl.glMatrixMode(gl.GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        gl.glLoadIdentity() # Clear the projection matrix
        glu.gluPerspective(fov_y,aspect_ratio,z_clip_near,z_clip_far) # Let GLU create a matrix and compose it
        matrix = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
        if matrix is None:
            # OpenGL wasn't started
            raise RuntimeError("OpenGL matrix operations can only take place once OpenGL context started.")
        apply(Projection.__init__,(self,),{'matrix':matrix})

class PerspectiveProjection(Projection):
    """A perspective projection"""
    def __init__(self,left,right,bottom,top,near,far):
        gl.glMatrixMode(gl.GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        gl.glLoadIdentity() # Clear the projection matrix
        glFrustum(left,right,top,bottom,near,far) # Let GL create a matrix and compose it
        matrix = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
        if matrix is None:
            # OpenGL wasn't started
            raise RuntimeError("OpenGL matrix operations can only take place once OpenGL context started.")
        apply(Projection.__init__,(self,),{'matrix':matrix})

####################################################################
#
#        Stimulus - Base class
#
####################################################################

class Stimulus(VisionEgg.ClassWithParameters):
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
    loops through stimuli this also imposes some important behaviors:
    
    First, the framebuffer will contain the results of any drawing
    operations performed since the last buffer swap by other instances
    of (subclasses of) Stimulus. Therefore, the order in which stimuli
    are added to an instance of Viewport may be important.
    Additionally, if there are overlapping viewports, the order in
    which viewports are added to an instance of Screen is important.

    Second, previously established OpenGL display lists and OpenGL
    texture objects will be available.  The __init__() method should
    establish these things.

    Third, there are several OpenGL state variables which are
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
    query its value and restore it later.  For example, upon calling
    the draw() method, the projection matrix will be that which was
    set by the viewport. If the draw() method alters the projection
    matrix, it must be restored. The glPushMatrix() and glPopMatrix()
    commands provide an easy way to do this.

    The default projection of Viewport maps eye coordinates in a 1:1
    fashion to window coordinates (in other words, it sets eye
    coordinates to use pixel units from the lower left corner of the
    viewport). Therefore the default parameters for a stimulus should
    specify pixel coordinates if possible (such as for a 2D
    stimulus). Assuming a window size of 640 by 480 for the default
    parameters is a pretty safe way to do things.

    Also, be sure to check for any assumptions made about the system
    in the __init__ method.  For example, if your stimulus needs alpha
    in the framebuffer, check the value of
    glGetIntegerv(GL_ALPHA_BITS) and raise an exception if it is not
    available."""
    
    parameters_and_defaults = {} # empty for base Stimulus class

    def __init__(self,**kw):
        """Get a Stimulus ready to draw.

        Set parameter values and create anything needed to draw the
        stimulus including OpenGL state variables such display lists
        and texture objects.

        In this base class, nothing needs to be done other than set
        parameter values.
        """
        apply(VisionEgg.ClassWithParameters.__init__,(self,),kw)
        
    def draw(self):
    	"""Draw the stimulus.  This method is called every frame.
    
        This method actually performs the OpenGL calls to draw the
        stimulus. In this base class, however, it does nothing."""
        pass
        
####################################################################
#
#        FixationSpot
#
####################################################################

class FixationSpot(Stimulus):
    """A rectangle stimulus, typically used as a fixation spot."""
    parameters_and_defaults = {'on':1,
                               'color':(1.0,1.0,1.0,1.0),
                               'center':(320.0,240.0), # place in center of 640x480 viewport
                               'size':(4.0,4.0)} # horiz and vertical size
    
    def __init__(self,**kw):
        """Create a fixation spot.
        """
        apply(Stimulus.__init__,(self,),kw)

    def draw(self):
        if self.parameters.on:
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glDisable(gl.GL_BLEND)

            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            c = self.parameters.color
            glColor(c[0],c[1],c[2],c[3])

            # This could go in a display list to speed it up, but then
            # size wouldn't be dynamically adjustable this way.  Could
            # still use one of the matrices to make it change size.
            x_size = self.parameters.size[0]/2.0
            y_size = self.parameters.size[1]/2.0
            x,y = self.parameters.center[0],self.parameters.center[1]
            x1 = x-x_size; x2 = x+x_size
            y1 = y-y_size; y2 = y+y_size
            gl.glBegin(gl.GL_QUADS)
            gl.glVertex2f(x1,y1)
            gl.glVertex2f(x2,y1)
            gl.glVertex2f(x2,y2)
            gl.glVertex2f(x1,y2)
            gl.glEnd() # GL_QUADS

####################################################################
#
#        Presentation
#
####################################################################

class Presentation(VisionEgg.ClassWithParameters):
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
    parameters_and_defaults = {'viewports' : [],
                               'duration' : (5.0,'seconds') }

    def __init__(self,**kw):
        apply(VisionEgg.ClassWithParameters.__init__,(self,),kw)

        # These next three lists contain all the parameters under control
        self.realtime_time_controllers = []
        self.realtime_frame_controllers = []
        self.transitional_controllers = []

        # An list that optionally records when frames were drawn by go() method.
        self.frame_draw_times = []

    def __check_controller_args(self,class_with_parameters,parameter_name):
        # Raise an Exception if the user tries to add/remove a controller
        # to an unknown parameter.
        if class_with_parameters is None and parameter_name is None:
            # Allow controllers not to control anything.  (Allows user
            # to define functions that get called like controllers.)
            return
        if not isinstance(class_with_parameters,VisionEgg.ClassWithParameters):
            raise ValueError('"%s" is not a subclass of %s'%(class_with_parameters,VisionEgg.ClassWithParameters))
        if not isinstance(class_with_parameters.parameters,VisionEgg.Parameters):
            raise EggError('Internal Vision Egg consistency error: attribute "parameters" of %s is not an instance of %s'%(class_with_parameters,VisionEgg.Parameters))
        if not hasattr(class_with_parameters.parameters,parameter_name):
            raise AttributeError('"%s" not an attribute of %s'%(parameter_name,class_with_parameters.parameters))

    def __add_controller( self, controller_list, class_with_parameters, parameter_name, controller_function):
        self.__check_controller_args(class_with_parameters,parameter_name)
        if class_with_parameters is not None:
            controller_list.append((class_with_parameters.parameters,parameter_name,controller_function))
        else:
            controller_list.append((None,None,controller_function))

    def __remove_controllers(self,controller_list,class_with_parameters,parameter_name, controller_function):
        self.__check_controller_args(class_with_parameters,parameter_name)
        i = 0
        if controller_function is None:
            # The controller function is not specified:
            # Delete all controllers that control the parameter specified.
            if class_with_parameters is None or parameter_name is None:
                raise ValueError("Must specify parameter from which controller should be removed.")
            while i < len(controller_list):
                orig_parameters,orig_parameter_name,orig_controller_function = controller_list[i]
                if orig_parameters == class_with_parameters.parameters and orig_parameter_name == parameter_name:
                    del controller_list[i]
                else:
                    i = i + 1
        else: # controller_function is specified
            # Delete only that specific controller
            while i < len(controller_list):
                orig_parameters,orig_parameter_name,orig_controller_function = controller_list[i]
                if orig_parameters == class_with_parameters.parameters and orig_parameter_name == parameter_name and orig_controller_function == controller_function:
                    del controller_list[i]
                else:
                    i = i + 1

    def __call_controllers(self,controller_list,arg):
        for parameters,parameter_name,controller_function in controller_list:
            if parameters is None and parameter_name is None:
                # Nothing under control- user utilizing controller to call other function
                controller_function(arg)
            else:
                # Set the parameters under controller
                setattr(parameters,parameter_name,controller_function(arg))
        
    def add_realtime_time_controller(self, class_with_parameters, parameter_name, controller_function):
        self.__add_controller( self.realtime_time_controllers, class_with_parameters, parameter_name, controller_function)
    def remove_realtime_time_controller(self, class_with_parameters, parameter_name, controller_function=None):
        self.__remove_controller(self.realtime_time_controllers,class_with_parameters,parameter_name, controller_function)
    def add_realtime_frame_controller(self, class_with_parameters, parameter_name, controller_function):
        self.__add_controller( self.realtime_frame_controllers, class_with_parameters, parameter_name, controller_function)
    def remove_realtime_frame_controller(self, class_with_parameters, parameter_name, controller_function=None):
        self.__remove_controller(self.realtime_frame_controllers,class_with_parameters,parameter_name, controller_function)
    def add_transitional_controller(self, class_with_parameters, parameter_name, controller_function):
        self.__add_controller( self.transitional_controllers, class_with_parameters, parameter_name, controller_function)
    def remove_transitional_controller(self, class_with_parameters, parameter_name, controller_function=None):
        self.__remove_controller(self.transitional_controllers,class_with_parameters,parameter_name, controller_function)

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
        # the main loop slightly by not performing name lookup each time.
        duration_value = self.parameters.duration[0]
        duration_units = self.parameters.duration[1]
        viewports = self.parameters.viewports

        # Get list of screens
        screens = []
        for viewport in viewports:
            if viewport.screen not in screens:
                screens.append(viewport.screen)

        # Tell transitional controllers a presentation is starting
        self.__call_controllers(self.transitional_controllers,0.0)

        # Clear any previous timing info if necessary
        if collect_timing_info:
            self.frame_draw_times = []

        # Still need to add DAQ hooks here...

        # Do the main loop
        start_time_absolute = VisionEgg.timing_func()
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
            self.__call_controllers(self.realtime_time_controllers,current_time)
            self.__call_controllers(self.realtime_frame_controllers,current_frame)
            # Clear the screen(s)
            for screen in screens:
                screen.clear()
            # Draw each viewport
            for viewport in viewports:
                viewport.draw()
            # Swap the buffers
            VisionEgg.swap_buffers()
            # If wanted, save time this frame was drawn for
            if collect_timing_info:
                self.frame_draw_times.append(current_time)
            # Get the time for the next frame
            current_time_absolute = VisionEgg.timing_func()
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
            impossibly_fast_frame_rate = 210.0
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
        self.__call_controllers(self.realtime_time_controllers,-1.0)
        self.__call_controllers(self.realtime_frame_controllers,-1)
        self.__call_controllers(self.transitional_controllers,-1.0)

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
        VisionEgg.swap_buffers()

    def export_movie_go(self, frames_per_sec=12.0, filename_suffix=".tif", filename_base="visionegg_movie", path="."):
        """Call this method rather than go() to save a movie of your experiment.
        """
        import Image # Could import this at the beginning of the file, but it breaks sometimes!
        
        # Tell transitional controllers a presentation is starting
        self.__call_controllers(self.transitional_controllers,0.0)

        # Create a few shorthand notations, which speeds
        # the main loop a little by not performing name lookup each time.
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
            self.__call_controllers(self.realtime_time_controllers,current_time)
            self.__call_controllers(self.realtime_frame_controllers,current_frame)
            # Clear the screen(s)
            for screen in screens:
                screen.clear()
            # Draw each viewport
            for viewport in viewports:
                viewport.draw()
            VisionEgg.swap_buffers()

            # Now save the contents of the framebuffer
            gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
            framebuffer = gl.glReadPixels(0,0,screen.size[0],screen.size[1],gl.GL_RGB,gl.GL_UNSIGNED_BYTE)
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
            frame_draw_times = Numeric.array(self.frame_draw_times)
            self.frame_draw_times = [] # clear the list
            frame_draw_times = frame_draw_times[1:] - frame_draw_times[:-1] # get inter-frame interval
            print (len(frame_draw_times)+1), "frames drawn."
            mean_sec = MLab.mean(frame_draw_times)
            print "mean frame to frame time: %.1f (usec) == mean fps: %.2f, max: %.1f"%(mean_sec*1.0e6,1.0/mean_sec,max(frame_draw_times)*1.0e6)
            bins = arange(0.0,15.0,1.0) # msec
            bins = bins*1.0e-3 # sec
            print "Inter-frame interval",
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
        print "histogram:"
        for line in range(lines):
            val = float(lines)-1.0-float(line)
            print "%6d"%(round(maxhist*val/10.0),),
            q = greater(hist,val)
            for qi in q:
                s = ' '
                if qi:
                    s = '*'
                print "%3s"%(s,),
            print
        print " Time:",
        for bin in bins:
            print "%3d"%(int(bin*1.0e3),),
        print "+",
        print "(msec)"
        print "Total:",
        for hi in h:
            print "%3d"%(hi,),
        print
        
####################################################################
#
#        Error handling and assumption checking
#
####################################################################

class Message:
    """Handles message/warning/error printing, exception raising"""

    # Levels are:
    TRIVIAL = 0
    INFO = 1
    NAG = 2
    WARNING = 3
    ERROR = 4
    FATAL = 5
    
    def __init__(self,
                 prefix="VisionEgg",
                 exception_level=ERROR,
                 print_level=INFO,
                 print_stream=sys.stderr):
        self.prefix = prefix
        self.message_queue = []
        self.exception_level = exception_level
        self.print_level = print_level
        self.print_stream = print_stream
        
    def add(self,text,level=INFO):
        self.message_queue.append((level,text))
        self.handle()

    def handle(self):
        while len(self.message_queue) > 0:
            level, text = self.message_queue.pop(0)
            if level >= self.print_level:
                self.print_stream.write(self.prefix)
                if level == Message.TRIVIAL:
                    self.print_stream.write(" trivial")
                elif level == Message.INFO:
                    self.print_stream.write(" info")
                elif level == Message.NAG:
                    self.print_stream.write(" nag")
                elif level == Message.WARNING:
                    self.print_stream.write(" WARNING")
                elif level == Message.ERROR:
                    self.print_stream.write(" ERROR")
                elif level == Message.FATAL:
                    self.print_stream.write(" FATAL")
                self.print_stream.write(" message: "+text+"\n")
                self.print_stream.flush()
            if level >= self.exception_level:
                raise EggError(text)
            if level == Message.FATAL:
                sys.exit(-1)

message = Message() # create instance of Message class for everything to use
    
class EggError(Exception):
    """Created whenever a Vision Egg specific error occurs"""
    def __init__(self,str):
        Exception.__init__(self,str)

gl_assumptions = []

def add_gl_assumption(gl_variable,required_value,failure_callback):
    """Save assumptions for later checking once OpenGL context created."""
    if type(failure_callback) != types.FunctionType:
        raise ValueError("failure_callback must be a function!")
    gl_assumptions.append((gl_variable,required_value,failure_callback))

def check_gl_assumptions():
    """Requires OpenGL context to be created."""
    for gl_variable,required_value,failure_callback in gl_assumptions:
        # Code required for each variable to be checked
        if string.upper(gl_variable) == "GL_VENDOR":
            value = string.split(string.lower(gl.glGetString(gl.GL_VENDOR)))[0]
            if value != required_value:
                raise EggError(gl_variable + " not equal " + required_value + ": " + failure_string)
        elif string.upper(gl_variable) == "GL_VERSION":
            value_str = string.split(gl.glGetString(gl.GL_VERSION))[0]
            value_ints = map(int,string.split(value_str,'.'))
            value = float( str(value_ints[0]) + "." + string.join(map(str,value_ints[1:]),''))
            if value < required_value:
                failure_callback()
