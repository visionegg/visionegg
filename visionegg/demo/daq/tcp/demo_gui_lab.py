#!/usr/bin/env python

import sys, socket, re, time, string
import Numeric, MLab
import Tkinter, tkMessageBox, tkSimpleDialog
import VisionEgg.Daq, VisionEgg.DaqOverTCP

class DataCanvas(Tkinter.Canvas):
    color_order = ['red','green','blue']
    axis_inset = 40
    def __init__(self,master=None,**kw):
        apply(Tkinter.Canvas.__init__,(self,master),kw)
        
        tk = self.winfo_toplevel()
        width, height = tk.getint(self['width']), tk.getint(self['height'])

        self.data_box = DataCanvas.axis_inset, height-DataCanvas.axis_inset, width-DataCanvas.axis_inset, DataCanvas.axis_inset
        x1,y1,x2,y2 = self.data_box
        
        self.xaxis = self.create_line(x1,y1,x2,y1,
                                      fill='black')
        self.yaxis = self.create_line(x1,y1,x1,y2,
                                      fill='black')

        self.xmin_tag = self.create_text( x1,y1,
                                          anchor="n")
        self.xmax_tag = self.create_text( x2,y1,
                                          anchor="n")
        self.ymin_tag = self.create_text( x1,y1,
                                          anchor="e")
        self.ymax_tag = self.create_text( x1,y2,
                                          anchor="e")

        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self.sync_axis_tags()
        self.waves = {}

    def sync_axis_tags(self):
        fmt = "%.1f"
        if self.xmin is None:
            self.itemconfigure(self.xmin_tag,text='')
        else:
            self.itemconfigure(self.xmin_tag,text=fmt%(self.xmin,))
        if self.xmax is None:
            self.itemconfigure(self.xmax_tag,text='')
        else:
            self.itemconfigure(self.xmax_tag,text=fmt%(self.xmax,))
        if self.ymin is None:
            self.itemconfigure(self.ymin_tag,text='')
        else:
            self.itemconfigure(self.ymin_tag,text=fmt%(self.ymin,))
            
        if self.ymax is None:
            self.itemconfigure(self.ymax_tag,text='')
        else:
            self.itemconfigure(self.ymax_tag,text=fmt%(self.ymax,))
            
    def add_channel(self,channel):
        gain = channel.constant_parameters.signal_type.constant_parameters.gain
        #print "gain",gain
        tmax = channel.constant_parameters.daq_mode.parameters.duration_sec
        tsamp = 1.0/channel.constant_parameters.daq_mode.parameters.sample_rate_hz
        times = Numeric.arange(0.0,tmax,tsamp)
        data = gain*channel.constant_parameters.functionality.get_data()

        data_max = MLab.max(data)
        data_min = MLab.min(data)

        tk = self.winfo_toplevel()
        width, height = tk.getint(self['width']), tk.getint(self['height'])
        self.data_box = DataCanvas.axis_inset, height-DataCanvas.axis_inset, width-DataCanvas.axis_inset, DataCanvas.axis_inset
        x1,y1,x2,y2 = self.data_box

        self.xmin = 0.0
        self.xmax = tmax

        self.ymin = data_min
        self.ymax = data_max
        for wave in self.waves.keys():
            old_channel,old_ymin,old_ymax,old_color = self.waves[wave]
            self.ymin = min(self.ymin,old_ymin)
            self.ymax = max(self.ymax,old_ymax)

        scale = (x2-x1)/float(tmax), (y2-y1)/float(self.ymax-self.ymin)
        offset = float(x1), -self.ymax*scale[1]+float(y2)

        #print "scale",scale
        #print "offset",offset
        x = times*scale[0] + offset[0]
        y = data *scale[1] + offset[1]

        args = []
        for i in xrange(times.shape[0]):
            args.append(x[i])
            args.append(y[i])
        color = DataCanvas.color_order[ len(self.waves.keys()) % len(DataCanvas.color_order) ]
        new_waves = [ (apply(self.create_line,args,{'fill':color}),channel,color) ]
            
        # re-evaluate old waves here
        for wave in self.waves.keys():
            old_channel,ymin,ymax,old_color = self.waves[wave]
            gain = old_channel.constant_parameters.signal_type.constant_parameters.gain
            #print "gain",gain
            tmax = old_channel.constant_parameters.daq_mode.parameters.duration_sec
            tsamp = 1.0/old_channel.constant_parameters.daq_mode.parameters.sample_rate_hz
            times = Numeric.arange(0.0,tmax,tsamp)
            data = gain*old_channel.constant_parameters.functionality.get_data()
            
            scale = (x2-x1)/float(tmax), (y2-y1)/float(self.ymax-self.ymin)
            offset = float(x1), -self.ymax*scale[1]+float(y2)

            x = times*scale[0] + offset[0]
            y = data *scale[1] + offset[1]

            args = []
            for i in xrange(times.shape[0]):
                args.append(x[i])
                args.append(y[i])
            new_waves.append( (apply(self.create_line,args,{'fill':old_color}),old_channel,old_color) )
            # delete original wave
            self.delete(wave)
            del self.waves[wave]

        for new_wave,channel,color in new_waves:
            self.waves[ new_wave ] = (channel,self.ymin,self.ymax,color)
        self.sync_axis_tags()

    def redraw(self):
        tk = self.winfo_toplevel()
        width, height = tk.getint(self['width']), tk.getint(self['height'])
        self.data_box = DataCanvas.axis_inset, height-DataCanvas.axis_inset, width-DataCanvas.axis_inset, DataCanvas.axis_inset
        x1,y1,x2,y2 = self.data_box
        for wave in self.waves.keys():
            old_channel,ymin,ymax,old_color = self.waves[wave]
            gain = old_channel.constant_parameters.signal_type.constant_parameters.gain
            #print "gain",gain
            tmax = old_channel.constant_parameters.daq_mode.parameters.duration_sec
            tsamp = 1.0/old_channel.constant_parameters.daq_mode.parameters.sample_rate_hz
            times = Numeric.arange(0.0,tmax,tsamp)
            data = gain*old_channel.constant_parameters.functionality.get_data()
            
            scale = (x2-x1)/float(tmax), (y2-y1)/float(self.ymax-self.ymin)
            offset = float(x1), -self.ymax*scale[1]+float(y2)

            x = times*scale[0] + offset[0]
            y = data *scale[1] + offset[1]

            args = []
            for i in xrange(times.shape[0]):
                args.append(x[i])
                args.append(y[i])
            new_waves.append( (apply(self.create_line,args,{'fill':old_color}),old_channel,old_color) )
            # delete original wave
            self.delete(wave)
            del self.waves[wave]

        for new_wave,channel,color in new_waves:
            self.waves[ new_wave ] = (channel,self.ymin,self.ymax,color)
            
    def clear(self):
        for wave in self.waves.keys():
            self.delete(wave)
        self.waves = {}
        
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self.sync_axis_tags()

