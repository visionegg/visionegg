%module darwin_app_stuff

/* ensure Python exceptions work even when function returns nothing */
%exception {
  $action
  if (PyErr_Occurred()) {
    goto fail;
  }
}

extern void set_icon( char * filename );

%exception;   /* Deletes previously defined handler */