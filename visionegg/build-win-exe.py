#!/usr/bin/env python
import string, os, glob
"""build-win-exe.py -- build .exe windows files

This is used to create the Win32 executable demo files.

Run this from a new directory, e.g.:

mkdir build-exe
cd build-exe
cp ../demo/*.py .
cp ../check-config.py .
../build-win-exe.py

This was written for Gordon McMillan's Installer Python scripts,
available from
http://www.mcmillan-inc.com/install1.html
"""

scripts_orig = glob.glob("*.py")
scripts = []
for script in scripts_orig:
    if script == "check-config.py":
        opts = ""
    else:
        opts = "--noconsole"
    scripts.append((script,opts))

python = "C:\Python22\python.exe"
makespec = "C:\cygwin\home\Administrator\other-peoples-src\installer5\Installer\Makespec.py"
build = "C:\cygwin\home\Administrator\other-peoples-src\installer5\Installer\Build.py"

output_dir = "sumo"
try:
    os.path.mkdir(output_dir)
except:
    pass

if not os.path.isdir(output_dir):
    raise RuntimeError("%s is not a directory, and couldn't create it"%(output_dir,))

for script, opts in scripts:
    print "================= BUILDING %s =================="%(script,)
    makespec_command = string.join([python,makespec,opts,script])
    #print makespec_command
    os.system(makespec_command)

    base_name = os.path.splitext(script)[0]
    spec_name = base_name + ".spec"
    if not os.path.isfile(spec_name):
        raise RuntimeError("%s is not a file."%(spec_name),)

    build_command = string.join([python,"-O",build,spec_name])
    #print build_command
    os.system(build_command)

    dist_dir = "dist" + base_name

    dist_file_glob = os.path.join(dist_dir,"*")
    dist_files = glob.glob(dist_file_glob)

    for dist_file in dist_files:
        output_name = os.path.join(output_dir,os.path.basename(dist_file))
        copy_command = string.join(["cp",dist_file,output_name])
        #print copy_command
        os.system(copy_command)
