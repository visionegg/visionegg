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

import sys,types,string, math                   # standard Python modules
import VisionEgg                                # Vision Egg base module (__init__.py)
import PlatformDependent                        # platform dependent Vision Egg C code

import pygame                                   # pygame handles OpenGL window setup
import pygame.locals
import pygame.display
swap_buffers = pygame.display.flip              # make shortcut name

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
        
        flags = pygame.locals.OPENGL | pygame.locals.DOUBLEBUF
        if self.constant_parameters.fullscreen:
            flags = flags | pygame.locals.FULLSCREEN

        # Choose an appropriate framebuffer pixel representation
        try_bpps = [32,24,0] # bits per pixel (32 = 8 bits red, 8 green, 8 blue, 8 alpha, 0 = any)
        try_bpps.insert(0,self.constant_parameters.preferred_bpp) # try the preferred size first

        if sys.platform[:4]=='linux' or sys.platform[:3]=='irix':
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
        if hasattr(pygame.display,"gl_set_attribute"):
            append_str = " (%d %d %d %d RGBA)."%(r,g,b,a)
        message.add("Initializing graphics at %d x %d, %d bpp%s"%(self.size[0],self.size[1],try_bpp,append_str))

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

        # Save the address of these function so they can be called
        # when closing the screen.
        self.cursor_visible_func = pygame.mouse.set_visible

        # Attempt to synchronize buffer swapping with vertical sync again
        if not sync_success:
            if not PlatformDependent.sync_swap_with_vbl_post_gl_init():
                message.add(
                    """Unable to detect or automatically synchronize
                    buffer swapping with vertical retrace. May be
                    possible by manually adjusting video
                    drivers. (Look for "Enable Vertical Sync" or
                    similar.)  If buffer swapping is not synchronized,
                    frame by frame control will not be possible.
                    Because of this, you will probably get a warning
                    about calculated frames per second different than
                    specified.""",
                    level=Message.INFO)

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

    def __del__(self):
        # Make sure mouse is visible after screen closed.
        if hasattr(self,"cursor_visible_func"):
            self.cursor_visible_func(1)
        
