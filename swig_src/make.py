#!/usr/bin/env python
import os, shutil, sys, stat

# This works on swig == 1.3.17 (And not on swig == 1.3.13).
# Check for swig version if possible
try:
    import commands
except:
    print "Unable to check for proper SWIG version because the commands module did not load."

swig_command = "swig"

if len(sys.argv) > 1:
    swig_command = sys.argv[1]

if 'commands' in globals().keys():
    status, output = commands.getstatusoutput(swig_command + " -version")
    if status != 0:
        print "WARNING: Error checking SWIG version"
    else:
        swig_version = output.split('\n')[1]
        if swig_version.find('SWIG Version 1.3.17') != 0:
            raise RuntimeError( "Wrong SWIG version: %s" % (swig_version,) )
else:
    print "WARNING: Error checking SWIG version"
        
swig_src_dir = os.path.split(sys.argv[0])[0]
if swig_src_dir: # the above returns '' if we're in it on Python2.1
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
    sys_string = "%s -python %s.i"%(swig_command,i)
    print sys_string
    if 'commands' in globals().keys():
        status, output = commands.getstatusoutput(sys_string)
        if status != 0:
            print "ERROR:", output
            raise RuntimeError("SWIG error")
    else:
        print "WARNING: Cannot verify success of operation"
        os.system(sys_string)
    for end_name in end_names:
        filename = i + end_name
        new_filename =  "../src/"+filename
        try:
#            if os.stat(filename)[stat.ST_MTIME] > os.stat(new_filename)[stat.ST_MTIME]:
             shutil.copyfile(filename,new_filename)
             print "copied %s to ../src/"%filename
        except:
            pass
