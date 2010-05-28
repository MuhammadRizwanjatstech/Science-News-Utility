#!/usr/bin/env python
# jw 1/28/2010

import csv, sys, urllib2, re
from BeautifulSoup import BeautifulSoup

ifile  = sys.stdin 
ofile  = sys.stdout

soup = BeautifulSoup(ifile.read())
#print soup

reg = re.compile(r'href="([^"]*)"')
container = soup.find('table',{'id' : 'entry-listing-table'})
#print container
hits = container.findAll("a",{"title" : "View entry"})

#links = list()
n=0
for h in hits:
    #links.append(h['href'])
    ofile.write(h['href']+'\n')
    n+=1

#print n
#print len(links)
ifile.close()
ofile.close()