def get_default_screen():
    """Return an instance of screen opened with to default values.

    Uses VisionEgg.config.VISIONEGG_GUI_INIT to determine how the
    default screen parameters should are determined.  If this value is
    0, the values from VisionEgg.cfg are used.  If this value is 1, a
    GUI panel is opened and allows manual settings of the screen
    parameters.  """

    global VisionEgg # module is in global namespace, not local
    if not VisionEgg.config.VISIONEGG_GUI_INIT:
        return Screen(size=(VisionEgg.config.VISIONEGG_SCREEN_W,
                                           VisionEgg.config.VISIONEGG_SCREEN_H),
                                     fullscreen=VisionEgg.config.VISIONEGG_FULLSCREEN,
                                     preferred_bpp=VisionEgg.config.VISIONEGG_PREFERRED_BPP)
    else:
        import VisionEgg.GUI # Could import in beginning, but no need if not using GUI
        return VisionEgg.GUI.get_screen_via_GUI()
    
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
                                                types.IntType)}
    
    def __init__(self,**kw):
        apply(VisionEgg.ClassWithParameters.__init__,(self,),kw)

        if self.parameters.handle_event_callbacks is None:
            self.parameters.handle_event_callbacks = []

        self.controllers = []
        self.num_frame_controllers = 0 # reference counter for controllers that are called on frame by frame basis

        # An list that optionally records when frames were drawn by go() method.
        self.frame_draw_times = []

    def add_controller( self, class_with_parameters, parameter_name, controller ):
        """Add a controller"""
        # Check if type checking needed
        if type(class_with_parameters) != types.NoneType and type(parameter_name) != types.NoneType:
            # Check if return type of controller eval is same as parameter type
            if class_with_parameters.is_constant_parameter(parameter_name):
                raise TypeError("Attempt to control constant parameter '%s' of class %s."%(parameter_name,class_with_parameters))
            if controller.returns_type() != class_with_parameters.get_specified_type(parameter_name):
                if not issubclass( controller.returns_type(), class_with_parameters.get_specified_type(parameter_name) ):
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
        if controller.temporal_variable_type == Controller.FRAMES_SINCE_GO:
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
                    if orig_controller.temporal_variable_type == Controller.FRAMES_SINCE_GO:
                        self.num_frame_controllers = self.num_frame_controllers - 1
                else:
                    i = i + 1
        else: # controller is specified
            # Delete only that specific controller
            while i < len(self.controllers):
                orig_parameters,orig_parameter_name,orig_controller = self.controllers[i]
                if orig_parameters == class_with_parameters.parameters and orig_parameter_name == parameter_name and orig_controller == controller:
                    del controller_list[i]
                    if orig_controller.temporal_variable_type == Controller.FRAMES_SINCE_GO:
                        self.num_frame_controllers = self.num_frame_controllers - 1
                else:
                    i = i + 1

    def __call_controllers(self,
                         time_sec_absolute=None,
                         time_sec_since_go=None,
                         frames_since_go=None,
                         go_started=None,
                         doing_transition=None):
        switch_to_transitional = [] # list of contollers
        for (parameters_instance, parameter_name, controller) in self.controllers:
            if doing_transition:
                if controller.eval_frequency == Controller.TRANSITIONS or controller.eval_frequency == Controller.NOW_THEN_TRANSITIONS: # or controller.eval_frequency == Controller.DEPRECATED_TRANSITIONAL:
                    if controller.eval_frequency == Controller.NOW_THEN_TRANSITIONS:
                        # We evaluated it once, switch to TRANSITIONS mode
                        switch_to_transitional.append(controller)
                    if go_started:
                        result = controller.during_go_eval()
                        if parameter_name is not None:
                            setattr(parameters_instance, parameter_name, result)
                    else:
                        result = controller.between_go_eval()
                        if parameter_name is not None:
                            setattr(parameters_instance, parameter_name, result)
            elif controller.eval_frequency == Controller.EVERY_FRAME or controller.eval_frequency == Controller.NOW_THEN_TRANSITIONS:
                if controller.eval_frequency == Controller.NOW_THEN_TRANSITIONS:
                    switch_to_transitional.append(controller)
                if controller.temporal_variable_type == Controller.TIME_SEC_SINCE_GO:
                    controller.temporal_variable = time_sec_since_go
                elif controller.temporal_variable_type == Controller.FRAMES_SINCE_GO:
                    controller.temporal_variable = frames_since_go
                elif controller.temporal_variable_type == Controller.TIME_SEC_ABSOLUTE:
                    controller.temporal_variable = time_sec_absolute
                    
                if go_started:
                    result = controller.during_go_eval()
                    if parameter_name is not None:
                        setattr(parameters_instance, parameter_name, result)
                else:
                    result = controller.between_go_eval()
                    if parameter_name is not None:
                        setattr(parameters_instance, parameter_name, result)
        for controller in switch_to_transitional:
            controller.eval_frequency = Controller.TRANSITIONS
        
    def go(self,collect_timing_info=0):
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

        Optional arguments:

        collect_timing_info -- Int (boolean) to control whether frame draw times recorded and statistics displayed
        """
        # Create shorthand notation, which speeds the main loop
        # slightly by not performing name lookup each time.
        p = self.parameters

        # Clear any previous timing info if necessary
        if collect_timing_info:
            self.frame_draw_times = []

        while (not p.trigger_armed) or (not p.trigger_go_if_armed):
            self.between_presentations()

        # Go!
            
        # Tell transitional controllers a presentation is starting
        self.__call_controllers(
            time_sec_absolute=VisionEgg.timing_func(),
            go_started=1,
            doing_transition=1)

        # Do the main loop
        start_time_absolute = VisionEgg.timing_func()
        current_time_absolute = start_time_absolute
        current_time = 0.0
        current_frame = 0
        if p.go_duration[0] == 'forever': # forever
            current_duration_value = 0
        elif p.go_duration[1] == 'seconds': # duration units
            current_duration_value = current_time
        elif p.go_duration[1] == 'frames': # duration units
            current_duration_value = current_frame
        else:
            raise RuntimeError("Unknown duration unit '%s'"%p.go_duration[1])
        while (current_duration_value < p.go_duration[0]):
            # Update all the realtime parameters
            self.__call_controllers(
                time_sec_absolute=current_time_absolute,
                time_sec_since_go=current_time,
                frames_since_go=current_frame,
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
                self.frame_draw_times.append(current_time)
                
            # Get the time for the next frame
            current_time_absolute = VisionEgg.timing_func()
            current_time = current_time_absolute-start_time_absolute
            current_frame = current_frame + 1
            
            # Make sure we use the right value to check if we're done
            if p.go_duration[0] == 'forever': # forever
                pass # current_duration_value already set to 0
            elif p.go_duration[1] == 'seconds':
                current_duration_value = current_time
            elif p.go_duration[1] == 'frames':
                current_duration_value = current_frame
            else:
                raise RuntimeError("Unknown duration unit '%s'"%p.go_duration[1])
            if p.check_events:
                for event in pygame.event.get():
                    for event_type, event_callback in p.handle_event_callbacks:
                        if event.type is event_type:
                            event_callback(event)
            
        # Tell transitional controllers a presentation has ended
        self.__call_controllers(
            time_sec_absolute=VisionEgg.timing_func(),
            go_started=0,
            doing_transition=1)
        
        # Check to see if frame by frame control was desired
        # but OpenGL not syncing to vertical retrace
        calculated_fps = current_frame / current_time
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
                
        # Warn if > 10% error in frame rate
        if abs(calculated_fps-VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ) / float(VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ) > 0.05:
            # Should also add VisionEgg.config.FRAME_LOCKED_MODE variable
            # and only print this warning if that variable is true
            message.add(
                """Calculated frames per second was %s, while
                VisionEgg.config specified %s."""%(calculated_fps,VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ),
                level=Message.WARNING
                )
                
        if collect_timing_info:
            self.__print_frame_timing_stats()

    def export_movie_go(self, frames_per_sec=12.0, filename_suffix=".tif", filename_base="visionegg_movie", path="."):
        """Emulates method 'go' but saves a movie."""
        import Image # Could import this at the beginning of the file, but it breaks sometimes!
        import os # Could also import this, but this is the only place its needed
        
        # Create shorthand notation, which speeds the main loop
        # slightly by not performing name lookup each time.
        p = self.parameters

        current_time = 0.0
        current_time_absolute = current_time
        current_frame = 0

        real_timing_func = VisionEgg.timing_func
        def fake_timing_func():
            return current_time_absolute
        VisionEgg.timing_func = fake_timing_func
        
        # Tell transitional controllers a presentation is starting
        self.__call_controllers(
            time_sec_absolute=0.0,
            go_started=1,
            doing_transition=1)

        # Do the main loop
        image_no = 1
        if p.go_duration[0] == 'forever': # forever
            current_duration_value = 0
        elif p.go_duration[1] == 'seconds': # duration units
            current_duration_value = current_time
        elif p.go_duration[1] == 'frames': # duration units
            current_duration_value = current_frame
        else:
            raise RuntimeError("Unknown duration unit '%s'"%p.go_duration[1])
        while (current_duration_value < p.go_duration[0]):
            # Update all the realtime parameters
            self.__call_controllers(
                time_sec_absolute=current_time,
                time_sec_since_go=current_time,
                frames_since_go=current_frame,
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
            current_time = current_time + 1.0/frames_per_sec
            current_time_absolute = current_time
            current_frame = current_frame + 1
            if p.go_duration[0] == 'forever':
                current_duration_value = 0
            elif p.go_duration[1] == 'seconds':
                current_duration_value = current_time
            elif p.go_duration[1] == 'frames':
                current_duration_value = current_frame
            else:
                raise RuntimeError("Unknown duration unit '%s'"%p.go_duration[1])

            if p.check_events:
                for event in pygame.event.get():
                    for event_type, event_callback in p.handle_event_callbacks:
                        if event.type is event_type:
                            event_callback(event)

        # Tell transitional controllers a presentation has ended
        self.__call_controllers(
            time_sec_absolute=current_time,
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
                    
        VisionEgg.timing_func = real_timing_func

    def run_forever(self):
        while 1:
            self.between_presentations()
            if self.parameters.enter_go_loop:
                self.parameters.enter_go_loop = 0
                self.go()

    def between_presentations(self):
        """Maintain display while between stimulus presentations.

        This function gets called as often as possible when not
        in the 'go' loop.

        Other than the difference in the time variable passed to the
        controllers, this routine is very similar to the inside of the
        main loop in the go method.
        """
        self.__call_controllers(
            time_sec_absolute=VisionEgg.timing_func(),
            time_sec_since_go=None,
            frames_since_go=None,
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
        
    def __print_frame_timing_stats(self):
        """Print a histogram of the last recorded frame drawing times.

        If argument 
        """
        if len(self.frame_draw_times) > 1:
            frame_draw_times = Numeric.array(self.frame_draw_times)
            self.frame_draw_times = [] # clear the list
            frame_draw_times = frame_draw_times[1:] - frame_draw_times[:-1] # get inter-frame interval
            timing_string = str((len(frame_draw_times)+1))+" frames drawn.\n"
            mean_sec = MLab.mean(frame_draw_times)
            timing_string = timing_string + "mean frame to frame time: %.1f (usec) == mean fps: %.2f, max: %.1f\n"%(mean_sec*1.0e6,1.0/mean_sec,max(frame_draw_times)*1.0e6)
            bins = Numeric.arange(0.0,15.0,1.0) # msec
            bins = bins*1.0e-3 # sec
            timing_string = timing_string + "Inter-frame interval\n"
            timing_string = self.__print_hist(frame_draw_times,bins,timing_string)
            timing_string = timing_string + "\n"
            message.add(timing_string,level=Message.INFO)

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
            timing_string = timing_string + "%6d "%(round(maxhist*val/10.0),)
            q = Numeric.greater(hist,val)
            for qi in q:
                s = ' '
                if qi:
                    s = '*'
                timing_string = timing_string + "%3s "%(s,)
            timing_string = timing_string + "\n"
        timing_string = timing_string + " Time: "
        for bin in bins:
            timing_string = timing_string + "%3d "%(int(bin*1.0e3),)
        timing_string = timing_string + "+(msec)\n"
        timing_string = timing_string + "Total: "
        for hi in h:
            timing_string = timing_string + "%3d "%(hi,)
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
    
    Possible values for eval_frequency:
    
    Controller.EVERY_FRAME
    Controller.TRANSITIONS
    Controller.NOW_THEN_TRANSITIONS

    Possible values for temporal_variable_type:

    Controller.TIME_SEC_ABSOLUTE
    Controller.TIME_SEC_SINCE_GO
    Controller.FRAMES_SINCE_GO

    Methods:
    
    returns_type -- Get the return type of this controller
    during_go_eval -- Evaluate controller during the main 'go' loop.
    between_go_eval -- Evaluate controller between runs of the main 'go' loop.
    
    """
    # Possible temporal variable types:
    TIME_SEC_ABSOLUTE = 1
    TIME_SEC_SINCE_GO = 2
    FRAMES_SINCE_GO = 3

    # Possible eval frequency:
    EVERY_FRAME = 1
    TRANSITIONS = 2
    NOW_THEN_TRANSITIONS = 3 # evaluate as soon as possible, then switch to TRANSITIONS
    
    def __init__(self,
                 return_type = None,
                 temporal_variable_type = TIME_SEC_SINCE_GO,
                 eval_frequency = EVERY_FRAME):
        """Arguments:

        eval_frequency -- Int (pseudo-enum)
        temporal_variable_type -- Int (pseudo-enum)
        return_type -- Set to the type of the parameter under control
        
        """
        if return_type is None:
            raise ValueError("Must set argument 'return_type' in Controller.")
        if type(return_type) not in [types.TypeType,types.ClassType]:
            raise TypeError("argument 'return_type' must specify a type or class.")
        self.return_type = return_type
        
        self.temporal_variable = None
        self.temporal_variable_type = temporal_variable_type
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
    
