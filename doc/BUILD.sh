#!/bin/bash

# This is explained in BUILD.txt.

# Exit immediately on any errors
set -o errexit

PY_DOC_SRC="$HOME/other-peoples-src/Python-2.4.3/Doc"

LINK_PATHS="html paper-a4 paper-letter perl templates texinputs tools"
for LINK_PATH in $LINK_PATHS; do
    rm -f $LINK_PATH
    ln -s $PY_DOC_SRC/$LINK_PATH $LINK_PATH
done

rm -f icons
/bin/ln -s $PY_DOC_SRC/html/icons icons

# make HTML
/usr/bin/python tools/mkhowto --iconserver "../images" -s 3 --up-link "http://www.visionegg.org/" --up-title "Vision Egg website" visionegg.tex

# make PDF
/usr/bin/python tools/mkhowto --pdf visionegg.tex