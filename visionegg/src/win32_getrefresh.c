#include <WINDOWS.H>

int getrefresh() {
  DEVMODE DevMode;

  DevMode.dmDriverExtra = 0;
  if (EnumDisplaySettings(NULL,ENUM_CURRENT_SETTINGS,&DevMode)) {
    return DevMode.dmDisplayFrequency;
  } else {
    return 0;
  }
}