class ConstantController(Controller):
    """Set parameters to a constant value."""
    def __init__(self,
                 during_go_value = None,
                 between_go_value = None,
                 **kw
                 ):
        if 'return_type' not in kw.keys():
            kw['return_type'] = type(during_go_value)
        apply(Controller.__init__,(self,),kw)
        if self.return_type is not types.NoneType and during_go_value is None:
            raise ValueError("Must specify during_go_value")
        if between_go_value is None:
            between_go_value = during_go_value
        if type(during_go_value) is not self.return_type:
            raise TypeError("going_value must be of type %s"%return_type)
        if type(between_go_value) is not self.return_type:
            raise TypeError("between_go_value must be of type %s"%return_type)
        self.during_go_value = during_go_value
        self.between_go_value = between_go_value
        
    def during_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        return self.during_go_value

    def between_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        return self.between_go_value

class EvalStringController(Controller):
    """Set parameters using dynamically interpreted Python string."""
    def __init__(self,
                 during_go_eval_string = None,
                 between_go_eval_string = None,
                 **kw
                 ):
        # Create a namespace for eval_strings to use
        self.eval_globals = {}

        if during_go_eval_string is None:
            raise ValueError("'during_go_eval_string' is a required argument")
        if between_go_eval_string is None:
            between_go_eval_string = during_go_eval_string
        
        # Make Numeric and math modules available
        self.eval_globals['Numeric'] = Numeric
        self.eval_globals['math'] = math
        # Make Numeric and math modules available without module name
        for key in dir(Numeric):
            self.eval_globals[key] = getattr(Numeric,key)
        for key in dir(math):
            self.eval_globals[key] = getattr(math,key)

        # Check to make sure return_type is set
        if 'return_type' not in kw.keys():
            message.add('Evaluating "%s" to test for return type.'%(during_go_eval_string,),
                        Message.TRIVIAL)
            temporal_variable_name = 't' # temporal_variable_type defaults to TIME_SEC_SINCE_GO
            initial_value = 0.0
            if 'temporal_variable_type' in kw.keys():
                if kw['temporal_variable_type'] == Controller.TIME_SEC_ABSOLUTE:
                    temporal_variable_name = 't_abs'
                    initial_value = VisionEgg.timing_func()
                elif kw['temporal_variable_type'] == Controller.TIME_SEC_SINCE_GO:
                    pass # don't change the default
                elif kw['temporal_variable_type'] == Controller.FRAMES_SINCE_GO:
                    temporal_variable_name = 'f'
                    initial_value = 0
                else:
                    raise ValueError("Unknown value for temporal_variable_type")
            eval_locals = {temporal_variable_name:initial_value}
            test_result = eval(during_go_eval_string,self.eval_globals,eval_locals)
            kw['return_type'] = type(test_result)

        # Call base class __init__ and copy eval_strings
        apply(Controller.__init__,(self,),kw)

        if self.temporal_variable_type == Controller.TIME_SEC_ABSOLUTE:
            self.temporal_variable_name = 't_abs'
        elif self.temporal_variable_type == Controller.TIME_SEC_SINCE_GO:
            self.temporal_variable_name = 't'
        elif self.temporal_variable_type == Controller.FRAMES_SINCE_GO:
            self.temporal_variable_name = 'f'

        self.during_go_eval_code = compile(during_go_eval_string,'<string>','eval')
        self.between_go_eval_code = compile(between_go_eval_string,'<string>','eval')

    def during_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        eval_locals = {self.temporal_variable_name:self.temporal_variable}
        return eval(self.during_go_eval_code,self.eval_globals,eval_locals)

    def between_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        eval_locals = {self.temporal_variable_name:self.temporal_variable}
        return eval(self.between_go_eval_code,self.eval_globals,eval_locals)
    
