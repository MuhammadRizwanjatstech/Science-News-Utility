#!/usr/bin/env python

"""File downloading from the web.
"""

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
    import sys
    inf = open(sys.argv[1],'r')
    for line in inf:
        print 'downloading',line
        download(line.strip(),'files/')
