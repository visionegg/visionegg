#emacs, this is -*-Python-*- mode
# Copyright (C) 2005-2006 California Institute of Technology
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL).

cimport darwinsys # for exported symbols

cdef extern from "darwinsys_compat.h":
    ctypedef int id_t

cdef extern from "Python.h":
    cdef object PyErr_SetFromErrno(object)

cdef extern from "stdlib.h":
    ctypedef int size_t
    cdef void* memset(void*, int, size_t)

cdef extern from "errno.h":
    cdef int errno

cdef extern from "sys/sysctl.h":
    cdef int CTL_HW
    cdef int HW_BUS_FREQ
    ctypedef unsigned int u_int
    cdef int sysctl(int *, u_int, void*, size_t*, void*, size_t)

cdef extern from "mach/mach.h":
    ctypedef unsigned int uint32_t
    ctypedef int boolean_t
    cdef struct thread_time_constraint_policy:
        uint32_t period
        uint32_t computation
        uint32_t constraint
        boolean_t preemptible
    ctypedef thread_time_constraint_policy thread_time_constraint_policy_data_t
    ctypedef thread_time_constraint_policy* thread_time_constraint_policy_t
    cdef int THREAD_TIME_CONSTRAINT_POLICY
    cdef size_t THREAD_TIME_CONSTRAINT_POLICY_COUNT
    ctypedef int kern_return_t
    ctypedef int thread_act_t
    ctypedef int thread_policy_flavor_t
    ctypedef int integer_t
    ctypedef integer_t* thread_policy_t
    ctypedef int mach_msg_type_number_t
    cdef kern_return_t thread_policy_set( thread_act_t,
                                          thread_policy_flavor_t,
                                          thread_policy_t,
                                          mach_msg_type_number_t)
    ctypedef int mach_port_t
    cdef mach_port_t mach_task_self()
    cdef mach_port_t mach_thread_self()

cdef extern from "sched.h":
    cdef struct sched_param:
        int sched_priority

cdef extern from "pthread.h":
    ctypedef int pthread_t
    cdef pthread_t pthread_self()
    cdef int pthread_setschedparam(pthread_t thread, 
                                   int policy,
                                   sched_param *)
    
# export symbols to Python
PRIO_PROCESS = darwinsys.PRIO_PROCESS

SCHED_OTHER = darwinsys.SCHED_OTHER
SCHED_RR = darwinsys.SCHED_RR
SCHED_FIFO = darwinsys.SCHED_FIFO

def get_bus_speed():
    cdef int bus_speed
    cdef int mlib[2]
    cdef size_t len
    
    mlib[0] = CTL_HW
    mlib[1] = HW_BUS_FREQ
    
    len = sizeof(bus_speed)
    sysctl(mlib, 2, &bus_speed, &len, NULL, 0)

    return bus_speed

def set_self_thread_time_constraint_policy( period,
                                            computation,
                                            constraint,
                                            preemptible ):
    
    cdef thread_time_constraint_policy_data_t ttcpolicy
    
    ttcpolicy.period = period
    ttcpolicy.computation = computation
    ttcpolicy.constraint = constraint
    ttcpolicy.preemptible = preemptible

    return thread_policy_set( mach_thread_self(),
                              THREAD_TIME_CONSTRAINT_POLICY,
                              <thread_policy_t>&ttcpolicy,
                              THREAD_TIME_CONSTRAINT_POLICY_COUNT)

def set_self_pthread_priority( policy, priority ):
    cdef sched_param sp

    memset(&sp,0,sizeof(sched_param))
    sp.sched_priority=priority
    return pthread_setschedparam(pthread_self(), policy, &sp)

def getpriority(arg0,arg1):
    cdef int result
    errno=0
    result = darwinsys.getpriority(arg0,arg1)
    if errno:
        PyErr_SetFromErrno(OSError)    
    return result

def sched_get_priority_max( arg0 ):
    cdef int result
    errno=0
    result = darwinsys.sched_get_priority_max(arg0)
    if errno:
        PyErr_SetFromErrno(OSError)    
    return result

def setpriority(arg0, arg1, arg2):
    cdef int result
    errno=0
    result = darwinsys.setpriority(arg0,arg1,arg2)
    if errno:
        PyErr_SetFromErrno(OSError)    
    return result
