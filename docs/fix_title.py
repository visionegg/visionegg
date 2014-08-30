import os, glob, urllib

for fname in glob.glob('*.rst'):
    print fname
    title_escaped = fname[:-4]
    title = urllib.unquote(title_escaped)

    lines = [line.rstrip() for line in open(fname,mode='r').readlines()]

    new_dir, new_fname = os.path.split(title)
    new_fname += '.rst'
    new_full_fname = os.path.join( new_dir, new_fname)
    try:
        os.mkdir(new_dir)
    except OSError as err:
        if err.errno==11:
            pass
        else:
            raise

    os.unlink(fname)

    if lines[0]=='#format rst':
        lines = lines[1:]
    if lines[0].startswith('## page was renamed from'):
        lines = lines[1:]
    with open(new_full_fname,mode='w') as fd:
        fd.write(title+'\n')
        fd.write('#'*len(title)+'\n')
        for line in lines:
            fd.write(line+'\n')
