"""Core Vision Egg functionality

This module contains the architectural foundations of the Vision Egg.

Classes:

Screen -- An OpenGL window
Viewport -- Connects stimuli to a screen
Projection -- Converts stimulus coordinates to viewport coordinates
Stimulus -- Base class for a stimulus
Presentation -- Handles the timing and coordination of stimulus presentation
Controller -- Control parameters
Message -- Handling of messages/warnings/errors

Subclasses of Projection:

OrthographicProjection
SimplePerspectiveProjection
PerspectiveProjection

Subclasses of Stimulus:

FixationSpot

Subclasses of Controller:

ConstantController -- constant value
EvalStringController -- use dynamically interpreted Python string
ExecStringController -- use potentially complex Python string
FunctionController -- use a Python function
EncapsulatedController -- use a controller to control a controller

Exceptions:

EggError -- A Vision Egg specific error

Public functions:

get_default_screen -- Create instance of Screen
add_gl_assumption -- Check assumption after OpenGL context created.

Public variables:

message -- Instance of Message class

"""

# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import sys,types,string, math, time             # standard Python modules
import VisionEgg                                # Vision Egg base module (__init__.py)
import PlatformDependent                        # platform dependent Vision Egg C code

import pygame                                   # pygame handles OpenGL window setup
import pygame.locals
import pygame.display
swap_buffers = pygame.display.flip              # make shortcut name

                                                # from PyOpenGL:
import OpenGL.GL                                #   main package
gl = OpenGL.GL                                  # shorthand

import Numeric  				# Numeric Python package
import MLab                                     # Matlab function imitation from Numeric Python

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

####################################################################
#
#        Screen
#
####################################################################

class Screen(VisionEgg.ClassWithParameters):
    """An OpenGL window, possibly displayed on 2 monitors.

    An easy way to make an instance of screen is to use a helper
    function in the VisionEgg.AppHelper class:
    
    >>> import VisionEgg.Core
    >>> VisionEgg.Core.get_default_screen()

    Make an instance of this class to create an OpenGL window for the
    Vision Egg to draw in.  For an instance of Screen to do anything
    useful, it must contain one or more instances of the Viewport
    class and one or more instances of the Stimulus class.

    Currently, only one OpenGL window is supported by the library with
    which the Vision Egg initializes graphics (pygame/SDL).  However,
    this need not limit display to a single physical display device.
    NVidia's video drivers, for example, allow applications to treat
    two separate monitors as one large array of contiguous pixels.  By
    sizing a window such that it occupies both monitors and creating
    separate viewports for the portion of the window on each monitor,
    a multiple screen effect can be created.

    Parameters:
    
    bgcolor -- Tuple of 4 floating point values specifying RGBA. The screen is cleared with this color before drawing each frame

    Public variables:

    size -- Tuple of 2 integers specifying width and height
    red_bits -- Integer (or None if not supported) specifying framebuffer depth
    green_bits -- Integer (or None if not supported) specifying framebuffer depth
    blue_bits -- Integer (or None if not supported) specifying framebuffer depth
    alpha_bits -- Integer (or None if not supported) specifying framebuffer depth

    """
    constant_parameters_and_defaults = {'size':((VisionEgg.config.VISIONEGG_SCREEN_W,
                                                 VisionEgg.config.VISIONEGG_SCREEN_H),
                                                types.TupleType),
                                        'fullscreen':(VisionEgg.config.VISIONEGG_FULLSCREEN,
                                                      types.IntType),
                                        'preferred_bpp':(VisionEgg.config.VISIONEGG_PREFERRED_BPP,
                                                         types.IntType),
                                        'maxpriority':(VisionEgg.config.VISIONEGG_MAXPRIORITY,
                                                       types.IntType)}

    parameters_and_defaults = {'bgcolor':((0.5,0.5,0.5,0.0),
                                          types.TupleType)}
    
    def __init__(self,**kw):
        
        apply(VisionEgg.ClassWithParameters.__init__,(self,),kw)

        # Attempt to synchronize buffer swapping with vertical sync
        if VisionEgg.config.VISIONEGG_SYNC_SWAP:
            sync_success = PlatformDependent.sync_swap_with_vbl_pre_gl_init()

        # Initialize pygame stuff
        if sys.platform == "darwin": # bug in Mac OS X version of pygame
            pygame.init()
        pygame.display.init()

        # Request framebuffer depths
        r = VisionEgg.config.VISIONEGG_REQUEST_RED_BITS
        g = VisionEgg.config.VISIONEGG_REQUEST_GREEN_BITS
        b = VisionEgg.config.VISIONEGG_REQUEST_BLUE_BITS
        a = VisionEgg.config.VISIONEGG_REQUEST_ALPHA_BITS
        if hasattr(pygame.display,"gl_set_attribute"):
            pygame.display.gl_set_attribute(pygame.locals.GL_RED_SIZE,r)
            pygame.display.gl_set_attribute(pygame.locals.GL_GREEN_SIZE,g)
            pygame.display.gl_set_attribute(pygame.locals.GL_BLUE_SIZE,b)
            pygame.display.gl_set_attribute(pygame.locals.GL_ALPHA_SIZE,a)
        else:
            message.add(
                """Could not request or query exact bit depths or
                alpha in framebuffer because you need pygame release
                1.4.9 or greater. This is only of concern if you use a
                stimulus that needs this. In that case, the stimulus
                should check for the desired feature(s).""",
                level=Message.NAG)
            
        if not hasattr(pygame.display,"set_gamma_ramp"):
            message.add(
                """set_gamma_ramp function not available because you
                need pygame release 1.5 or greater. This is only of
                concern if you need this feature.""",level=Message.NAG)
            
        pygame.display.set_caption("Vision Egg")
        
        flags = pygame.locals.OPENGL | pygame.locals.DOUBLEBUF #| pygame.locals.NOFRAME
        if self.constant_parameters.fullscreen:
            flags = flags | pygame.locals.FULLSCREEN

        # Choose an appropriate framebuffer pixel representation
        try_bpps = [32,24,0] # bits per pixel (32 = 8 bits red, 8 green, 8 blue, 8 alpha, 0 = any)
        try_bpps.insert(0,self.constant_parameters.preferred_bpp) # try the preferred size first

        if sys.platform[:5]=='linux' or sys.platform[:4]=='irix':
            # SDL doesn't like to give a 32 bpp depth, even if it works
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
                    if self.constant_parameters.size in modeList:
                        found_mode = 1
                    else:
                        self.constant_parameters.size = modeList[0]
                        message.add(
                            """WARNING: Using Screen size %dx%d instead
                            of requested size."""%(self.constant_parameters.size[0],self.constant_parameters.size[1]),
                            level=Message.WARNING)
                            
            if found_mode: # found the color depth to tell pygame
                try_bpp = bpp 
                break
        if found_mode == 0:
            message.add(
                """WARNING: Could not find acceptable video mode!
                Trying anyway with bpp=0...""",
                level=Message.WARNING)
            try_bpp = 0 # At least try something!

        self.size = self.constant_parameters.size

        append_str = ""
        if self.constant_parameters.fullscreen:
            screen_mode = "fullscreen"
        else:
            screen_mode = "window"
        if hasattr(pygame.display,"gl_set_attribute"):
            append_str = " (%d %d %d %d RGBA)."%(r,g,b,a)
        message.add("Requesting %s %d x %d %d bpp%s"%(screen_mode,self.size[0],self.size[1],try_bpp,append_str))

        try:
            pygame.display.set_mode(self.size, flags, try_bpp )
        except pygame.error, x:
            message.add("Failed execution of pygame.display.set_mode():%s"%x,
                        level=Message.FATAL)

        self.red_bits = None
        self.green_bits = None
        self.blue_bits = None
        self.alpha_bits = None
        got_bpp = pygame.display.Info().bitsize
        append_str = ""
        if hasattr(pygame.display,"gl_get_attribute"):
            self.red_bits = pygame.display.gl_get_attribute(pygame.locals.GL_RED_SIZE)
            self.green_bits = pygame.display.gl_get_attribute(pygame.locals.GL_GREEN_SIZE)
            self.blue_bits = pygame.display.gl_get_attribute(pygame.locals.GL_BLUE_SIZE)
            self.alpha_bits = pygame.display.gl_get_attribute(pygame.locals.GL_ALPHA_SIZE)
            append_str = " (%d %d %d %d RGBA)"%(self.red_bits,self.green_bits,self.blue_bits,self.alpha_bits)
        message.add("Video system reports %d bpp%s"%(got_bpp,append_str))
        if got_bpp < try_bpp:
            message.add(
                """Video system reports %d bits per pixel, while your program
                requested %d. Can you adjust your video drivers?"""%(got_bpp,try_bpp),
                level=Message.WARNING)

        # Save the address of these functions so they can be called
        # when closing the screen.
        self.cursor_visible_func = pygame.mouse.set_visible
        self.pygame_quit = pygame.quit

        # Attempt to synchronize buffer swapping with vertical sync again
        if VisionEgg.config.VISIONEGG_SYNC_SWAP:
            if not sync_success:
                if not PlatformDependent.sync_swap_with_vbl_post_gl_init():
                    message.add(
                        
                        """Although the configuration variable
                        VISIONEGG_SYNC_SWAP is set, unable to detect
                        or automatically synchronize buffer swapping
                        with vertical retrace. May be possible by
                        manually adjusting video drivers. (Look for
                        "Enable Vertical Sync" or similar.)  If buffer
                        swapping is not synchronized, frame by frame
                        control will not be possible.  Because of
                        this, you will probably get a warning about
                        calculated frames per second different than
                        specified.""",
                        
                        level=Message.WARNING)

        # Check previously made OpenGL assumptions now that we have OpenGL window
        check_gl_assumptions()
        
        #if self.constant_parameters.fullscreen:
        self.cursor_visible_func(0)

        # Attempt to set maximum priority (This may not be the best
        # place in the code to do it because it's an application-level
        # thing, not a screen-level thing, but it fits reasonably well
        # here for now.)
        if self.constant_parameters.maxpriority: 
            PlatformDependent.set_realtime()

        if hasattr(VisionEgg.config,'_open_screens'):
            VisionEgg.config._open_screens.append(self)
        else:
            VisionEgg.config._open_screens = [self]

    def clear(self):
        """Called by Presentation instance. Clear the screen."""

        c = self.parameters.bgcolor # Shorthand
        gl.glClearColor(c[0],c[1],c[2],c[3])
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

    def make_current(self):
        """Called by Viewport instance. Makes screen active for drawing.

        Can not be implemented until multiple screens are possible."""
        pass

    def set_gamma_ramp(self,*args,**kw):
        """Set the gamma_ramp, if supported.

        Call pygame.display.set_gamma_ramp, if available.

        Returns 1 on success, 0 otherwise."""
        if not hasattr(pygame.display,"set_gamma_ramp"):
            message.add(
                """Need pygame 1.5 or greater for set_gamma_ramp
                function.""", level=Message.ERROR)
            return 0
        return apply(pygame.display.set_gamma_ramp,args,kw)

    def close(self):
        """Close the screen.

        You can call this to close the screen.  Not necessary during
        normal operation because it gets automatically deleted."""
        # Close pygame if possible
        if hasattr(VisionEgg.config,'_open_screens'):
            if self in VisionEgg.config._open_screens:
                VisionEgg.config._open_screens.remove(self)
            if len(VisionEgg.config._open_screens) == 0:
                # no more open screens
                self.cursor_visible_func(1)
                pygame.quit()
        # No access to the cursor visible function anymore
        if hasattr(self,"cursor_visible_func"):
            del self.cursor_visible_func
            
    def __del__(self):
        # Make sure mouse is visible after screen closed.
        if hasattr(self,"cursor_visible_func"):
            try:
                self.cursor_visible_func(1)
                self.pygame_quit()
            except pygame.error, x:
                if str(x) != 'video system not initialized':
                    raise
            
