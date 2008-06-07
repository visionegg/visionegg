# The Vision Egg: FlowControl
#
# Copyright (C) 2001-2004 Andrew Straw.
# Copyright (C) 2008 California Institute of Technology
#
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""
Flow control for the Vision Egg.

"""

import logging
import logging.handlers

import VisionEgg
import VisionEgg.GL as gl # get all OpenGL stuff in one namespace
import VisionEgg.ParameterTypes as ve_types
import numpy.oldnumeric as Numeric, math, types
import pygame

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

    Parameters
    ==========
    check_events                 -- allow input event checking during 'go' loop? (Boolean)
                                    Default: True
    collect_timing_info          -- log timing statistics during go loop? (Boolean)
                                    Default: True
    enter_go_loop                -- test used by run_forever() to enter go loop (Boolean)
                                    Default: False
    go_duration                  -- Tuple to specify 'go' loop duration. Either (value,units) or ('forever',) (Sequence of AnyOf(Real or String))
                                    Default: (5.0, 'seconds')
    handle_event_callbacks       -- List of tuples to handle events. (event_type,event_callback_func) (Sequence of Sequence2 of AnyOf(Integer or Callable))
                                    Default: (determined at runtime)
    override_t_abs_sec           -- Override t_abs. Set only when reconstructing experiments. (units: seconds) (Real)
                                    Default: (determined at runtime)
    quit                         -- quit the run_forever loop? (Boolean)
                                    Default: False
    trigger_armed                -- test trigger on go loop? (Boolean)
                                    Default: True
    trigger_go_if_armed          -- trigger go loop? (Boolean)
                                    Default: True
    viewports                    -- list of Viewport instances to draw. Order is important. (Sequence of Instance of <class 'VisionEgg.ClassWithParameters'>)
                                    Default: (determined at runtime)
    warn_longest_frame_threshold -- threshold to print frame skipped warning (units: factor of inter-frame-interval) (Real)
                                    Default: 2.0
    warn_mean_fps_threshold      -- threshold to print observered vs. expected frame rate warning (fraction units) (Real)
                                    Default: 0.01
    """
    parameters_and_defaults = {
        'viewports' : (None,
                       # XXX should really require VisionEgg.Core.Viewport
                       # but that would lead to circular import problem
                       ve_types.Sequence(ve_types.Instance(VisionEgg.ClassWithParameters)),
                       'list of Viewport instances to draw. Order is important.'),
        'collect_timing_info' : (True,
                                 ve_types.Boolean,
                                 'log timing statistics during go loop?'),
        'go_duration' : ((5.0,'seconds'),
                         ve_types.Sequence(ve_types.AnyOf(ve_types.Real,
                                                          ve_types.String)),
                         "Tuple to specify 'go' loop duration. Either (value,units) or ('forever',)"),
        'check_events' : (True, # May cause slight performance hit, but probably negligible
                          ve_types.Boolean,
                          "allow input event checking during 'go' loop?"),
        'handle_event_callbacks' : (None,
                                    ve_types.Sequence(ve_types.Sequence2(ve_types.AnyOf(ve_types.Integer,ve_types.Callable))),
                                    "List of tuples to handle events. (event_type,event_callback_func)"),
        'trigger_armed':(True,
                         ve_types.Boolean,
                         "test trigger on go loop?"),
        'trigger_go_if_armed':(True,
                               ve_types.Boolean,
                               "trigger go loop?"),
        'enter_go_loop':(False,
                         ve_types.Boolean,
                         "test used by run_forever() to enter go loop"),
        'quit':(False,
                ve_types.Boolean,
                "quit the run_forever loop?"),
        'warn_mean_fps_threshold':(0.01, # fraction (0.1 = 10%)
                                   ve_types.Real,
                                   "threshold to print observered vs. expected frame rate warning (fraction units)"),
        'warn_longest_frame_threshold': (2.0, # fraction (set to 2.0 for no false positives)
                                         ve_types.Real,
                                         "threshold to print frame skipped warning (units: factor of inter-frame-interval)"),
        'override_t_abs_sec':(None, # override t_abs (in seconds) -- set only when reconstructing experiments
                              ve_types.Real,
                              "Override t_abs. Set only when reconstructing experiments. (units: seconds)"),
        }

    __slots__ = (
        'controllers',
        'num_frame_controllers',
        'frame_draw_times',
        'time_sec_absolute',
        'frames_absolute',
        'in_go_loop',
        'frames_dropped_in_last_go_loop',
        'last_go_loop_start_time_absolute_sec',
        'time_sec_since_go',
        'frames_since_go',
        )

    def __init__(self,**kw):
        VisionEgg.ClassWithParameters.__init__(self,**kw)

        if self.parameters.viewports is None:
            self.parameters.viewports = []

        if self.parameters.handle_event_callbacks is None:
            self.parameters.handle_event_callbacks = []

        self.controllers = []
        self.num_frame_controllers = 0 # reference counter for controllers that are called on frame by frame basis

        # A list that optionally records when frames were drawn by go() method.
        self.frame_draw_times = []

        self.time_sec_absolute=VisionEgg.time_func()
        self.frames_absolute=0

        self.in_go_loop = False
        self.frames_dropped_in_last_go_loop = False
        self.last_go_loop_start_time_absolute_sec = None

    def add_controller( self, class_with_parameters, parameter_name, controller ):
        """Add a controller"""
        # Check if type checking needed
        if type(class_with_parameters) != types.NoneType and type(parameter_name) != types.NoneType:
            # Check if return type of controller eval is same as parameter type
            if class_with_parameters.is_constant_parameter(parameter_name):
                raise TypeError("Attempt to control constant parameter '%s' of class %s."%(parameter_name,class_with_parameters))
            require_type = class_with_parameters.get_specified_type(parameter_name)
            try:
                ve_types.assert_type(controller.returns_type(),require_type)
            except TypeError:
                raise TypeError("Attempting to control parameter '%s' of type %s with controller that returns type %s"%(
                    parameter_name,
                    require_type,
                    controller.returns_type()))
            if not hasattr(class_with_parameters.parameters,parameter_name):
                raise AttributeError("%s has no instance '%s'"%parameter_name)
            self.controllers.append( (class_with_parameters.parameters,parameter_name, controller) )
        else: # At least one of class_with_parameters or parameter_name is None.
            # Make sure they both are None.
            if not (type(class_with_parameters) == types.NoneType and type(parameter_name) == types.NoneType):
                raise ValueError("Neither or both of class_with_parameters and parameter_name must be None.")
            self.controllers.append( (None,None,controller) )
        if controller.temporal_variables & (FRAMES_SINCE_GO|FRAMES_ABSOLUTE):
            self.num_frame_controllers = self.num_frame_controllers + 1

    def remove_controller( self, class_with_parameters, parameter_name, controller=None ):
        """Remove one (or more--see below) controller(s).

        If controller is None, all controllers affecting the
        specified parameter are removed.

        If class_with_parameters and paramter_name are None, the
        controller is removed completely

        If class_with_parameters, paramter_name, and controller are
        all None, all controllers are removed.

        """

        if class_with_parameters is None and parameter_name is None:
            if not isinstance(controller,Controller) and controller != None:

                raise TypeError( "When deleting a controller, specify an "
                                 "instance of VisionEgg.FlowControl.Controller class!")

            if controller == None: #Added by Tony, May30/2005
                self.controllers = []

            i = 0
            while i < len(self.controllers):
                orig_parameters,orig_parameter_name,orig_controller = self.controllers[i]
                if controller == orig_controller:
                    del self.controllers[i]
                else:
                    i = i + 1
            return
        if controller is None:
            # The controller function is not specified:
            # Delete all controllers that control the parameter specified.
            if class_with_parameters is None or parameter_name is None:
                raise ValueError("Must specify parameter from which controller should be removed.")
            i = 0
            while i < len(self.controllers):
                orig_parameters,orig_parameter_name,orig_controller = self.controllers[i]
                if (orig_parameters == class_with_parameters.parameters and
                    orig_parameter_name == parameter_name):
                    controller = self.controllers[i][2]
                    if controller.temporal_variables & (FRAMES_SINCE_GO|FRAMES_ABSOLUTE):
                        self.num_frame_controllers = self.num_frame_controllers - 1
                    del self.controllers[i]
                else:
                    i = i + 1
        else: # controller is specified
            # Delete only that specific controller
            i = 0
            while i < len(self.controllers):
                orig_parameters,orig_parameter_name,orig_controller = self.controllers[i]
                if (orig_parameters == class_with_parameters.parameters and
                    orig_parameter_name == parameter_name and
                    orig_controller == controller):
                    if controller.temporal_variables & (FRAMES_SINCE_GO|FRAMES_ABSOLUTE):
                        self.num_frame_controllers = self.num_frame_controllers - 1
                else:
                    i = i + 1

    def __call_controllers(self,
                         go_started=None,
                         doing_transition=None):
        done_once = [] # list of ONCE contollers to switch status of
        for (parameters_instance, parameter_name, controller) in self.controllers:
            evaluate = 0
            if controller.eval_frequency & ONCE:
                evaluate = 1
                done_once.append(controller)
            elif doing_transition and (controller.eval_frequency & TRANSITIONS):
                evaluate = 1
            elif controller.eval_frequency & EVERY_FRAME:
                evaluate = 1

            if evaluate:
                if controller.temporal_variables & TIME_SEC_ABSOLUTE:
                    controller.time_sec_absolute = self.time_sec_absolute
                if controller.temporal_variables & FRAMES_ABSOLUTE:
                    controller.frames_absolute = self.frames_absolute

                if go_started:
                    if not (controller.eval_frequency & NOT_DURING_GO):
                        if controller.temporal_variables & TIME_SEC_SINCE_GO:
                            controller.time_sec_since_go = self.time_sec_since_go
                        if controller.temporal_variables & FRAMES_SINCE_GO:
                            controller.frames_since_go = self.frames_since_go
                        result = controller.during_go_eval()
                        if parameter_name is not None:
                            setattr(parameters_instance, parameter_name, result)
                else:
                    if not (controller.eval_frequency & NOT_BETWEEN_GO):
                        if controller.temporal_variables & TIME_SEC_SINCE_GO:
                            controller.time_sec_since_go = None
                        if controller.temporal_variables & FRAMES_SINCE_GO:
                            controller.frames_since_go = None
                        result = controller.between_go_eval()
                        if parameter_name is not None:
                            setattr(parameters_instance, parameter_name, result)

        for controller in done_once:
            #Unset ONCE flag
            controller.eval_frequency = controller.eval_frequency & ~ONCE
            if isinstance(controller,EncapsulatedController):
                controller.contained_controller.eval_frequency = controller.contained_controller.eval_frequency & ~ONCE

    def is_in_go_loop(self):
        """Queries if the presentation is in a go loop.

        This is useful to check the state of the Vision Egg
        application from a remote client over Pyro."""
        return self.in_go_loop

    def were_frames_dropped_in_last_go_loop(self):
        return self.frames_dropped_in_last_go_loop

    def get_last_go_loop_start_time_absolute_sec(self):
        return self.last_go_loop_start_time_absolute_sec

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
        import VisionEgg.Core # here to prevent circular import
        self.in_go_loop = 1

        swap_buffers = VisionEgg.Core.swap_buffers # shorthand

        # Clear boolean indicator
        self.frames_dropped_in_last_go_loop = False

        # Create shorthand notation, which speeds the main loop
        # slightly by not performing name lookup each time.
        p = self.parameters

        if p.collect_timing_info:
            frame_timer = VisionEgg.Core.FrameTimer()

        while (not p.trigger_armed) or (not p.trigger_go_if_armed):
            self.between_presentations()

        # Go!

        self.time_sec_absolute=VisionEgg.time_func()

        if p.override_t_abs_sec is not None:
            raise NotImplementedError("Cannot override absolute time yet")

        self.last_go_loop_start_time_absolute_sec = self.time_sec_absolute
        self.time_sec_since_go = 0.0
        self.frames_since_go = 0

        synclync_connection = VisionEgg.config._SYNCLYNC_CONNECTION # create shorthand
        if synclync_connection:
            import synclync
            synclync_connection.next_control_packet.action_flags += (synclync.SL_CLEAR_VSYNC_COUNT +
                                                                     synclync.SL_CLEAR_NOTIFY_SWAPPED_COUNT +
                                                                     synclync.SL_CLEAR_FRAMESKIP_COUNT)
            synclync_hack_done_once = 0

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
            # Get list of screens
            screens = []
            for viewport in p.viewports:
                s = viewport.parameters.screen
                if s not in screens:
                    screens.append(s)

            # Clear the screen(s)
            for screen in screens:
                screen.clear()

            # Update all the realtime parameters
            self.__call_controllers(
                go_started=1,
                doing_transition=0)

            # Draw each viewport
            for viewport in p.viewports:
                viewport.draw()

            # Swap the buffers
            if synclync_connection:
                if not synclync_hack_done_once:
                    synclync_connection.next_control_packet.action_flags += (synclync.SL_NOTIFY_SWAPPED_BUFFERS +
                                                                             synclync.SL_NOTIFY_IN_GO_LOOP)
                    synclync_connection.send_control_packet()
                    synclync_hack_done_once = 1
                data_packet = synclync_connection.get_latest_data_packet()
            swap_buffers()

            # Set the time variables for the next frame
            self.time_sec_absolute=VisionEgg.time_func()
            last_time_sec_since_go = self.time_sec_since_go
            self.time_sec_since_go = self.time_sec_absolute - start_time_absolute
            self.frames_absolute += 1
            self.frames_since_go += 1

            if p.collect_timing_info:
                frame_timer.tick()

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

        # Tell SyncLync we're not in go loop anymore
        if synclync_connection:
            synclync_connection.send_control_packet() # nothing in action_flags -- finishes go loop

        # Check to see if frame by frame control was desired
        # but OpenGL not syncing to vertical retrace
        try:
            mean_frame_time_sec = frame_timer.get_average_ifi_sec()
            calculated_fps = 1.0/mean_frame_time_sec
        except:
            # the above fails when no frames were drawn
            mean_frame_time_sec = 0.0
            calculated_fps = 0.0

        if self.num_frame_controllers: # Frame by frame control desired
            impossibly_fast_frame_rate = 210.0
            if calculated_fps > impossibly_fast_frame_rate: # Let's assume no monitor can exceed impossibly_fast_frame_rate
                logger = logging.getLogger('VisionEgg.FlowControl')
                logger.error("Frame by frame control desired, but "
                             "average frame rate was %.2f frames per "
                             "second-- faster than any display device "
                             "(that I know of).  Set your drivers to "
                             "sync buffer swapping to vertical "
                             "retrace. (platform/driver "
                             "dependent)"%(calculated_fps))
        # Warn if > warn_mean_fps_threshold error in frame rate
        if abs(calculated_fps-VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ) / float(VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ) > self.parameters.warn_mean_fps_threshold:
            logger = logging.getLogger('VisionEgg.FlowControl')
            logger.warning("Calculated frames per second was %.3f, "
                           "while the VISIONEGG_MONITOR_REFRESH_HZ "
                           "variable is %s."%(calculated_fps,
                           VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ))
        frame_skip_fraction = self.parameters.warn_longest_frame_threshold
        inter_frame_inteval = 1.0/VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ

        if p.collect_timing_info:
            longest_frame_draw_time_sec = frame_timer.get_longest_frame_duration_sec()
            if longest_frame_draw_time_sec is not None:
                logger = logging.getLogger('VisionEgg.FlowControl')
                if longest_frame_draw_time_sec >= (frame_skip_fraction*inter_frame_inteval):
                    self.frames_dropped_in_last_go_loop = True
                    logger.warning("One or more frames took %.1f msec, "
                                   "which is signficantly longer than the "
                                   "expected inter frame interval of %.1f "
                                   "msec for your frame rate (%.1f Hz)."%(
                                   longest_frame_draw_time_sec*1000.0,
                                   inter_frame_inteval*1000.0,
                                   VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ))
                else:
                    logger.debug("Longest frame update was %.1f msec. "
                                 "Your expected inter frame interval is "
                                 "%f msec."%(longest_frame_draw_time_sec*1000.0,
                                 inter_frame_inteval*1000.0))
            frame_timer.log_histogram()

        self.in_go_loop = 0

    def export_movie_go(self, frames_per_sec=12.0, filename_suffix=".tif", filename_base="visionegg_movie", path="."):
        """Emulates method 'go' but saves a movie."""
        import VisionEgg.Core # here to prevent circular import
        import Image # Could import this at the beginning of the file, but it breaks sometimes!
        import os # Could also import this, but this is the only place its needed

        # Create shorthand notation, which speeds the main loop
        # slightly by not performing name lookup each time.
        p = self.parameters

        # Switch function VisionEgg.time_func
        self.time_sec_absolute=VisionEgg.time_func() # Set for real once
        true_time_func = VisionEgg.time_func
        def fake_time_func():
            return self.time_sec_absolute
        VisionEgg.time_func = fake_time_func

        logger = logging.getLogger('VisionEgg.FlowControl')

        # Go!

        self.time_sec_absolute=VisionEgg.time_func()
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
            # Get list of screens
            screens = []
            for viewport in p.viewports:
                s = viewport.parameters.screen
                if s not in screens:
                    screens.append(s)

            # Clear the screen(s)
            for screen in screens:
                screen.clear()

            # Update all the realtime parameters
            self.__call_controllers(
                go_started=1,
                doing_transition=0)

            # Draw each viewport
            for viewport in p.viewports:
                viewport.draw()

            # Swap the buffers
            VisionEgg.Core.swap_buffers()

            # Now save the contents of the framebuffer
            fb_image = screen.get_framebuffer_as_image(buffer='front',format=gl.GL_RGB)
            filename = "%s%04d%s"%(filename_base,image_no,filename_suffix)
            savepath = os.path.join( path, filename )
            logger.info("Saving '%s'"%filename)
            fb_image.save( savepath )
            image_no = image_no + 1

            # Set the time variables for the next frame
            self.time_sec_absolute += 1.0/frames_per_sec
            self.time_sec_since_go += 1.0/frames_per_sec
            self.frames_absolute += 1
            self.frames_since_go += 1

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
            logger.warning("Only saved movie from last screen.")

        scp = screen.constant_parameters
        if scp.red_bits is not None:
            warn_about_movie_depth = 0
            if scp.red_bits > 8:
                warn_about_movie_depth = 1
            elif scp.green_bits > 8:
                warn_about_movie_depth = 1
            elif scp.blue_bits > 8:
                warn_about_movie_depth = 1
            if warn_about_movie_depth:
                logger.warning("Only saved 8 bit per pixel movie, even "
                               "though your framebuffer supports more!")
        # Restore VisionEgg.time_func
        VisionEgg.time_func = true_time_func

    def run_forever(self):
        """Main control loop between go loops."""
        p = self.parameters
        # enter with transitional contoller call
        self.__call_controllers(
            go_started=0,
            doing_transition=1)
        while not p.quit:
            self.between_presentations()
            if self.parameters.enter_go_loop:
                self.parameters.enter_go_loop = False
                self.go()
            if p.check_events:
                for event in pygame.event.get():
                    for event_type, event_callback in p.handle_event_callbacks:
                        if event.type is event_type:
                            event_callback(event)

    def between_presentations(self):
        """Maintain display while between stimulus presentations.

        This function gets called as often as possible when in the
        'run_forever' loop except when execution has shifted to the
        'go' loop.

        Other than the difference in the time variable passed to the
        controllers, this routine is very similar to the inside of the
        main loop in the go method.
        """
        import VisionEgg.Core # here to prevent circular import

        self.time_sec_absolute=VisionEgg.time_func()

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
        VisionEgg.Core.swap_buffers()
        self.frames_absolute += 1

