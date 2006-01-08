import sys, os, glob

demos = glob.glob('demo/*.py') + ['check-config.py'] + glob.glob('test/*.py')
outdir = 'demo-dist'
os.mkdir(outdir)
os.mkdir(os.path.join(outdir,'test'))
for d in demos:
    if d.startswith('test'):
        newname = os.path.join(outdir,d)
    else:
        newname = os.path.join(outdir,os.path.split(d)[-1])
    print d
    os.link(d,newname)
