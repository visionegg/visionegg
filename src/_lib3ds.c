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
#  pragma comment(lib, "opengl32.lib")
#  include <windows.h>
#endif

#if defined(__APPLE__)
#  include <OpenGL/gl.h>
#else
#  include <GL/gl.h>
#endif

#define PY_CHECK(X,LINENO) if (!(X)) { fprintf(stderr,"Python exception _lib3ds.c line %d\n",LINENO); goto error; }
#define L3DCK(X,LINENO) if (!(X)) { fprintf(stderr,"_lib3ds error on line %d",LINENO); goto error; }

#define _LIB3DS_WARN_IF_MATERIAL_TEX_IS_NOT_NULL(X) if (m->X.name[0]) { fprintf(stderr,"WARNING: ignoring " #X " \"%s\" for material \"%s\"\n",&m->X.name[0],&m->name[0]); }

// forward declaration
static PyObject*
render_node(Lib3dsFile *file, PyObject *tex_dict, Lib3dsNode *node);

//////////////////////////////////////////////

static char draw__doc__[] = 
"Draw a model loaded from a .3ds file.\n";

static PyObject *draw(PyObject *self, PyObject *args)
{
  PyObject *py_c_file;
  Lib3dsFile *file=NULL;

  PyObject *tex_dict=NULL;
  PyObject *tex_dict_value=NULL;
  
  PY_CHECK(PyArg_ParseTuple(args,"OO",
			    &py_c_file,
			    &tex_dict),__LINE__);

  if (!PyCObject_Check(py_c_file)) {
    PyErr_SetString(PyExc_ValueError,"Must pass PyCObject as 1st argument");
    return NULL;
  }

  if (!PyDict_Check(tex_dict)) {
    PyErr_SetString(PyExc_ValueError,"Must pass PyDict as 2nd argument");
    return NULL;
  }  

  file = (Lib3dsFile*)PyCObject_AsVoidPtr(py_c_file);

  //  file = gFile;

  glShadeModel(GL_SMOOTH);
  glEnable(GL_LIGHTING);
  glEnable(GL_LIGHT0);
  glDisable(GL_LIGHT1);
  glDepthFunc(GL_LEQUAL);
  glEnable(GL_DEPTH_TEST);
  glEnable(GL_CULL_FACE);
  glCullFace(GL_BACK);

  glClear(GL_DEPTH_BUFFER_BIT);

  if (!file) {
    return NULL;
  }

  glMatrixMode(GL_MODELVIEW);
  glLoadIdentity();
  glRotatef(-90, 1.0,0,0);

  {
    GLfloat a[] = {0.0f, 0.0f, 0.0f, 1.0f};
    GLfloat c[] = {1.0f, 1.0f, 1.0f, 1.0f};
    GLfloat p[] = {0.0f, 0.0f, 0.0f, 1.0f};
    Lib3dsLight *l;
    
    int li=GL_LIGHT0;
    for (l=file->lights; l; l=l->next) {
      glEnable(li);

      glLightfv(li, GL_AMBIENT, a);
      glLightfv(li, GL_DIFFUSE, c);
      glLightfv(li, GL_SPECULAR, c);
      
      p[0] = l->position[0];
      p[1] = l->position[1];
      p[2] = l->position[2];
      glLightfv(li, GL_POSITION, p);

      if (!l->spot_light) {
        continue;
      }
      
      p[0] = l->spot[0] - l->position[0];
      p[1] = l->spot[1] - l->position[1];
      p[2] = l->spot[2] - l->position[2];      
      glLightfv(li, GL_SPOT_DIRECTION, p);
      ++li;
    }
  }
  
  {
    Lib3dsNode *p;
    for (p=file->nodes; p!=0; p=p->next) {
      PY_CHECK(render_node(file,tex_dict,p),__LINE__);
    }
  }

  Py_INCREF(Py_None);
  return Py_None;
 error:
  return NULL;
}

//////////////////////////////////////////////

static char c_init__doc__[] = 
"C helper for Model3DS.__init__.\n";

