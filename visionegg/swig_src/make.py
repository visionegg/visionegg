#!/usr/bin/env python
import os, shutil, sys

swig_src_dir = os.path.split(sys.argv[0])[0]
os.chdir(swig_src_dir)

interfaces = ["darwin_app_stuff",
              "darwin_maxpriority",
              "win32_maxpriority",
              "posix_maxpriority"]
end_names = ["_wrap.c",
             ".py",
             ".m",
             ".c"]
for i in interfaces:
    sys_string = "swig -python %s.i"%i    
    print sys_string
    os.system(sys_string)
    for end_name in end_names:
        filename = i + end_name
        try:
            shutil.copyfile(filename,"../src/"+filename)
            print "copied %s to ../src/"%filename
        except:
            pass
