#!/usr/bin/env python
"""gratingGUI.py -- Control stimulus produced by gratingTCP.py

When used with the gratingTCP demo, this is a near-complete
application for use in experiments.

Because this program sends commands to the Vision Egg only over TCP,
it can serve as a template for control of the Vision Egg via a TCP
connection from any language capable of making such a connection.

The most dominant source of complexity in this code is GUI creation,
followed by Python code to do networking and parse strings. To use the
Vision Egg over the TCP, you don't need to know Python (either for
networking or GUI creation).  Therefore, it would be instructive to
see what is sent over the TCP port without delving into this code.  If
you set the variable "log_tcp_commands" below, the program will save a
copy of everything sent over the TCP port.  That may be more
instructive than trying to understand this code!

Also, if you do want to exercise control from Python on a remote
computer, I highly recommend using Pyro rather than dealing with this
kind of stuff!"""

# Note that the Vision Egg is not imported!
# This script can be run on computers without the Vision Egg installed
import Tkinter, tkMessageBox
import sys, socket, time, select, re, string, types, traceback
import Numeric, math

# Save a copy of everything sent?
log_stream = sys.stdout

BUFSIZE = 4096

class SocketChecker:
    _re_controllable = re.compile(r'^"(.*)" controllable with this connection.$',re.MULTILINE)
    _re_error_line = re.compile(r"^(Error.*)\n",re.MULTILINE)
    def __init__(self,my_socket,starting_buffer,name_dict):
        self.socket = my_socket
        if starting_buffer is None:
            self.buffer = ""
        else:
            self.buffer = starting_buffer
        self.name_dict = name_dict
        self.name_handler = {}
        self.first_check_done = 0

    def check(self):
        # Check to see if anything has happened on the socket
        try:
            fileno = self.socket.fileno()
        except:
            return
        ready_to_read, temp, temp2 = select.select([fileno],[],[],0)
        new_info = 0
        while len(ready_to_read):
            try:
                new = self.socket.recv(BUFSIZE)
                if len(new) == 0:
                    # Disconnected
                    raise RuntimeError("Socket disconnected")
            except Exception, x:
                tkMessageBox.showwarning(title="Connection Error",
                                         message="%s:\n%s"%(str(x.__class__),str(x)))
                raise
            new_info = 1
            self.buffer += new
            try:
                fileno = self.socket.fileno()
            except:
                return
            ready_to_read, temp, temp2 = select.select([fileno],[],[],0)
            
        if new_info or not self.first_check_done:
            self.first_check_done = 1
            # Handle variations on newlines:
            self.buffer = string.replace(self.buffer,chr(0x0D),"") # no CR
            self.buffer = string.replace(self.buffer,chr(0x0A),"\n") # LF = newline
            # New names?
            self.buffer = SocketChecker._re_controllable.sub(self.new_name_parser,self.buffer)
            # New values from names?
            for tcp_name in self.name_handler.keys():
                (name_re_str, parser) = self.name_handler[tcp_name]
                self.buffer = name_re_str.sub(parser,self.buffer)
            # Unhandles lines?
            self.buffer = SocketChecker._re_error_line.sub(self.unhandled_line,self.buffer)
            
    def unhandled_line(self,match):
        tkMessageBox.showwarning(title="Unexpected error",
                                 message="The following error was received from the server:\n"+match.group(1))
        return ""
                
    def new_name_parser(self,match):
        class Parser:
            def __init__(self,tcp_name,name_dict):
                self.tcp_name = tcp_name
                self.name_dict = name_dict

            def parse_func(self,match):
                # Could make this into a lambda function
                self.name_dict[self.tcp_name] = match.groups()[-1]
                return ""
        tcp_name = match.group(1)
        name_re_str = re.compile("^"+tcp_name+r"\s*=\s*(.*)\s*$",re.MULTILINE)
        parser = Parser(tcp_name,self.name_dict).parse_func
        self.name_handler[tcp_name] = (name_re_str, parser)
        self.name_dict[tcp_name] = None # initial value
        # request value
        self.socket.send(tcp_name+"\n")
        return ""
    
class SocketLogger:
    def __init__(self,*args,**kw):
        self.socket = socket.socket(*args,**kw)
        for attr in dir(self.socket):
            if attr != "send" and attr != "recv" and attr[:2] != "__":
                setattr(self,attr,getattr(self.socket,attr))
    def send(self,message):
        log_stream.write(">>> "+message)
        self.socket.send(message)
    def recv(self,bufsize):
        message = self.socket.recv(bufsize)
        log_stream.write("<<< "+message)
        return message

