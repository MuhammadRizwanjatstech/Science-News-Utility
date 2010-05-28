#!/usr/bin/env python
# converts movable type author names into 8-character Active Directory style
# usernames -- first letter of first name + first 7 letters of last
# Richard Kerr ==> rkerr
# Erik Stokstad ==> estoksta
#
# Jue Wang
# 1/25/10
import re, string, sys

# initialize lookup table with exceptions
names = { 'Jue Wang':'juewang',
          'Jennifer Couzin-frankel':'jcouzin',
          'Science News Staff':'newsstaff',
          'No Primary Author':'noprimaryauthor',
          'policy blog':'newsstaff'}

inf = open(sys.argv[1], 'r')    # names file
source = open(sys.argv[2], 'r') # source entry data
out = open(sys.argv[3], 'w')    # output file

for line in inf:
    words = line.strip().lower().split(' ')
    if len(words) >= 2:
        first = words[0]
        last = words[len(words) - 1]
        
        uname = first[0]
        if len(last) <= 7:
            uname += last
        else:
            uname += last[0:7]

        if (line.strip() not in names):
            names[line.strip()] = uname
            
#print names
# sorted
l = sorted(names.items(), key=lambda(k,v):(v,k))
for i in l:
    print i[0],'\t\t',i[1]


# process entry data
re_authorfield = re.compile('^AUTHOR:\s*?(?P<authorfield>.*)')

for line in source:
    m = re_authorfield.search(line)
    if m:
        aname = m.group('authorfield').strip()
        if aname in names:
            line = line.replace(aname, names[aname])
    out.write(line)
    
