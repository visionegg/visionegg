#!/usr/bin/env python

DEBUG = 0

import unittest
import VisionEgg
import VisionEgg.Core
import OpenGL.GL as gl

# for some specific test cases:
import VisionEgg.Dots
import VisionEgg.Gratings
import VisionEgg.SphereMap
import VisionEgg.Textures
import Numeric
import Image
import ImageDraw
import os

if DEBUG:
    import VisionEgg.GLTrace
    VisionEgg.Core.gl = VisionEgg.GLTrace

# Use Python's bool constants if available, make aliases if not
try:
    True
except NameError:
    True = 1==1
    False = 1==0

class VETestCase(unittest.TestCase):
    def setUp(self):
        self.screen = VisionEgg.Core.Screen( size          = (512,512),
                                             fullscreen    = False,
                                             preferred_bpp = 32,
                                             maxpriority   = False,
                                             hide_mouse    = False,
                                             frameless     = False,
                                             bgcolor       = (0,0,0), # Black (RGB)
                                             )
        self.screen.clear()
        VisionEgg.Core.swap_buffers()
        self.ortho_viewport = VisionEgg.Core.Viewport( screen = self.screen )
        
    def tearDown(self):
        VisionEgg.Core.swap_buffers() # just for a brief flash...
        del self.screen

    def test_core_presentation_go(self):
        p = VisionEgg.Core.Presentation(go_duration=(5,'frames'))
        p.go()
        p.go() # check to make sure it works a second time
        p.parameters.go_duration = (0,'frames')
        p.go() # make sure it works with 0 duration

    def test_core_screen_query_refresh_rate(self):
        fps = self.screen.query_refresh_rate()
        if DEBUG:
            print fps,"= self.screen.query_refresh_rate()"

    def test_core_screen_measure_refresh_rate(self):
        fps = self.screen.measure_refresh_rate()
        if DEBUG:
            print fps,"= self.screen.measure_refresh_rate()"

    def test_core_refresh_rates_match(self):
        fps1 = self.screen.query_refresh_rate()
        # measure frame rate over a longish period for accuracy
        fps2 = self.screen.measure_refresh_rate(average_over_seconds=1.0)
        percent_diff = abs(fps1-fps2)/max(fps1,fps2)*100.0
        self.failUnless(percent_diff < 5.0,'measured and queried frame rates different (swap buffers may not be synced to vsync)')

    def test_dots_dotarea2d(self):
        stimulus = VisionEgg.Dots.DotArea2D()
        self.ortho_viewport.parameters.stimuli = [ stimulus ]
        self.ortho_viewport.draw()

    def test_gratings_singrating2d(self):
        stimulus = VisionEgg.Gratings.SinGrating2D()
        self.ortho_viewport.parameters.stimuli = [ stimulus ]
        self.ortho_viewport.draw()

    def test_gratings_singrating2d_2colors(self):
        stimulus = VisionEgg.Gratings.SinGrating2D(color1=(1,0,0),
                                                  color2=(0,0,1))
        self.ortho_viewport.parameters.stimuli = [ stimulus ]
        self.ortho_viewport.draw()

    def test_gratings_singrating2d_mask(self):
        mask = VisionEgg.Textures.Mask2D()
        stimulus = VisionEgg.Gratings.SinGrating2D(mask=mask)
        self.ortho_viewport.parameters.stimuli = [ stimulus ]
        self.ortho_viewport.draw()

    def test_spheremap_azelgrid(self):
        stimulus = VisionEgg.SphereMap.AzElGrid(my_viewport=self.ortho_viewport)
        self.ortho_viewport.parameters.stimuli = [ stimulus ]
        self.ortho_viewport.draw()

    def test_spheremap_spheremap(self):
        filename = os.path.join(VisionEgg.config.VISIONEGG_SYSTEM_DIR,"data","az_el.png")
        texture = VisionEgg.Textures.Texture(filename)
        stimulus = VisionEgg.SphereMap.SphereMap(texture=texture,
                                                 shrink_texture_ok=True)
        self.ortho_viewport.parameters.stimuli = [ stimulus ] 
        self.ortho_viewport.draw()

    def test_spheremap_spherewindow(self):
        stimulus = VisionEgg.SphereMap.SphereWindow()
        self.ortho_viewport.parameters.stimuli = [ stimulus ] 
        self.ortho_viewport.draw()

    def test_texture_pil(self):
        if DEBUG:
            print "test_texture_pil",'*'*80
        
        width, height = self.screen.size
        orig = Image.new("RGB",(width,height),(0,0,0))
        orig_draw = ImageDraw.Draw(orig)
        orig_draw.line( (0,0,width,height), fill=(255,255,255) )
        orig_draw.line( (0,height,width,0),  fill=(255,255,255) )
        texture = VisionEgg.Textures.Texture(orig)
        result = texture.get_texels_as_image()
        self.failUnless(result.tostring()==orig.tostring(),'exact texture reproduction with PIL textures failed')

    def test_texture_stimulus_3d(self):
        stimulus = VisionEgg.Textures.TextureStimulus3D()
        self.ortho_viewport.parameters.stimuli = [ stimulus ]
        self.ortho_viewport.draw()

    def test_textures_spinning_drum(self):
        stimulus = VisionEgg.Textures.SpinningDrum()
        self.ortho_viewport.parameters.stimuli = [ stimulus ]
        self.ortho_viewport.draw()

    def test_textures_fixation_cross(self):
        stimulus = VisionEgg.Textures.FixationCross()
        self.ortho_viewport.parameters.stimuli = [ stimulus ]
        self.ortho_viewport.draw()

    def test_texture_stimulus_pil(self):
        if DEBUG:
            print "test_texture_stimulus_pil",'*'*80

        width, height = self.screen.size
        orig = Image.new("RGB",(width,height),(0,0,0))
        orig_draw = ImageDraw.Draw(orig)
        orig_draw.line( (0,0,width,height), fill=(255,255,255) )
        orig_draw.line( (0,height,width,0),  fill=(255,255,255) )
        texture_stimulus = VisionEgg.Textures.TextureStimulus(
            texture = VisionEgg.Textures.Texture(orig),
            position = (0,0),
            anchor = 'lowerleft',
            texture_min_filter = gl.GL_NEAREST,
            texture_mag_filter = gl.GL_NEAREST,
            )

        self.ortho_viewport.parameters.stimuli = [ texture_stimulus ]
        self.ortho_viewport.draw()
        result = self.screen.get_framebuffer_as_image()
        self.failUnless(result.tostring()==orig.tostring(),'exact texture stimulus reproduction with PIL textures failed')

    def test_texture_stimulus_numpy(self):
        if DEBUG:
            print "test_texture_stimulus_numpy",'*'*80
        
        width, height = self.screen.size

        orig = Numeric.zeros((height,width,3),Numeric.UnsignedInt8)
        orig[ 4, 4,:]=255
        orig[ :, 0,:]=255
        orig[ :,-1,:]=255
        orig[ 0, :,:]=255
        orig[-1, :,:]=255
        texture_stimulus = VisionEgg.Textures.TextureStimulus(
            texture = VisionEgg.Textures.Texture(orig),
            position = (0,0),
            anchor = 'lowerleft',
            mipmaps_enabled = False, # not (yet?) supported for Numeric arrays
            )

        self.ortho_viewport.parameters.stimuli = [ texture_stimulus ]
        self.ortho_viewport.draw()
        result = self.screen.get_framebuffer_as_array()
        if DEBUG:
            print "low low"
            print orig[:10,:10,0]
            print result[:10,:10,0]
            print "low high"
            print orig[:10,-10:,0]
            print result[:10,-10:,0]
            print "high low"
            print orig[-10:,:10,0]
            print result[-10:,:10,0]
            print "high high"
            print orig[-10:,-10:,0]
            print result[-10:,-10:,0]
        self.failUnless(Numeric.allclose(orig,result),'exact texture reproduction with Numeric textures failed')
        