####################################################################
#
#        Controller
#
####################################################################

class Controller(object):
    """Control parameters.

    This abstract base class defines the interface to any controller.

    Methods:

    returns_type() -- Get the type of the value returned by the eval functions
    during_go_eval() -- Evaluate controller during the main 'go' loop.
    between_go_eval() -- Evaluate controller between runs of the main 'go' loop.

    The during_go_eval() and between_go_eval() methods are called to
    update a particular parameter such as the position of a stimulus
    on the screen.  These methods must return a value specified by the
    returns_type() method.  These methods are called at particular
    intervals as specified by eval_frequency and with temporal
    parameters specified by temporal_variables (see below for more
    details).  Also, see the documentation for the Presentation class.

    Attributes:

    return_type -- type of the value returned by the eval functions
    eval_frequency -- when eval functions called (see above)
    temporal_variables -- what time variables used (see above)

    A Controller instance's attribute "eval_frequency" controls when a
    controller is evaluated. This variable is a bitwise "or" (the |
    operator) of the following flags:

    EVERY_FRAME    -- every frame
    TRANSITIONS    -- on enter and exit from go loop
    ONCE           -- at the next chance possible (see below)
    NOT_DURING_GO  -- as above, but never during go loop (see below)
    NOT_BETWEEN_GO -- as above, but never between go loops (see below)

    The ONCE flag is automatically unset after evaluation,
    hence its name. As an example, if eval_frequency is set to
    ONCE | TRANSITIONS, it will be evaluated
    before drawing the next frame and then only before and after the
    go loop.

    NOT_DURING_GO and NOT_BETWEEN_GO modify other behavior. For
    example, to evaluate a controller on every frame during go loops
    but not between go loops:

    eval_frequency = EVERY_FRAME | NOT_BETWEEN_GO

    If none of the above flags is set, the value is:

    NEVER          -- this controller is never called

    A Controller instance's attribute "temporal_variables" controls
    what time variables are set for use. This variable is a bitwise
    "or" of the following flags:

    TIME_SEC_ABSOLUTE -- seconds, continuously increasing
    TIME_SEC_SINCE_GO -- seconds, reset to 0.0 each go loop
    FRAMES_ABSOLUTE   -- frames, continuously increasing
    FRAMES_SINCE_GO   -- frames, reset to 0 each go loop

    If none of these flags is set, the value is:

    TIME_INDEPENDENT -- No temporal variables.

    When the eval methods (during_go_eval and between_go_eval) are
    called, attributes are set depending on the temporal variables
    used:

    temporal_variable   attribute set
    -----------------   -------------
    TIME_SEC_ABSOLUTE   self.time_sec_absolute
    TIME_SEC_SINCE_GO   self.time_sec_since_go
    FRAMES_ABSOLUTE     self.frames_absolute
    FRAMES_SINCE_GO     self.frames_since_go

    Other information:

    Instances of Controller are called by instances of the
    Presentation class.  during_go_eval() is called during a go()
    loop, and between_go_eval() is called by between_presentations()
    (during run_forever(), for example).  Before calling these
    methods, attributes of the controller are set accoring to
    \attribute{temporal_variables}.

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
        if not ve_types.is_parameter_type_def(return_type):
            if type(return_type) == types.TypeType:
                raise TypeError("Argument 'return_type' in Controller must be a VisionEgg parameter type definition.  Hint: use VisionEgg.ParameterTypes.get_type() to get the type of your value")
            raise TypeError("Argument 'return_type' in Controller must be a VisionEgg parameter type definition")
        self.return_type = return_type

        self.temporal_variables = temporal_variables
        self.eval_frequency = eval_frequency

    def evaluate_now(self):
        """Call this after updating the values of a controller if it's not evaluated EVERY_FRAME."""
        self.eval_frequency = self.eval_frequency | ONCE

    def set_eval_frequency(self,eval_frequency):
        self.eval_frequency = eval_frequency

    def returns_type(self):
        """Called by Presentation. Get the return type of this controller."""
        return self.return_type

    def during_go_eval(self):
        """Called by Presentation. Evaluate during the main 'go' loop.

        Override this method in subclasses."""
        raise RuntimeError("%s: Definition of during_go_eval() in abstract base class Contoller must be overriden."%(str(self),))

    def between_go_eval(self):
        """Called by Presentation. Evaluate between runs of the main 'go' loop.

        Override this method in subclasses."""
        raise RuntimeError("%s: Definition of between_go_eval() in abstract base class Controller must be overriden."%(str(self),))

    def _test_self(self,go_started):
        """Test whether a controller works.

        This method performs everything the Presentation go() or
        run_forever() methods do when calling controllers, except that
        the temporal variables are set to -1 and that the return value
        is not used to set parameters."""

        if self.temporal_variables & TIME_SEC_ABSOLUTE:
            self.time_sec_absolute = -1.0
        if self.temporal_variables & FRAMES_ABSOLUTE:
            self.frames_absolute = -1

        if go_started:
            if not (self.eval_frequency & NOT_DURING_GO):
                if self.temporal_variables & TIME_SEC_SINCE_GO:
                    self.time_sec_since_go = -1.0
                if self.temporal_variables & FRAMES_SINCE_GO:
                    self.frames_since_go = -1
                return self.during_go_eval()
        else:
            if not (self.eval_frequency & NOT_BETWEEN_GO):
                if self.temporal_variables & TIME_SEC_SINCE_GO:
                    self.time_sec_since_go = None
                if self.temporal_variables & FRAMES_SINCE_GO:
                    self.frames_since_go = None
                return self.between_go_eval()