class AppWindow(Tkinter.Frame):
    def __init__(self,master=None,
                 hostname="localhost",
                 port=50003,
                 **cnf):
        # create and pack myself
        apply(Tkinter.Frame.__init__, (self,master), cnf)
        self.pack(expand=1,fill=Tkinter.BOTH)

        # Some initial guess values
        self.daq_hostname = Tkinter.StringVar()
        self.daq_hostname.set(hostname)

        self.daq_port = Tkinter.IntVar()
        self.daq_port.set(port)

        # server's trigger
        self.trigger=VisionEgg.DaqOverTCP.DaqServerTrigger()

        # create a menu bar
        self.bar = Tkinter.Frame(self, name='bar',
                                 relief=Tkinter.RAISED, borderwidth=2)
        self.bar.pack(fill=Tkinter.X)
        self.bar.file = BarButton(self.bar, text='File')
        self.bar.file.menu.add_command(label='Quit', command=self.quit)

        self.bar.daq_server = BarButton(self.bar, text='DAQ server')
        
        self.bar.daq_server.menu.add_command(label='Set DAQ server hostname', command=self.daq_set_hostname)
        self.bar.daq_server.menu.add_command(label='Set DAQ server port', command=self.daq_set_port)
        self.bar.daq_server.menu.add_command(label='Connect to DAQ server', command=self.daq_connect)
        self.bar.daq_server.menu.add_command(label='Disonnect from DAQ server', command=self.daq_close)
        self.bar.daq_server.menu.add_command(label='Close DAQ server', command=self.daq_quit_server)

        self.bar.channel_settings = BarButton(self.bar, text='Channel settings')
        self.bar.channel_settings.menu.add_command(label='Add channel',command=self.add_channel)
        self.bar.channel_settings.menu.add_command(label='Set gain',command=self.set_gain)
        
        self.bar.tk_menuBar(self.bar.file, self.bar.daq_server, self.bar.channel_settings)

        self.data_canvas = DataCanvas(self,bg='white')
        self.data_canvas.pack(expand=1,fill=Tkinter.BOTH)

        self.go = Tkinter.Button(self, text='Arm trigger/Go', command=self.arm)
        self.go.pack()

        self.tcp_daq_device = None
        self.channels = []
        self.gain = 0.2048

    def add_channel(self):
        print "Using default channel parameters, fix later..."
        channel = VisionEgg.DaqOverTCP.DaqServerChannel(
            channel_number=len(self.channels),
            daq_mode=VisionEgg.Daq.Buffered(trigger=self.trigger,
                                            sample_rate_hz=1000.0,
                                            duration_sec=0.1),
            signal_type=VisionEgg.Daq.Analog(gain=self.gain),
            functionality=VisionEgg.DaqOverTCP.DaqServerInputChannel()
            )
        self.channels.append(channel)
        if self.tcp_daq_device is not None:
            #channel.set_my_device(self.tcp_daq_device)
            self.tcp_daq_device.add_channel(channel)
        
    def arm(self):
        if self.tcp_daq_device is None:
            raise RuntimeError("Not connected to DAQ server!")
        if len(self.channels) < 1:
            raise RuntimeError("Must have 1 or more channels.")
        self.channels[0].arm_trigger()

        self.data_canvas.clear()
        for channel in self.channels:
            data = channel.constant_parameters.functionality.get_data()
            self.data_canvas.add_channel(channel)

    def set_gain(self):
        self.gain = tkSimpleDialog.askfloat("Gain","Gain",initialvalue=self.gain)

    def daq_set_hostname(self):
        try:
            self.daq_hostname.set( tkSimpleDialog.askstring("Hostname","DAQ Server hostname",initialvalue=self.daq_hostname.get()))
        except Exception, x:
            tkMessageBox.showerror(title=str(x.__class__),message=str(x))
            raise

    def daq_set_port(self):
        try:
            self.daq_port.set( tkSimpleDialog.askstring("Port","DAQ Server port",initialvalue=self.daq_port.get()))
        except Exception, x:
            tkMessageBox.showerror(title=str(x.__class__),message=str(x))
            raise

    def daq_connect(self):
        # Could get parameters via a dialog box
        try:
            app.winfo_toplevel().config(cursor="watch")
            #time.sleep(0.1) # sleep to give cursor time to change?
            self.tcp_daq_device = VisionEgg.DaqOverTCP.TCPDaqDevice(
                hostname=self.daq_hostname.get(),
                port=self.daq_port.get())
            app.winfo_toplevel().config(cursor="")

            if len(self.channels):
                for channel in self.channels:
                    channel.set_my_device(self)
                    self.add_channel(channel)
            
        except Exception,x:
            app.winfo_toplevel().config(cursor="")
            tkMessageBox.showerror(title=str(x.__class__),message=str(x))
            raise
            
    def daq_close(self):
        try:
            if self.tcp_daq_device:
                self.tcp_daq_device = None
            else:
                raise RuntimeError("Couldn't disconnect from DAQ server, because not connected!")
        except Exception,x:
            tkMessageBox.showerror(title=str(x.__class__),message=str(x))
            raise

    def daq_quit_server(self):
        try:
            if self.tcp_daq_device:
                self.tcp_daq_device.quit_server()
                self.tcp_daq_device = None
            else:
                raise RuntimeError("Couldn't close DAQ server, because not connected!")
        except Exception,x:
            tkMessageBox.showerror(title=str(x.__class__),message=str(x))
            raise

    def quit(self):
        self.tcp_daq_device = None # close any existing DAQ connection
        apply(Tkinter.Frame.quit, (self,))
        