def suite():
    ve_test_suite = unittest.TestSuite()
    ve_test_suite.addTest( VETestCase("test_core_presentation_go") )
    ve_test_suite.addTest( VETestCase("test_core_refresh_rates_match") )
    ve_test_suite.addTest( VETestCase("test_core_screen_query_refresh_rate") )
    ve_test_suite.addTest( VETestCase("test_core_screen_measure_refresh_rate") )
    ve_test_suite.addTest( VETestCase("test_dots_dotarea2d") )
    ve_test_suite.addTest( VETestCase("test_gratings_singrating2d") )
    ve_test_suite.addTest( VETestCase("test_gratings_singrating2d_mask") )
    ve_test_suite.addTest( VETestCase("test_gratings_singrating2d_2colors") )
    ve_test_suite.addTest( VETestCase("test_spheremap_azelgrid") )
    ve_test_suite.addTest( VETestCase("test_spheremap_spheremap") )
    ve_test_suite.addTest( VETestCase("test_spheremap_spherewindow") )
    ve_test_suite.addTest( VETestCase("test_texture_pil") )
    ve_test_suite.addTest( VETestCase("test_texture_stimulus_3d") )
    ve_test_suite.addTest( VETestCase("test_textures_spinning_drum") )
    ve_test_suite.addTest( VETestCase("test_textures_fixation_cross") )
    ve_test_suite.addTest( VETestCase("test_texture_stimulus_pil") )
    ve_test_suite.addTest( VETestCase("test_texture_stimulus_numpy") )
    return ve_test_suite

runner = unittest.TextTestRunner()
runner.run(suite())
