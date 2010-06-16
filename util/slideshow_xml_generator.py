#! /usr/bin/env python
# makes an xml file for slideshows
#
# Jue Wang
# 1/27/10
# -*- coding: utf-8 -*-
import re, string, sys

# initialize lookup table with captions and credits
captions = ["""<b>Eye spy</b>. Rather than spinning a cocoon, <i>Ridens panche</i> caterpillars roll up leaves using silken threads. If a bird cuts openthis shelter (<i>top</i>), the caterpillar immediately thrusts a scary back end at the invader (<i>bottom</i>)""",
            """<b>Two face</b>. Caterpillar patterns can appear different when viewed from different angles, such as these two <i>Cephise nuspesez</i>caterpillars, whose "face" depends on whether a predator approaches from the top or the side""",
            """<b>Hidden surprise</b>. Unless disturbed, the false eyes of these species stay hidden under skin folds. The caterpillars can thus avoiddisplaying bright, revealing colors until necessary""",
            """<b>Spot on</b>. Some species display an astonishingly detailed mimicry of snake eyes and scales""",
            """<b>Dot the eyes</b>. In many cases, even the slightest suggestion of eyes and faces is enough to drive off insect-eating birds""",
            """<b>Strike a pose</b>. Some caterpillars may establish an s-shaped pose to more closely resemble a snake while thrusting their false head ata bird""",
            """<b>Not obvious</b>. A casual observer might not notice a caterpillar's eyespot patterns, which are designed to be viewed from a particulardistance and angle. Seen here is an <i>Elymiotis janzen</i> caterpillar from the front (<i>left</i>) and the side (<i>right</i>)"""]

head = '''<?xml version="1.0" encoding="UTF-8"?>
<gallery>
<album lgpath="images/" tnpath="tn/" tnsmpath="tnsm/" fspath="fs/" tn="" title="" description="">'''
print head

newlines = re.compile('\s*\n\s*')
for i,cap in enumerate(captions):
    c = captions[i]
    c = c.replace('<','&lt;')
    c = c.replace('>','&gt;')
    c = newlines.sub(' ', c)
    
    print "\t<img",
    print "caption=\""+c+"\"",
    print "src='"+str(i+1)+".jpg' tn='"+str(i+1)+".jpg' tnsm='"+str(i+1)+".jpg' fs='"+str(i+1)+".jpg' />"

foot = '''</album>
</gallery>'''

print foot
