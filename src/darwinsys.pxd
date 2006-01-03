#emacs, this is -*-Python-*- mode

cdef extern from "sys/resource.h":
    cdef int PRIO_PROCESS
    cdef int getpriority(int, id_t)
    cdef int setpriority( int, id_t, int )
    cdef int sched_get_priority_max(int)

cdef extern from "pthread.h":
    cdef int SCHED_OTHER
    cdef int SCHED_RR
    cdef int SCHED_FIFO
