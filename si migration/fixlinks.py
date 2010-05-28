#!/usr/bin/env python
# Detects links to files on blogserver

# Jue Wang
# 1/20/10
import re, string, sys

# helper functions
# actual script begins here

# i/o, filenames

infile = open(sys.argv[1], 'r')
out = open(sys.argv[2], 'w')

DRY_RUN = False

# regular expressions
re_rootlink = re.compile(r'"(http://blogs.sciencemag.org/[^/]*?)"')
re_sirootlink = re.compile(r'"http://blogs.sciencemag.org/scienceinsider/(?P<name>[^/]*?)"')
re_link = re.compile(r'"http://blogs.sciencemag.org/.*?"')

ct = 0
print 'all links:'
for line in infile:
    urls = re_sirootlink.finditer(line)
    n=0
    if urls:
        for url in urls:
            print url.group(0).strip('"')
            n+=1
    if not DRY_RUN:
        line, n = re_sirootlink.subn('"/sciencenow-dev/scienceinsider/entry-assets/\g<name>"',line)
        out.write(line)
    #for i in matches:
     #   print i.group(0)
        
    ct += n
print 'total matches: ', ct

infile.close()
out.close()
