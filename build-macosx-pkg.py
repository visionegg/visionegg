#!/usr/bin/env python

"""build-macosx-pkg.py - Build OS X packages for Vision Egg.

This requires you to have just done a "python setup.py bdist_dumb" and
the bdist_dumb_results variable below set to the .tar.gz file that
command produced.

This is based on buildpkg_0.2.py by Dinu C. Gherman, gherman@europemail.com

Author: Andrew Straw <astraw@users.sourceforge.net>

"""

import os, string, shutil, copy, tempfile,sys, commands
import distutils.util
import setup # from local directory

if len(sys.argv) > 1:
    build_number = int(sys.argv[1])
else:
    build_number = 1

if sys.version.startswith("2.2"):
    py_version_short = "2.2"
elif sys.version.startswith("2.3"):
    py_version_short = "2.3"
else:
    raise RuntimeError("Build this with Python 2.2 or 2.3")

status, output = commands.getstatusoutput("sw_vers")
output_lines = output.split('\n')
mac_os_x_version = output_lines[1].split()[1]

# pkg_name must be short to deal with Stuffit Expander braindead-ness.
# The final number is a "build number" in case the packaging doesn't work.
pkg_name = "ve-%s-py%s-%d"%(setup.version,sys.version.split()[0],build_number)
if len(pkg_name + ".pkg.tar.gz") > 31:
    raise RuntimeError("Your package name will be too long for dumb Mac OS X apps")

framework_dir = "/Library/Frameworks/Python.framework"
current_link = os.path.join(framework_dir, "Versions" , "Current" )
default_location = "%s/Versions/%s"%(framework_dir,py_version_short)
if os.path.islink( current_link ):
    if os.path.realpath( current_link ) != default_location:
        raise RuntimeError("I think your current version of Python is not specied by %s"%(current_link,))
darwin_version = os.uname()[2]
bdist_dumb_results = "./dist/visionegg-%s.%s.tar.gz"%(setup.version,distutils.util.get_platform())
bdist_dumb_results = os.path.abspath(bdist_dumb_results)

# Initial screen
welcome_txt = setup.long_description

# "Important Information"
readme_txt = """
This package installs the Vision Egg library and associated files, including the demos.

The files will be installed to %s. This is the default Python %s framework directory. The system files will be in the subdirectory lib/python%s/site-packages/VisionEgg and a master copy of the user files will be in the subdirectory VisionEgg.

A copy of the user files will be made to /Applications/VisionEgg. Old files of the same name in this directory will be overwritten.

This release exposes a few known bugs with Mac OS X versions of software that the Vision Egg depends on.

This package has the following dependencies:

Mac OS X (built with %s, probably works with earlier versions)
Python %s Mac OS X framework build with Tkinter modules
PyOpenGL (Python module)
pygame (Python module)
Python Imaging Library (Python module)
Numeric (Python module)
Pyro (Python module) (optional)
"""%(default_location,py_version_short,
     py_version_short,
     mac_os_x_version,
     py_version_short)
readme_txt = string.strip(readme_txt)

install_sh = """#!/bin/sh

echo "Running post-install script"

INSTALLDIR=%s

SCRIPTDIR=$INSTALLDIR/VisionEgg
LIBDIR=$INSTALLDIR/lib/python%s/site-packages/VisionEgg

# Make sure system directories owned by root (an Installer bug changes them to user on upgrade)
chown -R root:admin $SCRIPTDIR
chown -R root:admin $LIBDIR

# Make a copy of the Vision Egg scripts in /Applications
echo "Copying to /Applications/VisionEgg"
cp -p -r $SCRIPTDIR /Applications
"""%(default_location,py_version_short)

post_install = """#!/bin/sh
# executed by Installer.app after installing the Vision Egg for the first time.

/bin/sh $1/install.sh
"""

post_upgrade = """#!/bin/sh
# executed by Installer.app after upgrading. (The Vision Egg was previously installed.)

/bin/sh $1/install.sh
"""

packageInfoDefaults = {
    'Title': None,
    'Version': None,
    'Description': '',
    'DefaultLocation': '/',
    'Diskname': '(null)',
    'DeleteWarning': '',
    'NeedsAuthorization': 'NO',
    'DisableStop': 'NO',
    'UseUserMask': 'YES',
    'OverwritePermissions' : 'NO',
    'Application': 'NO',
    'Relocatable': 'NO',
    'Required': 'NO',
    'InstallOnly': 'NO',
    'RequiresReboot': 'NO',
    'InstallFat': 'NO'}
    
PKG_INFO_FIELDS = """\
Title
Version
Description
DefaultLocation
Diskname
DeleteWarning
NeedsAuthorization
DisableStop
UseUserMask
OverwritePermissions
Application
Relocatable
Required
InstallOnly
RequiresReboot
InstallFat\
"""

