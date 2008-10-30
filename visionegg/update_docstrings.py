#!/usr/bin/env python
import os
import sys
import md5
import re

import VisionEgg
import VisionEgg.Core
import VisionEgg.Daq
import VisionEgg.DaqKeyboard
import VisionEgg.Dots
import VisionEgg.FlowControl
import VisionEgg.Gratings
import VisionEgg.MoreStimuli
import VisionEgg.ResponseControl
import VisionEgg.SphereMap
import VisionEgg.Text
import VisionEgg.Textures

mods = [VisionEgg,
        VisionEgg.Core,
        VisionEgg.Daq,
        VisionEgg.DaqKeyboard,
        VisionEgg.Dots,
        VisionEgg.FlowControl,
        VisionEgg.Gratings,
        VisionEgg.MoreStimuli,
        VisionEgg.ResponseControl,
        VisionEgg.SphereMap,
        VisionEgg.Text,
        VisionEgg.Textures,
        ]

mod_name_to_file = {}
file_buffers = {}
file_hashes = {}

for mod in mods:
    orig_file = mod.__file__
    if orig_file.endswith('pyc'):
        orig_file = orig_file[:-1]
    cur_file = os.path.join('VisionEgg',os.path.split(orig_file)[1])
    mod_name_to_file[mod.__name__] = cur_file

def get_str(xx,const=0):
    class_by_key = {}

    done_parameters_and_defaults = []
    classes = VisionEgg.recursive_base_class_finder( xx )
    # Fill self.parameters with parameter names and set to default values
    for klass in classes:
        if klass == object:
            continue # base class of new style classes - ignore
        if const:
            pd = klass.constant_parameters_and_defaults
        else:
            pd = klass.parameters_and_defaults
        if pd not in done_parameters_and_defaults:
            for parameter_name in pd.keys():
                class_by_key[parameter_name] = klass
            done_parameters_and_defaults.append(pd)
    ks = class_by_key.keys()
    ks.sort()

    if len(ks):
        out_strs = []
        if not const:
            out_strs.append('Parameters\n')
            out_strs.append('==========\n')
        else:
            out_strs.append('Constant Parameters\n')
            out_strs.append('===================\n')
        # pass 1:
        max_len = 0
        for param_name in ks:
            max_len = max(max_len, len(param_name))

        for param_name in ks:
            klass = class_by_key[param_name]
            if const:
                p = klass.constant_parameters_and_defaults
            else:
                p = klass.parameters_and_defaults
            if len(p[param_name]) > 3:
                if p[param_name][3] == VisionEgg.ParameterDefinition.DEPRECATED:
                    continue
            type_str = param_name
            default = p[param_name][0]
            ve_type = p[param_name][1]

            if len(p[param_name]) > 2:
                description = p[param_name][2] + ' '
            else:
                description = ''

            out_strs.append( '%s -- %s(%s)\n'%(param_name.ljust(max_len), description, str(ve_type)) )
            if xx != klass:
                if klass.__module__ != xx.__module__:
                    mod_name = '%s.'%klass.__module__
                else:
                    mod_name = ''
                out_strs.append( ' '*(max_len+4)+'Inherited from %s%s\n'%(mod_name,klass.__name__,))

            tmp = str(default).split('\n')
            if default is None:
                tmp = ['(determined at runtime)']
            if len(p[param_name]) > 3:
                if p[param_name][3] == VisionEgg.ParameterDefinition.OPENGL_ENUM:
                    if default is None:
                        gl_name = '(GL enum determined at runtime)'
                    else:
                        gl_name = str(default)
                    tmp = [gl_name]
            out_strs.append( ' '*(max_len+4)+'Default: '+tmp[0]+'\n')
            if len(tmp) > 1:
                for i in range(1,len(tmp)):
                    out_strs.append( ' '*(max_len+13)+tmp[i]+'\n')
        return out_strs

xl = []
for mod in mods:
    orig_file = mod.__file__
    if orig_file.endswith('pyc'):
        orig_file = orig_file[:-1]
    orig_fd = file(orig_file,"r")
    orig_hash = md5.new()
    orig_hash.update( orig_fd.read() )

    fname = mod_name_to_file[ mod.__name__ ]
    cur_fd = file(fname,"r")
    cur_hash = md5.new()
    cur_hash.update( cur_fd.read() )

    digest = cur_hash.digest()
    if orig_hash.digest() != digest:
        raise RuntimeError('%s is different in VisionEgg and site-packages'%fname)
    for x in mod.__dict__.keys():
        xx = getattr(mod,x)
        xl.append(xx)

    file_hashes[fname] = digest

