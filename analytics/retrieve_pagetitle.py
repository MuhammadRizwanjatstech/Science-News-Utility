#! /usr/bin/env python
# jw 1/28/2010

import csv, sys, urllib2, re
from BeautifulSoup import BeautifulSoup

ifile  = open(sys.argv[1], "rb")
reader = csv.reader(ifile)
ofile  = open(sys.argv[2], "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

reg = re.compile('(.*?)--')


rownum = 0
for row in reader:
    # Save header row.
    if rownum == 0:
        header = row
    else:
        if row[0]:
            root = row[0]
            stem = row[1]
            url = root+stem
            print url
            try:
                page = urllib2.urlopen(url)
                soup = BeautifulSoup(page)
                title = soup.head.title.contents[0].strip()
                m = reg.match(title)
                if m:
                    title = m.group(1)
                print title
                row.append(title.encode('utf-8'))
            except urllib2.HTTPError,e:
                row.append(url)
                print e
        writer.writerow(row)
    rownum += 1

ifile.close()
ofile.close()
