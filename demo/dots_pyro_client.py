#!/usr/bin/env python
"""Contact the server run by dots_pyro_server and modulate the display
"""
import time
import Pyro.core

Pyro.config.PYRO_MULTITHREADED = 0
Pyro.config.PYRO_TRACELEVEL = 3
Pyro.config.PYRO_USER_TRACELEVEL = 3
Pyro.config.PYRO_DETAILED_TRACEBACK = 1
Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

def main():
    Pyro.core.initClient(banner=0)
    
    hostname = 'localhost'
    port = 4321
    name = 'DotServer'
    
    URI = "PYROLOC://%s:%d/%s" % (hostname,port,name)
    dot_server_instance = Pyro.core.getProxyForURI(URI)

    try:
        while True:
            dot_server_instance.set_signal_fraction(1.0)
            time.sleep(0.5)
            dot_server_instance.set_signal_fraction(0.1)
            time.sleep(0.5)
    finally:
        dot_server_instance.quit()

if __name__=='__main__':
    main()
    