class BarButton(Tkinter.Menubutton):
    # Taken from Guido van Rossum's Tkinter svkill demo
        def __init__(self, master=None, **cnf):
                apply(Tkinter.Menubutton.__init__, (self, master), cnf)
                self.pack(side=Tkinter.LEFT)
                self.menu = Tkinter.Menu(self, name='menu')
                self['menu'] = self.menu
                
class Blahbject:
    """Encapsulates objects to have useful methods when used in GUI"""
    def __init__(self):
        raise RuntimeError("Abstract base class!")
    def get_str_30(self):
        return "**** this is a generic str_30 ****"
    def get_contained(self):
        return self.contained
    header = "unknown parameters"

def make_blah(container_class):
    """Factory function for Blahbject"""
    params = {}
    p = container_class.contained_class.parameters_and_defaults
    keys = p.keys()
    keys.sort()
    for pname in keys:
        if type(p[pname]) == types.StringType:
            params[pname] = tkSimpleDialog.askstring(pname,pname,initialvalue=p[pname])
        if type(p[pname]) == types.IntType:
            params[pname] = tkSimpleDialog.askinteger(pname,pname,initialvalue=p[pname])
        if type(p[pname]) == types.FloatType:
            params[pname] = tkSimpleDialog.askfloat(pname,pname,initialvalue=p[pname])
    contained = container_class.contained_class(**params)
    return container_class(contained)

