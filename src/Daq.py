import VisionEgg
import types

class Trigger(VisionEgg.ClassWithParameters):
    pass

class ChannelParameters(VisionEgg.ClassWithParameters):
    pass

class SignalType(ChannelParameters):
    constant_parameters_and_defaults = {'units':('Unknown units',types.StringType)}
    def __init__(self,**kw):
        if self.__class__ == SignalType:
            raise RuntimeError("Trying to instantiate abstract base class.")
        else:
            apply(ChannelParameters.__init__,(self,),kw)

class Analog(SignalType):
    constant_parameters_and_defaults = {'gain':(1.0,types.FloatType),
                                        'offset':(0.0,types.FloatType)}

class Digital(SignalType):
    pass

class DaqMode(ChannelParameters):
    def __init__(self,**kw):
        if self.__class__ == DaqMode:
            raise RuntimeError("Trying to instantiate abstract base class.")
        else:
            apply(ChannelParameters.__init__,(self,),kw)

class Buffered(DaqMode):
    parameters_and_defaults = {'sample_rate_hz':(5000.0,types.FloatType),
                               'duration_sec':(5.0,types.FloatType),
                               'trigger':(None,Trigger)}

class Immediate(DaqMode):
    pass

class Functionality(ChannelParameters):
    def __init__(self,**kw):
        if self.__class__ == Functionality:
            raise RuntimeError("Trying to instantiate abstract base class.")
        else:
            apply(ChannelParameters.__init__,(self,),kw)
   
class Input(Functionality):
    def get_data(self):
        raise RuntimeError("Must override get_data method with daq implementation!")

class Output(Functionality):
    def put_data(self):
        raise RuntimeError("Must override put_data method with daq implementation!")

class Channel(VisionEgg.ClassWithParameters):
    constant_parameters_and_defaults = { 'signal_type' : (None,SignalType),
                                         'daq_mode' : (None,DaqMode),
                                         'functionality' : (None,Functionality)}
    def arm_trigger(self):
        raise NotImpelemetedError("This method must be overridden.")

class Device:
    def __init__(self):
        if self.__class__ == Device:
            raise RuntimeError("Trying to instantiate abstract base class.")
        self.channels = []
        
    def add_channel(self,channel):
        # override this method if you need to do error checking
        if isinstance(channel,Channel):
            self.channels.append(channel)
        else:
            raise ValueError("%s not instance of VisionEgg.Daq.Channel"%channel)
