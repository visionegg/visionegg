#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Display unicode text strings."""

# data from http://www.columbia.edu/kermit/utf8.html
phrases = {'English':                           u"I can eat glass and it doesn't hurt me.",
           'Sanskrit':                          u"काचं शक्नोम्यत्तुम् । नोपहिनस्ति माम् ॥",
           'Sanskrit (standard transcription)': u"kācaṃ śaknomyattum; nopahinasti mām.",
           'Classical Greek':                   u"ὕαλον ϕαγεῖν δύναμαι· τοῦτο οὔ με βλάπτει.",
           'Greek':                             u"Μπορώ να φάω σπασμένα γυαλιά χωρίς να πάθω τίποτα.",
           'Thai':                              u"ฉันกินกระจกได้ แต่มันไม่ทำให้ฉันเจ็บ",
           'Chinese':                           u"我能吞下玻璃而不伤身体",
           'Chinese (Traditional)':             u"我能吞下玻璃而不傷身體",
           'Japanese':                          u"私はガラスを食べられます。それは私を傷つけません。",
           'Korean':                            u"나는 유리를 먹을 수 있어요. 그래도 아프지 않아요",
           'Arabic':                            u"أنا قادر على أكل الزجاج و هذا لا يؤلمني.",
           'Hebrew':                            u"אני יכול לאכול זכוכית וזה לא מזיק לי.",
}

# collect above data into 2 sequences:
language, phrase = zip(*[item for item in phrases.iteritems()])

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Text import *
import pygame
from pygame.locals import *

screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,1.0) # background blue (RGB)

if sys.platform == 'win32':
    font_name = r'C:\Windows\Fonts\Arial.ttf'
else:
    font_name = '/usr/share/fonts/truetype/Arial.ttf'

if not os.path.exists(font_name):
    print 'WARNING: font_name "%s" does not exist, using default font'%font_name
    font_name = None

text = Text(color=(1.0,1.0,1.0), # alpha is ignored (set with max_alpha_param)
            position=(screen.size[0]/2,screen.size[1]/2),
            ignore_size_parameter=False, # ignore font size (use texture size)
            size = (screen.size[0],max(screen.size[0]/10,10)),
            anchor='center',
            font_name=font_name)

viewport = Viewport(screen=screen,
                    size=screen.size,
                    stimuli=[text])

# The main loop below is an alternative to using the
# VisionEgg.FlowControl.Presentation class.

frame_timer = FrameTimer()
quit_now = 0
while not quit_now:
    for event in pygame.event.get():
        if event.type in (QUIT,KEYDOWN,MOUSEBUTTONDOWN):
            quit_now = 1

    idx = int(VisionEgg.time_func()%len(language))
    text.parameters.text = "%s: %s"%(language[idx],phrase[idx])
    screen.clear()
    viewport.draw()
    swap_buffers()
    frame_timer.tick()
frame_timer.log_histogram()
