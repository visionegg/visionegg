# The Vision Egg: PlatformDependent
#
# Copyright (C) 2001-2003 Andrew Straw.
# Copyright (C) 2008 California Institute of Technology
#
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""
Implementations of functions which vary by platform.

"""

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import logging

import sys, os
import VisionEgg
import VisionEgg.Core

import VisionEgg.GL as gl # get all OpenGL stuff in one namespace

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

    logger = logging.getLogger('VisionEgg.PlatformDependent')
    params = {}

    # set variable in local namespace
    for word in parse_me:
        # set the value from VisionEgg.config
        config_name = "VISIONEGG_"+word.upper()
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

            logger.info("Setting max priority mode for darwin platform "
                        "using conventional priority %d."%(
                        params['darwin_conventional_priority'],))

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
            logger.info("Setting max priority mode for darwin platform "
                        "using realtime threads. ( period = %d / %d, "
                        "computation = %d / %d, constraint = %d / %d, "
                        "preemptible = %d )" % (
                        bus_speed, params['darwin_realtime_period_denom'],
                        bus_speed, params['darwin_realtime_computation_denom'],
                        bus_speed, params['darwin_realtime_constraint_denom'],
                        params['darwin_realtime_preemptible'] ))
            period = bus_speed / params['darwin_realtime_period_denom']
            computation = bus_speed / params['darwin_realtime_computation_denom']
            constraint = bus_speed / params['darwin_realtime_constraint_denom']
            preemptible = params['darwin_realtime_preemptible']

            darwin_maxpriority.set_self_thread_time_constraint_policy( period, computation, constraint, preemptible )
    elif sys.platform == 'win32':
        import win32_maxpriority
        logger.info("Setting priority for win32 platform to "
                    "HIGH_PRIORITY_CLASS, THREAD_PRIORITY_HIGHEST. "
                    "(This is Microsoft's maximum recommended priority, "
                    "but you could still raise it higher.)")
        win32_maxpriority.set_self_process_priority_class(
            win32_maxpriority.HIGH_PRIORITY_CLASS )
        win32_maxpriority.set_self_thread_priority(
            win32_maxpriority.THREAD_PRIORITY_HIGHEST)

    elif sys.platform.startswith('irix') or sys.platform.startswith('linux') or sys.platform.startswith('posix'):
        import posix_maxpriority
        policy = posix_maxpriority.SCHED_FIFO
        max_priority = posix_maxpriority.sched_get_priority_max( policy )
        logger.info("Setting priority for POSIX-compatible platform to "
                    "policy SCHED_FIFO and priority to "
                    "%d"%max_priority)
        posix_maxpriority.set_self_policy_priority( policy, max_priority ) # Fails if you don't have permission (try running as root)
        posix_maxpriority.stop_memory_paging()
    else:
        raise RuntimeError("Cannot change priority.  Unknown platform '%s'"%sys.platform)

def linux_but_unknown_drivers():
    """Warn that platform is linux, but drivers not known."""
    # If you've added support for other drivers to sync with VBLANK under
    # linux, please let me know how!
    logger = logging.getLogger('VisionEgg.PlatformDependent')
    logger.warning("Could not sync buffer swapping to vblank because "
                   "you are running linux but not known/supported "
                   "drivers (only nVidia and recent Mesa DRI Radeon "
                   "currently supported).")

def sync_swap_with_vbl_pre_gl_init():
    """Try to synchronize buffer swapping and vertical retrace before starting OpenGL."""
    success = 0
    if sys.platform.startswith("linux"):
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
    elif sys.platform.startswith("irix"):
        # I think this is set using the GLX swap_control SGI
        # extension.  A C extension could be to be written to change
        # this value. (It probably cannot be set through an OpenGL
        # extension or an SDL/pygame feature.)
        logger = logging.getLogger('VisionEgg.PlatformDependent')
        logger.info("IRIX platform detected, assuming retrace sync.")
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
                logger = logging.getLogger('VisionEgg.PlatformDependent')
                logger.warning("Failed trying to synchronize buffer "
                               "swapping on darwin: %s: %s"%(str(x.__class__),str(x)))
    except:
        pass

    return success

def query_refresh_rate(screen):
    if sys.platform == 'win32':
        import win32_getrefresh
        return win32_getrefresh.getrefresh()
    elif sys.platform == 'darwin':
        import darwin_getrefresh
        return darwin_getrefresh.getrefresh()
    else:
        raise NotImplementedError("Platform dependent code to query frame rate not implemented on this platform.")

def attempt_to_load_multitexturing():
    """Attempt to load multitexturing functions and constants.

    Inserts the results into the gl module, which makes them globally
    available."""
    logger = logging.getLogger('VisionEgg.PlatformDependent')
    try:
        import ctypes
        if sys.platform.startswith('linux'):
            libGL = ctypes.cdll.LoadLibrary('/usr/lib/libGL.so')
        elif sys.platform == 'win32':
            libGL = ctypes.cdll.LoadLibrary('opengl32.dll')
        else:
            raise NotImplementedError("ctypes support not added for this platform")

        # make sure libGL has the appropriate functions
        libGL.glGetString.restype = ctypes.c_char_p
        vers = libGL.glGetString( ctypes.c_int( gl.GL_VERSION ) )
        logger.debug("ctypes loaded OpenGL %s"%vers)

        gl.glActiveTexture = libGL.glActiveTexture
        gl.glActiveTexture.argtypes = [ctypes.c_int]

        gl.glMultiTexCoord2f = libGL.glMultiTexCoord2f
        gl.glMultiTexCoord2f.argtypes = [ctypes.c_int, ctypes.c_float, ctypes.c_float]

        # assign constants found by looking at gl.h
        gl.GL_TEXTURE0 = 0x84C0
        gl.GL_TEXTURE1 = 0x84C1

        logger.debug("ctypes loaded OpenGL library and multitexture names "
                     "are present.  Workaround appears successful. ")
    except Exception, x:
        logger.debug("ctypes loading of OpenGL library failed %s: "
                     "%s"%(x.__class__, str(x)))

        if VisionEgg.Core.init_gl_extension('ARB','multitexture'):
            # copy from extenstion
            gl.glActiveTexture = gl.glActiveTextureARB
            gl.glMultiTexCoord2f = gl.glMultiTexCoord2fARB
            gl.GL_TEXTURE0 = gl.GL_TEXTURE0_ARB
            gl.GL_TEXTURE1 = gl.GL_TEXTURE1_ARB
            logger.debug("loaded multitexturing ARB extension")
        else:
            logger.warning("multitexturing not available after trying "
                           "ctypes and the OpenGL ARB extension. Some "
                           "features will not be available")

