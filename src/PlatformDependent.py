import sys,os,string
import VisionEgg.Core

############# Import Vision Egg C routines, if they exist #############
try:
    from _maxpriority import *                  # pickup set_realtime() function
except:
    def set_realtime():
        """Fake function definition.  Your system doesn't support the real function.
        """
        pass
    
try:
    from _dout import *
except:
    def toggle_dout():
        """Fake function definition.  Your system doesn't support the real function.
        """
        pass
    def set_dout(dummy_argument):
        """Fake function definition.  Your system doesn't support the real function.
        """
        pass

def sync_swap_with_vbl_pre_gl_init():
    """Synchronize buffer swapping and vertical retrace, if possible."""
    success = 0
    if sys.platform == "linux2":
        # Unfotunately, cannot check do glGetString(GL_VENDOR) to
        # check if drivers are nVidia because we have to do that requires
        # OpenGL context started, but this variable must be set
        # before OpenGL context started!
        
        # Assume drivers are nVidia
        VisionEgg.Core.add_gl_assumption("GL_VENDOR","nvidia","Failed assumption made in PlatformDependent.py function sync_swap_with_vbl()")
        # Set nVidia linux environmental variable
        os.environ["__GL_SYNC_TO_VBLANK"] = "1"
        success = 1
        
    return success

def sync_swap_with_vbl_post_gl_init():
    """Synchronize buffer swapping and vertical retrace, if possible."""
    success = 0
    try:
        if sys.platform == "win32":
            import OpenGL.WGL.EXT.swap_control
            if OpenGL.WGL.EXT.swap_control.wglInitSwapControlARB(): # Returns 1 if it's working
                OpenGL.WGL.EXT.swap_control.wglSwapIntervalEXT(1) # Swap only at frame syncs
                if OpenGL.WGL.EXT.swap_control.wglGetSwapIntervalEXT() == 1:
                    success = 1
    except:
        pass
    
    return success
