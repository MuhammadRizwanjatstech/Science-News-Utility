#! /usr/bin/env python
# makes an xml file for slideshows
#
# Jue Wang
# 1/27/10
# -*- coding: utf-8 -*-
import re, string, sys

# initialize lookup table with captions and credits
captions = ["""This unnamed species of lizard from the Liolaemus family in
            Bolivia could go extinct before scientists have a chance to study
            it. (Credit: Ignacio De La Riva)""",
            """Researchers constructed these makeshift "electronic lizards" to
            mimic a real lizard's light reflectivity and record how hot it would
            get during different parts of the day. (Credit: Barry Sinervo) """,
            """Cloud forest habitats in Peru are among the environments in
            danger of losing lizard species to global warming. (Credit: Ignacio
            De La Riva)""",
            """This chameleon in Madagascar, <i>Furcifer lateralis</i>, is
            already fighting extinction. Further global warming will likely seal
            its fate. (Credit: Ignacio De La Riva)""",
            """Madagascar's geckos, including this <i>Phelsuma
            quadriocellata</i>, are hanging on for life. Global warming could be
            their nail in the coffin. (Credit: Ignacio De La Riva)""",
            """The researchers's extinction model was based largely on die-offs
            of local populations in Mexico of lizards like this <i>Sceloporus
            bicanthalis</i>. The model fits lizards's extinction patterns
            worldwide, though. (Credit: Fausto Roberto M&#233;ndez de la
            Cruz)""",
            """Even though temperatures in Australia's Uluru-Kata Tjuta National
            Park are rising modestly, it may be enough to send lizards like this
            Great Desert Skink (<i>Liopholis kintorei)</i> into extinction.
            (Credit: Adam Stow)""",
            """Lizards who bear live young, like this <i>Liolaemus pictus
            </i>from Chile, are at greater risk of becoming extinct than lizards
            who lay eggs. (Credit: P. Victoriano)""",
            """Long, hot hours of daytime might prevent lizards like this
            <i>Liolaemus tenuis</i> in Central-Southern Chile from foraging
            enough to sustain their population. (Credit: P. Victoriano)""",
           ]
           
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
