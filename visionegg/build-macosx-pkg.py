#!/usr/bin/env python

"""build-macosx-pkg.py - Build OS X packages for Vision Egg.

This requires you to have just done a "python setup.py bdist_dumb" and
the bdist_dumb_results variable below set to the .tar.gz file that
command produced.

This is based on buildpkg_0.2.py by Dinu C. Gherman, gherman@europemail.com

Author: Andrew Straw <astraw@users.sourceforge.net>

"""

import os, string, shutil, copy, tempfile
import setup # from local directory

pkg_name = "visionegg" # Must be short to deal with Stuffit Expander braindead-ness
default_location = "/Library/Frameworks/Python.framework/Versions/2.2"
bdist_dumb_results = "./dist/visionegg-%s.darwin-5.5-Power_Macintosh.tar.gz"%(setup.version,)

# Initial screen
welcome_txt = setup.long_description

# "Important Information"
readme_txt = """
This package installs the Vision Egg library and associated files, including the demos.

The files will be installed to %s. This is the default Python 2.2 framework directory. The system files will be in the subdirectory lib/python2.2/site-packages/VisionEgg and a master copy of the user files will be in the subdirectory VisionEgg.

A copy of the user files will be made to $HOME/VisionEgg, where $HOME means your home directory, usually /Users/<username>.  If this directory does not exist, it will be created.  If this directory exists, files already in this directory named identically to files in the Vision Egg distribution will be overwritten. A link to this directory named VisionEgg will be made on your Desktop, removing anything named VisionEgg already there.

This release exposes a few known bugs with Mac OS X versions of software that the Vision Egg depends on. Checkbuttons in dialog windows are broken until a button is pressed (Tk bug), and when not run in fullscreen mode application scripts quit with a false error "The application Python has unexpectedly quit." On some Macs, fullscreen mode is not working (pygame bug).

This package has the following dependencies, all of which can be downloaded as a single archive from the Vision Egg website http://www.visionegg.org

Python with frameworks
PyOpenGL (Python module)
pygame (Python module)
Python Imaging Library (Python module)
Numeric (Python module)
"""%(default_location,)
readme_txt = string.strip(readme_txt)

install_sh = """#!/bin/sh

echo "Running post-install script"

INSTALLDIR=%s

SCRIPTDIR=$INSTALLDIR/VisionEgg
LIBDIR=$INSTALLDIR/lib/python2.2/site-packages/VisionEgg

# Make a local user copy of the Vision Egg scripts
echo "Copying to ~/VisionEgg"
cp -p -r $SCRIPTDIR ~

# Make the local copies owned by the user
chown -R $USER ~/VisionEgg

# Make sure system directories owned by root (an Installer bug changes them to user on upgrade)
chown -R root:admin $SCRIPTDIR
chown -R root:admin $LIBDIR

# Create a link on the Desktop
ln -fhs ~/VisionEgg ~/Desktop

# Make the link owned by the user
#chown $USER ~/Desktop/VisionEgg

"""%(default_location,)

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
cmd = "tar -xvzf %s"%(bdist_dumb_results,)
os.system(cmd)
##cmd = "sudo chown -R root.admin *"
##os.system(cmd)
os.chdir(orig_dir)

pkg_source = os.path.join(bdist_dumb_dir,"Library/Frameworks/Python.framework/Versions/Current")

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

##os.chdir(bdist_dumb_dir)
##cmd = "sudo chown -R astraw *"
##os.system(cmd)
##os.chdir(orig_dir)

shutil.rmtree(bdist_dumb_dir)