def get_default_screen():
    """Return an instance of screen opened with to default values.

    Uses VisionEgg.config.VISIONEGG_GUI_INIT to determine how the
    default screen parameters should are determined.  If this value is
    0, the values from VisionEgg.cfg are used.  If this value is 1, a
    GUI panel is opened and allows manual settings of the screen
    parameters.  """

    global VisionEgg # module is in global namespace, not local
    screen = None
    try:
        if not VisionEgg.config.VISIONEGG_GUI_INIT:
            screen = Screen(size=(VisionEgg.config.VISIONEGG_SCREEN_W,
                                  VisionEgg.config.VISIONEGG_SCREEN_H),
                            fullscreen=VisionEgg.config.VISIONEGG_FULLSCREEN,
                            preferred_bpp=VisionEgg.config.VISIONEGG_PREFERRED_BPP)
        else:
            import VisionEgg.GUI # Could import in beginning, but no need if not using GUI
            screen = VisionEgg.GUI.get_screen_via_GUI()
    finally:
        if screen is None:
            try:
                pygame.mouse.set_visible(1) # make sure mouse is visible
                pygame.quit() # close screen
            except pygame.error, x:
                if str(x) != 'video system not initialized':
                    raise

    if screen is None:
        raise RuntimeError("Screen open failed. Check your error log for a traceback.")
    
    return screen
    
####################################################################
#
#        Projection and derived classes
#
####################################################################

