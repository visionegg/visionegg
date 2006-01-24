# test suggested by Mason Smith on VE mailing list
import VisionEgg
from VisionEgg.Core import *
from VisionEgg.Text import *
import pygame
import pygame.locals

bpps = [32, 24, 16, 0]
sizes = [ (640,480), (800,600), (1024,768), (1280,1024) ]
for bpp in bpps:
    success = False
    for size in sizes:
        print 'trying to initialize window %d x %d, %d bpp'%(
            size[0], size[1], bpp)
        try:
            screen = VisionEgg.Core.Screen( size          = size,
                                            fullscreen    = False,
                                            preferred_bpp = bpp,
                                            maxpriority   = False,
                                            hide_mouse    = True,
                                            sync_swap     = True,
                                            )
            success = True
        except:
            pass
        if success:
            break # we don't need to try other resolutions
    if success:
        break

stims = []
for i in range(2000):
    print i
    t = Text()
    stims.append( t )
