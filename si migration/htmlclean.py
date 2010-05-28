#
#!/usr/bin/env python
# Basic html cleaning of MT export txt files

# Jue Wang
# 1/21/11
# 1/22/11 regexes for msoffice formatting
import re, string

# helper functions
def postlistfromfile(infile):
    # regular expressions
    re_newpost = re.compile('--------')

    # make list of posts
    thispost = ''
    posts = list()

    for line in infile:
        thispost += line
        np_m = re_newpost.search(line)
        
        if (np_m):  # new post delimiter found
            # record this post
            posts.append(thispost)
            thispost = ''
    return posts

# script starts here
iprefix = 'data/20100121/'
oprefix = 'data/20100121/'
iname = sys.argv[1]
oname = iname[0:len(iname)-4]+'-out.txt'
infile = open(iprefix+iname,'r')
outfile = open(oprefix+oname,'w')

posts = postlistfromfile(infile)
"""
filestr = ''
for post in posts:
    filestr += post
"""
res = [ re.compile(r'<(?P<tag>(?!embed)(?!iframe)\w+?)[^>]*></(?P=tag)>'),
        re.compile(r'\sclass="Mso.*?"', re.I),
        re.compile(r'\sdir="ltr"', re.I),
        re.compile(r'\sstyle="margin.*?:[0\w\s]*?;"', re.I),
        re.compile(r'<(?P<tag>(?!embed)(?!iframe)\w+?)[^>]*></(?P=tag)>'),
        re.compile(r'<(?P<tag>(?!embed)(?!iframe)\w+?)[^>]*></(?P=tag)>'),
        #re.compile(r'<p>.*?<br\s?/?>\s*(?:&nbsp;)*\s*<br\s?/?>', re.M),
        #re.compile(r'<br\s?/?>\s*(?:&nbsp;)*\s*<br\s?/?>.*?</p>', re.M)
    ]

ct = 0
filestr = ''

# process posts
for post in posts:
    for i,re in enumerate(res):
        post,n = re.subn('',post)
        ct += n
    filestr += post

#filestr,n = re_emptytag.subn('',filestr)


    
print 'substitutions made:', ct

outfile.write(filestr)
infile.close()
outfile.close()
