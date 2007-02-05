/* This file modified from the original distribution available at
   http://www.compuphase.com/vretrace.htm */

#include <windows.h>

HANDLE LoadDriver(LPSTR DriverName)
{
  OSVERSIONINFO VerInfo;
  char          DevicePath[64];

  // Check operating system
  VerInfo.dwOSVersionInfoSize = sizeof(OSVERSIONINFO);
  GetVersionEx(&VerInfo);
  if (VerInfo.dwPlatformId == VER_PLATFORM_WIN32_NT) {

    wsprintf(DevicePath, "\\\\.\\%s", (LPSTR)DriverName);
    return CreateFile(DevicePath,
                      GENERIC_READ | GENERIC_WRITE,
                      FILE_SHARE_READ | FILE_SHARE_WRITE,
                      0,                     // Default security
                      OPEN_EXISTING,
                      FILE_FLAG_OVERLAPPED,  // Perform asynchronous I/O
                      0);                    // No template

  } else {

    // Otherwise, assume Windows95/98
    wsprintf(DevicePath, "\\\\.\\%s.vxd", (LPSTR)DriverName);
    return CreateFile(DevicePath, 0,0,0,
                      CREATE_NEW,
                      FILE_FLAG_DELETE_ON_CLOSE | FILE_FLAG_OVERLAPPED, 0);
  }
}