class ExecStringController(Controller):
    """Set parameters using potentially complex Python string."""
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
        if between_go_exec_string is None:
            between_go_exec_string = during_go_exec_string

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

        # Check to make sure return_type is set
        if 'return_type' not in kw.keys():
            message.add('Executing "%s" to test for return type.'%(during_go_exec_string,),
                        Message.TRIVIAL)
            temporal_variable_name = 't' # temporal_variable_type defaults to TIME_SEC_SINCE_GO
            initial_value = 0.0
            if 'temporal_variable_type' in kw.keys():
                if kw['temporal_variable_type'] == Controller.TIME_SEC_ABSOLUTE:
                    temporal_variable_name = 't_abs'
                    initial_value = VisionEgg.timing_func()
                elif kw['temporal_variable_type'] == Controller.TIME_SEC_SINCE_GO:
                    pass # don't change the default
                elif kw['temporal_variable_type'] == Controller.FRAMES_SINCE_GO:
                    temporal_variable_name = 'f'
                    initial_value = 0
                else:
                    raise ValueError("Unknown value for temporal_variable_type")
            if self.restricted_namespace:
                eval_locals = {temporal_variable_name:initial_value}
                exec during_go_exec_string in self.eval_globals,eval_locals
                test_result = eval_locals['x']
            else:
                exec temporal_variable_name + "=" + repr(initial_value)
                exec during_go_exec_string
                test_result = x
            kw['return_type'] = type(test_result)
        
        # Call base class __init__ and copy eval_strings
        apply(Controller.__init__,(self,),kw)

        if self.temporal_variable_type == Controller.TIME_SEC_ABSOLUTE:
            self.temporal_variable_name = 't_abs'
        elif self.temporal_variable_type == Controller.TIME_SEC_SINCE_GO:
            self.temporal_variable_name = 't'
        elif self.temporal_variable_type == Controller.FRAMES_SINCE_GO:
            self.temporal_variable_name = 'f'

        self.during_go_exec_code = compile(during_go_exec_string,'<string>','exec')
        self.between_go_exec_code = compile(between_go_exec_string,'<string>','exec')

    def during_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        if self.restricted_namespace:
            eval_locals = {self.temporal_variable_name:self.temporal_variable}
            exec self.during_go_exec_code in self.eval_globals,eval_locals        
            return eval_locals['x']
        else:
            exec self.temporal_variable_name + "=" + repr(self.temporal_variable)
            exec self.during_go_exec_code
            return x

    def between_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        if self.restricted_namespace:
            eval_locals = {self.temporal_variable_name:self.temporal_variable}
            exec self.between_go_exec_code in self.eval_globals,eval_locals
            return eval_locals['x']
        else:
            exec self.temporal_variable_name + "=" + repr(self.temporal_variable)
            exec self.between_go_exec_code
            return x
    
