"""VisionEgg Core Library
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
    
    constant_parameters_and_defaults = {'size':((VisionEgg.config.VISIONEGG_SCREEN_W,
                                                 VisionEgg.config.VISIONEGG_SCREEN_H),
                                                types.TupleType),
                                        'fullscreen':(VisionEgg.config.VISIONEGG_FULLSCREEN,
                                                      types.IntType),
                                        'preferred_bpp':(VisionEgg.config.VISIONEGG_PREFERRED_BPP,
                                                         types.IntType),
                                        'maxpriority':(VisionEgg.config.VISIONEGG_MAXPRIORITY,
                                                       types.IntType)}

    parameters_and_defaults = {'bgcolor':(VisionEgg.config.VISIONEGG_SCREEN_BGCOLOR,
                                          types.TupleType),
                               'gamma_ramps':(None,
                                              Numeric.ArrayType)}
    
    def __init__(self,**kw):
        
        apply(VisionEgg.ClassWithParameters.__init__,(self,),kw)

        if self.parameters.gamma_ramps != None:
            raise NotImplementedError()
        
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
            message.add(
                """Could not request alpha in framebuffer because you
                need pygame release 1.4.9 or greater. This is only of
                concern if you use a stimulus that needs this
                feature. In that case, the stimulus should verify the
                presence of alpha.""",level=Message.NAG)
            
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

        message.add("Initializing graphics at %d x %d ( %d bpp )."%(self.constant_parameters.size[0],self.constant_parameters.size[1],try_bpp))

        try:
            pygame.display.set_mode(self.constant_parameters.size, flags, try_bpp )
        except pygame.error, x:
            message.add("Failed execution of pygame.display.set_mode():%s"%x,
                        level=Message.FATAL)

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

        self.size = self.constant_parameters.size # deprecated to use this, but for backwards compatibility

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
        # Make sure mouse is visible after screen closed.
        self.cursor_visible_func(1)
        
####################################################################
#
#        Projection and derived classes
#
####################################################################

class Projection(VisionEgg.ClassWithParameters):
    """Abstract base class to define interface for OpenGL projection matrices"""
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
        return OrthographicProjection(left=0,right=self.parameters.size[0],
                                      bottom=0,top=self.parameters.size[1],
                                      z_clip_near=0.0,
                                      z_clip_far=1.0)

    __add_stimulus_warning_sent = 0
    def add_stimulus(self,stimulus,draw_order=-1):
        """Add a stimulus to the list of those drawn in the viewport

        By default, the stimulus is drawn last, but this behavior
        can be changed with the draw_order argument.
        """
        if not self.__add_stimulus_warning_sent:
            message.add("Viewport.add_stumulus() called.",Message.DEPRECATION)
            __add_stimulus_warning_sent = 1
        if draw_order == -1:
            self.parameters.stimuli.append(stimulus)
        else:
            self.parameters.stimuli.insert(draw_order,stimulus)

    def remove_stimulus(self,stimulus):
        self.parameters.stimuli.remove(stimulus)

    def draw(self):
        """Set the viewport and draw stimuli."""
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
    parameters_and_defaults = {'on':(1,
                                     types.IntType),
                               'color':((1.0,1.0,1.0,1.0),
                                        types.TupleType),
                               'center':((320.0,240.0), # center if in 640x480 viewport
                                         types.TupleType),
                               'size':((4.0,4.0), # horiz and vertical size
                                       types.TupleType)} 
    
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
    parameters_and_defaults = {'viewports' : ([],
                                              types.ListType),
                               'duration' : ((5.0,'seconds'),
                                             types.TupleType),
                               'check_events' : (0, # May cause performance hit
                                                 types.IntType),
                               'handle_event_callbacks' : (None,
                                                           types.ListType),
                               'trigger_armed':(1, # boolean
                                                types.IntType),
                               'trigger_go_if_armed':(1, #boolean
                                                      types.IntType)}
    
    def __init__(self,**kw):
        apply(VisionEgg.ClassWithParameters.__init__,(self,),kw)

        self.controllers = []
        self.num_frame_controllers = 0 # reference counter for controllers that are called on frame by frame basis

        # An list that optionally records when frames were drawn by go() method.
        self.frame_draw_times = []

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

    def add_controller( self, class_with_parameters, parameter_name, controller ):
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

    def call_controllers(self,
                         time_sec_absolute=None,
                         time_sec_since_go=None,
                         frames_since_go=None,
                         go_started=None,
                         doing_transition=None):
        for (parameters_instance, parameter_name, controller) in self.controllers:
            if doing_transition:
                if controller.eval_frequency == Controller.TRANSITIONS: # or controller.eval_frequency == Controller.DEPRECATED_TRANSITIONAL:
                    if go_started:
                        result = controller.during_go_eval()
                        if parameter_name is not None:
                            setattr(parameters_instance, parameter_name, result)
                    else:
                        result = controller.between_go_eval()
                        if parameter_name is not None:
                            setattr(parameters_instance, parameter_name, result)
            elif controller.eval_frequency == Controller.EVERY_FRAME or controller.eval_frequency == Controller.DEPRECATED_TRANSITIONAL:
                if controller.temporal_variable_type == Controller.TIME_SEC_SINCE_GO:
                    controller.temporal_variable = time_sec_since_go
                elif controller.temporal_variable_type == Controller.FRAMES_SINCE_GO:
                    controller.temporal_variable = frames_since_go
                elif controller.temporal_variable_type == Controller.TIME_SEC_ABSOLUTE:
                    controller.temporal_variable = time_sec_absolute
                    
                if go_started:
                    if parameter_name is None:
                        controller.during_go_eval()
                    else:
                        # XXX This if statementis a hack that slows stuff down just
                        # to support deprecated DEPRECATED_TRANSITIONAL eval_frequency
                        if ((not controller.eval_frequency == Controller.DEPRECATED_TRANSITIONAL) or time_sec_since_go==0.0):
                            setattr(parameters_instance, parameter_name, controller.during_go_eval())
                else:
                    result = controller.between_go_eval()
                    if parameter_name is not None:
                        setattr(parameters_instance, parameter_name, result)

    # The next functions (those with "realtime" and "transitional" in
    # their names) are deprecated, so there's a deprecation warning.
    
    __DEPRECATION_WARNING_SENT = 0
    def add_realtime_time_controller(self, class_with_parameters, parameter_name, controller_function):
        """DEPRECATED"""
        if not Presentation.__DEPRECATION_WARNING_SENT:
            message.add(
                """Presentation method add_realtime_time_controller()
                and possibly other deprecated Presentation class
                methods called.  These methods will be removed from
                future releases.  They also create instances of
                DeprecatedCompatibilityController class, which is also
                deprecated.""",
                level=Message.DEPRECATION)
            Presentation.__DEPRECATION_WARNING_SENT = 1
        cc = DeprecatedCompatibilityController(eval_func=controller_function,
                                     temporal_variable_type=Controller.TIME_SEC_SINCE_GO)
        self.add_controller(class_with_parameters,parameter_name,cc)
    def remove_realtime_time_controller(self, class_with_parameters, parameter_name, controller_function):
        """DEPRECATED"""
        i=0
        while i < len(self.controllers):
            orig_parameters,orig_parameter_name,orig_controller = self.controllers[i]
            if isinstance(orig_controller, DeprecatedCompatibilityController) and orig_parameters==class_with_parameters.parameters and orig_parameter_name==parameter_name and orig_controller.eval_func == controller_function:
                self.remove_controller(class_with_parameters,parameter_name,orig_controller)
                break
            i = i + 1
    def add_realtime_frame_controller(self, class_with_parameters, parameter_name, controller_function):
        """DEPRECATED"""
        if not Presentation.__DEPRECATION_WARNING_SENT:
            message.add(
                """Presentation method add_realtime_frame_controller()
                and possibly other deprecated Presentation class
                methods called.  These methods will be removed from
                future releases.  They also create instances of
                DeprecatedCompatibilityController class, which is also
                deprecated.""",
                level=Message.DEPRECATION)
            Presentation.__DEPRECATION_WARNING_SENT = 1
        cc = DeprecatedCompatibilityController(eval_func=controller_function,
                                     temporal_variable_type=Controller.FRAMES_SINCE_GO)
        self.add_controller(class_with_parameters,parameter_name,cc)
    def remove_realtime_frame_controller(self, class_with_parameters, parameter_name, controller_function):
        """DEPRECATED"""
        i=0
        while i < len(self.controllers):
            orig_parameters,orig_parameter_name,orig_controller = self.controllers[i]
            if isinstance(orig_controller, DeprecatedCompatibilityController) and orig_parameters==class_with_parameters.parameters and orig_parameter_name==parameter_name and orig_controller.eval_func == controller_function:
                self.remove_controller(class_with_parameters,parameter_name,orig_controller)
                break
            i = i + 1
    def add_transitional_controller(self, class_with_parameters, parameter_name, controller_function):
        """DEPRECATED"""
        if not Presentation.__DEPRECATION_WARNING_SENT:
            message.add(
                """Presentation method add_transitional_controller()
                and possibly other deprecated Presentation class
                methods called.  These methods will be removed from
                future releases.  They also create instances of
                DeprecatedCompatibilityController class, which is also
                deprecated.""",
                level=Message.DEPRECATION)
            Presentation.__DEPRECATION_WARNING_SENT = 1
        cc = DeprecatedCompatibilityController(eval_func=controller_function,
                                     temporal_variable_type=Controller.TIME_SEC_SINCE_GO,
                                     eval_frequency=Controller.DEPRECATED_TRANSITIONAL)
        self.add_controller(class_with_parameters,parameter_name,cc)
    def remove_transitional_controller(self, class_with_parameters, parameter_name, controller_function):
        """DEPRECATED"""
        i=0
        while i < len(self.controllers):
            orig_parameters,orig_parameter_name,orig_controller = self.controllers[i]
            if isinstance(orig_controller, DeprecatedCompatibilityController) and orig_parameters==class_with_parameters.parameters and orig_parameter_name==parameter_name and orig_controller.eval_func == controller_function:
                self.remove_controller(class_with_parameters,parameter_name,orig_controller)
                break
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
        self.call_controllers(
            time_sec_absolute=VisionEgg.timing_func(),
            go_started=1,
            doing_transition=1)

        # Do the main loop
        start_time_absolute = VisionEgg.timing_func()
        current_time_absolute = start_time_absolute
        current_time = 0.0
        current_frame = 0
        if p.duration[1] == 'seconds': # duration units
            current_duration_value = current_time
        elif p.duration[1] == 'frames': # duration units
            current_duration_value = current_frame
        else:
            raise RuntimeError("Unknown duration unit '%s'"%p.duration[1])
        while (current_duration_value < p.duration[0]):
            # Update all the realtime parameters
            self.call_controllers(
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
            if p.duration[1] == 'seconds':
                current_duration_value = current_time
            elif p.duration[1] == 'frames':
                current_duration_value = current_frame
            else:
                raise RuntimeError("Unknown duration unit '%s'"%p.duration[1])
            if p.check_events:
                for event in pygame.event.get():
                    for event_type, event_callback in p.handle_event_callbacks:
                        if event.type is event_type:
                            event_callback()
            
        # Tell transitional controllers a presentation has ended
        self.call_controllers(
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

        if abs( calculated_fps / float(VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ) ) > 0.1:
            # Should also add VisionEgg.config.FRAME_LOCKED_MODE variable
            # and only print this warning if that variable is true
            message.add(
                """Calculated frames per second was %s, while
                VisionEgg.config specified %s."""%(calculated_fps,VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ),
                level=Message.WARNING
                )
                
        if collect_timing_info:
            self.print_frame_timing_stats()

    def between_presentations(self):
        """Maintain display while between stimulus presentations.

        This function gets called as often as possible when not
        in the 'go' loop.

        Other than the difference in the time variable passed to the
        controllers, this routine is very similar to the inside of the
        main loop in the go method.
        """
        self.call_controllers(
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
        # Draw each viewport
        for viewport in viewports:
            viewport.draw()
        swap_buffers()

    def export_movie_go(self, frames_per_sec=12.0, filename_suffix=".tif", filename_base="visionegg_movie", path="."):
        """Call this method rather than go() to save a movie of your experiment.
        """
        raise NotImplementedError("This function is broken until updated!")
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
            s = viewport.parameters.screen
            if s not in screens:
                screens.append(s)

        if len(screens) > 1:
            raise EggError("Can only export movie of one screen")

        current_time = 0.0
        current_frame = 0
        image_no = 1
        if p.duration[1] == 'seconds':
            current_duration_value = current_time
        elif p.duration[1] == 'frames':
            current_duration_value = current_frame
        else:
            raise RuntimeError("Unknown duration unit '%s'"%p.duration[1])
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
            current_frame = current_frame + 1
            if p.duration[1] == 'seconds':
                current_duration_value = current_time
            elif p.duration[1] == 'frames':
                current_duration_value = current_frame
            else:
                raise RuntimeError("Unknown duration unit '%s'"%p.duration[1])

    def print_frame_timing_stats(self):
        """Print a histogram of the last recorded frame drawing times.
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
            timing_string = self.print_hist(frame_draw_times,bins,timing_string)
            timing_string = timing_string + "\n"
            message.add(timing_string,level=Message.INFO)

    def histogram(self,a, bins):  
        """Create a histogram from data

        This function is taken straight from NumDoc.pdf, the Numeric Python
        documentation."""
        n = Numeric.searchsorted(Numeric.sort(a),bins)
        n = Numeric.concatenate([n, [len(a)]])
        return n[1:]-n[:-1]
        
    def print_hist(self,a, bins, timing_string):
        """Print a pretty histogram"""
        hist = self.histogram(a,bins)
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
    """Abstract base class that defines interface to any controller."""
    # Possible temporal variable types:
    TIME_SEC_ABSOLUTE = 1
    TIME_SEC_SINCE_GO = 2
    FRAMES_SINCE_GO = 3

    # Possible eval frequency:
    EVERY_FRAME = 1
    TRANSITIONS = 2
    DEPRECATED_TRANSITIONAL = 3 # only for deprecated behavior, don't use!
    
    def __init__(self,
                 return_type = None,
                 temporal_variable_type = TIME_SEC_SINCE_GO,
                 eval_frequency = EVERY_FRAME):
        if return_type is None:
            raise ValueError("Must set argument 'return_type' in Controller.")
        if type(return_type) not in [types.TypeType,types.ClassType]:
            raise TypeError("argument 'return_type' must specify a type or class.")
        self.return_type = return_type
        
        self.temporal_variable = None
        self.temporal_variable_type = temporal_variable_type
        self.eval_frequency = eval_frequency

    def returns_type(self):
        return self.return_type
    
    def during_go_eval(self):
        raise NotImplementedError("Definition in abstract base class Contoller must be overriden.")

    def between_go_eval(self):
        raise NotImplementedError("Definition in abstract base class Controller must be overriden.")
    
