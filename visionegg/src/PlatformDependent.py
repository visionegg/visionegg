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