class ConstantController(Controller):
    """Set parameters to a constant value."""
    def __init__(self,
                 during_go_value = None,
                 between_go_value = None,
                 **kw
                 ):
        kw.setdefault('return_type',ve_types.get_type(during_go_value))
        kw.setdefault('eval_frequency',ONCE | TRANSITIONS)
        Controller.__init__(self,**kw)
        if self.return_type is not types.NoneType and during_go_value is None:
            raise ValueError("Must specify during_go_value")
        if between_go_value is None:
            between_go_value = during_go_value
        ve_types.assert_type(ve_types.get_type(during_go_value),self.return_type)
        ve_types.assert_type(ve_types.get_type(between_go_value),self.return_type)
        self.during_go_value = during_go_value
        self.between_go_value = between_go_value

    def set_during_go_value(self,during_go_value):
        ve_types.assert_type(ve_types.get_type(during_go_value),self.return_type)
        self.during_go_value = during_go_value
##        if ve_types.get_type(during_go_value) is not self.return_type:
##            raise TypeError("during_go_value must be %s"%str(self.return_type))
##        else:
##            self.during_go_value = during_go_value

    def get_during_go_value(self):
        return self.during_go_value

    def set_between_go_value(self,between_go_value):
        ve_types.assert_type(ve_types.get_type(between_go_value),self.return_type)
        self.between_go_value = between_go_value
