#!/usr/bin/env python
"""Module containing the Multi-line text stimulus class WrappedText, as well
as a simple example of its use."""
# Copyright (c) 2007 Eamon Caddigan, University of Illinois
# License: LGPL (see LICENSE.txt distributed with this file)
# Created on 2007-11-15
# 
# TODO: (more of a wishlist)
#   * anchor parameter
#   * angle parameter (I dunno, maybe you want some paragraphs tilted)
#   * more robust line length calculation
#   * wholesale replacement of this module with *real* formatted text (e.g.,
#     ghostscript). The kerning of pygame's text is atrocious.

import VisionEgg.Core
import VisionEgg.Text
import VisionEgg.Textures
import VisionEgg.ParameterTypes as ve_types
import textwrap

class WrappedText(VisionEgg.Core.Stimulus):
  """Multi-line text stimulus. No fancy formatting, but line breaks ('\\n')
  are preserved, and text is wrapped to fit within the stimulus
  boundaries."""

  parameters_and_defaults = {
    'on':(True, ve_types.Boolean),
    'position':((0.0,0.0), 
        ve_types.AnyOf(ve_types.Sequence2(ve_types.Real),
          ve_types.Sequence3(ve_types.Real),
          ve_types.Sequence4(ve_types.Real))),
    'size':(None, ve_types.Sequence2(ve_types.Real),
        """Defaults to the size of the screen."""),
    'text':('hello', ve_types.AnyOf(ve_types.String,ve_types.Unicode)),
    'color':((1.0,1.0,1.0),
        ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
          ve_types.Sequence4(ve_types.Real)))
  }

  constant_parameters_and_defaults = {
    'font_name':(None, ve_types.AnyOf(ve_types.String,ve_types.Unicode),
        "Name of font to use. If None, use the default font"),
    'font_size':(30, ve_types.UnsignedInteger)
  }

  def __init__(self, **kw):
    """Initialize the object, perform the initial line-splitting"""
    VisionEgg.Core.Stimulus.__init__(self, **kw)

    if self.parameters.size is None:
      self.parameters.size = (VisionEgg.config.VISIONEGG_SCREEN_W,
          VisionEgg.config.VISIONEGG_SCREEN_H)

    self._splitText()

  def _splitText(self):
    """Split a single string into multiple lines of text, storing each as a
    VisionEgg.Text.Text instance"""
    p = self.parameters
    cp = self.constant_parameters

    self._text = p.text

    textAreaWidth = None
    maxLineLength = len(self._text)
    minLineLength = 1
    lineLength = maxLineLength
    while ((textAreaWidth > p.size[0]) or 
        ((maxLineLength-minLineLength) > 1)) and (maxLineLength > 1):
      nextPosition = p.position
      self._textLines = []

      try:
        textLineList = []
        for text in self._text.split("\n"):
          if text == "":
            textLineList.append("")
          else:
            textLineList.extend(textwrap.wrap(text, lineLength))

        textAreaWidth = None
        for textLine in textLineList:
          if textLine != "":
            line = VisionEgg.Text.Text(text=textLine,
                position = nextPosition,
                anchor = "upperleft",
                ignore_size_parameter = True,
                color = p.color,
                font_name = cp.font_name,
                font_size = cp.font_size)
            textAreaWidth = max(textAreaWidth, line.parameters.size[0])
            self._textLines.append(line)

          nextPosition = (nextPosition[0],
              nextPosition[1]-line.parameters.size[1])

          # Stop adding lines if the text area's height has been reached
          if (p.position[1] - nextPosition[1]) > p.size[1]:
            break

      except VisionEgg.Textures.TextureTooLargeError:
        textAreaWidth = p.size[0]+1

      if textAreaWidth > p.size[0]:
        maxLineLength = lineLength
      else:
        minLineLength = lineLength
      lineLength = (maxLineLength+minLineLength)/2

  def draw(self):
    """Draw the lines of text on the screen"""
    p = self.parameters

    if p.on:
      if p.text != self._text:
        self._splitText()

      for line in self._textLines:
        line.parameters.color = p.color
        line.draw()

def main():
  """Launch VisionEgg and demo the WrappedText object"""
  import VisionEgg
  VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()
  import VisionEgg.FlowControl

  screen = VisionEgg.Core.get_default_screen()

  message="""Hello.

This is a demonstration of the WrappedText object, which was created to allow users of VisionEgg to include large blocks of text in their programs. While this stimulus has many limitations, it should be useful for presenting on-screen instructions in experiments.

While you are welcome to modify this file to extend its functionality, I hope you consider sharing any such modifications with the VisionEgg community.

Eamon Caddigan,\nUniversity of Illinois\n15 November 2007"""

  wt = WrappedText(text=message, position=(50,screen.size[1]-50), 
    size=(screen.size[0]-100, screen.size[1]-100))

  viewport = VisionEgg.Core.Viewport(screen=screen, stimuli=[wt])

  # Frame-based presentation duration makes it easier to use pdb
  p = VisionEgg.FlowControl.Presentation(viewports=[viewport],
      go_duration=(VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ*30,'frames'))
  p.go()

  screen.close() # Called explicitly to behave better in interactive shells

if __name__ == "__main__":
  main()

