#! /usr/bin/env python
from BeautifulSoup import BeautifulSoup
import codecs
import re

f=open('news templates.html', 'r')
soup = BeautifulSoup(f)

links = soup.findAll('td',{'class':re.compile('.*(template-name|widgetmanager-name).*')})

for x in links:
    anchor = x.a
    if anchor:
        print '  * [[http://news.sciencemag.org'+anchor['href']+'|'+anchor.string+']]'

