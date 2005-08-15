/*
 * This is the C source code for interfacing with the Vision Egg with
 * the lib3ds library
 *
 * Copyright (C) 2002 Andrew Straw
 * Copyright (C) 2005 California Institute of Technology
 *
 * Distributed under the terms of the GNU Lesser General Public
 * License (LGPL).
 *
 * $Id$
 * Author = Andrew Straw <astraw@users.sourceforge.net>
 *
 */

#include "Python.h"

#include <lib3ds/file.h>                        
#include <lib3ds/mesh.h>
#include <lib3ds/node.h>
#include <lib3ds/material.h>
#include <lib3ds/matrix.h>
#include <lib3ds/vector.h>
#include <lib3ds/light.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

#if defined(MS_WINDOWS)
#  include <windows.h>
#endif

#if defined(__APPLE__)
#  include <OpenGL/gl.h>
#else
#  include <GL/gl.h>
#endif

#define PY_CHECK(X,LINENO) if (!(X)) { fprintf(stderr,"Python exception _lib3ds.c line %d\n",LINENO); goto error; }
#define L3DCK(X,LINENO) if (!(X)) { fprintf(stderr,"_lib3ds error on line %d",LINENO); goto error; }

#define MAX_WARN_STR 255
#define _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL(X) if (m->X.name[0]) { snprintf(warn_str,MAX_WARN_STR,"Ignoring data in %s because .3ds file support is incomplete. (" #X " \"%s\" for material \"%s\" was not loaded)",filename,&m->X.name[0],&m->name[0]); if (!warn_python(warn_str)) {goto error;} }

static PyObject *g_logger_warning = NULL;

// forward declarations
static PyObject*
render_node(Lib3dsFile *file, PyObject *tex_dict, Lib3dsNode *node);

static PyObject* 
get_logger_warning( void );

int warn_python(char *text);

//////////////////////////////////////////////

static char draw__doc__[] = 
"Draw a model loaded from a .3ds file.\n";

static PyObject *draw(PyObject *self, PyObject *args)
{
  PyObject *py_c_file;
  Lib3dsFile *file=NULL;

  PyObject *tex_dict=NULL;

  float scale_x, scale_y, scale_z;
  float pos_x, pos_y, pos_z;
  float orient_angle;
  float orient_x,orient_y,orient_z;
  
  PY_CHECK(PyArg_ParseTuple(args,"OOffffffffff",
			    &py_c_file,
			    &tex_dict,
			    &scale_x,&scale_y,&scale_z,
			    &pos_x,&pos_y,&pos_z,
			    &orient_angle,
			    &orient_x,&orient_y,&orient_z
			    ),__LINE__);

  if (!PyCObject_Check(py_c_file)) {
    PyErr_SetString(PyExc_ValueError,"Must pass PyCObject as 1st argument");
    return NULL;
  }

  if (!PyDict_Check(tex_dict)) {
    PyErr_SetString(PyExc_ValueError,"Must pass PyDict as 2nd argument");
    return NULL;
  }  

  file = (Lib3dsFile*)PyCObject_AsVoidPtr(py_c_file);

  glEnable(GL_TEXTURE_2D);
  //glShadeModel(GL_SMOOTH);
  //glEnable(GL_LIGHTING);
  //glDepthFunc(GL_LEQUAL);
  glEnable(GL_DEPTH_TEST);
  //glEnable(GL_CULL_FACE);
  //glCullFace(GL_BACK);

  //glClear(GL_DEPTH_BUFFER_BIT);

  if (!file) {
    return NULL;
  }

  glMatrixMode(GL_MODELVIEW);
  glPushMatrix();
  glTranslatef(pos_x,pos_y,pos_z);
  glRotatef(orient_angle,orient_x,orient_y,orient_z);
  glRotatef(-90, 1.0,0,0);
  glScalef(scale_x,scale_y,scale_z);

  {
    Lib3dsNode *p;
    for (p=file->nodes; p!=0; p=p->next) {
      PY_CHECK(render_node(file,tex_dict,p),__LINE__);
    }
  }

  glPopMatrix();

  //glDisable(GL_LIGHTING);

  Py_INCREF(Py_None);
  return Py_None;
 error:
  return NULL;
}

//////////////////////////////////////////////

