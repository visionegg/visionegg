#!/usr/bin/env python
import os, shutil

interfaces = ["darwin_maxpriority",
              "win32_maxpriority",
              "posix_maxpriority"]
end_names = ["_wrap.c",
             ".py",
             ".c"]
for i in interfaces:
    sys_string = "swig -python %s.i"%i    
    print sys_string
    os.system(sys_string)
    for end_name in end_names:
        filename = i + end_name
        print "copying %s to ../src/"%filename
        shutil.copyfile(filename,"../src/"+filename)
