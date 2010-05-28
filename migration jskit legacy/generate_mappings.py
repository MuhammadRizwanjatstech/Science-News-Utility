#! /usr/bin/env python
'''Generates URL mappings from sciencenow.sciencemag.org comment threads to
news.sciencemag.org comment threads. Both are on JS-Kit'''

import pprint
import sys
import re
import pickle
from BeautifulSoup import BeautifulStoneSoup

pp = pprint.PrettyPrinter(indent=2)
filename = 'sciencenow.sciencemag.org-comments.xml'#'test.xml' 
urlfile = 'urls.txt'

def extract_urls():
    print 'Parsing XML in', filename, '...'
    soup = BeautifulStoneSoup(open(filename,'r'))
    items = soup.findAll('item')
    outfile = open('urlfile','w')

    print 'Found',len(items),'comments. Outputting URLs to file...'
    for item in items:
        urltag = item.find('jskit:attribute', {'key':'permalink'})
        url = urltag['value']
        outfile.write(url+'\n')
    outfile.close()

def comments_per_url(outfile):
    f = open(urlfile, 'r')
    o = open(outfile, 'w')
    lines = f.readlines()
    print 'Found',len(lines),'comment urls in file',urlfile
    ulines = []
    counts = {}
    # we only need mappings for unique urls
    for line in lines:
        if line in ulines:
            counts[line] += 1
        else:
            ulines.append(line)
            counts[line] = 1
    ulines.sort()
    print 'Found',len(ulines),'unique comment urls'
    for line in ulines:
        print >>o, line.rstrip('\n'), 'has', counts[line],'comments.'

def pad(s, width):
    if len(s) < width:
        return str((width-len(s))*'0') + s
    else:
        return s[:width]

def generate_mappings(outfile):
    f = open(urlfile, 'r')
    o = open(outfile, 'w')
    lines = f.readlines()
    print 'Found',len(lines),'comment urls in file',urlfile
    ulines = []
    counts = {}
    # we only need mappings for unique urls
    for line in lines:
        if line in ulines:
            counts[line] += 1
        else:
            ulines.append(line)
            counts[line] = 1
    ulines.sort()
    print 'Found',len(ulines),'unique comment urls'

    mappings = []
    re1 = re.compile(r'http://sciencenow.sciencemag.org/cgi/content/(full|short|citation)/(?P<year>\d+)/(?P<monthdate>\d+)/(?P<num>\d+)')
    re2 = re.compile(r'http://sciencenow.sciencemag.org/cgi/content/full/sciencenow;(?P<year>\d+)/(?P<monthdate>\d+)/(?P<num>\d+)')
    root = 'http://news.sciencemag.org/sciencenow'
    for line in ulines:
        m = re1.search(line)
        if not m:
            m = re2.search(line)
        if m:
            year = m.group('year')
            monthdate = m.group('monthdate')
            month = monthdate[:-2]
            month = pad(month,2)
            date = monthdate[-2:]
            num = m.group('num')
            num = pad(num,2)
            newurl = root+'/'+year+'/'+month+'/'+date+'-'+num+'.html'
            line = line.rstrip('\n')
            mappings.append((line, newurl))
        else:
            print 'Not mapped:',line

    print 'Writing',len(mappings),' mappings to file',outfile
    for mapping in mappings:
        print >>o, mapping[0]+'\t->\t'+mapping[1]
    
if __name__ == '__main__':
    if len(sys.argv) > 0:
        if sys.argv[1] == 'generate':
            generate_mappings(sys.argv[2])
        if sys.argv[1] == 'urlprocess':
            url_process(sys.argv[2])
        if sys.argv[1] == 'count':
            comments_per_url(sys.argv[2])
