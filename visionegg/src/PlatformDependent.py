"""Set priority and other functions

Functions:

set_priority() -- Change the Vision Egg priority
linux_but_unknown_drivers() -- Warn that platform is linux, but drivers unknown
sync_swap_with_vbl_pre_gl_init() -- Try to synchronize buffer swapping and vertical retrace before starting OpenGL
sync_swap_with_vbl_post_gl_init() -- Try to synchronize buffer swapping and vertical retrace after starting OpenGL
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

def set_icon( name ):
    if sys.platform == 'darwin':
        import darwin_app_stuff
        darwin_app_stuff.set_icon( name )

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
        if hasattr(VisionEgg.config,config_name):
            value = getattr(VisionEgg.config,config_name)
        else:
            value = None
        # override default value if present in keyword arguments
        if word in kw.keys():
            value = kw[word]
        if value is not None:
            params[word] = value

    if sys.platform == 'darwin':

        # Everything to support realtime in Apple Mac OS X is based on
        # the following two things:
        #
        # 1) http://developer.apple.com/techpubs/macosx/Darwin/General/KernelProgramming/scheduler/Using_Mach__pplications.html
        #
        # 2) The Mac OS X port of the Esound daemon.
                   
        import darwin_maxpriority

        if params['darwin_maxpriority_conventional_not_realtime']:
            process = darwin_maxpriority.PRIO_PROCESS
            policy = darwin_maxpriority.SCHED_RR

            VisionEgg.Core.message.add(
                """Setting max priority mode for darwin platform
                using conventional priority %d."""%(
                params['darwin_conventional_priority'],),
                VisionEgg.Core.Message.INFO)
                
            # set the priority of the current process
            darwin_maxpriority.setpriority(process,0,params['darwin_conventional_priority'])

            # This sets the pthread priority, which only prioritizes
            # threads in the process.  Might as well do it, but it
            # shouldn't matter unless we're running multi-threaded.
            darwin_pthread_priority = params['darwin_pthread_priority']
            if darwin_pthread_priority == "max": # should otherwise be an int
                darwin_pthread_priority = darwin_maxpriority.sched_get_priority_max(policy)

            if darwin_maxpriority.set_self_pthread_priority(policy,
                                                            darwin_pthread_priority) == -1:
                raise RuntimeError("set_self_pthread failed.")

        else:
            bus_speed = darwin_maxpriority.get_bus_speed()

            VisionEgg.Core.message.add(
                """Setting max priority mode for darwin platform
                using realtime threads. ( period = %d / %d, 
                computation = %d / %d, constraint = %d / %d, 
                preemptible = %d )""" % ( bus_speed,
                params['darwin_realtime_period_denom'],
                bus_speed, params['darwin_realtime_computation_denom'],
                bus_speed, params['darwin_realtime_constraint_denom'],
                params['darwin_realtime_preemptible'] ),
                VisionEgg.Core.Message.INFO)

            period = bus_speed / params['darwin_realtime_period_denom']
            computation = bus_speed / params['darwin_realtime_computation_denom']
            constraint = bus_speed / params['darwin_realtime_constraint_denom']
            preemptible = params['darwin_realtime_preemptible']

            darwin_maxpriority.set_self_thread_time_constraint_policy( period, computation, constraint, preemptible )
    elif sys.platform == 'win32':
        import win32_maxpriority

        VisionEgg.Core.message.add(
            """Setting priority for win32 platform to
            HIGH_PRIORITY_CLASS, THREAD_PRIORITY_HIGHEST.  (This is
            Microsoft's maximum recommended priority, but you could
            still raise it higher.)""",
            VisionEgg.Core.Message.INFO)
                
        win32_maxpriority.set_self_process_priority_class(
            win32_maxpriority.HIGH_PRIORITY_CLASS )
        win32_maxpriority.set_self_thread_priority(
            win32_maxpriority.THREAD_PRIORITY_HIGHEST)
        
    elif sys.platform in ['linux2','irix','posix']:
        import posix_maxpriority

        policy = posix_maxpriority.SCHED_FIFO
        max_priority = posix_maxpriority.sched_get_priority_max( policy )

        VisionEgg.Core.message.add(
            """Setting priority for POSIX-compatible platform to
            policy SCHED_FIFO and priority to %d"""%max_priority,
            VisionEgg.Core.Message.INFO)
                
        posix_maxpriority.set_self_policy_priority( policy, max_priority )
        posix_maxpriority.stop_memory_paging()
    else:
        raise RuntimeError("Cannot change priority.  Unknown platform '%s'"%sys.platform)
            
def linux_but_unknown_drivers():
    """Warn that platform is linux, but drivers not known."""
    # If you've added support for other drivers to sync with VBLANK under
    # linux, please let me know how!
    VisionEgg.Core.message.add(
        """VISIONEGG WARNING: Could not sync buffer swapping to vblank
        because you are running linux but not known/supported drivers
        (nVidia or recent Mesa DRI Radeon)."""
        , level=VisionEgg.Core.Message.WARNING)
    
def sync_swap_with_vbl_pre_gl_init():
    """Try to synchronize buffer swapping and vertical retrace before starting OpenGL."""
    success = 0
    if sys.platform == "linux2":
        # Unfotunately, cannot check do glGetString(GL_VENDOR) to
        # check if drivers are nVidia because we have to do that requires
        # OpenGL context started, but this variable must be set
        # before OpenGL context started!
        
        # Assume drivers are nVidia or recent ATI
        VisionEgg.Core.add_gl_assumption("__SPECIAL__","linux_nvidia_or_new_ATI",linux_but_unknown_drivers)
        # Set for nVidia linux
        os.environ["__GL_SYNC_TO_VBLANK"] = "1"
        # Set for recent linux Mesa DRI Radeon
        os.environ["LIBGL_SYNC_REFRESH"] = "1"
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
