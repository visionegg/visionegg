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

def sync_swap_with_vbl(failure_ok = 0):
    """Synchronize buffer swapping and vertical retrace, if possible."""
    success = 0
    if sys.platform == "linux2":
        # Unfotunately, cannot check do glGetString(GL_VENDOR) to
        # check if drivers are nVidia because we have to do this
        # before the drivers are started...
        
        # Assume drivers are nVidia
        VisionEgg.Core.add_gl_assumption("GL_VENDOR","nvidia","Failed assumption made in PlatformDependent.py function sync_swap_with_vbl()")
#        print "Assuming nVidia OpenGL drivers in PlatformDependent.py"
        os.environ["__GL_SYNC_TO_VBLANK"] = "1"
        success = 1
        
    elif sys.platform == "win32":
##        import OpenGL.WGL.EXT.swap_control
##        OpenGL.WGL.EXT.swap_control.wglInitSwapControlARB()
##        OpenGL.WGL.EXT.swap_control.wglSwapIntervalEXT(1)
        success = 1

    if not success:
        if failure_ok:
            print "Failed to synchronize buffer swapping and vertical retrace"
        else:
            raise VisionEgg.Core.EggError("Failed to synchronize buffer swapping and vertical retrace")
