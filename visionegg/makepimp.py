#!/usr/bin/env python
import imp
import os
import sys
import distutils.util
import tarfile
import gzip
import md5
from plistlib import Plist

debug = True

HTTPBASE = 'http://osdn.dl.sourceforge.net/sourceforge/visionegg/'
UPLOADCMD = 'echo "upload %s" when you want'
PLISTDIR = "."

plat = distutils.util.get_platform()

def runsetup(commands, setup='setup.py'):
    cmd = '%s %s %s' % (sys.executable, setup, commands)
    return os.popen(cmd)
    
def main(httpbase=HTTPBASE, upload=True):
    plist = Plist.fromFile(os.path.join(PLISTDIR, plat+'.plist'))

    print 'Querying package information'
    spl = runsetup('--name --version --url --description').read().split('\n')[:-1]
    name, version, url = spl[:3]
    description = '\n'.join(spl[3:])

    print 'Building dumb distribution for %s-%s' % (name, version)
    runsetup('bdist_dumb').read()

    hash = md5.md5()
    fn = '%s-%s.%s.tar.gz' % (name, version, plat)
    print 'Calculating MD5 hash for', fn
    f = file(os.path.join('dist', fn), 'rb')
    while 1:
        s = f.read(1024)
        if not s:
            break
        hash.update(s)
    f.close()
    hash = hash.hexdigest()

    if upload:
        print 'Uploading', fn 
        os.system(UPLOADCMD % os.path.join('dist', fn))

    for pkg in plist.Packages:
        if pkg.Name == name and pkg.Flavor == 'binary':
            print 'Existing package metadata found'
            break
    else:
        print 'Creating new package metadata'
        pkg = {
            'Flavor':'binary',
            'Install-test':'\nimport %s\n\t\t\t' % (name,),
            'Prerequisites':[],
        }
        plist.Packages.append(pkg)
    pkg['Name'] = name
    pkg['Version'] = version
    pkg['MD5Sum'] = hash
    pkg['Download-URL'] = httpbase + fn
    if url:
        pkg['Home-page'] = url
    if description and not pkg.get('Description', None):
        pkg['Description'] = '\n%s\n\t\t\t' % (description,)
    print 'Writing out new plist'
    plist.write(os.path.join(PLISTDIR, plat+'.plist'))

if __name__=='__main__':
    main()
