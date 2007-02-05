/* This file from the original distribution available at
   http://www.compuphase.com/vretrace.htm */

;/*`........................... assembly language ...................
;
; Constants
;

; #define CTL_CODE( DeviceType, Function, Method, Access ) (                 \
;     ((DeviceType) << 16) | ((Access) << 14) | ((Function) << 2) | (Method) \
; )
;
; #define METHOD_BUFFERED                 0
; #define METHOD_IN_DIRECT                1
; #define METHOD_OUT_DIRECT               2
; #define METHOD_NEITHER                  3
;
; #define FILE_ANY_ACCESS                 0
; #define FILE_READ_ACCESS          ( 0x0001 )    // file & pipe
; #define FILE_WRITE_ACCESS         ( 0x0002 )    // file & pipe


METHOD_BUFFERED     EQU   0t
METHOD_IN_DIRECT    EQU   1t
METHOD_OUT_DIRECT   EQU   2t
METHOD_NEITHER      EQU   3t
FILE_ANY_ACCESS     EQU   0t
FILE_READ_ACCESS    EQU   000000001h
FILE_WRITE_ACCESS   EQU   000000002h

VR_TYPE                 EQU   00000c000h

IOCTL_CLOSE_HANDLE      EQU   -1
IOCTL_OPEN_HANDLE       EQU   0

IOCTL_VRETRACE_VERSION  EQU   0c0002000h
IOCTL_VRETRACE_TEST     EQU   0c0002004h
IOCTL_VRETRACE_WAIT     EQU   0c0002008h

VRETRACE_WAIT_INSIDE    EQU   0
VRETRACE_WAIT_START     EQU   1
VRETRACE_WAIT_END       EQU   2

 comment `..................... C language ......................... */

#if !defined _NTDDK_
  #include <winioctl.h>
#endif

// Driver names, add extensions .VXD and .SYS for the filenames
#define VRETRACE_NAME   "VRETRACE"

// Device type --- in the "User Defined" range."
#define VR_TYPE             0xc000

// IOCTL commands for both the VxD and the Kernel Mode driver
//      IOCTL_CLOSE_HANDLE            // predefined for VxDs at -1
//      IOCTL_OPEN_HANDLE             // predefined for VxDs at 0
        // get the version of the driver
#define IOCTL_VRETRACE_VERSION  CTL_CODE(VR_TYPE, 0x0800, METHOD_BUFFERED, FILE_ANY_ACCESS)
        // check whether Vertical Retrace is available
#define IOCTL_VRETRACE_TEST     CTL_CODE(VR_TYPE, 0x0801, METHOD_BUFFERED, FILE_ANY_ACCESS)            // test if vertical retraces are supported
        // wait for vertical retrace
#define IOCTL_VRETRACE_WAIT     CTL_CODE(VR_TYPE, 0x0802, METHOD_BUFFERED, FILE_ANY_ACCESS)

enum {
  VRETRACE_WAIT_INSIDE,
  VRETRACE_WAIT_START,
  VRETRACE_WAIT_END
};

//`........................... END .................................