##        if ve_types.get_type(between_go_value) is not self.return_type:
##            raise TypeError("between_go_value must be %s"%str(self.return_type))
##        else:
##            self.between_go_value = between_go_value

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

    The string, when evaluated as Python code, becomes the value used.
    For example, the string "1.0" would set parameter values to 1.0.

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
        import VisionEgg.Core # here to prevent circular import

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
        if not kw.has_key('return_type'):
            set_return_type = 1
            kw['return_type'] = types.NoneType

        # Call base class __init__
        Controller.__init__(self,**kw)
        if not_between_go:
            self.eval_frequency = self.eval_frequency|NOT_BETWEEN_GO
        if set_return_type:
            logger = logging.getLogger('VisionEgg.FlowControl')
            if not (self.eval_frequency & NOT_DURING_GO):
                logger.debug( 'Executing "%s" to test for return type.'%(during_go_eval_string,))
                self.return_type = ve_types.get_type(self._test_self(go_started=1))
            elif not (self.eval_frequency & NOT_BETWEEN_GO):
                logger.debug('Executing "%s" to test for return type.'%(between_go_eval_string,))
                self.return_type = ve_types.get_type(self._test_self(go_started=0))

    def set_during_go_eval_string(self,during_go_eval_string):
        self.during_go_eval_code = compile(during_go_eval_string,'<string>','eval')
        self.during_go_eval_string = during_go_eval_string

    def get_during_go_eval_string(self):
        return self.during_go_eval_string

    def set_between_go_eval_string(self,between_go_eval_string):
        self.between_go_eval_code = compile(between_go_eval_string,'<string>','eval')
        self.between_go_eval_string = between_go_eval_string
        self.eval_frequency = self.eval_frequency & ~NOT_BETWEEN_GO

    def get_between_go_eval_string(self):
        if hasattr(self,"between_go_eval_string"):
            return self.between_go_eval_string
        else:
            return None

    def during_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        eval_locals = {}
        if self.temporal_variables & TIME_SEC_ABSOLUTE:
            eval_locals['t_abs'] = self.time_sec_absolute
        if self.temporal_variables & TIME_SEC_SINCE_GO:
            eval_locals['t'] = self.time_sec_since_go
        if self.temporal_variables & FRAMES_ABSOLUTE:
            eval_locals['f_abs'] = self.frames_absolute
        if self.temporal_variables & FRAMES_SINCE_GO:
            eval_locals['f'] = self.frames_since_go
        return eval(self.during_go_eval_code,self.eval_globals,eval_locals)

    def between_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        eval_locals = {}
        if self.temporal_variables & TIME_SEC_ABSOLUTE:
            eval_locals['t_abs'] = self.time_sec_absolute
        if self.temporal_variables & FRAMES_ABSOLUTE:
            eval_locals['f_abs'] = self.frames_absolute
        return eval(self.between_go_eval_code,self.eval_globals,eval_locals)

