# This allows .pyz files to be loaded
# (Used in McMillan Installer applications.)

import os
import sys

home = os.path.dirname(sys.executable)
os.chdir(home)
sys.path.append('common.pyz')
