#!/usr/bin/env python
import string, os, glob, shutil, sys, fnmatch, tempfile, re
"""build_win_exe_demos.py -- build Windows binary demos.

This was written for Gordon McMillan's Installer Python scripts,
available from
http://www.mcmillan-inc.com/install1.html
"""

# Options
python = sys.executable
installer_dir = "C:\\Installer" # directory of Gordon McMillan's installer
if not os.path.isdir(installer_dir):
    raise RuntimeError("Can't find McMillan's Installer")
makespec = os.path.join(installer_dir,"Makespec.py")
build = os.path.join(installer_dir,"Build.py")

output_dir = "sumo"

# File list

scripts_orig = string.split(r"""
check-config.py
demo\displayText.py
demo\grating.py
demo\makeMovie.py
demo\mouseTarget.py
demo\movingPOV.py
demo\perspectiveGrating.py
demo\target.py
demo\targetBackground.py
demo\texture.py
demo\textureDrum.py
demo\tcp\gratingTCP.py
demo\tcp\gratingGUI.py
""")

copy_list = string.split(r"""
data/panorama.jpg
data/visionegg.bmp
VisionEgg.cfg
README-BINARY-DEMOS.txt
LICENSE.txt
CHANGELOG.txt
""")

# set options for each script
scripts = []
for script in scripts_orig:
    if script == "check-config.py":
        opts = "--tk --ascii"
    elif script == r"demo\tcp\gratingGUI.py":
        opts = "--tk --ascii"
    else:
        opts = "--noconsole --tk --ascii"
    scripts.append((script,opts))

re_id = re.compile(r"(\w+)")
re_a = re.compile(r"(^|\W)(a)(\W)")
re_pyz = re.compile(r"(^|\W)(pyz)(\W)")
re_exe = re.compile(r"(^|\W)(exe)([^'a-zA-Z0-9_])")
re_coll = re.compile(r"coll = .*\)\s*",re.DOTALL)

exes = []
binaries = []
sumo_buffer = ""
for script, opts in scripts:
    makespec_command = string.join([python,makespec,opts,script])
    os.system(makespec_command)

    base_name = os.path.splitext(os.path.basename(script))[0]
    spec_name = base_name+".spec"
    if not os.path.isfile(spec_name):
        raise RuntimeError("Did not generate specfile: %s is not a file."%(spec_name),)

    match = re_id.match(base_name)
    id = match.group(0)

    def replace_a_func(matchobj):
        a = matchobj.groups()
        return a[0]+id+a[2]

    def replace_pyz_func(matchobj):
        pyz = matchobj.groups()
        return pyz[0]+id+"_pyz"+pyz[2]

    def replace_exe_func(matchobj):
        exe = matchobj.groups()
        return exe[0]+id+"_exe"+exe[2]

    exes.append(id+"_exe")
    binaries.append(id+".binaries")
    spec_file = open(spec_name,"rb")
    spec = spec_file.read()
    spec_file.close()

    spec = re_a.sub(replace_a_func,spec)
    spec = re_pyz.sub(replace_pyz_func,spec)
    spec = re_exe.sub(replace_exe_func,spec)
    spec = re_coll.sub("",spec)
    
    base_name = os.path.splitext(os.path.basename(script))[0]
    orig_build_dir = "build"+base_name
    spec = string.replace(spec,orig_build_dir,"build"+output_dir)

    sumo_buffer += spec
    os.remove(spec_name)

sumo_buffer += "coll = COLLECT(TkTree(),\n"
for i in range(len(exes)):
    sumo_buffer += "       "+exes[i]+", "+binaries[i]+",\n"
sumo_buffer += "      name='%s')\n"%(output_dir,)

sumo_file = open("sumo.spec","wb")
sumo_file.write(sumo_buffer)
sumo_file.close()

command = string.join([python,"-O",build,"sumo.spec"])
print command
os.system(command)

for file in copy_list:
    dir,name = os.path.split(file)
    dest = output_dir
    if dir:
        dest = os.path.join(output_dir,dir)
        if not os.path.isdir(dest):
            os.makedirs(dest)
    dest = os.path.join(dest,name)
    if file == "README-BINARY-DEMOS.txt": # Rename file
        dest = os.path.join(os.path.split(dest)[0],"README.txt")
    shutil.copy2(file,dest)
    if dest[-4:] == ".txt":
        print "Converting newlines in %s"%(dest,)
        # convert newlines
        f = open(dest,"r")
        lines = f.readlines()
        f.close()
        f = open(dest,"w")
        f.write(string.join(lines,""))
        f.close()
