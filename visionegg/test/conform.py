#!/usr/bin/env python

import unittest
import VisionEgg
import VisionEgg.Core
import VisionEgg.FlowControl
import OpenGL.GL as gl

# for some specific test cases:
import VisionEgg.ParameterTypes
import VisionEgg.Dots
import VisionEgg.Gratings
import VisionEgg.MoreStimuli
import VisionEgg.SphereMap
import VisionEgg.Textures
import Numeric
import Image
import ImageDraw
import os
import time

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

# start logging to file
try:
    import logging
    import logging.handlers
except ImportError:
    import VisionEgg.py_logging as logging

log_fname = 'conform.log'
log_handler_logfile = logging.FileHandler( log_fname )
print "saving log file to",log_fname
log_handler_logfile.setFormatter( VisionEgg.log_formatter )
VisionEgg.logger.addHandler( log_handler_logfile )
 
  
    
class VETestCase(unittest.TestCase):
    def setUp(self):
        kw_params = {'size'          : (512,512),
                     'fullscreen'    : False,
                     'preferred_bpp' : 32,
                     'maxpriority'   : False,
                     'hide_mouse'    : False,
                     'frameless'     : False,
                     'bgcolor'       : (0.0, 0.0, 1.0),
                     'sync_swap'     : True,
                     }
        try:
            self.screen = VisionEgg.Core.Screen( **kw_params )
        except Exception, x:
            try:
                kw_params['preferred_bpp'] = 24
                self.screen = VisionEgg.Core.Screen( **kw_params )
            except Exception, x:
                kw_params['preferred_bpp'] = 0
                self.screen = VisionEgg.Core.Screen( **kw_params )
        self.screen.clear()
        VisionEgg.Core.swap_buffers()
        self.ortho_viewport = VisionEgg.Core.Viewport( screen = self.screen )
        
    def tearDown(self):
        VisionEgg.Core.swap_buffers() # just for a brief flash...
        del self.screen

    def pickle_test(self, pickleable):
        import pickle
        a = pickleable
        a_pickle = pickle.dumps(a)
        a_test = pickle.loads(a_pickle)
        for attr_name in dir(a):
            if hasattr(a,attr_name):
                attr_orig = getattr(a,attr_name)
                attr_test = getattr(a_test,attr_name)
                self.failUnless(type(attr_orig) == type(attr_test))
                if hasattr(attr_orig,'__dict__'):
                    for k in attr_orig.__dict__.keys():
                        self.failUnless(type(attr_orig.__dict__[k]) == type(attr_test.__dict__[k]))

    def test_feedback_mode(self):
        l = 250
        r = 300
        b = 200
        t = 350
        
        stimulus = VisionEgg.MoreStimuli.Target2D(
            position=(l,b),
            anchor='lowerleft',
            size=(r-l,t-b),
            )
        
        self.ortho_viewport.parameters.stimuli = [ stimulus ]

        gl.glFeedbackBuffer(1000,gl.GL_3D)
        
        gl.glRenderMode( gl.GL_FEEDBACK )
        self.ortho_viewport.draw()
        feedback_buffer = gl.glRenderMode( gl.GL_RENDER )

        sent_verts = [(l,b,0),
                      (r,b,0),
                      (r,t,0),
                      (l,t,0)]
        recv_verts = feedback_buffer[0][1]

        self.failUnless( len(sent_verts) == len(recv_verts),
                         'feedback received wrong number of verts')

        for s,r in zip(sent_verts,recv_verts):
            s=Numeric.asarray(s)
            r=Numeric.asarray(r)
            diff = abs(s-r)
            err = sum(diff)
            self.failUnless( err < 1e-10,
                             'verts changed')
            
    def test_ve3d_simple(self):
        import VisionEgg.ThreeDeeMath as ve3d

        l = 250
        r = 300
        b = 200
        t = 350
        
        sent_verts = [(l,b,0),
                      (r,b,0),
                      (r,t,0),
                      (l,t,0)]

        recv_verts = self.ortho_viewport.eye_2_window(sent_verts)
        for s,r in zip(sent_verts,recv_verts):
            s=Numeric.asarray(s[:2]) # only testing 2D
            r=Numeric.asarray(r[:2]) # only testing 2D
            diff = abs(s-r)
            err = sum(diff)
            self.failUnless( err < 1e-10,
                             'verts changed')
            
    def test_ve3d_transforms1(self):
        import VisionEgg.ThreeDeeMath as ve3d
        
        gl.glMatrixMode(gl.GL_PROJECTION)

        # identity
        M = ve3d.TransformMatrix()
        ve3d_m = M.matrix

        gl.glLoadIdentity()
        gl_m = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
                                                
        self.failUnless( Numeric.allclose(ve3d_m, gl_m),
                         'identity matrix different')

        # translate
        args=(10,20,30)
        M = ve3d.TransformMatrix()
        M.translate(*args)
        ve3d_m = M.matrix

        gl.glLoadIdentity()
        gl.glTranslatef(*args)
        gl_m = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
                                                
        self.failUnless( Numeric.allclose(ve3d_m, gl_m),
                         'translation matrix different')
        
        # rotate
        args=(-22.5,10,20,-30)
        M = ve3d.TransformMatrix()
        M.rotate(*args)
        ve3d_m = M.matrix

        gl.glLoadIdentity()
        gl.glRotatef(*args)
        gl_m = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
                                                
        self.failUnless( Numeric.allclose(ve3d_m, gl_m),
                         'rotation matrix different')

        # scale
        args=(1,10.5,123.2)
        M = ve3d.TransformMatrix()
        M.scale(*args)
        ve3d_m = M.matrix

        gl.glLoadIdentity()
        gl.glScalef(*args)
        gl_m = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
                                                
        self.failUnless( Numeric.allclose(ve3d_m, gl_m),
                         'scale matrix different')        
        
    def test_ve3d_transforms2(self):
        import VisionEgg.ThreeDeeMath as ve3d
        
        translate1 = (1,2,3)
        rotate = (45, 2, 5, 10)
        scale = (.1, 2.0, 4.0)
        translate2 = (-10,25,300)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glTranslatef(*translate1)
        gl.glRotatef(*rotate)
        gl.glScalef(*scale)
        gl.glTranslatef(*translate2)
        gl_m = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)

        M = ve3d.TransformMatrix()
        M.translate(*translate1)
        M.rotate(*rotate)
        M.scale(*scale)
        M.translate(*translate2)
        ve3d_m = M.matrix

        diff = abs(gl_m-ve3d_m)
        err = sum(diff)
        self.failUnless( err < 1e-10,
                         'matrices different')
        
    def test_ve3d_mixed_transforms(self):
        import VisionEgg.ThreeDeeMath as ve3d

        l = 250
        r = 300
        b = 200
        t = 350
        
        stimulus = VisionEgg.MoreStimuli.Target2D(
            position=(l,b),
            anchor='lowerleft',
            size=(r-l,t-b),
            )

        # M mimics the projection matrix (modelview matrix is effectively identity)
        M = self.ortho_viewport.parameters.projection.get_matrix().copy()
        M = ve3d.TransformMatrix(M)
        M.translate(10,20,0)
        self.ortho_viewport.parameters.projection.translate(10,20,0)
        
        self.ortho_viewport.parameters.stimuli = [ stimulus ]

        gl.glFeedbackBuffer(1000,gl.GL_3D)
        
        gl.glRenderMode( gl.GL_FEEDBACK )
        self.ortho_viewport.draw()
        feedback_buffer = gl.glRenderMode( gl.GL_RENDER )

        sent_verts = [(l,b,0),
                      (r,b,0),
                      (r,t,0),
                      (l,t,0)]
        gl_recv_verts = feedback_buffer[0][1]

        clip_coords = M.transform_vertices( sent_verts )
        norm_device = ve3d.normalize_homogeneous_rows(clip_coords)
        ve3d_recv_verts = self.ortho_viewport.norm_device_2_window(norm_device)

        # check x and y coords
        for g,v in zip(gl_recv_verts,ve3d_recv_verts):
            g=Numeric.asarray(g[:2])
            v=Numeric.asarray(v[:2])
            diff = abs(g-v)
            err = sum(diff)
            self.failUnless( err < 1e-10,
                             'VisionEgg.ThreeDeeMath calculated window position wrong')
        
        # check z coord
        for g,v in zip(gl_recv_verts,ve3d_recv_verts):
            err = abs(g[2]-v[2])
            self.failUnless( err < 1e-10,
                             'VisionEgg.ThreeDeeMath calculated window depth wrong')
        
    def test_ClassWithParameters_pickle_ability(self):
        self.pickle_test( VisionEgg.ClassWithParameters() )
            
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

    def test_core_screen_measure_refresh_rate(self):
        fps = self.screen.measure_refresh_rate()

    def test_core_refresh_rates_match(self):
        fps1 = self.screen.query_refresh_rate()
        # measure frame rate over a longish period for accuracy
        fps2 = self.screen.measure_refresh_rate(average_over_seconds=1.0)
        percent_diff = abs(fps1-fps2)/max(fps1,fps2)*100.0
        self.failUnless(percent_diff < 5.0,'measured (%.1f fps) and queried (%.1f fps) frame rates different (swap buffers may not be synced to vsync)'%(fps2,fps1))

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
        stimulus1 = VisionEgg.Textures.SpinningDrum()
        stimulus2 = VisionEgg.Textures.SpinningDrum()
        self.ortho_viewport.parameters.stimuli = [ stimulus1, stimulus2 ]
        self.ortho_viewport.draw()

    def test_textures_spinning_drum_flat(self):
        stimulus = VisionEgg.Textures.SpinningDrum(flat=1,
                                                   anchor='center',
                                                   )
        self.ortho_viewport.parameters.stimuli = [ stimulus ]
        self.ortho_viewport.draw()

    def test_textures_fixation_cross(self):
        stimulus = VisionEgg.Textures.FixationCross()
        self.ortho_viewport.parameters.stimuli = [ stimulus ]
        self.ortho_viewport.draw()

    def test_texture_stimulus_pil_rgb(self):
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
            position = (0,0),
            anchor = 'lowerleft',
            mipmaps_enabled = False, # not (yet?) supported for Numeric arrays
            )

        self.ortho_viewport.parameters.stimuli = [ texture_stimulus ]
        self.ortho_viewport.draw()
        result = self.screen.get_framebuffer_as_array(format=gl.GL_RGB)
        orig_test = orig.astype(Numeric.Int) # allow signed addition
        result_test = result.astype(Numeric.Int) # allow signed addition
        abs_diff = sum(abs(Numeric.ravel(orig_test) - Numeric.ravel(result_test)))
        self.failUnless(abs_diff == 0,'exact texture reproduction with Numeric RGB textures failed')
        
    def test_texture_stimulus_numpy_rgba(self):
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
            position = (0,0),
            anchor = 'lowerleft',
            mipmaps_enabled = False, # not (yet?) supported for Numeric arrays
            )

        self.ortho_viewport.parameters.stimuli = [ texture_stimulus ]
        self.ortho_viewport.draw()
        result = self.screen.get_framebuffer_as_array(format=gl.GL_RGBA)

        orig_test = orig.astype(Numeric.Int) # allow signed addition
        result_test = result.astype(Numeric.Int) # allow signed addition

        abs_diff = sum(abs(Numeric.ravel(orig_test) - Numeric.ravel(result_test)))
        
        self.failUnless(abs_diff == 0,'exact texture reproduction with Numeric RGBA textures failed')
        
def suite():
    ve_test_suite = unittest.TestSuite()
    ve_test_suite.addTest( VETestCase("test_feedback_mode") )
    ve_test_suite.addTest( VETestCase("test_ve3d_simple") )
    ve_test_suite.addTest( VETestCase("test_ve3d_transforms1") )
    ve_test_suite.addTest( VETestCase("test_ve3d_transforms2") )
    ve_test_suite.addTest( VETestCase("test_ve3d_mixed_transforms") )
    ve_test_suite.addTest( VETestCase("test_ClassWithParameters_pickle_ability") )
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
    ve_test_suite.addTest( VETestCase("test_textures_spinning_drum_flat") )
    ve_test_suite.addTest( VETestCase("test_textures_fixation_cross") )
    ve_test_suite.addTest( VETestCase("test_texture_stimulus_numpy_rgb") )
    ve_test_suite.addTest( VETestCase("test_texture_stimulus_numpy_rgba") )
    ve_test_suite.addTest( VETestCase("test_texture_stimulus_pil_rgb") )
    ve_test_suite.addTest( VETestCase("test_texture_stimulus_pil_rgba") )
    
    return ve_test_suite

runner = unittest.TextTestRunner()
runner.run(suite())