for xx in xl:
    found=0
    if type(xx) == type(VisionEgg.ClassWithParameters):
        if issubclass(xx,VisionEgg.ClassWithParameters):
            if not xx.__module__ in mod_name_to_file.keys():
                print xx,'not in modules -- skipping'
                continue
            fname = mod_name_to_file[xx.__module__]
            if file_buffers.has_key(fname):
                buf = file_buffers[fname]
            else:
                fd = file(fname,'r')
                buf = fd.readlines()
                fd.close()
                del fd
            search_str = re.compile( r'^class %s\W'%xx.__name__ )
            print 'searching for %s in %s'%(xx.__name__,fname)
            for line_no, line in enumerate(buf):
                if search_str.match(line):
                    #print xx.__name__,fname,line_no+1,line
                    found=1
                    break
            if not found:
                if xx.__name__ in ['StrokeText','GlutTextBase','BitmapText']:
                    print 'skipping %s - not found, probably because no glut'%xx.__name__
                    continue
                raise RuntimeError("didn't find source for %s"%xx.__name__)
            doc_find = re.compile(r'"""')
            doc_start = line_no+1
            if not doc_find.search(buf[doc_start]):
                print xx.__name__,fname,doc_start,": not doc string"
                continue
            doc_one_liner_find = re.compile(r'""".*"""')
            if doc_one_liner_find.search(buf[doc_start]):
                doc_stop = doc_start
                del_doc_stop = doc_stop+1

                doc_lines = buf[doc_start:del_doc_stop]
                del buf[doc_start:del_doc_stop]
            else:
                doc_stop = doc_start+1
                doc_found = 0
                while not doc_found:
                    if doc_find.search(buf[doc_stop]):
                        doc_found=1
                    doc_stop += 1
                    del_doc_stop = doc_stop

                doc_lines = buf[doc_start:del_doc_stop-1]
                del buf[doc_start:del_doc_stop]

            trimmed_doc_lines = []
            for doc_line in doc_lines:
                doc_line = doc_line.replace('"""','')
                if doc_line.startswith('    '):
                    trimmed_doc_lines.append(doc_line[4:])
                else:
                    trimmed_doc_lines.append(doc_line)
            doc_lines = trimmed_doc_lines

            # trim old parameter definitions from docstring
            idx = len(doc_lines)-1
            while idx >= 0:
                if doc_lines[idx] == 'Constant Parameters\n':
                    doc_lines = doc_lines[:idx]
                    break
                idx -= 1
            idx = len(doc_lines)-1
            while idx >= 0:
                if doc_lines[idx] == 'Parameters\n':
                    doc_lines = doc_lines[:idx]
                    break
                idx -= 1

            # insert new parameter defintion
##            params_lines = get_str(xx.parameters_and_defaults,const=0)
##            const_lines = get_str(xx.constant_parameters_and_defaults,const=1)
            params_lines = get_str(xx,const=0)
            const_lines = get_str(xx,const=1)
            new_lines = doc_lines#['"""'+''.join(doc_lines)]
            new_lines[0] = '"""'+new_lines[0]
            if params_lines is not None:
                if new_lines[-1].strip() != '':
                    new_lines.append('\n')
                new_lines.extend(params_lines)
            if const_lines is not None:
                if new_lines[-1].strip() != '':
                    new_lines.append('\n')
                new_lines.extend(const_lines)
            new_lines.append('"""\n')

            final_new_lines = []
            for new_line in new_lines:
                tmp = new_line.strip()
                if tmp == '':
                    final_new_lines.append('\n')
                else:
                    final_new_lines.append( '    '+new_line )
            new_lines = final_new_lines

            buf[line_no+1:line_no+1] = new_lines # insert new docstring

            file_buffers[fname] = buf # reassign new buffer

for fname, buf in file_buffers.iteritems():
    buf = ''.join(buf)
    new_hash = md5.new()
    new_hash.update(buf)
    if new_hash.digest() != file_hashes[fname]:
        print 'saving',fname
        fd = file(fname,'w')
        fd.write(buf)
        fd.close()
        print 'done'