class ConstantController(Controller):
    def __init__(self,
                 during_go_value = None,
                 between_go_value = None,
                 **kw
                 ):
        if during_go_value is None:
            raise ValueError("Must specify during_go_value")
        if between_go_value is None:
            between_go_value = during_go_value
        if 'return_type' not in kw.keys():
            kw['return_type'] = type(during_go_value)
        apply(Controller.__init__,(self,),kw)
        if type(during_go_value) is not self.return_type:
            raise TypeError("going_value must be of type %s"%return_type)
        if type(between_go_value) is not self.return_type:
            raise TypeError("between_go_value must be of type %s"%return_type)
        self.during_go_value = during_go_value
        self.between_go_value = between_go_value
        
    def during_go_eval(self):
        return self.during_go_value

    def between_go_eval(self):
        return self.between_go_value

class EvalStringController(Controller):
    def __init__(self,
                 during_go_eval_string = "",
                 between_go_eval_string = "",
                 **kw
                 ):
        # Create a namespace for eval_strings to use
        self.eval_globals = {}
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
            # XXX Todo - make 't' dependent on temporal variable type and other stuff?
            eval_locals = {'t':0.0}
            test_result = eval(during_go_eval_string,self.eval_globals,eval_locals)
            kw['return_type'] = type(test_result)

        # Call base class __init__ and copy eval_strings
        apply(Controller.__init__,(self,),kw)
        self.during_go_eval_string = during_go_eval_string
        self.between_go_eval_string = between_go_eval_string

    def during_go_eval(self):
        eval_locals = {'t':self.temporal_variable}
        return eval(self.during_go_eval_string,self.eval_globals,eval_locals)

    def between_go_eval(self):
        eval_locals = {'t':self.temporal_variable}
        return eval(self.between_go_eval_string,self.eval_globals,eval_locals)

class DeprecatedCompatibilityController(Controller):
    """DEPRECATED. Allows emulation of purely function-based controllers."""
    def __init__(self,
                 eval_func = lambda t: t,
                 **kw
                 ):

        if type(eval_func) not in [types.FunctionType,types.MethodType]:
            raise TypeError("Must pass function to DeprecatedCompatibilityController.")

        if 'eval_frequency' not in kw.keys():
            kw['eval_frequency'] = Controller.EVERY_FRAME

        test_result = eval_func(-1)
        result_type = type(test_result)
        if result_type == types.InstanceType:
            my_type = test_result.__class__
        else:
            my_type = result_type
        
        if 'return_type' in kw.keys():
            if kw['return_type'] != my_type:
                raise ValueError("return_type for DeprecatedCompatibilityController must be type(eval_func(-1))")
        else:
            kw['return_type'] = my_type

        apply(Controller.__init__,(self,),kw)
        self.eval_func = eval_func
            
    def during_go_eval(self):
        return self.eval_func(self.temporal_variable)

    def between_go_eval(self):
        return self.eval_func(-1)

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