def connect():
    class ConnectWindow(Tkinter.Frame):
        def __init__(self,master=None,host="",port=5000,**kw):
            Tkinter.Frame.__init__(self,master,**kw)
            self.next_row = 0
            self.socket = None
            self.buffer = ""

            real_problem = 0
            try:
                host = socket.getfqdn(host)
            except Exception, x:
                real_problem = x
            if real_problem:
                tkMessageBox.showerror(title="Fatal Error",
                                       message="Could not get default hostname and port:\n%s\n%s"%(str(real_problem.__class__),str(real_problem)))
                raise real_problem

            Tkinter.Label(self,
                          text="""Welcome to the Grating GUI demo of the Vision Egg!
This demo allows you to control a sinusoidal grating in realtime.

Please enter the hostname and port number of the computer on which you
have the "gratingTCP" demo running.  That computer should display a
dialog box saying "awaiting connection...".

This demo illustrates the concept of "Controllers" by exposing most of
their functionality.

Any errors produced by this program will be sent to Python's standard
error console.  Any errors produced by the gratingTCP program should
be logged in the normal Vision Egg way.

In this demo is possible to crash the Vision Egg TCP server. Because
this is still beta software, and because the purpose of this
demonstration is to expose as much power and functionality as
possible, you can set various controllers to values that will crash
the server.""").grid(row=self.next_row,column=0,columnspan=2)
                          
            self.next_row += 1

            Tkinter.Label(self,text="Hostname:").grid(row=self.next_row, column=0)
            self.hostname = Tkinter.StringVar()
            self.hostname.set(host)
            Tkinter.Entry(self,textvariable=self.hostname).grid(row=self.next_row, column=1)
            self.next_row += 1

            Tkinter.Label(self,text="Port:").grid(row=self.next_row, column=0)
            self.port = Tkinter.StringVar()
            self.port.set(port)
            Tkinter.Entry(self,textvariable=self.port).grid(row=self.next_row, column=1)
            self.next_row += 1

            b = Tkinter.Button(self,text="Connect",command=self.connect)
            b.bind("<Return>",self.connect)
            b.grid(row=self.next_row,columnspan=2)
            self.next_row += 1

        def connect(self,dummy_arg=None):
            global BUFSIZE

            host = self.hostname.get()
            try:
                port = int(self.port.get())
            except:
                port = self.port.get()

            try:
                host = socket.getfqdn(host)
            except Exception,x:
                traceback.print_exc()
                tkMessageBox.showwarning(title="Connection Error",
                                         message="%s:\n%s"%(str(x.__class__),str(x)))
                return

            self.socket = SocketLogger(socket.AF_INET,socket.SOCK_STREAM)

            try:
                self.socket.connect((host,port))
            except Exception,x:
                sys.stderr.write("Attempting to connect to \"%s\":\n"%(str(host),))
                traceback.print_exc()
                tkMessageBox.showwarning(title="Connection Error",
                                         message="%s:\n%s"%(str(x.__class__),str(x)))
                return
            
            self.socket.setblocking(0)
            timeout = 3.0
            ready_to_read, temp, temp2 = select.select([self.socket],[],[],timeout)

            while len(ready_to_read):
                try:
                    new = self.socket.recv(BUFSIZE)
                    if len(new) == 0:
                        # Disconnected
                        raise RuntimeError("Socket disconnected")
                except Exception, x:
                    traceback.print_exc()
                    tkMessageBox.showwarning(title="Connection Error",
                                             message="%s:\n%s"%(str(x.__class__),str(x)))
                    return
                self.buffer += new
                ready_to_read, temp, temp2 = select.select([self.socket],[],[],0)
            self.destroy()
            self.quit()
            
    connect_window = ConnectWindow()
    connect_window.pack()
    connect_window.winfo_toplevel().title("Vision Egg: Connect")
    connect_window.mainloop()
    return (connect_window.socket, connect_window.buffer)

class BarButton(Tkinter.Menubutton):
    # Taken from Guido van Rossum's Tkinter svkill demo
    def __init__(self, master=None, **cnf):
        Tkinter.Menubutton.__init__(self, master, **cnf)
        self.pack(side=Tkinter.LEFT)
        self.menu = Tkinter.Menu(self, name='menu')
        self['menu'] = self.menu

