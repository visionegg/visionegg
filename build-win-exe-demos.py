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
test/conform.py
test/display_dc_restoration.py
test/display_voltage_regulation.py
test/opengl_info.py
demo/alpha_texture.py
demo/az_el_grid.py
demo/color_grating.py
demo/convert3d_to_2d.py
demo/daq/simple_lpt_out.py
demo/daq/trigger_in.py
demo/daq/trigger_out.py
demo/displayText.py
demo/dots.py
demo/dots_simple_loop.py
demo/ephys_gui.py
demo/ephys_server.py
demo/flames_pygame.py
demo/flames_visionegg.py
demo/gabor.py
demo/gamma.py
demo/grating.py
demo/gratings_multi.py
demo/GUI/drumDemoGUI.py
demo/image_sequence_fast.py
demo/image_sequence_slow.py
demo/lib3ds-demo.py
demo/makeMovie.py
demo/makeMovie2.py
demo/mouse_gabor_2d.py
demo/mouse_gabor_perspective.py
demo/mouseTarget.py
demo/mouseTarget_user_loop.py
demo/movingPOV.py
demo/mpeg.py
demo/multi_stim.py
demo/plaid.py
demo/put_pixels.py
demo/pygame_texture.py
demo/Pyro/gratingPyroGUI.py
demo/Pyro/gratingPyroServer.py
demo/Pyro/metaPyroGUI.py
demo/Pyro/metaPyroGUI.pyc
demo/Pyro/metaPyroServer.py
demo/Pyro/simpleClient.py
demo/Pyro/simpleServer.py
demo/quicktime.py
demo/sphereMap.py
demo/target.py
demo/targetBackground.py
demo/tcp/gratingGUI.py
demo/tcp/gratingTCP.py
demo/texture.py
demo/textureDrum.py
demo/visual_jitter.py
""")

##scripts_orig = scripts_orig[:7]

scripts_orig = [ os.path.join( *x.split('/') ) for x in scripts_orig ]

per_file_extra_spec_lines = \
"""this_remove = []
for x in %(id)s.pure:
    if x[0].startswith('VisionEgg'):
        this_remove.append( x )
    elif x[0].startswith('OpenGL'):
        this_remove.append( x )
    elif x[0] == 'Tkinter':
        this_remove.append( x )
common = common + this_remove
%(id)s.pure = %(id)s.pure - this_remove
"""

### help generate list of files
##infile = 'demo/README.txt'
##infile_fd = open(infile,"r")
##fname = 'sumo_list.txt'
##fd = open(fname,"w")
##for line in infile_fd.readlines():
##    split_line = line.strip().split()
##    if not split_line:
##        continue
##    ft = split_line[0]
##    if ft.endswith('.py') or ft.endswith('.pyw'):
##        ft = ft.split('/')[-1]
##        new_name = os.path.splitext(ft)[0] + '.exe'
##        new_line = new_name+' '+' '.join(split_line[1:])+'\n'
##        fd.write(new_line)
##infile_fd.close()
##fd.close()

copy_list = string.split(r"""
data/az_el.png
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
    if script == "check-config.py" or script == r"demo\tcp\gratingGUI.py" \
           or script.startswith('test'):
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
sumo_buffer = """
common_modules = ['Tkinter','ConfigParser','Image','ImageFile',
    'Numeric','pickle','threading','traceback','warnings']

pyzsupport = Analysis(['pyz_support.py'],pathex=[])

common = TOC([])

"""

for script, opts in scripts:
    makespec_command = string.join([python,makespec,opts,script])
    print makespec_command
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
    spec = spec.replace('EXE(','EXE(pyzsupport.scripts,')
    spec = re_coll.sub("",spec)
    
    base_name = os.path.splitext(os.path.basename(script))[0]
    orig_build_dir = "build"+base_name
    spec = spec.replace(orig_build_dir,"build"+output_dir)

    extra = per_file_extra_spec_lines%locals()
    spec = spec.replace('pathex=[])','pathex=[])\n%s'%extra)
    sumo_buffer += spec

    os.remove(spec_name)

sumo_buffer += "common_pyz = PYZ(common,name='common.pyz')\n"
sumo_buffer += "coll = COLLECT(TkTree(),common_pyz,\n"
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
    if dest[-4:] in [".txt",".cfg"]:
        print "Converting newlines in %s"%(dest,)
        # convert newlines
        f = open(dest,"r")
        lines = f.readlines()
        f.close()
        f = open(dest,"w")
        f.write(string.join(lines,""))
        f.close()

print "************************"
print "don't forget to copy PyWinTypes22.dll into the sumo directory!"