def make_blah_defaults(container_class):
    """Factory function for Blahbject"""
    contained = container_class.contained_class()
    return container_class(contained)

class ScrollListFrame(Tkinter.Frame):
    def __init__(self,master=None,list_of_blahbjects=None,blahbject_maker=None,
                 container_class=Blahbject,
                 title='Blah',**cnf):
        apply(Tkinter.Frame.__init__, (self,master), cnf)
        if list_of_blahbjects is None:
            self.list = []
        else:
            self.list = list_of_blahbjects
        self.container_class = container_class

        # title
        Tkinter.Label(self,text=title).pack(fill=Tkinter.X)
        
        # The frame that has the list and the vscroll
        self.frame = Tkinter.Frame(self,borderwidth=2)
        self.frame.pack(fill=Tkinter.BOTH)
        self.header = Tkinter.StringVar(self)
        self.frame.label = Tkinter.Label(self.frame, relief=Tkinter.FLAT,anchor=Tkinter.NW,borderwidth=0,
                                 font='*-Courier-Bold-R-Normal-*',
                                 textvariable=self.header)
        self.frame.label.pack(fill=Tkinter.Y,anchor=Tkinter.W)

        self.frame.vscroll = Tkinter.Scrollbar(self.frame,orient=Tkinter.VERTICAL)
        self.frame.list = Tkinter.Listbox(
            self.frame,
            relief=Tkinter.SUNKEN,
            font='*-Courier-Medium-R-Normal-*',
            width=40, height=10,
            selectbackground='#eed5b7',
            selectborderwidth=0,
            selectmode=Tkinter.BROWSE,
            yscroll=self.frame.vscroll.set)
                                          
        self.frame.vscroll['command'] = self.frame.list.yview
        self.frame.vscroll.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.frame.list.pack(fill=Tkinter.BOTH)
        self.frame.list.bind('<Double-Button-1>',self.edit_selected)
        
        # The buttons on bottom
        self.bar = Tkinter.Frame(self,borderwidth=2)
        self.bar.pack(fill=Tkinter.X)
        self.bar.add = Tkinter.Button(self.bar,text='Add...',command=self.add_new)
        self.bar.add.pack(side=Tkinter.LEFT,fill=Tkinter.X)
##        self.bar.add_defaults = Tkinter.Button(self.bar,text='Add defaults',command=self.add_new_defaults)
##        self.bar.add_defaults.pack(side=Tkinter.LEFT,fill=Tkinter.X)
##        self.bar.edit = Tkinter.Button(self.bar,text='Edit...',command=self.edit_selected)
##        self.bar.edit.pack(side=Tkinter.LEFT,fill=Tkinter.X)
        self.bar.remove = Tkinter.Button(self.bar,text='Remove',command=self.remove_selected)
        self.bar.remove.pack(side=Tkinter.LEFT,fill=Tkinter.X)
##        self.bar.tk_menuBar(self.bar.add,self.bar.add_defaults,self.bar.edit,self.bar.remove)
        self.bar.tk_menuBar(self.bar.add,self.bar.remove)
        self.update_now()
        
    def get_list_uncontained(self):
        results = []
        for blah_item in self.list:
            results.append( blah_item.get_contained() )
        return results

    def update_now(self):
        self.header.set(self.container_class.header)
        self.frame.list.delete(0,Tkinter.AtEnd())
        for item in self.list:
            self.frame.list.insert(Tkinter.END,item.get_str_30())

    def add_new(self):
        self.list.append( make_blah(self.container_class) )
        self.update_now()

    def add_new_defaults(self):
        self.list.append( make_blah_defaults(self.container_class) )
        self.update_now()

    def get_selected(self):
        items = self.frame.list.curselection()
        try:
            items = map(int, items)
        except ValueError: pass
        if len(items) > 0:
            return items[0]
        else:
            return None

    def edit_selected(self,dummy=None):
        try:
            raise NotImplementedError("You want to edit item %d, but the code isn't done!"%self.get_selected())
        except Exception,x:
            tkMessageBox.showerror(title=str(x.__class__),message=str(x))
            raise
        
    def remove_selected(self):
        selected = self.get_selected()
        if selected is not None:
            del self.list[self.get_selected()]
            self.update_now()

if __name__ == '__main__':
    if len(sys.argv) == 3:
        app = AppWindow(None,hostname=sys.argv[1],port=int(sys.argv[2]),borderwidth=5)
    elif len(sys.argv) == 2:
        app = AppWindow(None,hostname=sys.argv[1],borderwidth=5)
    else:
        app = AppWindow(None,borderwidth=5)
    app.winfo_toplevel().title("Vision Egg DAQ")
    app.winfo_toplevel().minsize(1,1)
    app.mainloop()
