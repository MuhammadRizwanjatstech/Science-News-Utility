#! /usr/bin/env python
# makes an xml file for slideshows
#
# Jue Wang
# 1/27/10
# -*- coding: utf-8 -*-
import re, string, sys

# initialize lookup table with captions and credits
captions = [ """<b>Delicate.</b>This amoeba's skeleton is a single crystal that
            dissolves when the cell dies. Credit: Dr. Linda Amaral Zettler.""",
            """<b>Common drifter.</b> <i>Bacteriastrum</i>, a phytoplankton, can
            be quite abundant. Credit: J. Cole.""",
            """<b>Group living.</b> This cluster of 10 amoebae each live in a
            house called a test. Credit: D. J. Patterson, L. Amaral-Zettler, M.
            Peglar, and T. Nerad.""",
            """<b>Microbial menace.</b> This toxic alga causes red tide in Texas
            and Florida. Credit: Bob Andersen and D. J. Patterson.""",
            """<b>Ancient alga.</b> Three-billion-year-old fossils exist of this
            blue-green alga, or cyanobacterium. Credit: D. J. Patterson.""",
            """<b>Girdle-wearer.</b> Found 4141 meters deep, this burrowing
            loriciferan is just 0.25 millimeters long. Credit: Gunnar Gad, Marco
            Büntzow / Senckenberg Research Institute, Germany."""
           ]
           
head = '''<?xml version="1.0" encoding="UTF-8"?>
<gallery>
<album lgpath="images/" tnpath="tn/" tnsmpath="tnsm/" tn="" title="" description="">'''
print head

newlines = re.compile('\s*\n\s*')
for i,cap in enumerate(captions):
    c = captions[i]
    c = c.replace('<','&lt;')
    c = c.replace('>','&gt;')
    c = newlines.sub(' ', c)
    
    print "\t<img",
    print "caption=\""+c+"\"",
    print "src='"+str(i+1)+".jpg' tn='"+str(i+1)+".jpg' tnsm='"+str(i+1)+".jpg' />"

foot = '''</album>
</gallery>'''

print foot
