#!/usr/bin/env python

import sys

from VisionEgg.Core import *
from VisionEgg.AppHelper import *

import Pyro.naming
import Pyro.core
from Pyro.errors import PyroError,NamingError

def angle_as_function_of_time(t):
    return 90.0*t # rotate at 90 degrees per second

class GoObject(Pyro.core.ObjBase):
    def __init__(self,go_func=lambda: None):
        self.go_func = go_func
        apply(Pyro.core.ObjBase.__init__,(self,))

    def go(self):
        self.go_func()

def main():

    # Start Pyro
    Pyro.core.initServer()
    PyroDaemon = Pyro.core.Daemon()
    # locate the Pyro name server
    locator = Pyro.naming.NameServerLocator()
    print 'searching for Name Server...'
    ns = locator.getNS(Pyro.config.PYRO_NS_HOSTNAME)
    print 'Name Server found at',ns.URI.address,'('+(Pyro.protocol.getHostname(ns.URI.address) or '??')+') port',ns.URI.port
    PyroDaemon.useNameServer(ns)

    # get visionegg stimulus ready to go
    screen = get_default_screen()
    projection = SimplePerspectiveProjection(fov_x=45.0)
    viewport = Viewport(screen,(0,0),screen.size,projection)
    stimulus = Stimulus()
    stimulus.init_gl()
    viewport.add_stimulus(stimulus)
    p = Presentation(duration_sec=5.0,viewports=[viewport])
    p.add_realtime_controller(stimulus.parameters,'yrot', angle_as_function_of_time)

    # connect a new object implementation (first unregister previous one)
    try:
        ns.unregister('go_object')
    except NamingError:
        pass
    # connect new object implementation
    PyroDaemon.connect(GoObject( p.go ),'go_object')
    # enter the server loop
    print 'Server object "go_object" ready.'
    while 1:
        PyroDaemon.handleRequests(3.0)
        sys.stdout.write('.')
        sys.stdout.flush()

if __name__=="__main__":
    main()