static PyObject *c_init(PyObject *dummy_self, PyObject *args)
{
  char * filename=NULL;
  Lib3dsFile *file=NULL;
  Lib3dsMaterial* m;
  Lib3dsTextureMap texmap;
  PyObject *self=NULL;
  PyObject *self_draw=NULL;
  PyObject *self_dict=NULL;
  PyObject *py_c_file=NULL;

  PyObject *tex_dict=NULL;
  PyObject *tex_dict_value=NULL;

  PY_CHECK(PyArg_ParseTuple(args,"O!s",
			    &PyInstance_Type,&self,
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
      printf("c_init texture1_map %s: %s\n",&m->name[0],&texmap.name[0]);

      tex_dict_value = Py_BuildValue("i",-1); // new ref
      PY_CHECK(tex_dict_value,__LINE__);
      PY_CHECK(!PyDict_SetItemString(tex_dict,&texmap.name[0],tex_dict_value),__LINE__);
      Py_DECREF(tex_dict_value,__LINE__);

      /*
      tex_dict_value = Py_BuildValue("si",&texmap.name[0],-1); // new ref
      PY_CHECK(tex_dict_value,__LINE__);
      PY_CHECK(!PyDict_SetItemString(tex_dict,&m->name[0],tex_dict_value),__LINE__);
      Py_DECREF(tex_dict_value,__LINE__);
      */
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

    texmap = m->texture2_map;
    if (texmap.name[0]) {
      printf("c_init texture2_map %s: %s\n",&m->name[0],&texmap.name[0]);
    }
    texmap = m->bump_map;
    if (texmap.name[0]) {
      printf("c_init bump_map %s: %s\n",&m->name[0],&texmap.name[0]);
    } 
  }

  Py_XDECREF(py_c_file);
  //Py_INCREF(Py_None);
  //return Py_None;
  
  return tex_dict;

 error:
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

  //  file = gFile;

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
      //printf("Generating new display list\n");
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
	    if (mat->texture1_map.name[0]) { // use texture
	      printf("loading %s: ",&mat->texture1_map.name[0]);

	      tex_dict_value = PyDict_GetItemString(tex_dict,&mat->texture1_map.name[0]); // borrowed ref
	      PY_CHECK(tex_dict_value,__LINE__);

	      PyObject_Print(tex_dict_value,stdout,0);

	      printf("(C: %d)\n",PyInt_AsLong(tex_dict_value));
	      
	      if (!PyLong_Check(tex_dict_value)) {
		PyErr_SetString(PyExc_ValueError,"dictionary value must be int");
		goto error;
	      }

	      printf("(C: %d)\n",PyInt_AsLong(tex_dict_value));
	      

	      glBindTexture( GL_TEXTURE_2D, PyInt_AsLong(tex_dict_value) );

	    }
          }
          else {
            Lib3dsRgba a={0.2f, 0.2f, 0.2f, 1.0f};
            Lib3dsRgba d={0.8f, 0.8f, 0.8f, 1.0f};
            Lib3dsRgba s={0.0f, 0.0f, 0.0f, 1.0f};
            glMaterialfv(GL_FRONT, GL_AMBIENT, a);
            glMaterialfv(GL_FRONT, GL_DIFFUSE, d);
            glMaterialfv(GL_FRONT, GL_SPECULAR, s);
          }
          {
            int i;
            glBegin(GL_TRIANGLES);
              glNormal3fv(f->normal);
              for (i=0; i<3; ++i) {
                glNormal3fv(normalL[3*p+i]);
		glTexCoord2fv(mesh->texelL[f->points[i]]); 
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
      /*glutSolidSphere(50.0, 20,20);*/
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
"Draw a model loaded from a .3ds file.\n";

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
"Draw a model loaded from a .3ds file.\n";

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
"Draw a model loaded from a .3ds file.\n";

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
  { "dump_materials", (PyCFunction)dump_materials, METH_VARARGS, draw__doc__},  
  { "dump_nodes", (PyCFunction)dump_nodes, METH_VARARGS, draw__doc__},  
  { "dump_meshes", (PyCFunction)dump_meshes, METH_VARARGS, draw__doc__},  
  { NULL, NULL, 0, NULL} /* sentinel */
};

DL_EXPORT(void)
init_lib3ds(void)
{
  Py_InitModule("_lib3ds", lib3ds_c_methods);
  return;
}
