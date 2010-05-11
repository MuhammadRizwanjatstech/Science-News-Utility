"""
httpExists.py

A quick and dirty way to to check whether a web file is there.

Usage:
>>> from httpExists import *
>>> httpExists('http://www.python.org/')
1
>>> httpExists('http://www.python.org/PenguinOnTheTelly')
Status 404 Not Found : http://www.python.org/PenguinOnTheTelly
0
"""

import httplib
import urlparse

def httpExists(url):
    host, path = urlparse.urlsplit(url)[1:3]
    found = False
    try:
        connection = httplib.HTTPConnection(host)  ## Make HTTPConnection Object
        connection.request("HEAD", path)
        responseOb = connection.getresponse()      ## Grab HTTPResponse Object

        if responseOb.status == 200 or responseOb.status == 302:
            found = True
        else:
            print "Status %d %s : %s" % (responseOb.status, responseOb.reason, url)
    except Exception, e:
        print e.__class__,  e, url
        return e
    return found

def _test():
    import doctest, httpExists
    return doctest.testmod(httpExists)

if __name__ == "__main__":
    _test()