static PyObject *get_logger_warning( void ) {
  PyObject *loggingModule = NULL;
  PyObject *logging_getLogger = NULL;
  PyObject *logger = NULL;
  PyObject *logger_warning = NULL;

  // Now get VisionEgg.Core.message to pass message 
  loggingModule = PyImport_ImportModule("logging"); // New ref
  if (!loggingModule) {
    loggingModule = PyImport_ImportModule("VisionEgg.py_logging");
  }
  PY_CHECK(loggingModule,__LINE__);

  logging_getLogger = PyObject_GetAttrString(loggingModule,"getLogger"); // new ref
  PY_CHECK(logging_getLogger,__LINE__);

  logger = PyObject_CallObject(logging_getLogger,Py_BuildValue("(s)","VisionEgg._lib3ds")); // new ref
  PY_CHECK(logger,__LINE__);

  logger_warning = PyObject_GetAttrString(logger,"warning"); // new ref
  PY_CHECK(logger_warning,__LINE__);

  g_logger_warning = logger_warning;

  Py_DECREF(logger);
  Py_DECREF(logging_getLogger);
  Py_DECREF(loggingModule);
  return g_logger_warning;

 error:
  Py_XDECREF(logger);
  Py_XDECREF(logging_getLogger);
  Py_XDECREF(loggingModule);
  return NULL;
}

int warn_python(char *text) {
  PyObject* temp = NULL;

  if (!g_logger_warning) { // make sure can write to the log
    g_logger_warning = get_logger_warning();
    PY_CHECK(g_logger_warning,__LINE__);
  }
  temp = PyObject_CallObject(g_logger_warning,Py_BuildValue("(s)",text)); // new ref
  PY_CHECK(temp,__LINE__);
  Py_XDECREF(temp);
  return 1;
 error:
  Py_XDECREF(temp);
  return 0;
}

static char c_init__doc__[] = 
"C helper for Model3DS.__init__.\n";

static PyObject *c_init(PyObject *dummy_self, PyObject *args)
{
  char * filename=NULL;
  char * warn_str=NULL;
  Lib3dsFile *file=NULL;
  Lib3dsMaterial* m;
  Lib3dsLight *light;
  Lib3dsNode* new_node=NULL;
  Lib3dsNode* last_node=NULL;
  Lib3dsMesh* mesh;
  Lib3dsTextureMap texmap;
  PyObject *self=NULL;
  PyObject *self_draw=NULL;
  PyObject *self_dict=NULL;
  PyObject *py_c_file=NULL;

  PyObject *tex_dict=NULL;
  PyObject *tex_dict_value=NULL;

  warn_str = (char *)malloc(MAX_WARN_STR*sizeof(char));
  if (!warn_str) {
    PyErr_SetString(PyExc_SystemError,"malloc failed in _lib3ds.c");
    goto error;
  }

  PY_CHECK(PyArg_ParseTuple(args,"Os",
			    &self,
			    &filename),__LINE__);

  self_dict = PyObject_GetAttrString( self, "__dict__" ); // new ref
  PY_CHECK(self_dict,__LINE__);

  file=lib3ds_file_load(filename);
  if (!file) {
    PyErr_SetString(PyExc_RuntimeError,"lib3ds_file_load failed");
    return NULL;
  }
  
  lib3ds_file_eval(file,0);

  //  gFile = file;

  // Now do self._lib3ds_file = file
  // XXX should build destructor before here
  py_c_file = PyCObject_FromVoidPtr((void*)file,NULL); // new ref
  PY_CHECK(py_c_file,__LINE__);

  PY_CHECK(!PyDict_SetItemString(self_dict,"_lib3ds_file",py_c_file),__LINE__);

  // Get a list of the texture files to load

  tex_dict = PyDict_New(); // new ref
  PY_CHECK(tex_dict,__LINE__);

  for (m=file->materials; m!=0; m=m->next ) {
    texmap = m->texture1_map;
    if (texmap.name[0]) {
      //printf("c_init texture1_map %s: %s\n",&m->name[0],&texmap.name[0]);

      tex_dict_value = Py_BuildValue("i",-1); // new ref
      PY_CHECK(tex_dict_value,__LINE__);
      PY_CHECK(!PyDict_SetItemString(tex_dict,&texmap.name[0],tex_dict_value),__LINE__);
      Py_DECREF(tex_dict_value);

    }
    // we don't handle these yet, at least let the user know...
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( texture1_mask);
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( texture2_map);
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( texture2_mask);
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( opacity_map);
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( opacity_mask);
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( bump_map);
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( bump_mask);
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( specular_map);
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( specular_mask);
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( shininess_map);
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( shininess_mask);
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( self_illum_map);
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( self_illum_mask);
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( reflection_map);
    _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL( reflection_mask);
  }

  for (light=file->lights; light; light=light->next) {
    snprintf(warn_str,MAX_WARN_STR,"Ignoring data in %s because .3ds file support is incompelte. (Light \"%s\" not used because light support not implemented.)",filename,&light->name[0]);
    if (!warn_python(warn_str)) {
      goto error;
    }
  }

  Py_XDECREF(py_c_file);

  // If no nodes, warn and make one for each mesh
  if (file->nodes == 0) {
    if (file->meshes == 0) {
      if (!warn_python(".3ds file has no nodes and no meshes, not drawing anything.")) {
	goto error;
      }
    }
    for (mesh=file->meshes; mesh!=0; mesh=mesh->next) {
      snprintf(warn_str,MAX_WARN_STR,".3ds file has no nodes, making one for mesh \"%s\"",&mesh->name[0]);
      if (!warn_python(warn_str)) {
	goto error;
      }
      new_node = lib3ds_node_new_object();
      strncpy(&new_node->name[0],&mesh->name[0],64);
      if (file->nodes == 0) {
	file->nodes = new_node;
      } else {
	last_node->next = new_node;
      }
      last_node = new_node;
      //file->nodes->name = &file->meshes->name[0];
    }
  }

  free((void*)warn_str);
  return tex_dict;

 error:
  free((void*)warn_str);

  Py_XDECREF(tex_dict);
  Py_XDECREF(tex_dict_value);
  Py_XDECREF(self_dict);
  Py_XDECREF(self_draw);
  Py_XDECREF(py_c_file);
  return NULL;
}

