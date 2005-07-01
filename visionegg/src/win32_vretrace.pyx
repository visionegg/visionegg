# emacs, this is -*-Python-*- mode

# See http://www.compuphase.com/vretrace.htm

cdef extern from "windows.h":
    ctypedef void* HANDLE
    ctypedef void* LPVOID
    ctypedef char* LPSTR
    ctypedef int BOOL
    ctypedef int DWORD
    ctypedef DWORD* LPDWORD
    ctypedef void* LPOVERLAPPED
    ctypedef int size_t
    
    cdef HANDLE INVALID_HANDLE_VALUE
    cdef size_t sizeof(DWORD)
    cdef BOOL DeviceIoControl(HANDLE, DWORD, LPVOID, DWORD,
                              LPVOID, DWORD, LPDWORD, LPOVERLAPPED)
    #int, void*, size_t, void*, size_t, void*, size_t)
    cdef void CloseHandle(HANDLE)
                         
cdef extern from "win32_load_driver.h":
    HANDLE LoadDriver(LPSTR DriverName)

cdef extern from "win32_vretrace_orig.h":
    cdef char * VRETRACE_NAME # "VRETRACE"
    cdef int IOCTL_VRETRACE_VERSION
    cdef int IOCTL_VRETRACE_TEST
    cdef int IOCTL_VRETRACE_WAIT
    
    cdef DWORD VRETRACE_WAIT_INSIDE
    cdef DWORD VRETRACE_WAIT_START
    cdef DWORD VRETRACE_WAIT_END

# some constants
WAIT_INSIDE = VRETRACE_WAIT_INSIDE
WAIT_START = VRETRACE_WAIT_START
WAIT_END = VRETRACE_WAIT_END
    
cdef class VRetraceHandleKeeper:
    cdef HANDLE VRetrace_Handle

def LoadVRetraceDriver():
    cdef BOOL success
    cdef HANDLE VRetrace_Handle
    cdef DWORD dwVersion
    cdef DWORD dwCycles, dwRetCount, dwReturned
    cdef VRetraceHandleKeeper hk
    
    VRetrace_Handle = LoadDriver(VRETRACE_NAME)
    if VRetrace_Handle == INVALID_HANDLE_VALUE:
        raise RuntimeError('Could not load driver VRETRACE.SYS')

    # check the version (should be non-zero)
    dwVersion = 0
    success = DeviceIoControl(VRetrace_Handle, IOCTL_VRETRACE_VERSION,
                              NULL, 0,
                              &dwVersion, sizeof(dwVersion),
                              &dwReturned, NULL)

    if not success or dwVersion < 0x100:
        CloseHandle(VRetrace_Handle)
        raise RuntimeError('Invalid version (%lx) returned'%dwVersion)
    
    # if we got the vertical retrace driver, check whether the video
    # card vertical retraces at all
    dwCycles = 0
    success = DeviceIoControl(VRetrace_Handle, IOCTL_VRETRACE_TEST,
                              &dwCycles, sizeof(dwCycles),
                              &dwRetCount, sizeof(dwRetCount),
                              &dwReturned, NULL);

    if not success or dwRetCount == 0:
        CloseHandle(VRetrace_Handle)
        raise RuntimeError('No vertical retrace detected')

    # return the handle for later use
    hk = VRetraceHandleKeeper()
    hk.VRetrace_Handle = VRetrace_Handle
    return hk

def WaitForRetrace(wait_start=WAIT_START):
    """Wait for a vertical retrace signal

    Arguments:
    wait_start -- if true, will wait for the next retrace if one is already active

    """
    
    cdef DWORD dwWaitCode, dwReturned
    global hk
    
    dwWaitCode = wait_start
    DeviceIoControl(hk.VRetrace_Handle, IOCTL_VRETRACE_WAIT,
                    &dwWaitCode,
                    sizeof(dwWaitCode),
                    NULL, 0,
                    &dwReturned, NULL)

cdef VRetraceHandleKeeper hk
hk = LoadVRetraceDriver() # initialize driver and keep handle to it

