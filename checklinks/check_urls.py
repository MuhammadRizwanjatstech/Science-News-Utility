#!/usr/bin/env python

"""Broken link checker for Insider
"""
import sys
import urllib2
import os
import pprint
import re
import simplejson as json
from httpExists import *
from httplib import HTTP
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup
 
pp = pprint.PrettyPrinter(indent=2)

def get_entry_urls(urlfile='entryurls.json',refresh=False):
    """Return list of all entry URLs in ScienceInsider archives"""
    if refresh:
        os.remove(urlfile)
    try:
        urls = json.load(open(urlfile,'r'))
        print len(urls),'URLs loaded from file',urlfile
    except:
        # get monthly archive urls
        archiveindex = 'http://news.sciencemag.org/scienceinsider/archives.html'
        page = urllib2.urlopen(archiveindex)
        soup = BeautifulSoup(page)
        archivediv = soup.find('ul',{'class':'archive-list'})
        months = [x['href'] for x in archivediv.findAll('a')]
        print 'Getting entry urls...'
        urls = []
        for month in months:
            print month,'...'
            page = urllib2.urlopen(month)
            soup = BeautifulSoup(page)
            items = soup.findAll('div',{'class':re.compile('.*sci-item.*')})
            for item in items:
                link = item.h3.a['href']
                urls.append(link)
            print len(items),'entries.'
        print len(urls),'URLs written to',urlfile
        json.dump(urls,open(urlfile,'w'))
    return urls

def get_asset_urls(urls, urlfile='asseturls.json',refresh=False):
    """Return list of all asset URLs, extracted from a given list of entries"""
    if refresh:
        os.remove(urlfile)
    try:
        tocheck = json.load(open(urlfile,'r'))
        count = reduce(lambda ct,item: ct+len(item[1]), tocheck, 0)
        print count,'asset URLs in',len(tocheck),'entries loaded from file',urlfile
    except:
        # get monthly archive urls
        print 'Getting image/anchor links from',len(urls),'entries...'
        tocheck = []
        linkct=0
        for n,url in enumerate(urls):
            print str(n)+': ',url
            page = urllib2.urlopen(url)
            soup = BeautifulSoup(page)
            content = soup.find('div',{'class':re.compile('.*sci-content-bd.*')})
            images = content.findAll('img')
            imageurls = [x['src'] for x in images]
            print len(imageurls),'images,',
            add_root('http://news.sciencemag.org',imageurls)
            anchors = content.findAll('a')
            anchorurls = [x['href'] for x in anchors]
            add_root('http://news.sciencemag.org',anchorurls)
            print len(anchorurls),'anchors'
            combined = []
            combined.extend(imageurls)
            combined.extend(anchorurls)
            tocheck.append((url,combined))
            linkct += len(imageurls)+len(anchorurls)
        print len(tocheck),'URLs written to',urlfile
        json.dump(tocheck,open(urlfile,'w'))
    return tocheck

def find_broken(urls):
    broken = []
    for i in urls:
        # any http request that doesn't return 200
        if httpExists(i) != 1:
            broken.append(i)
    return broken

def add_root(root, urls):
    """Adds a root url to relative urls"""
    for i,url in enumerate(urls):
        if url and url[0] == '/':
            urls[i] = root+url

def check_urls(outfile='broken2.txt',refresh=False):
    """Checks all entries in ScienceInsider archive for broken <a href> and
    <img> URLs, lists the ones it finds"""
    urls = get_entry_urls(refresh=refresh)
    tocheck = get_asset_urls(urls, refresh=refresh)
    count = reduce(lambda ct,item: ct+len(item[1]), tocheck, 0)
    # check all the entries for broken images / anchors
    print 'Checking',count,'urls in',len(tocheck),'entries for broken links...'
    allbroken = []
    tab = '  '
    for entry in tocheck:
        url,links = entry
        print 'In',url,'...'
        broken = find_broken(links)
        allbroken.extend(broken)
    print 'Found',len(allbroken),'broken links.'

    f = open(outfile,'w')
    for url in allbroken:
        print >>f, url


def download(url, prefix=''):
	"""Copy the contents of a file from a given URL
	to a local file.
	"""
	import urllib
	webFile = urllib.urlopen(url)
	localFile = open(prefix+urllib.unquote(url.split('/')[-1]), 'w')
	localFile.write(webFile.read())
	webFile.close()
	localFile.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'check':
            if len(sys.argv) > 2 and sys.argv[2] == 'refresh':
                check_urls(refresh=True)
            else:
                check_urls()
