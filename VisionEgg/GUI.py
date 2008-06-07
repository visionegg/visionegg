# The Vision Egg: GUI
#
# Copyright (C) 2001-2003 Andrew Straw.
# Copyright (C) 2008 California Institute of Technology
#
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""
Graphical user interface classes and functions.

"""

import VisionEgg

####################################################################
#
#        Import all the necessary packages
#
####################################################################


import logging                              # available in Python 2.3

import VisionEgg
import os
import sys

class _delay_import_error:
    """Defer import errors until they cause problems."""
    def __init__(self,orig_traceback):
        self.orig_traceback = orig_traceback
    def __getattr__(self,name):
        raise self.orig_traceback # ImportError deferred from earlier failure

try:
    import Tkinter
except ImportError, x: # don't fail on this until it becomes a problem...
    Tkinter = _delay_import_error(x)

try:
    import tkMessageBox
except ImportError, x: # don't fail on this until it becomes a problem...
    tkMessageBox = _delay_import_error(x)

try:
    import tkFileDialog
except ImportError, x: # don't fail on this until it becomes a problem...
    tkFileDialog = _delay_import_error(x)

def showexception(exc_type, exc_value, traceback_str):
    # private subclass of Tkinter.Frame
    class ShowExceptionFrame(Tkinter.Frame):
        """A window that shows a string and has a quit button."""
        def __init__(self,master,exc_type, exc_value, traceback_str):
            VisionEgg.config._Tkinter_used = True
            Tkinter.Frame.__init__(self,master,borderwidth=20)
            title="Vision Egg: exception caught"
            first_str = "An unhandled exception was caught."
            type_value_str = "%s: %s"%(str(exc_type),str(exc_value))

            frame = self

            top = frame.winfo_toplevel()
            top.title(title)
            top.protocol("WM_DELETE_WINDOW",self.close_window)

            Tkinter.Label(frame,text=first_str).pack()
            Tkinter.Label(frame,text=type_value_str).pack()
            if traceback_str:
                Tkinter.Label(frame,text="Traceback (most recent call last):").pack()
                Tkinter.Label(frame,text=traceback_str).pack()

            b = Tkinter.Button(frame,text="OK",command=self.close_window)
            b.pack()
            b.focus_set()
	    b.grab_set()
            b.bind('<Return>',self.close_window)

        def close_window(self,dummy_arg=None):
            self.quit()
    # create instance of class
    parent = Tkinter._default_root
    if parent:
        top = Tkinter.Toplevel(parent)
        top.transient(parent)
    else:
        top = None
    f = ShowExceptionFrame(top, exc_type, exc_value, traceback_str)
    f.pack()
    f.mainloop()
    f.winfo_toplevel().destroy()

class AppWindow(Tkinter.Frame):
    """A GUI Window that can be subclassed for a main application window"""
    def __init__(self,master=None,idle_func=lambda: None,**cnf):
        VisionEgg.config._Tkinter_used = True
        Tkinter.Frame.__init__(self,master,**cnf)
        self.winfo_toplevel().title('Vision Egg')

        self.info_frame = InfoFrame(self)
        self.info_frame.pack()

        self.idle_func = idle_func
        self.after(1,self.idle) # register idle function with Tkinter

    def idle(self):
        self.idle_func()
        self.after(1,self.idle) # (re)register idle function with Tkinter

class ProgressBar(Tkinter.Frame):
    def __init__(self, master=None, orientation="horizontal",
                 min=0, max=100, width=100, height=18,
                 doLabel=1, fillColor="LightSteelBlue1", background="gray",
                 labelColor="black", labelFont="Helvetica",
                 labelText="", labelFormat="%d%%",
                 value=50, **cnf):
        Tkinter.Frame.__init__(self,master)
        # preserve various values
        self.master=master
        self.orientation=orientation
        self.min=min
        self.max=max
        self.width=width
        self.height=height
        self.doLabel=doLabel
        self.fillColor=fillColor
        self.labelFont= labelFont
        self.labelColor=labelColor
        self.background=background
        self.labelText=labelText
        self.labelFormat=labelFormat
        self.value=value
        self.canvas=Tkinter.Canvas(self, height=height, width=width, bd=0,
                                    highlightthickness=0, background=background)
        self.scale=self.canvas.create_rectangle(0, 0, width, height,
                                                fill=fillColor)
        self.label=self.canvas.create_text(self.canvas.winfo_reqwidth() / 2,
                                           height / 2, text=labelText,
                                           anchor="c", fill=labelColor,
                                           font=self.labelFont)
        self.update()
        self.canvas.pack(side='top', fill='x', expand='no')

    def updateProgress(self, newValue, newMax=None):
        if newMax:
            self.max = newMax
        self.value = newValue
        self.update()

    def update(self):
        # Trim the values to be between min and max
        value=self.value
        if value > self.max:
            value = self.max
        if value < self.min:
            value = self.min
        # Adjust the rectangle
        if self.orientation == "horizontal":
            self.canvas.coords(self.scale, 0, 0,
              float(value) / self.max * self.width, self.height)
        else:
            self.canvas.coords(self.scale, 0,
                               self.height - (float(value) /
                                              self.max*self.height),
                               self.width, self.height)
        # Now update the colors
        self.canvas.itemconfig(self.scale, fill=self.fillColor)
        self.canvas.itemconfig(self.label, fill=self.labelColor)
        # And update the label
        if self.doLabel:
            if value:
                if value >= 0:
                    pvalue = int((float(value) / float(self.max)) *
                                   100.0)
                else:
                    pvalue = 0
                self.canvas.itemconfig(self.label, text=self.labelFormat
                                         % pvalue)
            else:
                self.canvas.itemconfig(self.label, text='')
        else:
            self.canvas.itemconfig(self.label, text=self.labelFormat %
                                   self.labelText)
        self.canvas.update_idletasks()

class GraphicsConfigurationWindow(Tkinter.Frame):
    """Graphics Configuration Window"""
    def __init__(self,master=None,**cnf):
        VisionEgg.config._Tkinter_used = True
        Tkinter.Frame.__init__(self,master,**cnf)
        self.winfo_toplevel().title('Vision Egg - Graphics configuration')
        self.pack()

        self.clicked_ok = 0 # So we can distinguish between clicking OK and closing the window

        row = 0
        Tkinter.Label(self,
                      text="Vision Egg - Graphics configuration",
                      font=("Helvetica",14,"bold")).grid(row=row,columnspan=2)
        row += 1

        ################## begin topframe ##############################

        topframe = Tkinter.Frame(self)
        topframe.grid(row=row,column=0,columnspan=2)
        topframe_row = 0

        Tkinter.Label(topframe,
                      text=self.format_string("The default value for these variables and the presence of this dialog window can be controlled via the Vision Egg config file. If this file exists in the Vision Egg user directory, that file is used.  Otherwise, the configuration file found in the Vision Egg system directory is used."),
                      ).grid(row=topframe_row,column=1,columnspan=2,sticky=Tkinter.W)
        topframe_row += 1

        try:
            import _imaging, _imagingtk
            import ImageFile, ImageFileIO, BmpImagePlugin, JpegImagePlugin
            import Image,ImageTk
            im = Image.open(os.path.join(VisionEgg.config.VISIONEGG_SYSTEM_DIR,'data','visionegg.bmp'))
            self.tk_im=ImageTk.PhotoImage(im)
            Tkinter.Label(topframe,image=self.tk_im).grid(row=0,rowspan=topframe_row,column=0)
        except Exception,x:
            logger = logging.getLogger('VisionEgg.GUI')
            logger.info("No Vision Egg logo :( because of error while "
                        "trying to display image in "
                        "GUI.GraphicsConfigurationWindow: %s: "
                        "%s"%(str(x.__class__),str(x)))

        ################## end topframe ##############################

        row += 1

        ################## begin file_frame ##############################

        file_frame = Tkinter.Frame(self)
        file_frame.grid(row=row,columnspan=2,sticky=Tkinter.W+Tkinter.E,pady=5)

        # Script name and location
        file_row = 0
        Tkinter.Label(file_frame,
                      text="This script:").grid(row=file_row,column=0,sticky=Tkinter.E)
        Tkinter.Label(file_frame,
                      text="%s"%(os.path.abspath(sys.argv[0]),)).grid(row=file_row,column=1,sticky=Tkinter.W)
        file_row += 1
        # Vision Egg system dir
        Tkinter.Label(file_frame,
                      text="Vision Egg system directory:").grid(row=file_row,column=0,sticky=Tkinter.E)
        Tkinter.Label(file_frame,
                      text="%s"%(os.path.abspath(VisionEgg.config.VISIONEGG_SYSTEM_DIR),)).grid(row=file_row,column=1,sticky=Tkinter.W)
        file_row += 1

        # Vision Egg user dir
        Tkinter.Label(file_frame,
                      text="Vision Egg user directory:").grid(row=file_row,column=0,sticky=Tkinter.E)
        Tkinter.Label(file_frame,
                      text="%s"%(os.path.abspath(VisionEgg.config.VISIONEGG_USER_DIR),)).grid(row=file_row,column=1,sticky=Tkinter.W)
        file_row += 1

        # Config file
        Tkinter.Label(file_frame,
                      text="Config file location:").grid(row=file_row,column=0,sticky=Tkinter.E)
        if VisionEgg.config.VISIONEGG_CONFIG_FILE:
            Tkinter.Label(file_frame,
                          text="%s"%(os.path.abspath(VisionEgg.config.VISIONEGG_CONFIG_FILE),)).grid(row=file_row,column=1,sticky=Tkinter.W)
        else:
            Tkinter.Label(file_frame,
                          text="(None)").grid(row=file_row,column=1,sticky=Tkinter.W)
        file_row += 1

        # Log file location
        Tkinter.Label(file_frame,
                      text="Log file location:").grid(row=file_row,column=0,sticky=Tkinter.E)
        if VisionEgg.config.VISIONEGG_LOG_FILE:
            Tkinter.Label(file_frame,
                          text="%s"%(os.path.abspath(VisionEgg.config.VISIONEGG_LOG_FILE),)).grid(row=file_row,column=1,sticky=Tkinter.W)
        else:
            Tkinter.Label(file_frame,
                          text="(stderr console)").grid(row=file_row,column=1,sticky=Tkinter.W)

        ################## end file_frame ##############################

        row += 1

        ################## begin cf ##############################

        cf = Tkinter.Frame(self)
        cf.grid(row=row,column=0,padx=10)

        cf_row = 0
        # Fullscreen
        self.fullscreen = Tkinter.BooleanVar()
        self.fullscreen.set(VisionEgg.config.VISIONEGG_FULLSCREEN)
        Tkinter.Checkbutton(cf,
                            text='Fullscreen',
                            variable=self.fullscreen,
                            relief=Tkinter.FLAT).grid(row=cf_row,column=0,sticky=Tkinter.W)

        cf_row += 1
        self.synclync_present = Tkinter.BooleanVar()
        self.synclync_present.set(VisionEgg.config.SYNCLYNC_PRESENT)
        try:
            import synclync
            self.show_synclync_option = 1
        except:
            self.show_synclync_option = 0

        if self.show_synclync_option:
            Tkinter.Checkbutton(cf,
                                text='SyncLync device present',
                                variable=self.synclync_present,
                                relief=Tkinter.FLAT).grid(row=cf_row,column=0,sticky=Tkinter.W)


        cf_row += 1
        # Maximum priority
        self.maxpriority = Tkinter.BooleanVar()
        self.maxpriority.set(VisionEgg.config.VISIONEGG_MAXPRIORITY)

        Tkinter.Checkbutton(cf,
                            text='Maximum priority (use with caution)',
                            variable=self.maxpriority,
                            relief=Tkinter.FLAT).grid(row=cf_row,column=0,sticky=Tkinter.W)
        cf_row += 1

        if sys.platform=='darwin':
            # Only used on darwin platform
            self.darwin_conventional = Tkinter.IntVar()
            self.darwin_conventional.set(VisionEgg.config.VISIONEGG_DARWIN_MAXPRIORITY_CONVENTIONAL_NOT_REALTIME)
            self.darwin_priority = Tkinter.StringVar()
            self.darwin_priority.set(str(VisionEgg.config.VISIONEGG_DARWIN_CONVENTIONAL_PRIORITY))
            self.darwin_realtime_period_denom = Tkinter.StringVar()
            self.darwin_realtime_period_denom.set(str(VisionEgg.config.VISIONEGG_DARWIN_REALTIME_PERIOD_DENOM))
            self.darwin_realtime_computation_denom = Tkinter.StringVar()
            self.darwin_realtime_computation_denom.set(str(VisionEgg.config.VISIONEGG_DARWIN_REALTIME_COMPUTATION_DENOM))
            self.darwin_realtime_constraint_denom = Tkinter.StringVar()
            self.darwin_realtime_constraint_denom.set(str(VisionEgg.config.VISIONEGG_DARWIN_REALTIME_CONSTRAINT_DENOM))
            self.darwin_realtime_preemptible = Tkinter.BooleanVar()
            self.darwin_realtime_preemptible.set(not VisionEgg.config.VISIONEGG_DARWIN_REALTIME_PREEMPTIBLE)
            Tkinter.Button(cf,text="Maximum priority options...",
                           command=self.darwin_maxpriority_tune).grid(row=cf_row,column=0)
            cf_row += 1

        # Sync swap
        self.sync_swap = Tkinter.BooleanVar()
        self.sync_swap.set(VisionEgg.config.VISIONEGG_SYNC_SWAP)
        Tkinter.Checkbutton(cf,
                            text='Attempt vsync',
                            variable=self.sync_swap,
                            relief=Tkinter.FLAT).grid(row=cf_row,column=0,sticky=Tkinter.W)
        cf_row += 1

        # Frameless window
        self.frameless = Tkinter.BooleanVar()
        self.frameless.set(VisionEgg.config.VISIONEGG_FRAMELESS_WINDOW)
        Tkinter.Checkbutton(cf,
                            text='No frame around window',
                            variable=self.frameless,
                            relief=Tkinter.FLAT).grid(row=cf_row,column=0,sticky=Tkinter.W)
        cf_row += 1

        # Hide mouse
        self.mouse_visible = Tkinter.BooleanVar()
        self.mouse_visible.set(not VisionEgg.config.VISIONEGG_HIDE_MOUSE)
        Tkinter.Checkbutton(cf,
                            text='Mouse cursor visible',
                            variable=self.mouse_visible,
                            relief=Tkinter.FLAT).grid(row=cf_row,column=0,sticky=Tkinter.W)
        cf_row += 1

        # Stereo
        self.stereo = Tkinter.BooleanVar()
        self.stereo.set(VisionEgg.config.VISIONEGG_REQUEST_STEREO)
        Tkinter.Checkbutton(cf,
                            text='Stereo',
                            variable=self.stereo,
                            relief=Tkinter.FLAT).grid(row=cf_row,column=0,sticky=Tkinter.W)
        cf_row += 1

        if sys.platform == 'darwin':
            if sys.version == '2.2 (#11, Jan  6 2002, 01:00:42) \n[GCC 2.95.2 19991024 (release)]':
                if Tkinter.TkVersion == 8.4:
                    # The Tk in Bob Ippolito's kitchensink distro had
                    # a bug in Checkbutton
                    Tkinter.Label(cf,text="If you want to check any buttons\n(Mac OS X Tk 8.4a4 bug workaround):").grid(row=cf_row,column=0)
                    cf_row += 1
                    Tkinter.Button(cf,text="PRESS ME FIRST").grid(row=cf_row,column=0)
                    cf_row += 1

        ################## end cf ##############################

        ################## begin entry_frame ###################

        entry_frame = Tkinter.Frame(self)
        entry_frame.grid(row=row,column=1,padx=10,sticky="n")
        row += 1
        ef_row = 0

        # frame rate
        Tkinter.Label(entry_frame,text="What will your monitor refresh's rate be (Hz):").grid(row=ef_row,column=0,sticky=Tkinter.E)
        self.frame_rate = Tkinter.StringVar()
        self.frame_rate.set("%s"%str(VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ))
        Tkinter.Entry(entry_frame,textvariable=self.frame_rate).grid(row=ef_row,column=1,sticky=Tkinter.W)
        ef_row += 1

        # width
        Tkinter.Label(entry_frame,text="Window width (pixels):").grid(row=ef_row,column=0,sticky=Tkinter.E)
        self.width = Tkinter.StringVar()
        self.width.set("%s"%str(VisionEgg.config.VISIONEGG_SCREEN_W))
        Tkinter.Entry(entry_frame,textvariable=self.width).grid(row=ef_row,column=1,sticky=Tkinter.W)
        ef_row += 1

        # height
        Tkinter.Label(entry_frame,text="Window height (pixels):").grid(row=ef_row,column=0,sticky=Tkinter.E)
        self.height = Tkinter.StringVar()
        self.height.set("%s"%str(VisionEgg.config.VISIONEGG_SCREEN_H))
        Tkinter.Entry(entry_frame,textvariable=self.height).grid(row=ef_row,column=1,sticky=Tkinter.W)
        ef_row += 1

        # color depth
        Tkinter.Label(entry_frame,text="Requested total color depth (bits per pixel):").grid(row=ef_row,column=0,sticky=Tkinter.E)
        self.color_depth = Tkinter.StringVar()
        self.color_depth.set(str(VisionEgg.config.VISIONEGG_PREFERRED_BPP))
        Tkinter.Entry(entry_frame,textvariable=self.color_depth).grid(row=ef_row,column=1,sticky=Tkinter.W)
        ef_row += 1

        # red depth
        Tkinter.Label(entry_frame,text="Requested red bits per pixel:").grid(row=ef_row,column=0,sticky=Tkinter.E)
        self.red_depth = Tkinter.StringVar()
        self.red_depth.set(str(VisionEgg.config.VISIONEGG_REQUEST_RED_BITS))
        Tkinter.Entry(entry_frame,textvariable=self.red_depth).grid(row=ef_row,column=1,sticky=Tkinter.W)
        ef_row += 1

        # green depth
        Tkinter.Label(entry_frame,text="Requested green bits per pixel:").grid(row=ef_row,column=0,sticky=Tkinter.E)
        self.green_depth = Tkinter.StringVar()
        self.green_depth.set(str(VisionEgg.config.VISIONEGG_REQUEST_GREEN_BITS))
        Tkinter.Entry(entry_frame,textvariable=self.green_depth).grid(row=ef_row,column=1,sticky=Tkinter.W)
        ef_row += 1

        # blue depth
        Tkinter.Label(entry_frame,text="Requested blue bits per pixel:").grid(row=ef_row,column=0,sticky=Tkinter.E)
        self.blue_depth = Tkinter.StringVar()
        self.blue_depth.set(str(VisionEgg.config.VISIONEGG_REQUEST_BLUE_BITS))
        Tkinter.Entry(entry_frame,textvariable=self.blue_depth).grid(row=ef_row,column=1,sticky=Tkinter.W)
        ef_row += 1

        # alpha depth
        Tkinter.Label(entry_frame,text="Requested alpha bits per pixel:").grid(row=ef_row,column=0,sticky=Tkinter.E)
        self.alpha_depth = Tkinter.StringVar()
        self.alpha_depth.set(str(VisionEgg.config.VISIONEGG_REQUEST_ALPHA_BITS))
        Tkinter.Entry(entry_frame,textvariable=self.alpha_depth).grid(row=ef_row,column=1,sticky=Tkinter.W)
        ef_row += 1

        ################## end entry_frame ###################

        ################## gamma_frame ###################

        # gamma stuff
        row += 1
        gamma_frame = Tkinter.Frame(self)
        gamma_frame.grid(row=row,columnspan=2,sticky="we")
        self.gamma_source = Tkinter.StringVar()
        self.gamma_source.set(str(VisionEgg.config.VISIONEGG_GAMMA_SOURCE).lower()) # can be 'none', 'invert', or 'file'
        Tkinter.Label(gamma_frame,
                      text="Gamma:").grid(row=0,column=0)
        Tkinter.Radiobutton(gamma_frame,
                            text="Native",
                            value="none",
                            variable = self.gamma_source).grid(row=0,column=1,padx=1)
        Tkinter.Radiobutton(gamma_frame,
                            text="Quick",
                            value="invert",
                            variable = self.gamma_source).grid(row=0,column=2)
        Tkinter.Label(gamma_frame,
                      text="R:").grid(row=0,column=3)
        self.gamma_invert_red = Tkinter.DoubleVar()
        self.gamma_invert_red.set( VisionEgg.config.VISIONEGG_GAMMA_INVERT_RED )
        Tkinter.Entry(gamma_frame,
                      textvariable=self.gamma_invert_red,
                      width=3).grid(row=0,column=4)
        Tkinter.Label(gamma_frame,
                      text="G:").grid(row=0,column=5)
        self.gamma_invert_green = Tkinter.DoubleVar()
        self.gamma_invert_green.set( VisionEgg.config.VISIONEGG_GAMMA_INVERT_GREEN )
        Tkinter.Entry(gamma_frame,
                      textvariable=self.gamma_invert_green,
                      width=3).grid(row=0,column=6)
        Tkinter.Label(gamma_frame,
                      text="B:").grid(row=0,column=7)
        self.gamma_invert_blue = Tkinter.DoubleVar()
        self.gamma_invert_blue.set( VisionEgg.config.VISIONEGG_GAMMA_INVERT_BLUE )
        Tkinter.Entry(gamma_frame,
                      textvariable=self.gamma_invert_blue,
                      width=3).grid(row=0,column=8)
        Tkinter.Radiobutton(gamma_frame,
                            text="Custom:",
                            value="file",
                            variable = self.gamma_source).grid(row=0,column=9)
        self.gamma_file = Tkinter.StringVar()
        if os.path.isfile(VisionEgg.config.VISIONEGG_GAMMA_FILE):
            self.gamma_file.set( VisionEgg.config.VISIONEGG_GAMMA_FILE )
        else:
            self.gamma_file.set("")
        Tkinter.Entry(gamma_frame,
                      textvariable=self.gamma_file,
                      width=15).grid(row=0,column=10)
        Tkinter.Button(gamma_frame,
                       command=self.set_gamma_file,
                       text="Set...").grid(row=0,column=11)

        ################## end gamma_frame ###################

        row += 1
        bf = Tkinter.Frame(self)
        bf.grid(row=row,columnspan=2,sticky=Tkinter.W+Tkinter.E)

        # Save settings to config file
        b = Tkinter.Button(bf,text="Save current settings to config file",command=self.save)
        b.grid(row=0,column=0,padx=20)
        b.bind('<Return>',self.start)

        # Start button
        b2 = Tkinter.Button(bf,text="ok",command=self.start)
        b2.grid(row=0,column=1,padx=20)
        b2.focus_force()
        b2.bind('<Return>',self.start)

        # Raise our application on darwin
        if sys.platform == 'darwin':
            try:
                # from Jack Jansen email 20 April 2003
                # WMAvailable() returns true if you can use the window
                # manager, and as a side #effect it raises the
                # application to the foreground.
                import MacOS
                if not MacOS.WMAvailable():
                    raise "Cannot reach the window manager"
            except:
                pass

    def set_gamma_file(self,dummy_arg=None):
        filename = tkFileDialog.askopenfilename(
            parent=self,
            defaultextension=".ve_gamma",
            filetypes=[('Configuration file','*.ve_gamma')],
            initialdir=VisionEgg.config.VISIONEGG_USER_DIR)
        if not filename:
            return
        self.gamma_file.set(filename)

    def format_string(self,in_str):
        # This probably a slow way to do things, but it works!
        min_line_length = 60
        in_list = in_str.split()
        out_str = ""
        cur_line = ""
        for word in in_list:
            cur_line = cur_line + word + " "
            if len(cur_line) > min_line_length:
                out_str = out_str + cur_line[:-1] + "\n"
                cur_line = "    "
        out_str = out_str + cur_line + "\n"
        return out_str

    def darwin_maxpriority_tune(self):
        class DarwinFineTuneDialog(ToplevelDialog):
            def __init__(self,parent,**cnf):
                # Bugs in Tk 8.4a4 for Darwin seem to prevent use of "grid" in this dialog
                ToplevelDialog.__init__(self,**cnf)
                self.title("Fine tune maximum priority")
                f = Tkinter.Frame(self)
                f.pack(expand=1,fill=Tkinter.BOTH,ipadx=2,ipady=2)
                row = 0
                Tkinter.Label(f,
                              text=parent.format_string(

                    """This information is used by the Vision Egg when
                    in "maximum priority" mode.  These values fine
                    tune this behavior on the Mac OS X ("darwin")
                    platform. For conventional priority, the valid
                    values range from -20 (highest priority) to 20
                    (worst priority).  In the realtime settings, the
                    numerical values represent a fraction of the total
                    cycles available on the computer. For more
                    information, please refer to
                    http://developer.apple.com/ techpubs/ macosx/
                    Darwin/ General/ KernelProgramming/ scheduler/
                    Using_Mach__pplications.html Hint: Try the
                    realtime task method with the framerate as the
                    denominator.  """

                    )).grid(row=row,columnspan=4,column=0)
                row = 1
#                Tkinter.Checkbutton(f,text="Use conventional priority",variable=parent.darwin_conventional).grid(row=row,column=0,columnspan=4)
                row = 2
#                Tkinter.Label(f,text="Conventional priority settings").grid(row=row,column=0,columnspan=2)
                Tkinter.Radiobutton(f,
                              text="Conventional priority method",
                              variable=parent.darwin_conventional,
                              value=1).grid(row=row,column=0,columnspan=2)
                row += 1
                Tkinter.Label(f,text="Priority").grid(row=row,column=0,sticky=Tkinter.E)
                Tkinter.Entry(f,textvariable=parent.darwin_priority).grid(row=row,column=1,sticky=Tkinter.W)
                row = 2
                Tkinter.Radiobutton(f,
                              text="Realtime task method",
                              variable=parent.darwin_conventional,
                              value=0).grid(row=row,column=2,columnspan=2)
#                Tkinter.Label(f,text="Realtime settings").grid(row=row,column=2,columnspan=2)
                row += 1
                Tkinter.Label(f,text="Realtime period denominator").grid(row=row,column=2,sticky=Tkinter.E)
                Tkinter.Entry(f,textvariable=parent.darwin_realtime_period_denom).grid(row=row,column=3,sticky=Tkinter.W)
                row += 1
                Tkinter.Label(f,text="Realtime computation denominator").grid(row=row,column=2,sticky=Tkinter.E)
                Tkinter.Entry(f,textvariable=parent.darwin_realtime_computation_denom).grid(row=row,column=3,sticky=Tkinter.W)
                row += 1
                Tkinter.Label(f,text="Realtime constraint denominator").grid(row=row,column=2,sticky=Tkinter.E)
                Tkinter.Entry(f,textvariable=parent.darwin_realtime_constraint_denom).grid(row=row,column=3,sticky=Tkinter.W)
                row += 1
                Tkinter.Checkbutton(f,text="Do not preempt",variable=parent.darwin_realtime_preemptible).grid(row=row,column=2,columnspan=2)
                row += 1
                Tkinter.Button(f, text="ok",command=self.ok).grid(row=row,column=0,columnspan=4)
                self.wait_window(self)

            def ok(self):
                self.destroy()

        DarwinFineTuneDialog(parent=self)

    def _set_config_values(self):
        VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ = float(self.frame_rate.get())
        VisionEgg.config.VISIONEGG_FULLSCREEN = self.fullscreen.get()
        VisionEgg.config.VISIONEGG_GAMMA_SOURCE = self.gamma_source.get()
        VisionEgg.config.VISIONEGG_GAMMA_INVERT_RED = self.gamma_invert_red.get()
        VisionEgg.config.VISIONEGG_GAMMA_INVERT_GREEN = self.gamma_invert_green.get()
        VisionEgg.config.VISIONEGG_GAMMA_INVERT_BLUE = self.gamma_invert_blue.get()
        VisionEgg.config.VISIONEGG_GAMMA_FILE = self.gamma_file.get()
        VisionEgg.config.VISIONEGG_MAXPRIORITY = self.maxpriority.get()
        VisionEgg.config.VISIONEGG_SYNC_SWAP = self.sync_swap.get()
        VisionEgg.config.VISIONEGG_FRAMELESS_WINDOW = self.frameless.get()
        VisionEgg.config.VISIONEGG_HIDE_MOUSE = not self.mouse_visible.get()
        VisionEgg.config.VISIONEGG_REQUEST_STEREO = self.stereo.get()
        VisionEgg.config.VISIONEGG_SCREEN_W = int(self.width.get())
        VisionEgg.config.VISIONEGG_SCREEN_H = int(self.height.get())
        VisionEgg.config.VISIONEGG_PREFERRED_BPP = int(self.color_depth.get())
        VisionEgg.config.VISIONEGG_REQUEST_RED_BITS = int(self.red_depth.get())
        VisionEgg.config.VISIONEGG_REQUEST_GREEN_BITS = int(self.green_depth.get())
        VisionEgg.config.VISIONEGG_REQUEST_BLUE_BITS = int(self.blue_depth.get())
        VisionEgg.config.VISIONEGG_REQUEST_ALPHA_BITS = int(self.alpha_depth.get())

        if sys.platform=='darwin':
            # Only used on darwin platform
            VisionEgg.config.VISIONEGG_DARWIN_MAXPRIORITY_CONVENTIONAL_NOT_REALTIME = self.darwin_conventional.get()
            VisionEgg.config.VISIONEGG_DARWIN_CONVENTIONAL_PRIORITY = int(self.darwin_priority.get())
            VisionEgg.config.VISIONEGG_DARWIN_REALTIME_PERIOD_DENOM = int(self.darwin_realtime_period_denom.get())
            VisionEgg.config.VISIONEGG_DARWIN_REALTIME_COMPUTATION_DENOM = int(self.darwin_realtime_computation_denom.get())
            VisionEgg.config.VISIONEGG_DARWIN_REALTIME_CONSTRAINT_DENOM = int(self.darwin_realtime_constraint_denom.get())
            VisionEgg.config.VISIONEGG_DARWIN_REALTIME_PREEMPTIBLE = int(not self.darwin_realtime_preemptible.get())

        if self.show_synclync_option:
            VisionEgg.config.SYNCLYNC_PRESENT = self.synclync_present.get()

    def save(self,dummy_arg=None):
        self._set_config_values()
        try:
            VisionEgg.Configuration.save_settings()
        except IOError, x:
            try:
                import tkMessageBox
                if str(x).find('Permission denied') != -1:
                    tkMessageBox.showerror(title="Permission denied",
                                           message="Permission denied when trying to save settings.\n\nTry making a copy of the config file in the Vision Egg user directory %s and making sure you have write permission."%(os.path.abspath(VisionEgg.config.VISIONEGG_USER_DIR),))
            except:
                raise x

    def start(self,dummy_arg=None):
        self.clicked_ok = 1
        self._set_config_values()
        for child in self.children.values():
            child.destroy()
        Tkinter.Tk.destroy(self.master) # OK, now close myself

class InfoFrame(Tkinter.Frame):
    def __init__(self,master=None,**cnf):
        VisionEgg.config._Tkinter_used = True
        Tkinter.Frame.__init__(self,master,**cnf)

        Tkinter.Label(self,text="Vision Egg information:").pack()
        self.sub_frame = Tkinter.Frame(self,relief=Tkinter.GROOVE)
        self.sub_frame.pack()
        self.update()

    def update(self):
        for child in self.sub_frame.children.values():
            child.destroy()
        if VisionEgg.config.VISIONEGG_FULLSCREEN:
            Tkinter.Label(self.sub_frame,text="fullscreen mode").pack()
        else:
            Tkinter.Label(self.sub_frame,text="window mode").pack()
##        if VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION:
##            Tkinter.Label(self.sub_frame,text="Texture compression on").pack()
##        else:
##            Tkinter.Label(self.sub_frame,text="Texture compression off").pack()

        #Tkinter.Button(self.sub_frame,text="Update information",command=self.update).pack()

class ToplevelDialog(Tkinter.Toplevel):
    """Base class for a dialog that runs on the top level."""
    def __init__(self,**kw):
        VisionEgg.config._Tkinter_used = True
        Tkinter.Toplevel.__init__(self,**kw)
        self.transient(self)

    def destroy(self):
        Tkinter.Toplevel.destroy(self)

class GetKeypressDialog(ToplevelDialog):
    """Open a dialog box which returns when a valid key is pressed.

    Arguments are:
    master - a Tkinter widget (defaults to None)
    title - a string for the title bar of the widget
    text - a string to display as the text in the body of the dialog
    key_list - a list of acceptable keys, e.g. ['q','1','2','<Return>']

    The following example will print whatever character was pressed:
    d = GetKeypressDialog(key_list=['q','1','2','<Return>','<Escape>'])
    print d.result

    The implementation is somewhat obscure because a new Tk/Tcl
    interpreter may be created if this Dialog is called with no
    master widget."""
    def __init__(self,
                 title="Press a key",
                 text="Press a key",
                 key_list=[],
                 **kw):

        ToplevelDialog.__init__(self,**kw)
        self.title(title)
        self.result = None

        # The dialog box body
        Tkinter.Label(self.frame, text=text).pack()

        for key in key_list:
            self.bind(key,self.keypress)
        self.wait_window(self)

    def keypress(self,tkinter_event):
        self.result = tkinter_event.keysym
        self.destroy()
