#include <WINDOWS.H>

double getrefresh() {
  DEVMODE DevMode;

  DevMode.dmDriverExtra = 0;
  if (EnumDisplaySettings(NULL,ENUM_CURRENT_SETTINGS,&DevMode)) {
    return (double)DevMode.dmDisplayFrequency;
  } else {
    return 0;
  }
}