class GratingControl(Tkinter.Frame):
    def __init__(self,master=None,socket=None,**kw):
        Tkinter.Frame.__init__(self,master,**kw)
        self.socket = socket
        self.next_row = 0
        self.last_values = {}
        self.complete_list = {}
        self.names = []
        self.columnconfigure(2,weight=2)#,minsize=300)
        self.columnconfigure(3,weight=2)#,minsize=300)

        Tkinter.Label(self,text="Controlled parameter").grid(row=self.next_row,column=0)
        Tkinter.Label(self,text="Controller class").grid(row=self.next_row,column=1)
        Tkinter.Label(self,text="During go loop").grid(row=self.next_row,column=2)
        Tkinter.Label(self,text="Between go loops").grid(row=self.next_row,column=3)
        Tkinter.Label(self,text="Evaluation frequency").grid(row=self.next_row,column=4,columnspan=4)
        Tkinter.Label(self,text="Temporal variables available\n to eval_str and exec_str").grid(row=self.next_row,column=8,columnspan=4)
        self.next_row += 1

        Tkinter.Label(self,text="Time (seconds)").grid(row=self.next_row,column=8,columnspan=2)
        Tkinter.Label(self,text="Frames").grid(row=self.next_row,column=10,columnspan=2)
        self.next_row += 1
        
        Tkinter.Label(self,text="Every frame").grid(row=self.next_row,column=4)
        Tkinter.Label(self,text="Transitions").grid(row=self.next_row,column=5)
        Tkinter.Label(self,text="Not during go").grid(row=self.next_row,column=6)
        Tkinter.Label(self,text="Not between go").grid(row=self.next_row,column=7)

        Tkinter.Label(self,text="Absolute").grid(row=self.next_row,column=8)
        Tkinter.Label(self,text="Since go").grid(row=self.next_row,column=9)
        Tkinter.Label(self,text="Absolute").grid(row=self.next_row,column=10)
        Tkinter.Label(self,text="Since go").grid(row=self.next_row,column=11)
        self.next_row += 1
        
        self.make_tkinter_stuff("sf")
        self.next_row += 1

        self.make_tkinter_stuff("tf")
        self.next_row += 1

        self.make_tkinter_stuff("contrast")
        self.next_row += 1

        self.make_tkinter_stuff("phase")
        self.next_row += 1

        self.make_tkinter_stuff("orient")
        self.next_row += 1

        self.make_tkinter_stuff("size")
        self.next_row += 1

        self.make_tkinter_stuff("center")
        self.next_row += 1

        self.make_tkinter_stuff("num_samples")
        self.next_row += 1

        self.make_tkinter_stuff("bit_depth")
        self.next_row += 1

        # take up extra vertical space
        extra_space = Tkinter.Frame(self)
        self.rowconfigure(self.next_row, weight=1)
        extra_space.grid(row=self.next_row,sticky=Tkinter.NW+Tkinter.SE,columnspan=4)
        self.next_row += 1

    def make_tkinter_stuff(self,tcp_name):
        if tcp_name == "sf":
            text = "Spatial frequency (cycles/pixel)"
        elif tcp_name == "tf":
            text = "Temporal frequency (hz)"
        elif tcp_name == "contrast":
            text = "Contrast"
        elif tcp_name == "center":
            text = "Center (x,y pixels)"
        elif tcp_name == "size":
            text = "Size (x,y pixels)"
        elif tcp_name == "phase":
            text = "Phase (degrees)"
        elif tcp_name == "orient":
            text = "Orientation (degrees)"
        elif tcp_name == "num_samples":
            text = "Number of spatial samples"
        elif tcp_name == "bit_depth":
            text = "Bit depth"
        else:
            raise RuntimeError("Unknown tcp_name %s"%(tcp_name,))
        self.names.append(tcp_name)
        
        # comments will show what's happening for tcp_name == "sf"
        setattr(self,tcp_name+"_class",Tkinter.StringVar()) # self.sf_class = Tkinter.StringVar()
        setattr(self,tcp_name+"_during",Tkinter.StringVar()) # self.sf_during = Tkinter.StringVar()
        setattr(self,tcp_name+"_between",Tkinter.StringVar()) # self.sf_between = Tkinter.StringVar()
        setattr(self,tcp_name+"_eval_flag_every",Tkinter.IntVar())
        setattr(self,tcp_name+"_eval_flag_trans",Tkinter.IntVar())
        setattr(self,tcp_name+"_eval_flag_ndur",Tkinter.IntVar())
        setattr(self,tcp_name+"_eval_flag_nbet",Tkinter.IntVar())
        setattr(self,tcp_name+"_t_flag_t_abs",Tkinter.IntVar())
        setattr(self,tcp_name+"_t_flag_t",Tkinter.IntVar())
        setattr(self,tcp_name+"_t_flag_f_abs",Tkinter.IntVar())
        setattr(self,tcp_name+"_t_flag_f",Tkinter.IntVar())
        
        class_var = getattr(self,tcp_name+"_class")
        during_var = getattr(self,tcp_name+"_during")
        between_var = getattr(self,tcp_name+"_between")
        eval_flag_every_var = getattr(self,tcp_name+"_eval_flag_every")
        eval_flag_trans_var = getattr(self,tcp_name+"_eval_flag_trans")
        eval_flag_ndur_var = getattr(self,tcp_name+"_eval_flag_ndur")
        eval_flag_nbet_var = getattr(self,tcp_name+"_eval_flag_nbet")
        t_flag_t_abs_var = getattr(self,tcp_name+"_t_flag_t_abs")
        t_flag_t_var = getattr(self,tcp_name+"_t_flag_t")
        t_flag_f_abs_var = getattr(self,tcp_name+"_t_flag_f_abs")
        t_flag_f_var = getattr(self,tcp_name+"_t_flag_f")
        
        self.last_values[tcp_name+"_class"] = class_var.get()
        self.last_values[tcp_name+"_during"] = during_var.get()
        self.last_values[tcp_name+"_between"] = between_var.get()
        self.last_values[tcp_name+"_eval_flag_every"] = eval_flag_every_var.get()
        self.last_values[tcp_name+"_eval_flag_trans"] = eval_flag_trans_var.get()
        self.last_values[tcp_name+"_eval_flag_ndur"] = eval_flag_ndur_var.get()
        self.last_values[tcp_name+"_eval_flag_nbet"] = eval_flag_nbet_var.get()
        self.last_values[tcp_name+"_t_flag_t_abs"] = t_flag_t_abs_var.get()
        self.last_values[tcp_name+"_t_flag_t"] = t_flag_t_var.get()
        self.last_values[tcp_name+"_t_flag_f_abs"] = t_flag_f_abs_var.get()
        self.last_values[tcp_name+"_t_flag_f"] = t_flag_f_var.get()
        
        Tkinter.Label(self, text=text).grid(row=self.next_row, column=0)

        setattr(self,tcp_name+"_class_update",self.make_updater(tcp_name,"class"))
        class_updater = getattr(self,tcp_name+"_class_update")
        bar = Tkinter.Menubutton(self,textvariable=class_var,relief=Tkinter.RAISED)
        bar.grid(row=self.next_row,column=1,sticky=Tkinter.W+Tkinter.E,pady=2,padx=2)
        bar.menu = Tkinter.Menu(bar)
        bar.menu.add_radiobutton(label="const",variable=class_var,value="const",command=class_updater)
        bar.menu.add_radiobutton(label="eval_str",variable=class_var,value="eval_str",command=class_updater)
        bar.menu.add_radiobutton(label="exec_str",variable=class_var,value="exec_str",command=class_updater)
        bar['menu'] = bar.menu
        
        during_entry = Tkinter.Entry(self, textvariable=during_var)
        during_entry.grid(row=self.next_row, column=2, sticky=Tkinter.W+Tkinter.E,padx=2,ipady=2)
        setattr(self,tcp_name+"_during_update",self.make_updater(tcp_name,"during")) # self.sf_during_update = self.make_updater("sf","during")
        during_updater = getattr(self,tcp_name+"_during_update")
        during_entry.bind("<FocusOut>",during_updater)
        during_entry.bind("<Return>",during_updater)

        between_entry = Tkinter.Entry(self, textvariable=between_var )
        between_entry.grid(row=self.next_row, column=3, sticky=Tkinter.W+Tkinter.E,padx=2,ipady=2)
        setattr(self,tcp_name+"_between_update",self.make_updater(tcp_name,"between")) # self.sf_between_update = self.make_updater("sf","between")
        between_updater = getattr(self,tcp_name+"_between_update")
        between_entry.bind("<FocusOut>",between_updater)
        between_entry.bind("<Return>",between_updater)

        setattr(self,tcp_name+"_eval_flag_every_update",self.make_updater(tcp_name,"eval_flag_every"))
        updater = getattr(self,tcp_name+"_eval_flag_every_update")
        eval_flag_every_check = Tkinter.Checkbutton(self, variable=eval_flag_every_var, command=updater, takefocus=0)
        eval_flag_every_check.grid(row=self.next_row, column=4)

        setattr(self,tcp_name+"_eval_flag_trans_update",self.make_updater(tcp_name,"eval_flag_trans"))
        updater = getattr(self,tcp_name+"_eval_flag_trans_update")
        eval_flag_trans_check = Tkinter.Checkbutton(self, variable=eval_flag_trans_var, command=updater, takefocus=0)
        eval_flag_trans_check.grid(row=self.next_row, column=5)

        setattr(self,tcp_name+"_eval_flag_ndur_update",self.make_updater(tcp_name,"eval_flag_ndur"))
        updater = getattr(self,tcp_name+"_eval_flag_ndur_update")
        eval_flag_ndur_check = Tkinter.Checkbutton(self, variable=eval_flag_ndur_var, command=updater, takefocus=0)
        eval_flag_ndur_check.grid(row=self.next_row, column=6)

        setattr(self,tcp_name+"_eval_flag_nbet_update",self.make_updater(tcp_name,"eval_flag_nbet"))
        updater = getattr(self,tcp_name+"_eval_flag_nbet_update")
        eval_flag_nbet_check = Tkinter.Checkbutton(self, variable=eval_flag_nbet_var, command=updater, takefocus=0)
        eval_flag_nbet_check.grid(row=self.next_row, column=7)

        setattr(self,tcp_name+"_t_flag_t_abs_update",self.make_updater(tcp_name,"t_flag_t_abs"))
        updater = getattr(self,tcp_name+"_t_flag_t_abs_update")
        t_flag_t_abs_check = Tkinter.Checkbutton(self, variable=t_flag_t_abs_var, command=updater, takefocus=0)
        t_flag_t_abs_check.grid(row=self.next_row, column=8)

        setattr(self,tcp_name+"_t_flag_t_update",self.make_updater(tcp_name,"t_flag_t"))
        updater = getattr(self,tcp_name+"_t_flag_t_update")
        t_flag_t_check = Tkinter.Checkbutton(self, variable=t_flag_t_var, command=updater, takefocus=0)
        t_flag_t_check.grid(row=self.next_row, column=9)

        setattr(self,tcp_name+"_t_flag_f_abs_update",self.make_updater(tcp_name,"t_flag_f_abs"))
        updater = getattr(self,tcp_name+"_t_flag_f_abs_update")
        t_flag_f_abs_check = Tkinter.Checkbutton(self, variable=t_flag_f_abs_var, command=updater, takefocus=0)
        t_flag_f_abs_check.grid(row=self.next_row, column=10)

        setattr(self,tcp_name+"_t_flag_f_update",self.make_updater(tcp_name,"t_flag_t"))
        updater = getattr(self,tcp_name+"_t_flag_f_update")
        t_flag_f_check = Tkinter.Checkbutton(self, variable=t_flag_f_var, command=updater, takefocus=0)
        t_flag_f_check.grid(row=self.next_row, column=11)

    def make_updater(self,tcp_name,attr_name):
        my_last_value_key = tcp_name+"_"+attr_name # sf_during
        my_value_var = getattr(self,my_last_value_key) # my_value_var = self.sf_during
        class UpdaterClass:
            def __init__(self,my_value_var,my_last_value_key,parent,tcp_name,attr_name):
                self.my_value_var = my_value_var
                self.my_last_value_key = my_last_value_key
                self.parent = parent
                self.tcp_name = tcp_name
                self.attr_name = attr_name
            def update_func(self,dummy_arg=None):
                tcp_name = self.tcp_name
                attr_name = self.attr_name
                my_value_var = self.my_value_var
                my_last_value_key = self.my_last_value_key
                new_value = my_value_var.get()
                if new_value != self.parent.last_values[my_last_value_key]:
                    self.parent.last_values[my_last_value_key] = new_value
                    if tcp_name in self.parent.complete_list.keys():
                        # send string over TCP
                        controller_tuple = self.parent.complete_list[tcp_name]
                        klass, during, between, eval_frequency, temporal_variables, return_type = controller_tuple
                        if attr_name == "class":
                            if klass != "const" and new_value == "const":
                                #convert from strings
                                try:
                                    during = eval(during,{},{})
                                except:
                                    during = 0.
                                    during_var = getattr(self.parent,tcp_name+"_during")
                                    during_var.set(str(during))
                                try:
                                    between = eval(between,{},{})
                                except:
                                    between = 0.
                                    between_var = getattr(self.parent,tcp_name+"_between")
                                    between_var.set(str(between))
                            elif klass == "const" and new_value != "const":
                                #convert to strings
                                during = str(during)
                                between = str(between)
                            klass = new_value
                        elif attr_name == "during":
                            if klass == "const":
                                try:
                                    new_value = eval(new_value,{},{})
                                except:
                                    new_value = 0.0
                                    my_value_var.set(str(new_value))
                            during = new_value
                        elif attr_name == "between":
                            if klass == "const":
                                try:
                                    new_value = eval(new_value,{},{})
                                except:
                                    new_value = 0.0
                                    my_value_var.set(str(new_value))
                            between = new_value
                        elif attr_name == "eval_flag_every":
                            mask = eval_frequency_flags['EVERY_FRAME']
                            # set the mask bit, but leave the others unchanged
                            eval_frequency = (new_value * mask) + (eval_frequency & ~mask)
                        elif attr_name == "eval_flag_trans":
                            mask = eval_frequency_flags['TRANSITIONS']
                            # set the mask bit, but leave the others unchanged
                            eval_frequency = (new_value * mask) + (eval_frequency & ~mask)
                        elif attr_name == "eval_flag_ndur":
                            mask = eval_frequency_flags['NOT_DURING_GO']
                            # set the mask bit, but leave the others unchanged
                            eval_frequency = (new_value * mask) + (eval_frequency & ~mask)
                        elif attr_name == "eval_flag_nbet":
                            mask = eval_frequency_flags['NOT_BETWEEN_GO']
                            # set the mask bit, but leave the others unchanged
                            eval_frequency = (new_value * mask) + (eval_frequency & ~mask)
                        elif attr_name == "t_flag_t_abs":
                            mask = temporal_variables_flags['TIME_SEC_ABSOLUTE']
                            # set the mask bit, but leave the others unchanged
                            temporal_variables = (new_value * mask) + (temporal_variables & ~mask)
                        elif attr_name == "t_flag_t":
                            mask = temporal_variables_flags['TIME_SEC_SINCE_GO']
                            # set the mask bit, but leave the others unchanged
                            temporal_variables = (new_value * mask) + (temporal_variables & ~mask)
                        elif attr_name == "t_flag_f_abs":
                            mask = temporal_variables_flags['FRAMES_ABSOLUTE']
                            # set the mask bit, but leave the others unchanged
                            temporal_variables = (new_value * mask) + (temporal_variables & ~mask)
                        elif attr_name == "t_flag_f":
                            mask = temporal_variables_flags['FRAMES_SINCE_GO']
                            # set the mask bit, but leave the others unchanged
                            temporal_variables = (new_value * mask) + (temporal_variables & ~mask)
                        controller_tuple = klass, during, between, eval_frequency, temporal_variables, return_type
                        self.parent.complete_list[tcp_name] = controller_tuple
                        if type(during) == types.StringType:
                            send_during = '"' + during + '"'
                        else:
                            send_during = str(during)
                        if type(between) == types.StringType:
                            send_between = '"' + between + '"'
                        else:
                            send_between = str(between)
                        send_eval = eval2str(eval_frequency) + " | ONCE"
                        send_temporal = temporal2str(temporal_variables)
                        tcp_command = "%s=%s( %s, %s, %s, %s)\n"%(tcp_name,klass,send_during,send_between,send_eval,send_temporal)
                        self.parent.socket.send(tcp_command)
        instance = UpdaterClass(my_value_var,my_last_value_key,self,tcp_name,attr_name)
        return instance.update_func

    def check_dict(self,name_dict):
        for name in self.names:
            if name in name_dict.keys():
                tcp_string = name_dict[name]
                if tcp_string is not None:
                    controller_tuple = parse_tcp_string(tcp_string)
                    self.complete_list[name] = controller_tuple
                    klass, during, between, eval_frequency, temporal_variables, return_type = controller_tuple
                    name_dict[name] = None
                    class_name = name+"_class"
                    class_var = getattr(self,class_name)
                    class_var.set(klass)
                    self.last_values[class_name] = klass
                    during_name = name+"_during"
                    during_var = getattr(self,during_name)
                    during_var.set(str(during))
                    self.last_values[during_name] = during
                    between_name = name+"_between"
                    between_var = getattr(self,between_name)
                    between_var.set(str(between))
                    self.last_values[between_name] = between
                    
                    e_name = name+"_eval_flag_every"
                    e_var = getattr(self,e_name)
                    e_var.set( (eval_frequency & eval_frequency_flags['EVERY_FRAME']) != 0 )
                    self.last_values[e_name] = e_var.get()
                    e_name = name+"_eval_flag_trans"
                    e_var = getattr(self,e_name)
                    e_var.set( (eval_frequency & eval_frequency_flags['TRANSITIONS']) != 0 )
                    self.last_values[e_name] = e_var.get()
                    e_name = name+"_eval_flag_ndur"
                    e_var = getattr(self,e_name)
                    e_var.set( (eval_frequency & eval_frequency_flags['NOT_DURING_GO']) != 0 )
                    self.last_values[e_name] = e_var.get()
                    e_name = name+"_eval_flag_nbet"
                    e_var = getattr(self,e_name)
                    e_var.set( (eval_frequency & eval_frequency_flags['NOT_BETWEEN_GO']) != 0 )
                    self.last_values[e_name] = e_var.get()

                    t_name = name+"_t_flag_t_abs"
                    t_var = getattr(self,t_name)
                    t_var.set( (temporal_variables & temporal_variables_flags['TIME_SEC_ABSOLUTE']) != 0 )
                    self.last_values[t_name] = t_var.get()
                    t_name = name+"_t_flag_t"
                    t_var = getattr(self,t_name)
                    t_var.set( (temporal_variables & temporal_variables_flags['TIME_SEC_SINCE_GO']) != 0 )
                    self.last_values[t_name] = t_var.get()
                    t_name = name+"_t_flag_f_abs"
                    t_var = getattr(self,t_name)
                    t_var.set( (temporal_variables & temporal_variables_flags['FRAMES_ABSOLUTE']) != 0 )
                    self.last_values[t_name] = t_var.get()
                    t_name = name+"_t_flag_f"
                    t_var = getattr(self,t_name)
                    t_var.set( (temporal_variables & temporal_variables_flags['FRAMES_SINCE_GO']) != 0 )
                    self.last_values[t_name] = t_var.get()

