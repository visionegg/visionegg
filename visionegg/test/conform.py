#!/usr/bin/env python

DEBUG = 0

import unittest
import VisionEgg
import VisionEgg.Core
import VisionEgg.FlowControl
import OpenGL.GL as gl

# for some specific test cases:
import VisionEgg.ParameterTypes
import VisionEgg.Dots
import VisionEgg.Gratings
import VisionEgg.SphereMap
import VisionEgg.Textures
import Numeric
import Image
import ImageDraw
import os
import time

if DEBUG:
    import VisionEgg.GLTrace
    VisionEgg.Core.gl = VisionEgg.GLTrace

# Use Python's bool constants if available, make aliases if not
try:
    True
except NameError:
    True = 1==1
    False = 1==0

# Define "sum" if it's not available as Python function
try:
    sum
except NameError:
    import operator
    def sum( values ):
        return reduce(operator.add, values )
    
class VETestCase(unittest.TestCase):
    def setUp(self):
        kw_params = {'size'          : (512,512),
                     'fullscreen'    : False,
                     'preferred_bpp' : 32,
                     'maxpriority'   : False,
                     'hide_mouse'    : False,
                     'frameless'     : False,
                     'bgcolor'       : (0.0, 0.0, 1.0),
                     }
        try:
            self.screen = VisionEgg.Core.Screen( **kw_params )
        except Exception, x:
            kw_params['preferred_bpp'] = 24
            self.screen = VisionEgg.Core.Screen( **kw_params )
        self.screen.clear()
        VisionEgg.Core.swap_buffers()
        self.ortho_viewport = VisionEgg.Core.Viewport( screen = self.screen )
        
    def tearDown(self):
        VisionEgg.Core.swap_buffers() # just for a brief flash...
        del self.screen

    def test_parameter_types_simple(self):
        ve_types = VisionEgg.ParameterTypes
        b = ve_types.Boolean
        ui = ve_types.UnsignedInteger
        i = ve_types.Integer
        r = ve_types.Real
        ve_types.assert_type(b,ui)
        ve_types.assert_type(b,i)
        ve_types.assert_type(b,r)
        ve_types.assert_type(ui,i)
        ve_types.assert_type(ui,r)
        ve_types.assert_type(i,r)

    def test_parameter_types_sequence(self):
        ve_types = VisionEgg.ParameterTypes
        sr = ve_types.Sequence( ve_types.Real )
        s4r = ve_types.Sequence4( ve_types.Real )
        s3r = ve_types.Sequence3( ve_types.Real )
        s2r = ve_types.Sequence2( ve_types.Real )
        ve_types.assert_type(s4r,sr)
        ve_types.assert_type(s3r,sr)
        ve_types.assert_type(s2r,sr)
        s4i = ve_types.Sequence4( ve_types.Integer )
        s3i = ve_types.Sequence3( ve_types.Integer )
        s2i = ve_types.Sequence2( ve_types.Integer )
        ve_types.assert_type(s4i,sr)
        ve_types.assert_type(s3i,sr)
        ve_types.assert_type(s2i,sr)
        
    def test_parameter_types_instance(self):
        ve_types = VisionEgg.ParameterTypes
        istim = ve_types.Instance( VisionEgg.Core.Stimulus )
        itext = ve_types.Instance( VisionEgg.Text.Text )
        ve_types.assert_type(itext,istim)
        
        class A: # classic classes
            pass
        class B(A):
            pass
        ia = ve_types.Instance( A )
        ib = ve_types.Instance( B )
        ve_types.assert_type(ib, ia)
        
        class An(object): # new style classes
            pass
        class Bn(An):
            pass
        ian = ve_types.Instance( An )
        ibn = ve_types.Instance( Bn )
        ve_types.assert_type(ibn, ian)

    def test_presentation_go(self):
        p = VisionEgg.FlowControl.Presentation(go_duration=(5,'frames'))
        p.go()

    def test_presentation_go_twice(self):
        p = VisionEgg.FlowControl.Presentation(go_duration=(5,'frames'))
        p.go()
        p.go() # check to make sure it works a second time

    def test_presentation_go_duration(self):
        p = VisionEgg.FlowControl.Presentation(go_duration=(1,'frames'))
        p.go()
        p.parameters.go_duration = (2,'frames')
        p.go()
        p.parameters.go_duration = (3,'frames')
        p.go()
        p.parameters.go_duration = (0,'frames')
        p.go()
        p.parameters.go_duration = (0.05,'seconds')
        p.go()

    def test_presentation_go_not(self):
        p = VisionEgg.FlowControl.Presentation(go_duration=(0,'frames'))
        p.go() # make sure it works with 0 duration


    def test_presentation_frame_drop_test(self):
        p = VisionEgg.FlowControl.Presentation(go_duration=(0,'frames'))
        p.go() # make sure it works with 0 duration
        p.were_frames_dropped_in_last_go_loop()
        self.failUnless(not p.were_frames_dropped_in_last_go_loop(),'frame drop test false positive')

        orig_framerate_setting = VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ
        fake_hz = 200.0
        VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ = fake_hz
        skip_frame = VisionEgg.FlowControl.FunctionController(
            during_go_func = lambda t: time.sleep(2.0/fake_hz))
        p.add_controller(None,None,skip_frame)
        p.parameters.go_duration = 3,'frames'
        orig_threshold = p.parameters.warn_longest_frame_threshold
        p.parameters.warn_longest_frame_threshold = 1.1
        p.go()
        p.remove_controller(None,None,skip_frame)
        
        VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ = orig_framerate_setting
        p.parameters.warn_longest_frame_threshold = orig_threshold
        
        self.failUnless(p.were_frames_dropped_in_last_go_loop(),'missed simulated dropped frame')

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

    def test_core_fixation_spot(self):
        stimulus = VisionEgg.Core.FixationSpot()
        self.ortho_viewport.parameters.stimuli = [ stimulus ]
        self.ortho_viewport.draw()

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
        orig = Image.new("RGB",(width,height),(255,0,0))
        orig_draw = ImageDraw.Draw(orig)
        # white cross        
        orig_draw.line( (0,0,width,height), fill=(255,255,255) )
        orig_draw.line( (0,height,width,0),  fill=(255,255,255) )
        # blue vertical line
        orig_draw.line( (10,0,10,height),  fill=(0,0,255) )
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

    def test_texture_stimulus_pil_rgb(self):
        if DEBUG:
            print "test_texture_stimulus_pil_rgb",'*'*80

        width, height = self.screen.size
        orig = Image.new("RGB",(width,height),(0,255,0))
        orig_draw = ImageDraw.Draw(orig)
        # white cross
        orig_draw.line( (0,0,width,height), fill=(255,255,255) )
        orig_draw.line( (0,height,width,0),  fill=(255,255,255) )
        # blue vertical line
        orig_draw.line( (10,0,10,height),  fill=(0,0,255) )
        texture_stimulus = VisionEgg.Textures.TextureStimulus(
            texture = VisionEgg.Textures.Texture(orig),
            internal_format = gl.GL_RGB,
            position = (0,0),
            anchor = 'lowerleft',
            texture_min_filter = gl.GL_NEAREST, # XXX shouldn't have to do this!
            texture_mag_filter = gl.GL_NEAREST, # XXX shouldn't have to do this!
            )

        self.ortho_viewport.parameters.stimuli = [ texture_stimulus ]
        self.ortho_viewport.draw()
        result = self.screen.get_framebuffer_as_image(format=gl.GL_RGB)
        self.failUnless(result.tostring()==orig.tostring(),'exact texture stimulus reproduction with PIL RGB textures failed')

    def test_texture_stimulus_pil_rgba(self):
        if DEBUG:
            print "test_texture_stimulus_pil_rgba",'*'*80

        width, height = self.screen.size
        
        # Note: all alpha should be 255 (=OpenGL 1.0) for this test to
        # work because otherwise the test image gets blended with
        # whatever OpenGL has in the background
        
        orig = Image.new("RGBA",(width,height),(0,255,0,255)) # green, full alpha background
        orig_draw = ImageDraw.Draw(orig)
        # white cross
        orig_draw.line( (0,0,width,height), fill=(255,255,255,255) )
        orig_draw.line( (0,height,width,0),  fill=(255,255,255,255) )
        # blue vertical line
        orig_draw.line( (10,0,10,height),  fill=(0,0,255,255) )
        # this breaks test (alpha != 255)
        # orig_draw.line( (20,0,20,height),  fill=(0,0,255,127) ) 
        # orig_draw.line( (30,0,30,height),  fill=(255,0,0,127) ) 
        texture_stimulus = VisionEgg.Textures.TextureStimulus(
            texture = VisionEgg.Textures.Texture(orig),
            internal_format = gl.GL_RGBA,
            position = (0,0),
            anchor = 'lowerleft',
            texture_min_filter = gl.GL_NEAREST, # XXX shouldn't have to do this!
            texture_mag_filter = gl.GL_NEAREST, # XXX shouldn't have to do this!
            )

        self.ortho_viewport.parameters.stimuli = [ texture_stimulus ]
        self.ortho_viewport.draw()
        result = self.screen.get_framebuffer_as_image(format=gl.GL_RGBA)
        self.failUnless(result.tostring()==orig.tostring(),'exact texture stimulus reproduction with PIL RGBA textures failed')

    def test_texture_stimulus_numpy_rgb(self):
        if DEBUG:
            print "test_texture_stimulus_numpy_rgb",'*'*80
        
        width, height = self.screen.size

        orig = Numeric.zeros((height,width,3),Numeric.UnsignedInt8)
        # sprinkle a few test pixels
        orig[ 4, 4, :]=255
        orig[ 6, 6, 0]=255
        orig[ 8, 8, 1]=127
        # more text pixels as border
        orig[ :, 0,:]=255
        orig[ :,-1,:]=255
        orig[ 0, :,:]=255
        orig[-1, :,:]=255
        texture_stimulus = VisionEgg.Textures.TextureStimulus(
            texture = VisionEgg.Textures.Texture(orig),
            internal_format = gl.GL_RGB,
            texture_min_filter = gl.GL_NEAREST, # XXX shouldn't have to do this!
            texture_mag_filter = gl.GL_NEAREST, # XXX shouldn't have to do this!
            position = (0,0),
            anchor = 'lowerleft',
            mipmaps_enabled = False, # not (yet?) supported for Numeric arrays
            )

        self.ortho_viewport.parameters.stimuli = [ texture_stimulus ]
        self.ortho_viewport.draw()
        result = self.screen.get_framebuffer_as_array(format=gl.GL_RGB)
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
        orig_test = orig.astype(Numeric.Int) # allow signed addition
        result_test = result.astype(Numeric.Int) # allow signed addition
        abs_diff = sum(abs(Numeric.ravel(orig_test) - Numeric.ravel(result_test)))
        self.failUnless(abs_diff == 0,'exact texture reproduction with Numeric RGB textures failed')
        
    def test_texture_stimulus_numpy_rgba(self):
        if DEBUG:
            print "test_texture_stimulus_numpy_rgba",'*'*80
        
        width, height = self.screen.size

        orig = Numeric.zeros((height,width,4),Numeric.UnsignedInt8)
        
        # Note: all alpha should be 255 (=OpenGL 1.0) for this test to
        # work because otherwise the test image gets blended with
        # whatever OpenGL has in the background
        
        # set alpha all on
        orig[ :, :, 3]=255
        # sprinkle a few test pixels
        orig[ 4, 4, :]=255
        orig[ 6, 6, 0]=255
        orig[ 8, 8, 1]=127
        # alpha breaks the test:
        #orig[ 2, 2, 3]=0
        #orig[ 9, 9, 0]=255
        #orig[ 9, 9, 3]=127
        # more text pixels as border
        orig[ :, 0,:]=255
        orig[ :,-1,:]=255
        orig[ 0, :,:]=255
        orig[-1, :,:]=255
        texture_stimulus = VisionEgg.Textures.TextureStimulus(
            texture = VisionEgg.Textures.Texture(orig),
            internal_format = gl.GL_RGBA,
            texture_min_filter = gl.GL_NEAREST, # XXX shouldn't have to do this!
            texture_mag_filter = gl.GL_NEAREST, # XXX shouldn't have to do this!
            position = (0,0),
            anchor = 'lowerleft',
            mipmaps_enabled = False, # not (yet?) supported for Numeric arrays
            )

        self.ortho_viewport.parameters.stimuli = [ texture_stimulus ]
        self.ortho_viewport.draw()
        result = self.screen.get_framebuffer_as_array(format=gl.GL_RGBA)

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
        orig_test = orig.astype(Numeric.Int) # allow signed addition
        result_test = result.astype(Numeric.Int) # allow signed addition
        abs_diff = sum(abs(Numeric.ravel(orig_test) - Numeric.ravel(result_test)))
        self.failUnless(abs_diff == 0,'exact texture reproduction with Numeric RGBA textures failed')
        
