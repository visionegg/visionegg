# This file was created automatically by SWIG.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.
import _posix_maxpriority
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


SCHED_RR = _posix_maxpriority.SCHED_RR
SCHED_FIFO = _posix_maxpriority.SCHED_FIFO
set_self_policy_priority = _posix_maxpriority.set_self_policy_priority

stop_memory_paging = _posix_maxpriority.stop_memory_paging

sched_get_priority_max = _posix_maxpriority.sched_get_priority_max