_re_const = re.compile(r'^const\(\s?(.*)\s?\)$',re.DOTALL)
_re_eval_str = re.compile(r'^eval_str\(\s?(.*)\s?\)$',re.DOTALL)
_re_exec_str = re.compile(r'^exec_str\(\s?(\*)?\s?(.*)\s?\)$',re.DOTALL)
_parse_args_globals = {'Numeric':Numeric,'math':math}
_parse_args_locals = {}
eval_frequency_flags = {
    # eval_frequency flags:
    'NEVER'          : 0x00,
    'EVERY_FRAME'    : 0x01,
    'TRANSITIONS'    : 0x02,
    'ONCE'           : 0x04,
    'NOT_DURING_GO'  : 0x08,
    'NOT_BETWEEN_GO' : 0x10,
    }
temporal_variables_flags = {
    # temporal_variables flags:
    'TIME_INDEPENDENT'  : 0x00,
    'TIME_SEC_ABSOLUTE' : 0x01,
    'TIME_SEC_SINCE_GO' : 0x02,
    'FRAMES_ABSOLUTE'   : 0x04,
    'FRAMES_SINCE_GO'   : 0x08,
    }

for key in dir(Numeric):
    if key[:2] != "__":
        _parse_args_locals[key] = getattr(Numeric,key)