class FunctionController(Controller):
    """Set parameters using a Python function."""
    def __init__(self,
                 during_go_func = None,
                 between_go_func = None,
                 **kw
                 ):
        if during_go_func is None:
            raise ValueError("Must specify during_go_func")
        if between_go_func is None:
            between_go_func = during_go_func
        if 'return_type' not in kw.keys():
            try:
                # try a float for temporal variable
                # emulate modes TIME_SEC_ABSOLUTE and TIME_SEC_SINCE_GO
                kw['return_type'] = type(during_go_func(0.0))
            except:
                try:
                    # try an int for temporal variable
                    # emulate mode FRAMES_SINCE_GO
                    kw['return_type'] = type(during_go_func(0))
                except:
                    raise
        apply(Controller.__init__,(self,),kw)
        self.during_go_func = during_go_func
        self.between_go_func = between_go_func
        
    def during_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        return self.during_go_func(self.temporal_variable)

    def between_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        return self.between_go_func(self.temporal_variable)

####################################################################
#
#        Error handling and assumption checking
#
####################################################################

class Message:
    """Handles message/warning/error printing, exception raising."""

    # Levels are:
    TRIVIAL = 0
    INFO = 1
    NAG = 2
    DEPRECATION = 3
    WARNING = 4
    ERROR = 5
    FATAL = 6
    
    def __init__(self,
                 prefix="VisionEgg",
                 exception_level=ERROR,
                 print_level=INFO,
                 output_stream=sys.stderr):
        self.prefix = prefix
        self.message_queue = []
        self.exception_level = exception_level
        self.print_level = print_level
        self.output_stream = output_stream
        
    def add(self,text,level=INFO):
        self.message_queue.append((level,text))
        self.handle()

    def handle(self):
        while len(self.message_queue) > 0:
            level, text = self.message_queue.pop(0)
            if level >= self.print_level:
                self.output_stream.write(self.prefix)
                if level == Message.TRIVIAL:
                    self.output_stream.write(" trivial")
                elif level == Message.INFO:
                    self.output_stream.write(" info")
                elif level == Message.NAG:
                    self.output_stream.write(" nag")
                elif level == Message.DEPRECATION:
                    self.output_stream.write(" deprecation")
                elif level == Message.WARNING:
                    self.output_stream.write(" WARNING")
                elif level == Message.ERROR:
                    self.output_stream.write(" ERROR")
                elif level == Message.FATAL:
                    self.output_stream.write(" FATAL")
                self.output_stream.write(" message: "+text+"\n")
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