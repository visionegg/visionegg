# This file was created automatically by SWIG.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.
import _darwin_maxpriority
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


PRIO_PROCESS = _darwin_maxpriority.PRIO_PROCESS
SCHED_OTHER = _darwin_maxpriority.SCHED_OTHER
SCHED_RR = _darwin_maxpriority.SCHED_RR
SCHED_FIFO = _darwin_maxpriority.SCHED_FIFO
get_bus_speed = _darwin_maxpriority.get_bus_speed

set_self_thread_time_constraint_policy = _darwin_maxpriority.set_self_thread_time_constraint_policy

set_self_pthread_priority = _darwin_maxpriority.set_self_pthread_priority

getpriority = _darwin_maxpriority.getpriority

setpriority = _darwin_maxpriority.setpriority

sched_get_priority_max = _darwin_maxpriority.sched_get_priority_max

cvar = _darwin_maxpriority.cvar