for key in dir(math):
    if key[:2] != "__":
        _parse_args_locals[key] = getattr(math,key)
for key in eval_frequency_flags.keys():
    _parse_args_locals[key] = eval_frequency_flags[key]
for key in temporal_variables_flags.keys():
    _parse_args_locals[key] = temporal_variables_flags[key]

def eval2str(flags):
    str = ""
    for key in eval_frequency_flags.keys():
        if flags & eval_frequency_flags[key]:
            str += key + " | "
    if str:
        str = str[:-3]
    else:
        str = "NEVER"
    return str

def temporal2str(flags):
    str = ""
    for key in temporal_variables_flags.keys():
        if flags & temporal_variables_flags[key]:
            str += key + " | "
    if str:
        str = str[:-3]
    else:
        str = "TIME_INDEPENDENT"
    return str

def parse_tcp_string(tcp_string):
    tcp_string = string.replace(tcp_string,r"\n","\n")
    match = _re_const.match(tcp_string)
    if match:
        klass = "const"
    if not match:
        match = _re_eval_str.match(tcp_string)
        if match:
            klass = "eval_str"
    if not match:
        match = _re_exec_str.match(tcp_string)
        if match:
            klass = "exec_str"
    if not match:
        raise RuntimeError("Unknown value")
    arg_string = match.group(1)
    args = eval("tuple(("+arg_string+"))",_parse_args_globals,_parse_args_locals)
    num_args = len(args)
    if num_args == 0:
        result = (klass,None,None,None,None,None)
    elif num_args == 1:
        result = (klass,args[0],None,None,None,None)
    elif num_args == 2:
        result = (klass,args[0],args[1],None,None,None)
    elif num_args == 3:
        result = (klass,args[0],args[1],args[2],None,None)
    elif num_args == 4:
        result = (klass,args[0],args[1],args[2],args[3],None)
    elif num_args == 5:
        result = (klass,args[0],args[1],args[2],args[3],args[4])
    else:
        raise RuntimeError
    return result

