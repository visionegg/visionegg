# This file was created automatically by SWIG.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.
import _win32_maxpriority
def _swig_setattr(self,class_type,name,value):
    if (name == "this"):
        if isinstance(value, class_type):
            self.__dict__[name] = value.this
            if hasattr(value,"thisown"): self.__dict__["thisown"] = value.thisown
            del value.thisown
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    self.__dict__[name] = value

def _swig_getattr(self,class_type,name):
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0


IDLE_PRIORITY_CLASS = _win32_maxpriority.IDLE_PRIORITY_CLASS
BELOW_NORMAL_PRIORITY_CLASS = _win32_maxpriority.BELOW_NORMAL_PRIORITY_CLASS
NORMAL_PRIORITY_CLASS = _win32_maxpriority.NORMAL_PRIORITY_CLASS
ABOVE_NORMAL_PRIORITY_CLASS = _win32_maxpriority.ABOVE_NORMAL_PRIORITY_CLASS
HIGH_PRIORITY_CLASS = _win32_maxpriority.HIGH_PRIORITY_CLASS
REALTIME_PRIORITY_CLASS = _win32_maxpriority.REALTIME_PRIORITY_CLASS
THREAD_PRIORITY_IDLE = _win32_maxpriority.THREAD_PRIORITY_IDLE
THREAD_PRIORITY_LOWEST = _win32_maxpriority.THREAD_PRIORITY_LOWEST
THREAD_PRIORITY_BELOW_NORMAL = _win32_maxpriority.THREAD_PRIORITY_BELOW_NORMAL
THREAD_PRIORITY_NORMAL = _win32_maxpriority.THREAD_PRIORITY_NORMAL
THREAD_PRIORITY_ABOVE_NORMAL = _win32_maxpriority.THREAD_PRIORITY_ABOVE_NORMAL
THREAD_PRIORITY_HIGHEST = _win32_maxpriority.THREAD_PRIORITY_HIGHEST
THREAD_PRIORITY_TIME_CRITICAL = _win32_maxpriority.THREAD_PRIORITY_TIME_CRITICAL
set_self_process_priority_class = _win32_maxpriority.set_self_process_priority_class

set_self_thread_priority = _win32_maxpriority.set_self_thread_priority


