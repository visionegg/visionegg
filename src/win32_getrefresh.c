#include <WINDOWS.H>

#ifndef ENUM_CURRENT_SETTINGS 
#define ENUM_CURRENT_SETTINGS       ((DWORD)-1) 
#endif

double getrefresh() {
  DEVMODE DevMode;

  DevMode.dmDriverExtra = 0;
  if (EnumDisplaySettings(NULL,ENUM_CURRENT_SETTINGS,&DevMode)) {
    return (double)DevMode.dmDisplayFrequency;
  } else {
    return 0;
  }
}
