#!/bin/sh
if test ! -n "$PYTHON"; then
  echo "Specify which python with the PYTHON environment variable"
  exit 1
fi

$PYTHON pydoc.py -w VisionEgg
$PYTHON pydoc.py -w VisionEgg.Configuration
$PYTHON pydoc.py -w VisionEgg.Core
$PYTHON pydoc.py -w VisionEgg.Daq
$PYTHON pydoc.py -w VisionEgg.DaqLPT
$PYTHON pydoc.py -w VisionEgg.DaqOverTCP
$PYTHON pydoc.py -w VisionEgg.Deprecated
$PYTHON pydoc.py -w VisionEgg.Dots
$PYTHON pydoc.py -w VisionEgg.FlowControl
$PYTHON pydoc.py -w VisionEgg.GL
$PYTHON pydoc.py -w VisionEgg.GLTrace
$PYTHON pydoc.py -w VisionEgg.GUI
$PYTHON pydoc.py -w VisionEgg.Gratings
$PYTHON pydoc.py -w VisionEgg.Lib3DS
$PYTHON pydoc.py -w VisionEgg.MoreStimuli
$PYTHON pydoc.py -w VisionEgg.ParameterTypes
$PYTHON pydoc.py -w VisionEgg.PlatformDependent
$PYTHON pydoc.py -w VisionEgg.PyroApps
$PYTHON pydoc.py -w VisionEgg.PyroApps.ColorCalGUI
$PYTHON pydoc.py -w VisionEgg.PyroApps.ColorCalServer
$PYTHON pydoc.py -w VisionEgg.PyroApps.EPhysGUI
$PYTHON pydoc.py -w VisionEgg.PyroApps.EPhysGUIUtils
$PYTHON pydoc.py -w VisionEgg.PyroApps.EPhysServer
$PYTHON pydoc.py -w VisionEgg.PyroApps.FlatGratingGUI
$PYTHON pydoc.py -w VisionEgg.PyroApps.FlatGratingServer
$PYTHON pydoc.py -w VisionEgg.PyroApps.GridGUI
$PYTHON pydoc.py -w VisionEgg.PyroApps.GridServer
$PYTHON pydoc.py -w VisionEgg.PyroApps.MouseTargetGUI
$PYTHON pydoc.py -w VisionEgg.PyroApps.MouseTargetServer
$PYTHON pydoc.py -w VisionEgg.PyroApps.ScreenPositionGUI
$PYTHON pydoc.py -w VisionEgg.PyroApps.ScreenPositionServer
$PYTHON pydoc.py -w VisionEgg.PyroApps.SphereGratingGUI
$PYTHON pydoc.py -w VisionEgg.PyroApps.SphereGratingServer
$PYTHON pydoc.py -w VisionEgg.PyroApps.SpinningDrumGUI
$PYTHON pydoc.py -w VisionEgg.PyroApps.SpinningDrumServer
$PYTHON pydoc.py -w VisionEgg.PyroApps.TargetGUI
$PYTHON pydoc.py -w VisionEgg.PyroApps.TargetServer
$PYTHON pydoc.py -w VisionEgg.PyroClient
$PYTHON pydoc.py -w VisionEgg.PyroHelpers
$PYTHON pydoc.py -w VisionEgg.QuickTime
$PYTHON pydoc.py -w VisionEgg.SphereMap
$PYTHON pydoc.py -w VisionEgg.TCPController
$PYTHON pydoc.py -w VisionEgg.Text
$PYTHON pydoc.py -w VisionEgg.Textures
$PYTHON pydoc.py -w VisionEgg.ThreeDeeMath
$PYTHON pydoc.py -w VisionEgg.darwin_getrefresh
$PYTHON pydoc.py -w VisionEgg.darwin_maxpriority
$PYTHON pydoc.py -w VisionEgg.gl_qt
$PYTHON pydoc.py -w VisionEgg.posix_maxpriority
$PYTHON pydoc.py -w VisionEgg.py_logging
$PYTHON pydoc.py -w VisionEgg.win32_getrefresh.py
$PYTHON pydoc.py -w VisionEgg.win32_maxpriority