class ExecStringController(Controller):
    """Set parameters using potentially complex Python string.

    You can execute arbitrarily complex Python code with this
    controller.  The return value must be contained within the
    variable "x".  In other words, this string must assign the
    variable x, so setting the string to "x=1.0" would set the
    parameter under control to 1.0.

    To increase speed, the string is compiled to Python's
    bytecode format.

    The string can make use of temporal variables, which are made
    available depending on the controller's temporal_variables
    attribute. Note that only the absolute temporal variables are
    available when the go loop is not running.

    flag(s) present    variable  description
    -----------------  --------  ----------------------------------
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
        import VisionEgg.Core # here to prevent circular import

        # Create a namespace for eval_strings to use
        self.eval_globals = {}

        if during_go_exec_string is None:
            raise ValueError, "'during_go_exec_string' is a required argument"

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
        if not kw.has_key('return_type'):
            set_return_type = 1
            kw['return_type'] = types.NoneType

        # Call base class __init__
        Controller.__init__(self,**kw)
        if not_between_go:
            self.eval_frequency = self.eval_frequency|NOT_BETWEEN_GO
        if set_return_type:
            logger = logging.getLogger('VisionEgg.FlowControl')
            if not (self.eval_frequency & NOT_DURING_GO):
                logger.debug('Executing "%s" to test for return type.'%(during_go_exec_string,))
                self.return_type = ve_types.get_type(self._test_self(go_started=1))
            elif not (self.eval_frequency & NOT_BETWEEN_GO):
                logger.debug('Executing "%s" to test for return type.'%(between_go_exec_string,))
                self.return_type = ve_types.get_type(self._test_self(go_started=0))

    def set_during_go_exec_string(self,during_go_exec_string):
        self.during_go_exec_code = compile(during_go_exec_string,'<string>','exec')
        self.during_go_exec_string = during_go_exec_string

    def get_during_go_exec_string(self):
        return self.during_go_exec_string

    def set_between_go_exec_string(self,between_go_exec_string):
        self.between_go_exec_code = compile(between_go_exec_string,'<string>','exec')
        self.between_go_exec_string = between_go_exec_string
        self.eval_frequency = self.eval_frequency & ~NOT_BETWEEN_GO

    def get_between_go_exec_string(self):
        if hasattr(self,"between_go_exec_string"):
            return self.between_go_exec_string
        else:
            return None

    def during_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        eval_locals = {}
        if self.temporal_variables & TIME_SEC_ABSOLUTE:
            eval_locals['t_abs'] = self.time_sec_absolute
        if self.temporal_variables & TIME_SEC_SINCE_GO:
            eval_locals['t'] = self.time_sec_since_go
        if self.temporal_variables & FRAMES_ABSOLUTE:
            eval_locals['f_abs'] = self.frames_absolute
        if self.temporal_variables & FRAMES_SINCE_GO:
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
        if self.temporal_variables & TIME_SEC_ABSOLUTE:
            eval_locals['t_abs'] = self.time_sec_absolute
        if self.temporal_variables & FRAMES_ABSOLUTE:
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
            return x # x should be assigned by the exec string

class FunctionController(Controller):
    """Set parameters using a Python function.

    This is a very commonly used subclass of Controller, because it is
    very intuitive and requires a minimum of code to set up.  Many of
    the Vision Egg demo programs create instances of
    FunctionController.

    A number of parameters are passed to the function depending on the
    value of temporal_variables:

    The function can make use of temporal variables, which are made
    available by passingkeyword argument(s) depending on the
    controller's temporal_variables attribute. Note that only the
    absolute temporal variables are available when the go loop is not
    running.

    flag(s) present    argument  description
    -----------------  --------  ----------------------------------
    TIME_SEC_ABSOLUTE  t_abs     seconds, continuously increasing
    TIME_SEC_SINCE_GO  t         seconds, reset to 0.0 each go loop
    FRAMES_ABSOLUTE    f_abs     frames, continuously increasing
    FRAMES_SINCE_GO    f         frames, reset to 0 each go loop

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
        import VisionEgg.Core # here to prevent circular import

        if during_go_func is None:
            raise ValueError("Must specify during_go_func")

        # Set default value if not set
        kw.setdefault('temporal_variables',TIME_SEC_SINCE_GO) # default value

        # Check to make sure return_type is set
        if not kw.has_key('return_type'):
            logger = logging.getLogger('VisionEgg.FlowControl')
            logger.debug('Evaluating %s to test for return type.'%(str(during_go_func),))
            call_args = {}
            if kw['temporal_variables'] & TIME_SEC_ABSOLUTE:
                call_args['t_abs'] = VisionEgg.time_func()
            if kw['temporal_variables'] & TIME_SEC_SINCE_GO:
                call_args['t'] = 0.0
            if kw['temporal_variables'] & FRAMES_ABSOLUTE:
                call_args['f_abs'] = 0
            if kw['temporal_variables'] & FRAMES_SINCE_GO:
                call_args['f'] = 0
            # Call the function with time variables
            kw['return_type'] = ve_types.get_type(during_go_func(**call_args))
        Controller.__init__(self,**kw)
        self.during_go_func = during_go_func
        self.between_go_func = between_go_func
        if between_go_func is None:
            self.eval_frequency = self.eval_frequency|NOT_BETWEEN_GO

    def during_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        call_args = {}
        if self.temporal_variables & TIME_SEC_ABSOLUTE:
            call_args['t_abs'] = self.time_sec_absolute
        if self.temporal_variables & TIME_SEC_SINCE_GO:
            call_args['t'] = self.time_sec_since_go
        if self.temporal_variables & FRAMES_ABSOLUTE:
            call_args['f_abs'] = self.frames_absolute
        if self.temporal_variables & FRAMES_SINCE_GO:
            call_args['f'] = self.frames_since_go
        return self.during_go_func(**call_args)

    def between_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        call_args = {}
        if self.temporal_variables & TIME_SEC_ABSOLUTE:
            call_args['t_abs'] = self.time_sec_absolute
        if self.temporal_variables & FRAMES_ABSOLUTE:
            call_args['f_abs'] = self.frames_absolute
        return self.between_go_func(**call_args)

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
        Controller.__init__(self,**{'return_type':types.NoneType})
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
        import VisionEgg.Core # here to prevent circular import
        if self.temporal_variables & TIME_SEC_ABSOLUTE:
            self.contained_controller.time_sec_absolute = self.time_sec_absolute
        if self.temporal_variables & TIME_SEC_SINCE_GO:
            self.contained_controller.time_sec_since_go = self.time_sec_since_go
        if self.temporal_variables & FRAMES_ABSOLUTE:
            self.contained_controller.frames_absolute = self.frames_absolute
        if self.temporal_variables & FRAMES_SINCE_GO:
            self.contained_controller.frames_since_go = self.frames_since_go
        return self.contained_controller.during_go_eval()

    def between_go_eval(self):
        """Called by Presentation. Overrides method in Controller base class."""
        import VisionEgg.Core # here to prevent circular import
        import VisionEgg.FlowControl
        if self.temporal_variables & TIME_SEC_ABSOLUTE:
            self.contained_controller.time_sec_absolute = self.time_sec_absolute
        if self.temporal_variables & FRAMES_ABSOLUTE:
            self.contained_controller.frames_absolute = self.frames_absolute
        return self.contained_controller.between_go_eval()

# Constants (These are a copy of the static class variables from the
# Controller class into the module-level namespace. This is done for
# convenience.)
#     temporal_variables flags:
TIME_INDEPENDENT  = Controller.TIME_INDEPENDENT
TIME_SEC_ABSOLUTE = Controller.TIME_SEC_ABSOLUTE
TIME_SEC_SINCE_GO = Controller.TIME_SEC_SINCE_GO
FRAMES_ABSOLUTE   = Controller.FRAMES_ABSOLUTE
FRAMES_SINCE_GO   = Controller.FRAMES_SINCE_GO
#     eval_frequency flags:
NEVER          = Controller.NEVER
EVERY_FRAME    = Controller.EVERY_FRAME
TRANSITIONS    = Controller.TRANSITIONS
ONCE           = Controller.ONCE
NOT_DURING_GO  = Controller.NOT_DURING_GO
NOT_BETWEEN_GO = Controller.NOT_BETWEEN_GO