def suite():
    ve_test_suite = unittest.TestSuite()
    ve_test_suite.addTest( VETestCase("test_parameter_types_simple") )
    ve_test_suite.addTest( VETestCase("test_parameter_types_sequence") )
    ve_test_suite.addTest( VETestCase("test_parameter_types_instance") )
    ve_test_suite.addTest( VETestCase("test_presentation_go") )
    ve_test_suite.addTest( VETestCase("test_presentation_go_twice") )
    ve_test_suite.addTest( VETestCase("test_presentation_go_duration") )
    ve_test_suite.addTest( VETestCase("test_presentation_go_not") )
    ve_test_suite.addTest( VETestCase("test_presentation_frame_drop_test") )
    ve_test_suite.addTest( VETestCase("test_core_refresh_rates_match") )
    ve_test_suite.addTest( VETestCase("test_core_screen_query_refresh_rate") )
    ve_test_suite.addTest( VETestCase("test_core_screen_measure_refresh_rate") )
    ve_test_suite.addTest( VETestCase("test_core_fixation_spot") )
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
    ve_test_suite.addTest( VETestCase("test_texture_stimulus_numpy_rgb") )
    ve_test_suite.addTest( VETestCase("test_texture_stimulus_numpy_rgba") )
    ve_test_suite.addTest( VETestCase("test_texture_stimulus_pil_rgb") )
    ve_test_suite.addTest( VETestCase("test_texture_stimulus_pil_rgba") )
    
    return ve_test_suite

runner = unittest.TextTestRunner()
runner.run(suite())