class TCPApp(Tkinter.Frame):
    def __init__(self,master=None,socket=None,starting_buffer=None,**kw):
        Tkinter.Frame.__init__(self,master,**kw)
        self.socket = socket
        self.name_dict = {}
        self.other_interested_instances = [] # also want to know what's happening on the socket
        self.next_row = 0
        
        self.columnconfigure(1,weight=2)#,minsize=300)
        self.columnconfigure(2,weight=2)#,minsize=300)
        
        # create a menu bar
        self.bar = Tkinter.Frame(self, name='bar',
                                 relief=Tkinter.RAISED, borderwidth=2)
        self.bar.grid(row=self.next_row, column=0, columnspan=3, sticky=Tkinter.W+Tkinter.E+Tkinter.N)
        self.bar.file = BarButton(self.bar, text='File')
        self.bar.file.menu.add_command(label='Quit', command=self.quit)
        self.bar.file.menu.add_command(label='Also Quit Server', command=self.quit_server)
        self.bar.tk_menuBar(self.bar.file)
        self.next_row += 1

        # create go loop information
        b = Tkinter.Button(self,text="Enter go loop",command=self.go)
        b.bind("<Return>",self.go)
        b.grid(row=self.next_row,column=0)
        Tkinter.Label(self,text="Go loop duration (value, units):").grid(row=self.next_row, column=1, sticky=Tkinter.E)
        self.go_duration = Tkinter.StringVar()
        self.last_duration_value = self.go_duration.get()
        e = Tkinter.Entry(self,textvariable=self.go_duration)
        e.bind("<FocusOut>",self.duration_updater)
        e.bind("<Return>",self.duration_updater)
        e.grid(row=self.next_row, column=2,sticky=Tkinter.W+Tkinter.E)
        self.next_row += 1

        # make horizontal rule
        horiz_rule = Tkinter.Frame(self, relief=Tkinter.SUNKEN, borderwidth=2)
        self.rowconfigure(self.next_row, minsize=4)
        horiz_rule.grid(row=self.next_row,sticky=Tkinter.NW+Tkinter.SE,columnspan=3)
        self.next_row += 1

        self.socket_checker = SocketChecker(self.socket,starting_buffer,self.name_dict)
        self.after(100,self.check_socket) # check socket every 100 msec
        
    def duration_updater(self,dummy_arg=None):
        new_value = self.go_duration.get()
        if new_value != self.last_duration_value:
            self.last_duration_value=new_value
            self.socket.send("go_duration=const(%s,None,ONCE)\n"%(new_value,))
            
    def register_interest(self,instance):
        self.other_interested_instances.append(instance)
    def go(self,dummy_arg=None):
        self.socket.send("go=const(0,1,ONCE)\n")
    def quit_server(self,dummy_arg=None):
        # send server quit command
        self.socket.send("quit\n")
        time.sleep(0.1) # give it a bit of time...
        self.socket.shutdown(1)
        self.socket.close()
        self.quit()
        
    def check_socket(self):
        self.socket_checker.check()
        if 'go_duration' in self.name_dict.keys():
            tcp_string = self.name_dict['go_duration']
            if tcp_string is not None:
                klass, during, between, eval_frequency, temporal_variables, return_type = parse_tcp_string(tcp_string)
                if str(during) != self.last_duration_value:
                    self.last_duration_value = str(during)
                    self.go_duration.set( self.last_duration_value )
                self.name_dict['go_duration'] = None # reset
        for instance in self.other_interested_instances:
            instance.check_dict(self.name_dict)
        self.after(100,self.check_socket) # check socket every 100 msec

if __name__ == '__main__':
    # Connect
    (socket, start_buffer) = connect()
    if socket is None:
        print "Didn't get a socket, quitting."
        sys.exit()

    # Create main application window
    tcp_app = TCPApp(socket=socket, starting_buffer=start_buffer)
    tcp_app.pack(expand=1,fill=Tkinter.BOTH)
    tcp_app.winfo_toplevel().title("Vision Egg: Grating GUI")

    # Create grating controller
    tcp_app.grating_control = GratingControl(master=tcp_app, socket=socket)
    tcp_app.register_interest(tcp_app.grating_control)
    tcp_app.rowconfigure(tcp_app.next_row, weight=2)
    tcp_app.grating_control.grid( row=tcp_app.next_row, column=0, columnspan=3, sticky=Tkinter.NW+Tkinter.SE)
    tcp_app.next_row += 1

    # Run until quit
    tcp_app.mainloop()
