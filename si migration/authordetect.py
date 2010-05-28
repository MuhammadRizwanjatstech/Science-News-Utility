#!/usr/bin/env python
# Detects author names in body of ScienceInsider posts (in MT export format)
# and populates 'author' metadata field.
#
# Doesn't recognize em dashes before author names, so must convert those
# to -- before running this script

# Jue Wang
# 1/20/10
# 1/21/10 - added roundup detection
# 1/25/10 - removes author names now
import re, string, sys

# helper functions
def settostr( s=set() ):
    st = ''
    st += '(set of '+str(len(s))+')\n'
    for i in s:
        st += "\t"+i+"\n"
    return st

def separate_drafts( posts = list() ):
    published = list()
    draft = list()
    re_draft = re.compile(r'^STATUS: Draft', re.M)
    for p in posts:
        matches = re_draft.findall(p)
        if len(matches) > 0:
            #print 'A DRAFT:'
            draft.append(p)
        else:
            #print 'NOT A DRAFT:'
            published.append(p)
    print len(posts), 'separated into', len(published), 'published and', len(draft), 'drafts'
    return published, draft

def list_to_file( l, ofile):
    for i in l:
        ofile.write(i)
        
# actual script begins here

# constants
RU_AUTHOR = "Science News Staff"
DRY_RUN = True  # no writing, just output
            
# i/o, filenames
iprefix = 'data/current/'
oprefix = 'data/current/'
infilename = sys.argv[1]
outfilename = oprefix+'posts.txt'
bylined_name = oprefix+'posts-a.txt'
nobyline_name = oprefix+'posts-noa.txt'

infile = open(infilename, 'r')
if not DRY_RUN:
    outfile = open(outfilename, 'w')
    bylinefile = open(bylined_name, 'w')
    nobylinefile = open(nobyline_name, 'w')
    nobyline_published_file = open(oprefix+'posts-noa-pub.txt','w')
    nobyline_draft_file = open(oprefix+'posts-noa-dr.txt','w')
    nobyline_ru_file = open(oprefix+'posts-noa-rd.txt','w')

# regular expressions
re_newpost = re.compile('--------')
re_authorfield = re.compile('^AUTHOR: (?P<authorfield>.*)')
re_realauthor = re.compile(ur"<p[^<>]*?>\s*(--|&#8212;|\u2014|by |By |BY )\s*(?P<realauthor>\w+? (\w\. )*(\w|-)+?)\.?(&nbsp;|<[^p].*?>|\s)*?</p>")
re_roundup = re.compile(r'^TITLE:.*?Roundup', re.M)

# some bookkeeping
postdelimcount = 0
authorfldcount = 0;
realauthorcount = 0;
lookingforauthorfield = True
lookingforrealauthor = False
authorassigned = False
isroundup = False
thispost = ''

# data we want
posts_all = list()
posts_byline = list()
posts_nobyline = list()
posts_nobyline_published = list()
posts_nobyline_draft = list()
posts_nobyline_ru = list()
authorfieldset = set()
realauthorset = set()

# start reading
thispost = ''

#print "post #", postdelimcount+1
ct = 0
for line in infile:
    ct += 1
    #print line
    #print ct, lookingforauthorfield, lookingforrealauthor, authorassigned, isroundup
    np_m = re_newpost.search(line)
    aufld_m = re_authorfield.search(line)
    
    if (np_m):  # new post delimiter found
        postdelimcount = postdelimcount + 1
        #print "\npost #", postdelimcount+1
        thispost += line
        
        # record this post
        posts_all.append(thispost)
        if (authorassigned):
            posts_byline.append(thispost)
        elif (isroundup):
            # swap RU_AUTHOR into author field
            #print 'swapping in roundup author', RU_AUTHOR
            thispost = re_authorfield.sub("AUTHOR: "+RU_AUTHOR, thispost, 1)
            posts_nobyline_ru.append(thispost)
        else:
            posts_nobyline.append(thispost)
        thispost = ''        
        lookingforauthorfield = True
        lookingforrealauthor = False
        authorassigned = False
        isroundup = False
    elif (lookingforauthorfield and aufld_m):   # author field found
        authorfldcount = authorfldcount +1
        authorfield = aufld_m.group('authorfield')
        authorfieldset.add(authorfield)
        #print "Author field:", authorfield
        lookingforauthorfield = False
        lookingforrealauthor = True
        thispost += line      
    elif (lookingforrealauthor):    # looking for real author
        rlau_m = re_realauthor.search(line)
        rd_m = re_roundup.search(line)
        thispost += line

        if (rlau_m):    # real author found
            realauthorcount = realauthorcount +1
            realauthor = rlau_m.group('realauthor')
            realauthor = string.capwords(realauthor)
            realauthorset.add(realauthor)
            #print "Real author:", realauthor
            authorassigned = True
            lookingforrealauthor = False

            # swap realauthor into author field
            #print 'swapping in ',realauthor
            thispost = re_authorfield.sub("AUTHOR: "+realauthor, thispost, 1)
            # remove mention of author from body
            thispost = re_realauthor.sub("", thispost, 1)
            #authorline = rlau_m.group(0)
            #print authorline
            #thispost = thispost.replace(authorline,'',1)
            #print thispost
        elif (rd_m):    # it's a roundup, set author to Science News Staff
            isroundup = True
    else:   # write the rest of post data 
        thispost += line

# separate drafts
posts_nobyline_published, posts_nobyline_draft = separate_drafts(posts_nobyline)

# output data
if not DRY_RUN:
    list_to_file(posts_all, outfile)
    list_to_file(posts_byline, bylinefile)
    list_to_file(posts_nobyline, nobylinefile)
    list_to_file(posts_nobyline_published, nobyline_published_file)
    list_to_file(posts_nobyline_draft, nobyline_draft_file)
    list_to_file(posts_nobyline_ru, nobyline_ru_file)
        
print '\nSUMMARY:\n-----------'
if DRY_RUN:
    print 'DRY RUN ONLY. NO OUTPUT FILES WERE WRITTEN.'
print 'post delimiters found:', postdelimcount
print 'author fields found:', authorfldcount
print 'real authors found:', realauthorcount
print 'posts:', len(posts_all)
print 'bylined posts:', len(posts_byline)
print 'unbylined posts:', len(posts_nobyline)
print '\tpublished:', len(posts_nobyline_published)
print '\tdraft:', len(posts_nobyline_draft)
print 'roundups (author set to',RU_AUTHOR,'):', len(posts_nobyline_ru)
print 'unique author fields: ', settostr(authorfieldset)
print 'unique real authors: ', settostr(realauthorset)

infile.close()
if not DRY_RUN:
    outfile.close()
    bylinefile.close()
    nobylinefile.close()
    nobyline_published_file.close()
    nobyline_draft_file.close()
    nobyline_ru_file.close()

    