/////////////////////////////////////////////

static PyObject*
render_node(Lib3dsFile *file, PyObject *tex_dict, Lib3dsNode *node)
{
  PyObject *tex_dict_value=NULL;
  /*
  Lib3dsRgba a;
  Lib3dsRgba d;
  Lib3dsRgba s;
  */
  ASSERT(file);

  {
    Lib3dsNode *p;
    for (p=node->childs; p!=0; p=p->next) {
      PY_CHECK(render_node(file,tex_dict,p),__LINE__);
    }
  }
  if (node->type==LIB3DS_OBJECT_NODE) {
    if (strcmp(node->name,"$$$DUMMY")==0) {
      L3DCK(0,__LINE__);
    }

    if (!node->user.d) {
      Lib3dsMesh *mesh;
      
      mesh=lib3ds_file_mesh_by_name(file, node->name);
      ASSERT(mesh);
      if (!mesh) {
	L3DCK(0,__LINE__);
      }

      node->user.d=glGenLists(1);
      glNewList(node->user.d, GL_COMPILE);

      {
        unsigned p;
        Lib3dsVector *normalL=malloc(3*sizeof(Lib3dsVector)*mesh->faces);

        {
          Lib3dsMatrix M;
          lib3ds_matrix_copy(M, mesh->matrix);
          lib3ds_matrix_inv(M);
          glMultMatrixf(&M[0][0]);
        }
        lib3ds_mesh_calculate_normals(mesh, normalL);

        for (p=0; p<mesh->faces; ++p) {
          Lib3dsFace *f=&mesh->faceL[p];
          Lib3dsMaterial *mat=0;
          if (f->material[0]) {
            mat=lib3ds_file_material_by_name(file, f->material);
          }

          if (mat) {
	    
	    /*
	    /////////////////////
            static GLfloat a[4]={0,0,0,1};
            float s;
            glMaterialfv(GL_FRONT, GL_AMBIENT, a);
            glMaterialfv(GL_FRONT, GL_DIFFUSE, mat->diffuse);
            glMaterialfv(GL_FRONT, GL_SPECULAR, mat->specular);
            s = (float)pow(2, 10.0*mat->shininess);
            if (s>128.0) {
              s=128.0;
            }
            glMaterialf(GL_FRONT, GL_SHININESS, s);
	    /////////////////////
	    */

	    if (mat->texture1_map.name[0]) { // use texture

	      tex_dict_value = PyDict_GetItemString(tex_dict,&mat->texture1_map.name[0]); // borrowed ref
	      PY_CHECK(tex_dict_value,__LINE__);


	      if (!PyLong_Check(tex_dict_value)) {
		PyErr_SetString(PyExc_ValueError,"dictionary value must be int");
		goto error;
	      }

	      glBindTexture( GL_TEXTURE_2D, PyInt_AsLong(tex_dict_value) );

	    } else {
	      // no texture...
	    }
          } else {
	    /*
	    ////////////////////////
            a[0]=0.2f; a[1]=0.2f; a[2]=0.2f; a[3]=1.0f;
            d[0]=0.8f; d[1]=0.8f; d[2]=0.8f; d[3]=1.0f;
            s[0]=0.0f; s[1]=0.0f; s[2]=0.0f; s[3]=1.0f;
            glMaterialfv(GL_FRONT, GL_AMBIENT, a);
            glMaterialfv(GL_FRONT, GL_DIFFUSE, d);
            glMaterialfv(GL_FRONT, GL_SPECULAR, s);
	    ////////////////////////
	    */
          }
          {
            int i;
            glBegin(GL_TRIANGLES);
              glNormal3fv(f->normal);
              for (i=0; i<3; ++i) {
                glNormal3fv(normalL[3*p+i]);
		if (mesh->texels) {
		  glTexCoord2fv(mesh->texelL[f->points[i]]); 
		}
                glVertex3fv(mesh->pointL[f->points[i]].pos);
              }
            glEnd();
          }
        }

        free(normalL);
      }

      glEndList();
    }

    if (node->user.d) {
      Lib3dsObjectData *d;

      glPushMatrix();
      d=&node->data.object;
      glMultMatrixf(&node->matrix[0][0]);
      glTranslatef(-d->pivot[0], -d->pivot[1], -d->pivot[2]);
      glCallList(node->user.d);
      glPopMatrix();
    }
  }

  Py_INCREF(Py_None);
  return Py_None;
 error:
  return NULL;
}