class Projection(VisionEgg.ClassWithParameters):
    """Converts stimulus coordinates to viewport coordinates.

    This is an abstract base class which should be subclassed for
    actual use.

    This class is largely convenience for using OpenGL's
    PROJECTION_MATRIX.

    """
    parameters_and_defaults = {'matrix':(
        Numeric.array([[1.0, 0.0, 0.0, 0.0], # 4x4 identity matrix
                       [0.0, 1.0, 0.0, 0.0],
                       [0.0, 0.0, 1.0, 0.0],
                       [0.0, 0.0, 0.0, 1.0]]),
                      Numeric.ArrayType) }
                               
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
    def __init__(self,fov_x=45.0,z_clip_near = 0.1,z_clip_far=10000.0,aspect_ratio=4.0/3.0):
        fov_y = fov_x / aspect_ratio
        gl.glMatrixMode(gl.GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        gl.glLoadIdentity() # Clear the projection matrix
        matrix = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
        if matrix is None:
            # OpenGL wasn't started
            raise RuntimeError("OpenGL matrix operations can only take place once OpenGL context started.")
        # This is a translation of what gluPerspective does:
        #glu.gluPerspective(fov_y,aspect_ratio,z_clip_near,z_clip_far) # Let GLU create a matrix and compose it
        radians = fov_y / 2.0 * math.pi / 180.0
        delta_z = z_clip_far - z_clip_near
        sine = math.sin(radians)
        if (delta_z == 0.0) or (sine == 0.0) or (aspect_ratio == 0.0):
            raise ValueError("Invalid parameters passed to SimpleProjection.__init__()")
        cotangent = math.cos(radians) / sine
        matrix[0][0] = cotangent/aspect_ratio
        matrix[1][1] = cotangent
        matrix[2][2] = -(z_clip_far + z_clip_near) / delta_z
        matrix[2][3] = -1.0
        matrix[3][2] = -2.0 * z_clip_near * z_clip_far / delta_z
        matrix[3][3] = 0.0
        apply(Projection.__init__,(self,),{'matrix':matrix})

class PerspectiveProjection(Projection):
    """A perspective projection"""
    def __init__(self,left,right,bottom,top,near,far):
        gl.glMatrixMode(gl.GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        gl.glLoadIdentity() # Clear the projection matrix
        gl.glFrustum(left,right,top,bottom,near,far) # Let GL create a matrix and compose it
        matrix = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
        if matrix is None:
            # OpenGL wasn't started
            raise RuntimeError("OpenGL matrix operations can only take place once OpenGL context started.")
        apply(Projection.__init__,(self,),{'matrix':matrix})

####################################################################
#
#        Viewport
#
####################################################################

class Viewport(VisionEgg.ClassWithParameters):
    """Connects stimuli to a screen.

    A viewport defines a (possibly clipped region) of the screen on
    which stimuli are drawn.

    A screen may have multiple viewports.  The viewports may be
    overlapping.

    A viewport may have multiple stimuli.

    A single stimulus may be drawn simultaneously by several
    viewports, although this is typically useful only for 3D stimuli
    to represent different views of the same object.

    The coordinates of the stimulus are converted to screen
    coordinates via several steps, the most important of which is the
    projection, which is defined by an instance of the Projection
    class.

    By default, a viewport has a projection which maps eye coordinates
    to viewport coordinates in 1:1 manner.  In other words, eye
    coordinates specify pixel location in the viewport.

    For cases where pixel units are not natural to describe
    coordinates of a stimulus, the application should specify the a
    projection other than the default.  This is usually the case for
    3D stimuli.
    
    For details of the projection and clipping process, see the
    section 'Coordinate Transformations' in the book/online document
    'The OpenGL Graphics System: A Specification'

    User methods:

    make_new_pixel_coord_projection -- Create a projection with pixel coordinates

    Parameters:

    screen -- Instance of Screen on which to draw
    lowerleft -- Tuple (length 2) specifying viewport lowerleft corner position in pixels relative to screen lowerleft corner.
    size -- Tuple (length 2) specifying viewport size in pixels
    projection -- Instance of Projection
    stimuli -- List of instances of Stimulus to draw
    
    """
    parameters_and_defaults = {'screen':(None,
                                         Screen),
                               'lowerleft':((0,0), # tuple of length 2
                                            types.TupleType), 
                               'size':(None,       # tuple of length 2, will use screen.size if not specified
                                       types.TupleType),
                               'projection':(None, # instance of VisionEgg.Core.Projection
                                             Projection),
                               'stimuli':(None,
                                          types.ListType)} 

    def __init__(self,**kw):
        """Create a new instance.

        Required arguments:

        screen

        Optional arguments (specify parameter value other than default):

        lowerleft -- defaults to (0,0)
        size -- defaults to screen.size
        projection -- defaults to self.make_new_pixel_coord_projection()
        stimuli -- defaults to empty list
        """
        apply(VisionEgg.ClassWithParameters.__init__,(self,),kw)

        if self.parameters.screen is None:
            raise EggError("Must specify screen when creating an instance of Viewport.")
        
        self.stimuli = []
        if self.parameters.size is None:
            self.parameters.size = self.parameters.screen.constant_parameters.size
        if self.parameters.projection is None:
            # Default projection maps eye coordinates 1:1 on window (pixel) coordinates
            self.parameters.projection = self.make_new_pixel_coord_projection()
        if self.parameters.stimuli is None:
            self.parameters.stimuli = []

    def make_new_pixel_coord_projection(self):
        """Create instance of Projection mapping eye coordinates 1:1 with pixel coordinates."""
        return OrthographicProjection(left=0,right=self.parameters.size[0],
                                      bottom=0,top=self.parameters.size[1],
                                      z_clip_near=0.0,
                                      z_clip_far=1.0)

    def draw(self):
        """Called by Presentation. Set the viewport and draw stimuli."""
        self.parameters.screen.make_current()
        gl.glViewport(self.parameters.lowerleft[0],self.parameters.lowerleft[1],self.parameters.size[0],self.parameters.size[1])

        self.parameters.projection.set_gl_projection()
        
        for stimulus in self.parameters.stimuli:
            stimulus.draw()

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

    To illustrate the concept of the Stimulus class, here is a
    description of several methods of drawing two spots.  If your
    experiment displays two spots simultaneously, you could create two
    instances of (a single subclass of) Stimulus, varying parameters
    so each draws at a different location.  Another possibility is to
    create one instance of a subclass that draws two spots.  Another,
    somewhat obscure, possibility is to create a single instance and
    add it to two different viewports.  (Something that will not work
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
    are present in the stimuli list of an instance of Viewport may be
    important.  Additionally, if there are overlapping viewports, the
    order in which viewports are added to an instance of Screen is
    important.

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
        """Instantiate and get ready to draw.

        Set parameter values and create anything needed to draw the
        stimulus including OpenGL state variables such display lists
        and texture objects.

        In this base class, nothing needs to be done other than set
        parameter values.
        """
        apply(VisionEgg.ClassWithParameters.__init__,(self,),kw)
        
    def draw(self):
    	"""Called by Viewport. Draw the stimulus.

        This method is called every frame.  This method actually
        performs the OpenGL calls to draw the stimulus.

        Override this method in a subclass .In this base class it does
        nothing.
        """
        pass
        
####################################################################
#
#        FixationSpot
#
####################################################################

class FixationSpot(Stimulus):
    """A rectangle stimulus, typically used as a fixation spot."""
    parameters_and_defaults = {'on':(1,
                                     types.IntType),
                               'color':((1.0,1.0,1.0,1.0),
                                        types.TupleType),
                               'center':((320.0,240.0), # center if in 640x480 viewport
                                         types.TupleType),
                               'size':((4.0,4.0), # horiz and vertical size
                                       types.TupleType)} 
    
    def __init__(self,**kw):
        apply(Stimulus.__init__,(self,),kw)

    def draw(self):
        if self.parameters.on:
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glDisable(gl.GL_BLEND)

            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            c = self.parameters.color
            gl.glColor(c[0],c[1],c[2],c[3])

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
    Egg. It contains the main 'go' loop, and maintains the association
    between 'controllers', instances of the Controller class, and the
    parameters they control.

    During the main 'go' loop and at other specific times, the
    parameters are updated via function calls to the controllers.

    Between entries into the 'go' loop, a Vision Egg application
    should call the method between_presentations as often as possible
    to ensure parameter values are kept up to date and any
    housekeeping done by controllers is done.

    No OpenGL environment I know of can guarantee that a new frame is
    drawn and the double buffers swapped before the monitor's next
    vertical retrace sync pulse.  Still, although one can worry
    endlessly about this problem, it works.  In other words, on a fast
    computer with a fast graphics card running even a pre-emptive
    multi-tasking operating system (see below for specific
    information), a new frame is drawn before every monitor update. If
    this did become a problem, the go() method could be re-implemented
    in C, along with the functions it calls.  This would probably
    result in speed gains, but without skipping frames at 200 Hz, why
    bother?

    As I update this in June 2002, I have never seen a skipped frame
    in Windows 2000 Pro (dual Athlon 1200 MHz, nVidia GeForce 2 Pro)
    or SGI IRIX 6.5 on a (SGI FUEL/V10 workstation). Linux 2.4.12 with
    low latency kernel patches skips the occasional frame, even with
    POSIX scheduler calls to set FIFO maximum priority on the same
    dual Athlon machine. Mac OS X 10.1.2 skips quite pre-empts the
    Vision Egg quite frequently, although I have not established
    maximum POSIX scheduler priorities.

    Parameters:

    viewports -- List of Viewport instances to draw. Order is important.
    go_duration -- Tuple to specify 'go' loop duration. Either (value,units) or ('forever',)
    check_events -- Int (boolean) to allow input event checking during 'go' loop
    handle_event_callbacks -- List of tuples to handle events. (event_type,event_callback_func)
    trigger_armed -- Int (boolean) to gate the trigger on the 'go' loop
    trigger_go_if_armed -- Int (boolean) the trigger on the 'go' loop
    enter_go_loop -- Int (boolean) used by run_forever to enter 'go' loop
    quit -- Int (boolean) quits the run_forever loop if set
    warn_mean_fps_threshold -- Float (fraction) threshold to print observered vs. expected frame rate warning
    warn_longest_frame_threshold -- Float (fraction) threshold to print frame skipped warning
    
    Methods:

    add_controller -- Add a controller
    remove_controller -- Remove controller from internal list
    go -- Main control loop during stimulus presentation
    export_movie_go -- Emulates method 'go' but saves a movie
    between_presentations -- Maintain display while between stimulus presentations
    
    """
    parameters_and_defaults = {'viewports' : ([],
                                              types.ListType),
                               'go_duration' : ((5.0,'seconds'),
                                                types.TupleType),
                               'check_events' : (0, # May cause performance hit
                                                 types.IntType),
                               'handle_event_callbacks' : (None,
                                                           types.ListType),
                               'trigger_armed':(1, # boolean
                                                types.IntType),
                               'trigger_go_if_armed':(1, #boolean
                                                      types.IntType),
                               'enter_go_loop':(0, #boolean
                                                types.IntType),
                               'quit':(0, #boolean
                                       types.IntType),
                               'warn_mean_fps_threshold':(0.01, # fraction (0.1 = 10%)
                                                          types.FloatType),
                               'warn_longest_frame_threshold':(1.5, # fraction
                                                               types.FloatType),
                               }
    
    def __init__(self,**kw):
        apply(VisionEgg.ClassWithParameters.__init__,(self,),kw)

        if self.parameters.handle_event_callbacks is None:
            self.parameters.handle_event_callbacks = []

        self.controllers = []
        self.num_frame_controllers = 0 # reference counter for controllers that are called on frame by frame basis

        # An list that optionally records when frames were drawn by go() method.
        self.frame_draw_times = []

        self.time_sec_absolute=VisionEgg.timing_func()
        self.frames_absolute=0

    def add_controller( self, class_with_parameters, parameter_name, controller ):
        """Add a controller"""
        # Check if type checking needed
        if type(class_with_parameters) != types.NoneType and type(parameter_name) != types.NoneType:
            # Check if return type of controller eval is same as parameter type
            if class_with_parameters.is_constant_parameter(parameter_name):
                raise TypeError("Attempt to control constant parameter '%s' of class %s."%(parameter_name,class_with_parameters))
            require_type = class_with_parameters.get_specified_type(parameter_name)
            try:
                VisionEgg.assert_type(controller.returns_type(),require_type)
            except TypeError,x:
                raise TypeError("Attempting to control parameter '%s' of type %s with controller that returns type %s"%(
                    parameter_name,
                    class_with_parameters.get_specified_type(parameter_name),
                    controller.returns_type()))                
            if not hasattr(class_with_parameters.parameters,parameter_name):
                raise AttributeError("%s has no instance '%s'"%parameter_name)
            self.controllers.append( (class_with_parameters.parameters,parameter_name, controller) )
        else: # At least one of class_with_parameters or parameter_name is None.
            # Make sure they both are None.
            if not (type(class_with_parameters) == types.NoneType and type(parameter_name) == types.NoneType):
                raise ValueError("Neither or both of class_with_parameters and parameter_name must be None.")
            self.controllers.append( (None,None,controller) )
        if controller.temporal_variables & (Controller.FRAMES_SINCE_GO|Controller.FRAMES_ABSOLUTE):
            self.num_frame_controllers = self.num_frame_controllers + 1

    def remove_controller( self, class_with_parameters, parameter_name, controller ):
        """Remove one (or more--see below) controller(s).

        If controller is None, all controllers affecting the
        specified parameter are removed."""
        
        if controller is None:
            # The controller function is not specified:
            # Delete all controllers that control the parameter specified.
            if class_with_parameters is None or parameter_name is None:
                raise ValueError("Must specify parameter from which controller should be removed.")
            while i < len(self.controllers):
                orig_parameters,orig_parameter_name,orig_controller = self.controllers[i]
                if orig_parameters == class_with_parameters.parameters and orig_parameter_name == parameter_name:
                    del self.controllers[i]
                    if controller.temporal_variables & (Controller.FRAMES_SINCE_GO|Controller.FRAMES_ABSOLUTE):
                        self.num_frame_controllers = self.num_frame_controllers - 1
                else:
                    i = i + 1
        else: # controller is specified
            # Delete only that specific controller
            while i < len(self.controllers):
                orig_parameters,orig_parameter_name,orig_controller = self.controllers[i]
                if orig_parameters == class_with_parameters.parameters and orig_parameter_name == parameter_name and orig_controller == controller:
                    del controller_list[i]
                    if controller.temporal_variables & (Controller.FRAMES_SINCE_GO|Controller.FRAMES_ABSOLUTE):
                        self.num_frame_controllers = self.num_frame_controllers - 1
                else:
                    i = i + 1

    def __call_controllers(self,
                         go_started=None,
                         doing_transition=None):
        done_once = [] # list of ONCE contollers to switch status of
        for (parameters_instance, parameter_name, controller) in self.controllers:
            evaluate = 0
            if controller.eval_frequency & Controller.ONCE:
                evaluate = 1
                done_once.append(controller)
            elif doing_transition and (controller.eval_frequency & Controller.TRANSITIONS):
                evaluate = 1
            elif controller.eval_frequency & Controller.EVERY_FRAME:
                evaluate = 1

            if evaluate:
                if controller.temporal_variables & Controller.TIME_SEC_ABSOLUTE:
                    controller.time_sec_absolute = self.time_sec_absolute
                if controller.temporal_variables & Controller.FRAMES_ABSOLUTE:
                    controller.frames_absolute = self.frames_absolute

                if go_started:
                    if not (controller.eval_frequency & Controller.NOT_DURING_GO):
                        if controller.temporal_variables & Controller.TIME_SEC_SINCE_GO:
                            controller.time_sec_since_go = self.time_sec_since_go
                        if controller.temporal_variables & Controller.FRAMES_SINCE_GO:
                            controller.frames_since_go = self.frames_since_go
                        result = controller.during_go_eval()
                        if parameter_name is not None:
                            setattr(parameters_instance, parameter_name, result)
                else:
                    if not (controller.eval_frequency & Controller.NOT_BETWEEN_GO):
                        if controller.temporal_variables & Controller.TIME_SEC_SINCE_GO:
                            controller.time_sec_since_go = None
                        if controller.temporal_variables & Controller.FRAMES_SINCE_GO:
                            controller.frames_since_go = None
                        result = controller.between_go_eval()
                        if parameter_name is not None:
                            setattr(parameters_instance, parameter_name, result)

        for controller in done_once:
            #Unset ONCE flag
            controller.eval_frequency = controller.eval_frequency & ~Controller.ONCE
            if isinstance(controller,EncapsulatedController):
                controller.contained_controller.eval_frequency = controller.contained_controller.eval_frequency & ~Controller.ONCE
        
    def go(self):
        """Main control loop during stimulus presentation.

        This is the heart of realtime control in the Vision Egg, and
        contains the main loop during a stimulus presentation. This
        coordinates the timing of calling the controllers.

        In the main loop, the current time (in absolute seconds,
        go-loop-start-relative seconds, and go-loop-start-relative
        frames) is computed, the appropriate controllers are called
        with this information, the screen is cleared, each viewport is
        drawn to the back buffer (while the video card continues
        painting the front buffer on the display), and the buffers are
        swapped.

        """
        collect_timing_info = VisionEgg.config.VISIONEGG_RECORD_TIMES
        # Create shorthand notation, which speeds the main loop
        # slightly by not performing name lookup each time.
        p = self.parameters

        # Clear any previous timing info if necessary
        if collect_timing_info:
            self.frame_draw_times = []

        while (not p.trigger_armed) or (not p.trigger_go_if_armed):
            self.between_presentations()

        # Go!

        longest_frame_draw_time_sec = 0.0
            
        self.time_sec_absolute=VisionEgg.timing_func()
        self.time_sec_since_go = 0.0
        self.frames_since_go = 0
        
        # Tell transitional controllers a presentation is starting
        self.__call_controllers(
            go_started=1,
            doing_transition=1)

        # Do the main loop
        start_time_absolute = self.time_sec_absolute
        if p.go_duration[0] == 'forever': # forever
            current_duration_value = 0
        elif p.go_duration[1] == 'seconds': # duration units
            current_duration_value = self.time_sec_since_go
        elif p.go_duration[1] == 'frames': # duration units
            current_duration_value = self.frames_since_go
        else:
            raise RuntimeError("Unknown duration unit '%s'"%p.go_duration[1])
        while (current_duration_value < p.go_duration[0]):
            # Update all the realtime parameters
            self.__call_controllers(
                go_started=1,
                doing_transition=0)
            
            # Get list of screens
            screens = []
            for viewport in p.viewports:
                s = viewport.parameters.screen
                if s not in screens:
                    screens.append(s)
                
            # Clear the screen(s)
            for screen in screens:
                screen.clear()
                
            # Draw each viewport
            for viewport in p.viewports:
                viewport.draw()
                
            # Swap the buffers
            swap_buffers()
            
            # If wanted, save time this frame was drawn for
            if collect_timing_info:
                self.frame_draw_times.append(self.time_sec_since_go)
                
            # Set the time variables for the next frame
            self.time_sec_absolute=VisionEgg.timing_func()
            last_time_sec_since_go = self.time_sec_since_go
            self.time_sec_since_go = self.time_sec_absolute - start_time_absolute
            self.frames_absolute = self.frames_absolute+1
            self.frames_since_go = self.frames_since_go+1

            longest_frame_draw_time_sec = max(longest_frame_draw_time_sec,self.time_sec_since_go-last_time_sec_since_go)
        
            # Make sure we use the right value to check if we're done
            if p.go_duration[0] == 'forever': # forever
                pass # current_duration_value already set to 0
            elif p.go_duration[1] == 'seconds':
                current_duration_value = self.time_sec_since_go
            elif p.go_duration[1] == 'frames':
                current_duration_value = self.frames_since_go
            else:
                raise RuntimeError("Unknown duration unit '%s'"%p.go_duration[1])

            # Check events if requested
            if p.check_events:
                for event in pygame.event.get():
                    for event_type, event_callback in p.handle_event_callbacks:
                        if event.type is event_type:
                            event_callback(event)
            
        # Tell transitional controllers a presentation has ended
        self.__call_controllers(
            go_started=0,
            doing_transition=1)
        
        # Check to see if frame by frame control was desired
        # but OpenGL not syncing to vertical retrace
        calculated_fps = self.frames_since_go / self.time_sec_since_go
        if self.num_frame_controllers: # Frame by frame control desired
            impossibly_fast_frame_rate = 210.0
            if calculated_fps > impossibly_fast_frame_rate: # Let's assume no monitor can exceed impossibly_fast_frame_rate
                message.add(
                    """Frame by frame control desired, but average
                    frame rate was %f frames per second-- faster than
                    any display device (that I know of).  Set your
                    drivers to sync buffer swapping to vertical
                    retrace. (platform/driver
                    dependent)"""%(calculated_fps),
                    level=Message.ERROR
                    )
                
        # Warn if > warn_mean_fps_threshold error in frame rate
        if abs(calculated_fps-VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ) / float(VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ) > self.parameters.warn_mean_fps_threshold:
            # Should also add VisionEgg.config.FRAME_LOCKED_MODE variable
            # and only print this warning if that variable is true
            message.add(
                """Calculated frames per second was %s, while
                VisionEgg.config specified %s."""%(calculated_fps,VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ),
                level=Message.WARNING
                )

        frame_skip_fraction = self.parameters.warn_longest_frame_threshold
        inter_frame_inteval = 1.0/VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ

        if longest_frame_draw_time_sec >= (frame_skip_fraction*inter_frame_inteval):
            message.add(

                """One or more frames took %.1f msec, which is
                signficantly longer than the expected inter frame
                interval of %.1f msec for your frame rate (%.1f Hz)."""%(
         
                longest_frame_draw_time_sec*1000.0,inter_frame_inteval*1000.0,VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ),
                level=Message.WARNING)
        else:
            message.add(

                """Longest frame update was %.1f msec.  Your expected
                inter frame interval is %f msec."""%(

                longest_frame_draw_time_sec*1000.0,inter_frame_inteval*1000.0),
                level=Message.TRIVIAL)
                
        if collect_timing_info:
            self.__print_frame_timing_stats()

    def export_movie_go(self, frames_per_sec=12.0, filename_suffix=".tif", filename_base="visionegg_movie", path="."):
        """Emulates method 'go' but saves a movie."""
        import Image # Could import this at the beginning of the file, but it breaks sometimes!
        import os # Could also import this, but this is the only place its needed
        
        # Create shorthand notation, which speeds the main loop
        # slightly by not performing name lookup each time.
        p = self.parameters
        
        # Switch function VisionEgg.timing_func
        self.time_sec_absolute=VisionEgg.timing_func() # Set for real once
        real_timing_func = VisionEgg.timing_func
        def fake_timing_func():
            return self.time_sec_absolute
        VisionEgg.timing_func = fake_timing_func
        
        # Go!
            
        self.time_sec_absolute=VisionEgg.timing_func()
        self.time_sec_since_go = 0.0
        self.frames_since_go = 0
        
        # Tell transitional controllers a presentation is starting
        self.__call_controllers(
            go_started=1,
            doing_transition=1)

        # Do the main loop
        image_no = 1
        if p.go_duration[0] == 'forever': # forever
            current_duration_value = 0
        elif p.go_duration[1] == 'seconds': # duration units
            current_duration_value = self.time_sec_since_go
        elif p.go_duration[1] == 'frames': # duration units
            current_duration_value = self.frames_since_go
        else:
            raise RuntimeError("Unknown duration unit '%s'"%p.go_duration[1])
        while (current_duration_value < p.go_duration[0]):
            # Update all the realtime parameters
            self.__call_controllers(
                go_started=1,
                doing_transition=0)
            
            # Get list of screens
            screens = []
            for viewport in p.viewports:
                s = viewport.parameters.screen
                if s not in screens:
                    screens.append(s)
                
            # Clear the screen(s)
            for screen in screens:
                screen.clear()
                
            # Draw each viewport
            for viewport in p.viewports:
                viewport.draw()
                
            # Swap the buffers
            swap_buffers()
            
            # Now save the contents of the framebuffer
            gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
            framebuffer = gl.glReadPixels(0,0,screen.size[0],screen.size[1],gl.GL_RGB,gl.GL_UNSIGNED_BYTE)
            fb_image = Image.fromstring('RGB',screen.size,framebuffer)
            fb_image = fb_image.transpose( Image.FLIP_TOP_BOTTOM )
            filename = "%s%04d%s"%(filename_base,image_no,filename_suffix)
            savepath = os.path.join( path, filename )
            message.add("Saving '%s'"%filename)
            fb_image.save( savepath )
            image_no = image_no + 1

            # Set the time variables for the next frame
            self.time_sec_absolute= self.time_sec_absolute + 1.0/frames_per_sec
            self.time_sec_since_go = self.time_sec_since_go + 1.0/frames_per_sec
            self.frames_absolute = self.frames_absolute+1
            self.frames_since_go = self.frames_since_go+1

            # Make sure we use the right value to check if we're done
            if p.go_duration[0] == 'forever':
                pass # current_duration_value already set to 0
            elif p.go_duration[1] == 'seconds':
                current_duration_value = self.time_sec_since_go
            elif p.go_duration[1] == 'frames':
                current_duration_value = self.frames_since_go
            else:
                raise RuntimeError("Unknown duration unit '%s'"%p.go_duration[1])
            
            # Check events if requested
            if p.check_events:
                for event in pygame.event.get():
                    for event_type, event_callback in p.handle_event_callbacks:
                        if event.type is event_type:
                            event_callback(event)

        # Tell transitional controllers a presentation has ended
        self.__call_controllers(
            go_started=0,
            doing_transition=1)

        if len(screens) > 1:
            message.add(
                """Only saved movie from last screen.""", level=Message.INFO)

        if screen.red_bits is not None:
            warn_about_movie_depth = 0
            if screen.red_bits > 8:
                warn_about_movie_depth = 1
            elif screen.green_bits > 8:
                warn_about_movie_depth = 1
            elif screen.blue_bits > 8:
                warn_about_movie_depth = 1
            if warn_about_movie_depth:
                message.add(
                    """Only saved 8 bit per pixel movie, even
                    though your framebuffer supports more!""",
                    level=Message.WARNING)

        # Restore VisionEgg.timing_func
        VisionEgg.timing_func = real_timing_func

    def run_forever(self):
        p = self.parameters
        # enter with transitional contoller call
        self.__call_controllers(
            go_started=0,
            doing_transition=1)
        while not p.quit:
            self.between_presentations()
            if self.parameters.enter_go_loop:
                self.parameters.enter_go_loop = 0
                self.go()
            if p.check_events:
                for event in pygame.event.get():
                    for event_type, event_callback in p.handle_event_callbacks:
                        if event.type is event_type:
                            event_callback(event)

    def between_presentations(self):
        """Maintain display while between stimulus presentations.

        This function gets called as often as possible when not
        in the 'go' loop.

        Other than the difference in the time variable passed to the
        controllers, this routine is very similar to the inside of the
        main loop in the go method.
        """
        
        self.time_sec_absolute=VisionEgg.timing_func()
        
        self.__call_controllers(
            go_started=0,
            doing_transition=0)

        viewports = self.parameters.viewports

        # Get list of screens
        screens = []
        for viewport in viewports:
            s = viewport.parameters.screen
            if s not in screens:
                screens.append(s)
            
        # Clear the screen(s)
        for screen in screens:
            screen.clear()
        # Draw each viewport, including each stimulus
        for viewport in viewports:
            viewport.draw()
        swap_buffers()
        self.frames_absolute = self.frames_absolute+1
        
    def __print_frame_timing_stats(self):
        """Print a histogram of the last recorded frame drawing times.

        If argument 
        """
        if len(self.frame_draw_times) > 1:
            frame_draw_times = Numeric.array(self.frame_draw_times)
            self.frame_draw_times = [] # clear the list
            frame_draw_times = frame_draw_times[1:] - frame_draw_times[:-1] # get inter-frame interval
            timing_string = "During the last \"go\" loop, "+str((len(frame_draw_times)+1))+" frames were drawn.\n"
            mean_sec = MLab.mean(frame_draw_times)
            timing_string = timing_string + "mean frame to frame time: %.3f msec (== %.2f fps), max time: %.3f msec\n"%(mean_sec*1.0e3,1.0/mean_sec,max(frame_draw_times)*1.0e3)
            bins = Numeric.arange(0.0,19.0,1.0) # msec
            bins = bins*1.0e-3 # sec
            timing_string = self.__print_hist(frame_draw_times,bins,timing_string)
            timing_string = timing_string + "\n"
            message.add(timing_string,level=Message.INFO,preserve_formatting=1)

    def __histogram(self,a, bins):  
        """Create a histogram from data

        This function is taken straight from NumDoc.pdf, the Numeric Python
        documentation."""
        n = Numeric.searchsorted(Numeric.sort(a),bins)
        n = Numeric.concatenate([n, [len(a)]])
        return n[1:]-n[:-1]
        
    def __print_hist(self,a, bins, timing_string):
        """Print a pretty histogram"""
        hist = self.__histogram(a,bins)
        lines = 10
        maxhist = float(max(hist))
        h = hist # copy
        hist = hist.astype('f')/maxhist*float(lines) # normalize to 10
        timing_string = timing_string + "histogram:\n"
        for line in range(lines):
            val = float(lines)-1.0-float(line)
            timing_string = timing_string + "%6d   "%(round(maxhist*val/10.0),)
            q = Numeric.greater(hist,val)
            for qi in q:
                s = ' '
                if qi:
                    s = '*'
                timing_string = timing_string + "%4s "%(s,)
            timing_string = timing_string + "\n"
        timing_string = timing_string + " Time: "
        for bin in bins:
            timing_string = timing_string + "%4d "%(int(bin*1.0e3),)
        timing_string = timing_string + "+(msec)\n"
        timing_string = timing_string + "Total:    "
        for hi in h:
            if hi <= 999:
                num_str = string.center(str(hi),5)
            else:
                num_str = " +++ "
            timing_string = timing_string + num_str
        timing_string = timing_string+"\n"
        return timing_string
        
####################################################################
#
#        Controller
#
####################################################################

class Controller:
    """Control parameters.

    This abstract base class defines interface to any controller.

    A Controller instance's attribute "eval_frequency" controls when a
    controller is evaluated. This variable is a bitwise "or" of the
    following flags:

    Controller.NEVER          -- never
    Controller.EVERY_FRAME    -- every frame
    Controller.TRANSITIONS    -- on enter and exit from go loop
    Controller.ONCE           -- as above and at the next chance possible
    Controller.NOT_DURING_GO  -- as above, but never during go loop
    Controller.NOT_BETWEEN_GO -- as above, but never between go loops

    The Controller.ONCE flag is automatically unset after evaluation,
    hence its name.

    As an example, if eval_frequency is set to Controller.ONCE |
    Controller.TRANSITIONS (the bitwise "or"), it will be evaluated
    before drawing the next frame and then only before and after the
    go loop.

    A Controller instance's attribute "temporal_variables" controls
    what time variables are set for use. This variable is a bitwise
    "or" of the following flags:

    Controller.TIME_SEC_ABSOLUTE -- seconds, continuously increasing
    Controller.TIME_SEC_SINCE_GO -- seconds, reset to 0.0 each go loop
    Controller.FRAMES_ABSOLUTE   -- frames, continuously increasing
    Controller.FRAMES_SINCE_GO   -- frames, reset to 0 each go loop

    Attributes:

    return_type -- type of the value returned by the eval functions
    eval_frequency -- when eval functions called (see above)
    temporal_variables -- what time variables used (see above)
    
    Methods:
    
    returns_type -- Get the type of the value returned by the eval functions
    during_go_eval -- Evaluate controller during the main 'go' loop.
    between_go_eval -- Evaluate controller between runs of the main 'go' loop.
    
    """
    # temporal_variables flags:
    TIME_INDEPENDENT  = 0x00
    TIME_SEC_ABSOLUTE = 0x01
    TIME_SEC_SINCE_GO = 0x02
    FRAMES_ABSOLUTE   = 0x04
    FRAMES_SINCE_GO   = 0x08

    # eval_frequency flags:
    NEVER          = 0x00
    EVERY_FRAME    = 0x01
    TRANSITIONS    = 0x02
    ONCE           = 0x04
    NOT_DURING_GO  = 0x08
    NOT_BETWEEN_GO = 0x10

    flag_dictionary = {
        'TIME_INDEPENDENT'  : TIME_INDEPENDENT,
        'TIME_SEC_ABSOLUTE' : TIME_SEC_ABSOLUTE,
        'TIME_SEC_SINCE_GO' : TIME_SEC_SINCE_GO,
        'FRAMES_ABSOLUTE'   : FRAMES_ABSOLUTE,
        'FRAMES_SINCE_GO'   : FRAMES_SINCE_GO,
        
        'NEVER'             : NEVER,
        'EVERY_FRAME'       : EVERY_FRAME,
        'TRANSITIONS'       : TRANSITIONS,
        'ONCE'              : ONCE,
        'NOT_DURING_GO'     : NOT_DURING_GO,
        'NOT_BETWEEN_GO'    : NOT_BETWEEN_GO}
    
    def __init__(self,
                 eval_frequency = EVERY_FRAME,
                 temporal_variables = TIME_SEC_SINCE_GO,
                 return_type = None):
        """Create instance of Controller. 

        Arguments:

        eval_frequency -- Int, bitwise "or" of flags
        temporal_variables -- Int, bitwise "or" of flags
        return_type -- Set to type() of the parameter under control
        
        """
        if return_type is None: # Can be types.NoneType, but not None!
            raise ValueError("Must set argument 'return_type' in Controller.")
        if type(return_type) not in [types.TypeType,types.ClassType]:
            raise TypeError("argument 'return_type' must specify a type or class.")
        self.return_type = return_type
        
        self.temporal_variables = temporal_variables
        self.eval_frequency = eval_frequency

    def evaluate_now(self):
        """Call this after updating the values of a controller if it's not evaluated EVERY_FRAME."""
        self.eval_frequency = self.eval_frequency | Controller.ONCE

    def set_eval_frequency(self,eval_frequency):
        self.eval_frequency = eval_frequency
        
    def returns_type(self):
        """Called by Presentation. Get the return type of this controller."""
        return self.return_type
    
    def during_go_eval(self):
        """Called by Presentation. Evaluate during the main 'go' loop.

        Override this method in base classes."""
        raise NotImplementedError("Definition in abstract base class Contoller must be overriden.")

    def between_go_eval(self):
        """Called by Presentation. Evaluate between runs of the main 'go' loop.
        
        Override this method in base classes.""" 
        raise NotImplementedError("Definition in abstract base class Controller must be overriden.")

    def _test_self(self,go_started):
        """Test whether a controller works.
        
        This method performs everything the Presentation go() or
        run_forever() methods do when calling controllers, except that
        the temporal variables are set to -1 and that the return value
        is not used to set parameters."""
        
        if self.temporal_variables & Controller.TIME_SEC_ABSOLUTE:
            self.time_sec_absolute = -1.0
        if self.temporal_variables & Controller.FRAMES_ABSOLUTE:
            self.frames_absolute = -1

        if go_started:
            if not (self.eval_frequency & Controller.NOT_DURING_GO):
                if self.temporal_variables & Controller.TIME_SEC_SINCE_GO:
                    self.time_sec_since_go = -1.0
                if self.temporal_variables & Controller.FRAMES_SINCE_GO:
                    self.frames_since_go = -1
                return self.during_go_eval()
        else:
            if not (self.eval_frequency & Controller.NOT_BETWEEN_GO):
                if self.temporal_variables & Controller.TIME_SEC_SINCE_GO:
                    self.time_sec_since_go = None
                if self.temporal_variables & Controller.FRAMES_SINCE_GO:
                    self.frames_since_go = None
                return self.between_go_eval()
    
class ConstantController(Controller):
    """Set parameters to a constant value."""
    def __init__(self,
                 during_go_value = None,
                 between_go_value = None,
                 **kw
                 ):
        if 'return_type' not in kw.keys():
            kw['return_type'] = VisionEgg.get_type(during_go_value)
        if 'eval_frequency' not in kw.keys():
            kw['eval_frequency'] = Controller.ONCE | Controller.TRANSITIONS
        apply(Controller.__init__,(self,),kw)
        if self.return_type is not types.NoneType and during_go_value is None:
            raise ValueError("Must specify during_go_value")
        if between_go_value is None:
            between_go_value = during_go_value
        VisionEgg.assert_type(VisionEgg.get_type(during_go_value),self.return_type)
        VisionEgg.assert_type(VisionEgg.get_type(between_go_value),self.return_type)
        self.during_go_value = during_go_value
        self.between_go_value = between_go_value

    def set_during_go_value(self,during_go_value):
        if type(during_go_value) is not self.return_type:
            raise TypeError("during_go_value must be of type %s"%return_type)
        else:
            self.during_go_value = during_go_value

    def get_during_go_value(self):
        return self.during_go_value
        
    def set_between_go_value(self,between_go_value):
        if type(between_go_value) is not self.return_type:
            raise TypeError("between_go_value must be of type %s"%return_type)
        else:
            self.between_go_value = between_go_value

    def get_between_go_value(self):
        return self.between_go_value
            
    def during_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        return self.during_go_value

    def between_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        return self.between_go_value

class EvalStringController(Controller):
    """Set parameters using dynamically interpreted Python string.
    
    To increase speed, the string is compiled to Python's bytecode
    format.
    
    The string can make use of temporal variables, which are made
    available depending on the controller's temporal_variables
    attribute. Note that only the absolute temporal variables are
    available when the go loop is not running.

    flag(s) present    variable  description
    
    TIME_SEC_ABSOLUTE  t_abs     seconds, continuously increasing
    TIME_SEC_SINCE_GO  t         seconds, reset to 0.0 each go loop
    FRAMES_ABSOLUTE    f_abs     frames, continuously increasing
    FRAMES_SINCE_GO    f         frames, reset to 0 each go loop
    
    """
    def __init__(self,
                 during_go_eval_string = None,
                 between_go_eval_string = None,
                 **kw
                 ):
        # Create a namespace for eval_strings to use
        self.eval_globals = {}

        if during_go_eval_string is None:
            raise ValueError("'during_go_eval_string' is a required argument")
        
        # Make Numeric and math modules available
        self.eval_globals['Numeric'] = Numeric
        self.eval_globals['math'] = math
        # Make Numeric and math modules available without module name
        for key in dir(Numeric):
            self.eval_globals[key] = getattr(Numeric,key)
        for key in dir(math):
            self.eval_globals[key] = getattr(math,key)

        self.during_go_eval_code = compile(during_go_eval_string,'<string>','eval')
        self.during_go_eval_string = during_go_eval_string
        not_between_go = 0
        if between_go_eval_string is None:
            not_between_go = 1
        else:
            self.between_go_eval_code = compile(between_go_eval_string,'<string>','eval')
            self.between_go_eval_string = between_go_eval_string
            
        # Check to make sure return_type is set
        set_return_type = 0
        if 'return_type' not in kw.keys():
            set_return_type = 1
            kw['return_type'] = types.NoneType
            
        # Call base class __init__
        apply(Controller.__init__,(self,),kw)
        if not_between_go:
            self.eval_frequency = self.eval_frequency|Controller.NOT_BETWEEN_GO
        if set_return_type:
            if not (self.eval_frequency & Controller.NOT_DURING_GO):
                message.add('Executing "%s" to test for return type.'%(during_go_eval_string,),
                            Message.TRIVIAL)
                self.return_type = type(self._test_self(go_started=1))
            elif not (self.eval_frequency & Controller.NOT_BETWEEN_GO):
                message.add('Executing "%s" to test for return type.'%(between_go_eval_string,),
                            Message.TRIVIAL)
                self.return_type = type(self._test_self(go_started=0))
                
    def set_during_go_eval_string(self,during_go_eval_string):
        self.during_go_eval_code = compile(during_go_eval_string,'<string>','eval')
        self.during_go_eval_string = during_go_eval_string

    def get_during_go_eval_string(self):
        return self.during_go_eval_string

    def set_between_go_eval_string(self,between_go_eval_string):
        self.between_go_eval_code = compile(between_go_eval_string,'<string>','eval')
        self.between_go_eval_string = between_go_eval_string
        self.eval_frequency = self.eval_frequency & ~Controller.NOT_BETWEEN_GO

    def get_between_go_eval_string(self):
        if hasattr(self,"between_go_eval_string"):
            return self.between_go_eval_string
        else:
            return None

    def during_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        eval_locals = {}
        if self.temporal_variables & Controller.TIME_SEC_ABSOLUTE:
            eval_locals['t_abs'] = self.time_sec_absolute
        if self.temporal_variables & Controller.TIME_SEC_SINCE_GO:
            eval_locals['t'] = self.time_sec_since_go
        if self.temporal_variables & Controller.FRAMES_ABSOLUTE:
            eval_locals['f_abs'] = self.frames_absolute
        if self.temporal_variables & Controller.FRAMES_SINCE_GO:
            eval_locals['f'] = self.frames_since_go
        return eval(self.during_go_eval_code,self.eval_globals,eval_locals)

    def between_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        eval_locals = {}
        if self.temporal_variables & Controller.TIME_SEC_ABSOLUTE:
            eval_locals['t_abs'] = self.time_sec_absolute
        if self.temporal_variables & Controller.FRAMES_ABSOLUTE:
            eval_locals['f_abs'] = self.frames_absolute
        return eval(self.between_go_eval_code,self.eval_globals,eval_locals)
    
class ExecStringController(Controller):
    """Set parameters using potentially complex Python string.

    You can execute arbitrarily complex Python code with this
    controller.  To increase speed, the string is compiled to Python's
    bytecode format.

    The string can make use of temporal variables, which are made
    available depending on the controller's temporal_variables
    attribute. Note that only the absolute temporal variables are
    available when the go loop is not running.

    flag(s) present    variable  description
    
    TIME_SEC_ABSOLUTE  t_abs     seconds, continuously increasing
    TIME_SEC_SINCE_GO  t         seconds, reset to 0.0 each go loop
    FRAMES_ABSOLUTE    f_abs     frames, continuously increasing
    FRAMES_SINCE_GO    f         frames, reset to 0 each go loop

    """
    def __init__(self,
                 during_go_exec_string = None,
                 between_go_exec_string = None,
                 restricted_namespace = 1,
                 **kw
                 ):
        # Create a namespace for eval_strings to use
        self.eval_globals = {}

        if during_go_exec_string is None:
            raise ValueError("'during_go_exec_string' is a required argument")

        self.restricted_namespace = restricted_namespace

        if self.restricted_namespace:
            # Make Numeric and math modules available
            self.eval_globals['Numeric'] = Numeric
            self.eval_globals['math'] = math
            # Make Numeric and math modules available without module name
            for key in dir(Numeric):
                self.eval_globals[key] = getattr(Numeric,key)
            for key in dir(math):
                self.eval_globals[key] = getattr(math,key)

        self.during_go_exec_code = compile(during_go_exec_string,'<string>','exec')
        self.during_go_exec_string = during_go_exec_string
        not_between_go = 0
        if between_go_exec_string is None:
            not_between_go = 1
        else:
            self.between_go_exec_code = compile(between_go_exec_string,'<string>','exec')
            self.between_go_exec_string = between_go_exec_string

        # Check to make sure return_type is set
        set_return_type = 0
        if 'return_type' not in kw.keys():
            set_return_type = 1
            kw['return_type'] = types.NoneType

        # Call base class __init__
        apply(Controller.__init__,(self,),kw)
        if not_between_go:
            self.eval_frequency = self.eval_frequency|Controller.NOT_BETWEEN_GO        
        if set_return_type:
            if not (self.eval_frequency & Controller.NOT_DURING_GO):
                message.add('Executing "%s" to test for return type.'%(during_go_exec_string,),
                            Message.TRIVIAL)
                self.return_type = type(self._test_self(go_started=1))
            elif not (self.eval_frequency & Controller.NOT_BETWEEN_GO):
                message.add('Executing "%s" to test for return type.'%(between_go_exec_string,),
                            Message.TRIVIAL)
                self.return_type = type(self._test_self(go_started=0))

    def set_during_go_exec_string(self,during_go_exec_string):
        self.during_go_exec_code = compile(during_go_exec_string,'<string>','exec')
        self.during_go_exec_string = during_go_exec_string

    def get_during_go_exec_string(self):
        return self.during_go_exec_string

    def set_between_go_exec_string(self,between_go_exec_string):
        self.between_go_exec_code = compile(between_go_exec_string,'<string>','exec')
        self.between_go_exec_string = between_go_exec_string
        self.eval_frequency = self.eval_frequency & ~Controller.NOT_BETWEEN_GO

    def get_between_go_exec_string(self):
        if hasattr(self,"between_go_exec_string"):
            return self.between_go_exec_string
        else:
            return None

    def during_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        eval_locals = {}
        if self.temporal_variables & Controller.TIME_SEC_ABSOLUTE:
            eval_locals['t_abs'] = self.time_sec_absolute
        if self.temporal_variables & Controller.TIME_SEC_SINCE_GO:
            eval_locals['t'] = self.time_sec_since_go
        if self.temporal_variables & Controller.FRAMES_ABSOLUTE:
            eval_locals['f_abs'] = self.frames_absolute
        if self.temporal_variables & Controller.FRAMES_SINCE_GO:
            eval_locals['f'] = self.frames_since_go
        if self.restricted_namespace:
            exec self.during_go_exec_code in self.eval_globals,eval_locals
            return eval_locals['x']
        else:
            setup_locals_str = "\n"
            for local_variable_name in eval_locals.keys():
                setup_locals_str = setup_locals_str + local_variable_name + "=" + repr(eval_locals[local_variable_name]) + "\n"
                exec setup_locals_str
            exec self.during_go_exec_code
            return x

    def between_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        eval_locals = {}
        if self.temporal_variables & Controller.TIME_SEC_ABSOLUTE:
            eval_locals['t_abs'] = self.time_sec_absolute
        if self.temporal_variables & Controller.FRAMES_ABSOLUTE:
            eval_locals['f_abs'] = self.frames_absolute
        if self.restricted_namespace:
            exec self.between_go_exec_code in self.eval_globals,eval_locals
            return eval_locals['x']
        else:
            setup_locals_str = "\n"
            for local_variable_name in eval_locals.keys():
                setup_locals_str = setup_locals_str + local_variable_name + "=" + repr(eval_locals[local_variable_name]) + "\n"
                exec setup_locals_str
            exec self.between_go_exec_code
            return x
    
class FunctionController(Controller):
    """Set parameters using a Python function.

    This is a very commonly used subclass of Controller, because it is
    very intuitive and requires a minimum of code to set up.  Many of
    the Vision Egg demo programs create instances of
    FunctionController.

    """
    def __init__(self,
                 during_go_func = None,
                 between_go_func = None,
                 **kw
                 ):
        """Create an instance of FunctionController.

        Arguments:
    
        during_go_func -- function evaluted during go loop
        between_go_func -- function evaluted not during go loop
        
        """
        if during_go_func is None:
            raise ValueError("Must specify during_go_func")
            
        # Set default value if not set
        if 'temporal_variables' not in kw.keys():
            kw['temporal_variables'] = Controller.TIME_SEC_SINCE_GO # default value

        # Check to make sure return_type is set
        if 'return_type' not in kw.keys():
            message.add('Evaluating %s to test for return type.'%(str(during_go_func),),
                        Message.TRIVIAL)
            call_args = {}
            if kw['temporal_variables'] & Controller.TIME_SEC_ABSOLUTE:
                call_args['t_abs'] = VisionEgg.timing_func()
            if kw['temporal_variables'] & Controller.TIME_SEC_SINCE_GO:
                call_args['t'] = 0.0
            if kw['temporal_variables'] & Controller.FRAMES_ABSOLUTE:
                call_args['f_abs'] = 0
            if kw['temporal_variables'] & Controller.FRAMES_SINCE_GO:
                call_args['f'] = 0
            # Call the function with time variables
            kw['return_type'] = type(apply(during_go_func,(),call_args))
        apply(Controller.__init__,(self,),kw)
        self.during_go_func = during_go_func
        self.between_go_func = between_go_func
        if between_go_func is None:
            self.eval_frequency = self.eval_frequency|Controller.NOT_BETWEEN_GO

    def during_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        call_args = {}
        if self.temporal_variables & Controller.TIME_SEC_ABSOLUTE:
            call_args['t_abs'] = self.time_sec_absolute
        if self.temporal_variables & Controller.TIME_SEC_SINCE_GO:
            call_args['t'] = self.time_sec_since_go
        if self.temporal_variables & Controller.FRAMES_ABSOLUTE:
            call_args['f_abs'] = self.frames_absolute
        if self.temporal_variables & Controller.FRAMES_SINCE_GO:
            call_args['f'] = self.frames_since_go
        return apply(self.during_go_func,(),call_args)

    def between_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        call_args = {}
        if self.temporal_variables & Controller.TIME_SEC_ABSOLUTE:
            call_args['t_abs'] = self.time_sec_absolute
        if self.temporal_variables & Controller.FRAMES_ABSOLUTE:
            call_args['f_abs'] = self.frames_absolute
        return apply(self.between_go_func,(),call_args)

class EncapsulatedController(Controller):
    """Set parameters by encapsulating another Controller.

    Allows a new instance of Controller to control the same parameter
    as an old instance.

    You probably won't ever have to use this class directly.  Both the
    VisionEgg.TCPController.TCPController and
    VisionEgg.PyroHelpers.PyroEncapsulatedController classes subclass
    this class.

    """
    def __init__(self,initial_controller):
        # Initialize base class without raising error for no return_type
        apply(Controller.__init__,(self,),{'return_type':types.NoneType})
        self.contained_controller = initial_controller
        self.__sync_mimic()
        
    def __sync_mimic(self):
        self.return_type = self.contained_controller.return_type
        self.temporal_variables = self.contained_controller.temporal_variables
        self.eval_frequency = self.contained_controller.eval_frequency
        
    def set_new_controller(self,new_controller):
        """Call this to encapsulate a (new) controller."""
        self.contained_controller = new_controller
        self.__sync_mimic()

    def during_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        if self.temporal_variables & VisionEgg.Core.Controller.TIME_SEC_ABSOLUTE:
            self.contained_controller.time_sec_absolute = self.time_sec_absolute
        if self.temporal_variables & VisionEgg.Core.Controller.TIME_SEC_SINCE_GO:
            self.contained_controller.time_sec_since_go = self.time_sec_since_go
        if self.temporal_variables & VisionEgg.Core.Controller.FRAMES_ABSOLUTE:
            self.contained_controller.frames_absolute = self.frames_absolute
        if self.temporal_variables & VisionEgg.Core.Controller.FRAMES_SINCE_GO:
            self.contained_controller.frames_since_go = self.frames_since_go
        return self.contained_controller.during_go_eval()

    def between_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        if self.temporal_variables & VisionEgg.Core.Controller.TIME_SEC_ABSOLUTE:
            self.contained_controller.time_sec_absolute = self.time_sec_absolute
        if self.temporal_variables & VisionEgg.Core.Controller.FRAMES_ABSOLUTE:
            self.contained_controller.frames_absolute = self.frames_absolute
        return self.contained_controller.between_go_eval()
        
####################################################################
#
#        Error handling and assumption checking
#
####################################################################

class Message:
    """Handles message/warning/error printing, exception raising."""

    # Levels are:
    TRIVIAL = 0
    NAG = 1
    INFO = 2
    DEPRECATION = 3
    WARNING = 4
    ERROR = 5
    FATAL = 6
    
    def __init__(self,
                 prefix="VisionEgg",
                 exception_level=ERROR,
                 print_level=VisionEgg.config.VISIONEGG_MESSAGE_LEVEL,
                 output_stream=None):
        self.prefix = prefix
        self.message_queue = []
        self.exception_level = exception_level
        self.print_level = print_level
        self.orig_stderr = sys.stderr
        if output_stream is None:
            if VisionEgg.config.VISIONEGG_LOG_FILE:
                try:
                    self.output_stream = open(VisionEgg.config.VISIONEGG_LOG_FILE,"a")
                except:
                    self.output_stream = sys.stderr
                    self.add("Could not open log file %s, writing to stderr instead.",
                             level=Message.WARNING)
            else:
                self.output_stream = sys.stderr
        else:
            if hasattr(output_stream,"write") and hasattr(output_stream,"flush"):
                self.output_stream = output_stream
            else:
                raise TypeError("argument output_stream must have write and flush methods.")
        if self.output_stream != sys.stderr:
            sys.stderr = self.output_stream
        self.add(sys.argv[0]+" started.",level=Message.INFO)

    def __del__(self):
        self.output_stream.write("\n")
        try:
            sys.stderr = self.orig_stderr
        except:
            pass
        
    def add(self,message,level=INFO,preserve_formatting=0):
        date_str = time.strftime("%Y-%m-%d %H:%M:%S")
        self.message_queue.append((level,message,preserve_formatting,date_str))
        self.handle()
        
    def format_string(self,in_str):
        # This probably a slow way to do things, but it works!
        min_line_length = 90
        in_list = string.split(in_str)
        out_str = ""
        cur_line = ""
        for word in in_list:
            cur_line = cur_line + word + " "
            if len(cur_line) > min_line_length:
                out_str = out_str + cur_line[:-1] + "\n"
                cur_line = "    "
        out_str = out_str + cur_line + "\n"
        return out_str
            
    def handle(self):
        while len(self.message_queue) > 0:
            my_str = ""
            level,text,preserve_formatting,date_str = self.message_queue.pop(0)
            if level >= self.print_level:
                my_str=my_str+self.prefix+" "
                if level == Message.TRIVIAL:
                    my_str=my_str+" trivial"
                elif level == Message.INFO:
                    my_str=my_str+" info"
                elif level == Message.NAG:
                    my_str=my_str+" nag"
                elif level == Message.DEPRECATION:
                    my_str=my_str+" deprecation"
                elif level == Message.WARNING:
                    my_str=my_str+" WARNING"
                elif level == Message.ERROR:
                    my_str=my_str+" ERROR"
                elif level == Message.FATAL:
                    my_str=my_str+" FATAL"
                my_str=my_str+" ("+date_str+"): "+text
                if not preserve_formatting:
                    my_str = self.format_string(my_str)
                self.output_stream.write(my_str)
                self.output_stream.flush()
            if level >= self.exception_level:
                raise EggError(text)
            if level == Message.FATAL:
                sys.exit(-1)

message = Message() # create instance of Message class for everything to use
    
class EggError(Exception):
    """A Vision Egg specific error"""
    def __init__(self,str):
        Exception.__init__(self,str)

gl_assumptions = []

def add_gl_assumption(gl_variable,required_value,failure_callback):
    """Save assumptions for later checking once OpenGL context created."""
    if type(failure_callback) != types.FunctionType:
        raise ValueError("failure_callback must be a function!")
    gl_assumptions.append((gl_variable,required_value,failure_callback))

def check_gl_assumptions():
    """Called by Screen instance. Requires OpenGL context to be created."""
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
