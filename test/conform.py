#!/usr/bin/env python

DEBUG = 1

import unittest
import VisionEgg
import VisionEgg.Core
import OpenGL.GL as gl

if DEBUG:
    import VisionEgg.GLTrace
    VisionEgg.gl = VisionEgg.GLTrace
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
                                             frameless     = False)
        self.ortho_viewport = VisionEgg.Core.Viewport( screen = self.screen )
        
    def tearDown(self):
        del self.screen

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

    def test_texture_pil(self):
        if DEBUG:
            print "test_texture_pil",'*'*80
        
        import VisionEgg.Textures
        if DEBUG:
            VisionEgg.Textures.gl = VisionEgg.GLTrace
        import Image
        import ImageDraw
        
        width, height = self.screen.size
        orig = Image.new("RGB",(width,height),(0,0,0))
        orig_draw = ImageDraw.Draw(orig)
        orig_draw.line( (0,0,width,height), fill=(255,255,255) )
        orig_draw.line( (0,height,width,0),  fill=(255,255,255) )
        texture = VisionEgg.Textures.Texture(orig)
        result = texture.get_texels_as_image()
        self.failUnless(result.tostring()==orig.tostring(),'exact texture reproduction with PIL textures failed')

    def test_texture_stimulus_pil(self):
        if DEBUG:
            print "test_texture_stimulus_pil",'*'*80

        import VisionEgg.Textures
        if DEBUG:
            VisionEgg.Textures.gl = VisionEgg.GLTrace
        import Image
        import ImageDraw

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
            texture_wrap_s = gl.GL_REPEAT,
            texture_wrap_t = gl.GL_REPEAT,
            )

        self.ortho_viewport.parameters.stimuli = [ texture_stimulus ]
        self.ortho_viewport.draw()
        result = self.screen.get_framebuffer_as_image()
        self.failUnless(result.tostring()==orig.tostring(),'exact texture stimulus reproduction with PIL textures failed')

    def test_texture_stimulus_numpy(self):
        if DEBUG:
            print "test_texture_stimulus_numpy",'*'*80
        
        import VisionEgg.Textures
        if DEBUG:
            VisionEgg.Textures.gl = VisionEgg.GLTrace
        import Numeric

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
            texture_min_filter = gl.GL_NEAREST,
            texture_mag_filter = gl.GL_NEAREST,
            texture_wrap_s = gl.GL_REPEAT,
            texture_wrap_t = gl.GL_REPEAT,
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
    ve_test_suite.addTest( VETestCase("test_core_screen_query_refresh_rate") )
    ve_test_suite.addTest( VETestCase("test_core_screen_measure_refresh_rate") )
    ve_test_suite.addTest( VETestCase("test_core_refresh_rates_match") )
    ve_test_suite.addTest( VETestCase("test_texture_pil") )
    ve_test_suite.addTest( VETestCase("test_texture_stimulus_pil") )
    ve_test_suite.addTest( VETestCase("test_texture_stimulus_numpy") )
    return ve_test_suite

runner = unittest.TextTestRunner()
runner.run(suite())