//////////////////////////////////////////////

static char dump_materials__doc__[] = 
"Print the materials of a .3ds file.\n";

static PyObject *dump_materials(PyObject *self, PyObject *args)
{
  PyObject *py_c_file;
  Lib3dsFile *file=NULL;
  
  PY_CHECK(PyArg_ParseTuple(args,"O",
			    &py_c_file),__LINE__);

  if (!PyCObject_Check(py_c_file)) {
    PyErr_SetString(PyExc_ValueError,"Must pass PyCObject");
    return NULL;
  }

  file = (Lib3dsFile*)PyCObject_AsVoidPtr(py_c_file);

  lib3ds_file_dump_materials(file);

  Py_INCREF(Py_None);
  return Py_None;

 error:
  return NULL;
}

//////////////////////////////////////////////

static char dump_nodes__doc__[] = 
"Print the nodes of a .3ds file.\n";

static PyObject *dump_nodes(PyObject *self, PyObject *args)
{
  PyObject *py_c_file;
  Lib3dsFile *file=NULL;
  
  PY_CHECK(PyArg_ParseTuple(args,"O",
			    &py_c_file),__LINE__);

  if (!PyCObject_Check(py_c_file)) {
    PyErr_SetString(PyExc_ValueError,"Must pass PyCObject");
    return NULL;
  }

  file = (Lib3dsFile*)PyCObject_AsVoidPtr(py_c_file);

  lib3ds_file_dump_nodes(file);

  Py_INCREF(Py_None);
  return Py_None;

 error:
  return NULL;
}

//////////////////////////////////////////////

static char dump_meshes__doc__[] = 
"Print the meshes of a .3ds file.\n";

static PyObject *dump_meshes(PyObject *self, PyObject *args)
{
  PyObject *py_c_file;
  Lib3dsFile *file=NULL;
  
  PY_CHECK(PyArg_ParseTuple(args,"O",
			    &py_c_file),__LINE__);

  if (!PyCObject_Check(py_c_file)) {
    PyErr_SetString(PyExc_ValueError,"Must pass PyCObject");
    return NULL;
  }

  file = (Lib3dsFile*)PyCObject_AsVoidPtr(py_c_file);

  lib3ds_file_dump_meshes(file);

  Py_INCREF(Py_None);
  return Py_None;

 error:
  return NULL;
}

//////////////////////////////////////////////

static PyMethodDef
lib3ds_c_methods[] = {
  { "c_init", (PyCFunction)c_init, METH_VARARGS, c_init__doc__},  
  { "draw", (PyCFunction)draw, METH_VARARGS, draw__doc__},  
  { "dump_materials", (PyCFunction)dump_materials, METH_VARARGS, dump_materials__doc__},  
  { "dump_nodes", (PyCFunction)dump_nodes, METH_VARARGS, dump_nodes__doc__},  
  { "dump_meshes", (PyCFunction)dump_meshes, METH_VARARGS, dump_meshes__doc__},  
  { NULL, NULL, 0, NULL} /* sentinel */
};

DL_EXPORT(void)
init_lib3ds(void)
{
  Py_InitModule("_lib3ds", lib3ds_c_methods);
  return;
}