pkg_name_pkg = pkg_name + ".pkg"
base_dir = os.path.split(setup.__file__)[0]
dist_dir = os.path.join(base_dir,"dist")

# Expand archive made by distutils bdist_dumb
orig_dir = os.path.abspath(os.curdir)
bdist_dumb_dir = "XXX_temp_dir_XXX"
os.mkdir(bdist_dumb_dir)
os.chdir(bdist_dumb_dir)
cmd = "tar -xvzf '%s'"%(bdist_dumb_results,)
print cmd
os.system(cmd)
##cmd = "sudo chown -R root.admin *"
##os.system(cmd)
os.chdir(orig_dir)

pkg_source = os.path.join(bdist_dumb_dir,"Library/Frameworks/Python.framework/Versions/%s"%py_version_short)

if not os.path.isdir(dist_dir):
    os.mkdir(dist_dir)
pkg_dir = os.path.join(dist_dir,pkg_name_pkg)

if os.path.isdir(pkg_dir):
    shutil.rmtree(pkg_dir)

os.mkdir(pkg_dir)

bom_file = os.path.abspath(os.path.join(pkg_dir,"%s.bom"%(pkg_name,)))
pax_file = os.path.abspath(os.path.join(pkg_dir,"%s.pax"%(pkg_name,)))
info_file = os.path.abspath(os.path.join(pkg_dir,"%s.info"%(pkg_name,)))
sizes_file = os.path.abspath(os.path.join(pkg_dir,"%s.sizes"%(pkg_name,)))
post_install_file = os.path.abspath(os.path.join(pkg_dir,"%s.post_install"%(pkg_name,)))
post_upgrade_file = os.path.abspath(os.path.join(pkg_dir,"%s.post_upgrade"%(pkg_name,)))
welcome_file = os.path.abspath(os.path.join(pkg_dir,"Welcome.txt"))
readme_file = os.path.abspath(os.path.join(pkg_dir,"ReadMe.txt"))
install_sh_file = os.path.abspath(os.path.join(pkg_dir,"install.sh"))

make_bom_command = string.join(["mkbom",pkg_source,bom_file])
print make_bom_command
if os.system(make_bom_command):
    print "Error, quitting"
    raise SystemExit
os.system("lsbom %s"%(bom_file,))

print "cd",pkg_source
os.chdir(pkg_source)
pax_command = string.join(["pax","-w","-f %s"%(os.path.abspath(pax_file),),"."])
print pax_command
if os.system(pax_command):
    print "Error, quitting"
    raise SystemExit
print "cd",orig_dir
os.chdir(orig_dir)
os.system("pax -f %s"%(pax_file,))

pkg_info = copy.deepcopy(packageInfoDefaults)
pkg_info['Title'] = setup.description
pkg_info['Version'] = setup.version
pkg_info['Description'] = "Vision Egg for Mac OS X (http://www.visionegg.org)"
pkg_info['DefaultLocation'] = default_location
pkg_info['NeedsAuthorization'] =  "YES"

info = ""
for f in string.split(PKG_INFO_FIELDS, "\n"):
    info = info + "%s %%(%s)s\n" % (f, f)
info = info % pkg_info

print "Writing %s"%(info_file,)
f= open(info_file,"w")
f.write(info)
f.close()

# Apple's Installer App doesn't seem to care too much about these values,
# so here is a quick and dirty way to get the info

print_files_cmd =  "lsbom -p s %s"%(bom_file,)
tmpname = tempfile.mktemp()
os.system(print_files_cmd + " > %s"%(tmpname,))
f=open(tmpname,"r")
results = f.readlines()
num_files = len(results)
sizes = map(string.strip,results)
sizes = map(int,string.split(string.strip(string.join(sizes))))
installed_size = 0
for size in sizes:
    installed_size += size

cmd = "gzip %s"%(pax_file,)
os.system(cmd)
zipped_size = os.stat(pax_file+".gz")[6]

print "Writing %s"%(sizes_file,)
f = open(sizes_file, "w")
format = "NumFiles %d\nInstalledSize %d\nCompressedSize %d"
f.write(format % (num_files, installed_size, zipped_size))

print "Writing %s"%(readme_file,)
f = open(readme_file, "w")
f.write(readme_txt)

print "Writing %s"%(welcome_file,)
f = open(welcome_file, "w")
f.write(welcome_txt)

print "Writing %s"%(install_sh_file,)
f = open(install_sh_file, "w")
f.write(install_sh)
f.close()
os.chmod(install_sh_file,0755)

print "Writing %s"%(post_install_file,)
f = open(post_install_file, "w")
f.write(post_install)
f.close()
os.chmod(post_install_file,0755)

print "Writing %s"%(post_upgrade_file,)
f = open(post_upgrade_file, "w")
f.write(post_upgrade)
f.close()
os.chmod(post_upgrade_file,0755)

shutil.rmtree(bdist_dumb_dir)
