#!/usr/bin/env python
import sys, socket
import Pyro.naming, Pyro.core

Pyro.core.initClient()
# locate the NS
locator = Pyro.naming.NameServerLocator()
print 'Searching Name Server...',
ns = locator.getNS(Pyro.config.PYRO_NS_HOSTNAME)

print 'Name Server found at',ns.URI.address,'('+(Pyro.protocol.getHostname(ns.URI.address) or '??')+') port',ns.URI.port

# resolve the Pyro object
print 'binding to object'
try:
    URI=ns.resolve('go_object')
    print 'URI:',URI
except Pyro.core.PyroError,x:
    print 'Couldn\'t bind object, nameserver says:',x
    raise SystemExit

go_object = Pyro.core.getProxyForURI(URI)
go_object.go()
