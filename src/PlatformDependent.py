"""Attempt to isolate platform dependencies in one place

Functions:

set_realtime -- Raise the Vision Egg to maximum priority
linux_but_not_nvidia -- Warn that platform is linux, but drivers not nVidia
sync_swap_with_vbl_pre_gl_init -- Try to synchronize buffer swapping and vertical retrace before starting OpenGL
sync_swap_with_vbl_post_gl_init -- Try to synchronize buffer swapping and vertical retrace after starting OpenGL
"""

# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import sys, os, string
import VisionEgg.Core

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

############# Import Vision Egg C routines, if they exist #############
def set_priority(*args,**kw):
    """Set the priority of the Vision Egg application.

    Defaults to maximum priority, but can be changed via keyword
    arguments.

    Raises an exception on failure.
    """
    
    # potential keywords
    parse_me = ["darwin_realtime_period_denom",
                "darwin_realtime_computation_denom",
                "darwin_realtime_constraint_denom",
                "darwin_realtime_preemptible",
                "darwin_maxpriority_conventional_not_realtime",
                "darwin_conventional_priority",
                "darwin_pthread_priority"]

    params = {}
    # set variable in local namespace
    for word in parse_me:
        # set the value from VisionEgg.config
        config_name = "VISIONEGG_"+string.upper(word)
        value = getattr(VisionEgg.config,config_name)
        # set the value if present in keyword arguments
        if word in kw.keys():
            value = kw[word]
        params[word] = value

    if sys.platform != 'darwin':
        try:
            import _maxpriority
            apply(_maxpriority.set_realtime,args,kw)
        except:
            raise NotImplementedError("No support for setting the priority on this platform")
    elif sys.platform == 'darwin':

        # Everything to support realtime in Apple Mac OS X is based on
        # the following two things:
        #
        # 1) http://developer.apple.com/techpubs/macosx/Darwin/General/KernelProgramming/scheduler/Using_Mach__pplications.html
        #
        # 2) The Mac OS X port of the Esound daemon.
                   
        import darwin_maxpriority

        if params['darwin_maxpriority_conventional_not_realtime']:
            import errno
            darwin_maxpriority.cvar.errno = 0 # set errno in c
            current_priority = darwin_maxpriority.getpriority(darwin_maxpriority.PRIO_PROCESS,0)
            if darwin_maxpriority.cvar.errno != 0:
                raise RuntimeError("Error calling getpriority(): %s"%errno.errorcode[darwin_maxpriority.cvar.errno])

            if not darwin_maxpriority.setpriority(darwin_maxpriority.PRIO_PROCESS,0,params['darwin_conventional_priority']):
                raise RuntimeError("Error calling getpriority(): %s"%errno.errorcode[darwin_maxpriority.cvar.errno])

            darwin_pthread_priority = params['darwin_pthread_priority']
            if darwin_pthread_priority == "max": # should otherwise be an int
                darwin_pthread_priority = darwin_maxpriority.sched_get_priority_max(darwin_maxpriority.SCHED_RR)

            VisionEgg.Core.message.add( "Setting max priority mode for darwin platform "\
                                        "using conventional priority.",
                                        VisionEgg.Core.Message.INFO)

            if darwin_maxpriority.set_self_pthread_priority(darwin_maxpriority.SCHED_RR,
                                                            darwin_pthread_priority) == -1:
                raise RuntimeError("set_self_pthread failed.")

        else:
            bus_speed = darwin_maxpriority.get_bus_speed()

            VisionEgg.Core.message.add( "Setting max priority mode for darwin platform "\
                                        "using realtime threads. ( period = %d / %d, "\
                                        "computation = %d / %d, constraint = %d / %d, "\
                                        "preemptible = %d )"%
                                        ( bus_speed, params['darwin_realtime_period_denom'],
                                          bus_speed, params['darwin_realtime_computation_denom'],
                                          bus_speed, params['darwin_realtime_constraint_denom'],
                                          params['darwin_realtime_preemptible'] ),
                                        VisionEgg.Core.Message.INFO)

            period = bus_speed / params['darwin_realtime_period_denom']
            computation = bus_speed / params['darwin_realtime_computation_denom']
            constraint = bus_speed / params['darwin_realtime_constraint_denom']
            preemptible = params['darwin_realtime_preemptible']

            darwin_maxpriority.set_self_thread_time_constraint_policy( period, computation, constraint, preemptible )
            
def linux_but_not_nvidia():
    """Warn that platform is linux, but drivers not nVidia."""
    # If you've added support for other drivers to sync with VBL under
    # linux, please let me know how!
    VisionEgg.Core.message.add(
        """VISIONEGG WARNING: Could not sync buffer swapping to
        vertical blank pulse because you are running linux but not the
        nVidia drivers.  It is quite possible this can be enabled,
        it's just that I haven't had access to anything but nVidia
        cards under linux!""", level=VisionEgg.Core.Message.WARNING)
    
def sync_swap_with_vbl_pre_gl_init():
    """Try to synchronize buffer swapping and vertical retrace before starting OpenGL."""
    success = 0
    if sys.platform == "linux2":
        # Unfotunately, cannot check do glGetString(GL_VENDOR) to
        # check if drivers are nVidia because we have to do that requires
        # OpenGL context started, but this variable must be set
        # before OpenGL context started!
        
        # Assume drivers are nVidia
        VisionEgg.Core.add_gl_assumption("GL_VENDOR","nvidia",linux_but_not_nvidia)
        # Set nVidia linux environmental variable
        os.environ["__GL_SYNC_TO_VBLANK"] = "1"
        success = 1
    elif sys.platform[:4] == "irix":
        
        # I think this is set using the GLX swap_control SGI
        # extension.  A C extension could be to be written to change
        # this value. (It probably cannot be set through an OpenGL
        # extension or an SDL/pygame feature.)
        
        VisionEgg.Core.message.add("IRIX platform detected, assuming retrace sync.",
                                   level=VisionEgg.Core.Message.TRIVIAL)
        
    return success

def sync_swap_with_vbl_post_gl_init():
    """Try to synchronize buffer swapping and vertical retrace after starting OpenGL."""
    success = 0
    try:
        if sys.platform == "win32":
            import OpenGL.WGL.EXT.swap_control
            if OpenGL.WGL.EXT.swap_control.wglInitSwapControlARB(): # Returns 1 if it's working
                OpenGL.WGL.EXT.swap_control.wglSwapIntervalEXT(1) # Swap only at frame syncs
                if OpenGL.WGL.EXT.swap_control.wglGetSwapIntervalEXT() == 1:
                    success = 1
        elif sys.platform == "darwin":
            try:
                import _darwin_sync_swap
                
                _darwin_sync_swap.sync_swap()
                success = 1
            except Exception,x:
                VisionEgg.Core.message.add("Failed trying to synchronize buffer swapping on darwin: %s: %s"%(str(x.__class__),str(x)))
    except:
        pass
    
    return success
