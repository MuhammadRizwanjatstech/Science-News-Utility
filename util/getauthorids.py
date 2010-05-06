#!/usr/bin/env python
# jw 1/28/2010

import csv, sys, urllib2, re
from BeautifulSoup import BeautifulSoup

ifile  = open(sys.argv[1], "rb")
reader = csv.reader(ifile)
soupfile = open(sys.argv[2], "r")
ofile  = open(sys.argv[3], "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

soup = BeautifulSoup(soupfile.read())

userid = re.compile(r'&amp;id=(\d*)')
author = re.compile(r'<a[^<>]*>(\w*)</a>')
usertags = soup.findAll('td', {'class':'username'})
idlinks = [tag.contents[0] for tag in usertags]
authors = [author.findall(str(i))[0] for i in idlinks]
print authors
ids = [userid.findall(str(i))[0] for i in idlinks]
lookup = dict();

for i,item in enumerate(authors):
    lookup[item]=ids[i]

print lookup

rownum = 0
for row in reader:
    # Save header row.
    if rownum == 0:
        header = row
    else:
        username = row[3]
        print username
        if username in lookup:
            row.append(lookup[username])
        else:
            row.append('no id')
    writer.writerow(row)
    rownum += 1

ifile.close()
ofile.close()
