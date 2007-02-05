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
            if swig_version.find('SWIG Version 1.3.24') != 0:
                raise RuntimeError( "Wrong SWIG version: %s" % (swig_version,) )
else:
    print "WARNING: Error checking SWIG version"
        
swig_src_dir = os.path.split(sys.argv[0])[0]
if swig_src_dir: # the above returns '' if we're in it on Python2.1
    os.chdir(swig_src_dir)

interfaces = ["darwin_getrefresh",
              "gl_qt",
              "posix_maxpriority",
              "win32_getrefresh",
              "win32_maxpriority",
              ]
product_suffixes = ["_wrap.c",
                    ".py"]
other_source_suffixes = [".m",
                         ".c",
                         ".h"]
for i in interfaces:
    interface_filename = i+".i"
    products = map(i.__add__,product_suffixes)
    other_sources = map(i.__add__,other_source_suffixes)
    mod_time = os.stat(interface_filename)[stat.ST_MTIME]
    must_rebuild = False
    found_any = False
    for product in products:
        if os.path.exists(product):
            found_any = True
            if os.stat(product)[stat.ST_MTIME] < mod_time:
                must_rebuild = True
    if not found_any: must_rebuild = True
    if must_rebuild:
        sys_string = "%s -python %s"%(swig_command,interface_filename)
        print sys_string
        if 'commands' in globals().keys():
            status, output = commands.getstatusoutput(sys_string)
            if status != 0:
                print "ERROR:", output
                raise RuntimeError("SWIG error")
        else:
            print "WARNING: Cannot verify success of operation"
            os.system(sys_string)
    else:
        pass
    copy_files = products + other_sources
    for filename in copy_files:
        if not os.path.exists(filename):
            continue
        new_filename =  "../VisionEgg/"+filename
        if not os.path.exists(new_filename) or os.stat(new_filename)[stat.ST_MTIME] < os.stat(filename)[stat.ST_MTIME]:
            shutil.copy2(filename,new_filename) # copy2 preserves attributes
            print "copied %s to ../VisionEgg/"%filename
