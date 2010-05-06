#! /usr/bin/env python
import sys
import cPickle
import urlparse
from GenericAPIWrapper import GenericAPIWrapper
from datetime import datetime
from BeautifulSoup import BeautifulStoneSoup
# globals
API_URL = "http://disqus.com/api/%s/"
API_VERSION = "1.1"
API_KEY = 'J02qcLb3NIgHS06Ow5CD5xEPXwyRuZjYBNPM4hVxf7pX01w3lcectGqlpPyMBcz5'
forum_api_key = None
forum_index = 1 
globalparams = {'api_version': API_VERSION,
                'user_api_key': API_KEY}
inputfile = 'hetnieuwewerkenblog.nl-comments.xml' 
api = GenericAPIWrapper(debug_level=1)

def get_forum_api_key():
    params = globalparams.copy()
    params['forum_id'] = forum_index
    print api.FetchUrl(API_URL % 'get_forum_api_key', parameters=params)

def parse_threads(refresh=False, cachefile='soup.cPickle'):
    if refresh:
        try:
            os.remove(cachefile)
        except os.OSError:
            pass
    try:
        threads = cPickle.load(open(cachefile,'r'))
    except IOError:
        soup = BeautifulStoneSoup(open(inputfile))
        print 'Parsing xml file',inputfile
        channels = soup.findAll('channel')
        threads = []
        for channel in channels:
            title = channel.find('title').contents[0]
            link = channel.find('link').contents[0]
            print 'Thread:',link
            items = channel.findAll('item')
            print len(items),' comments'
            comments = []
            for item in items:
                com = dict()
                com['id'] = item.find('guid').contents[0]
                iptag = item.find('jskit:attribute', {'key' : 'IP'})
                if iptag:
                    com['ip'] = iptag['value']
                else:
                    com['ip'] = '255.255.255.0'
                com['name'] = item.find('author')
                if com['name']:
                    com['name'] = com['name'].contents[0]
                    com['email'] = com['name'].replace(' ','_')+'@jskit.hetnieuwewerkenblog.nl'
                else:
                    com['name'] = 'Guest'
                    com['email'] = 'guest@jskit.hetnieuwewerkenblog.nl'
                com['url'] = None
                com['msg'] = item.find('description').contents[0]
                datestring = item.find('pubdate').contents[0]
                com['created'] = datetime.strptime(datestring,'%a, %d %b %Y %H:%M:%S +0000')
                parent = item.find('jskit:parent-guid')
                if parent:
                    com['parent'] = parent.contents[0]
                else:
                    com['parent'] = None
                comments.append(com)
            threads.append((link, comments))
        cPickle.dump(threads, open(cachefile,'w'))
    return threads

def dsq_threadcheck():
    get_forum_api_key()
    threads = parse_threads()
    ids = {}
    print 'Checking threads...'
    f = open('threadlog.txt','w')
    for thread in threads:
        url,comments = thread
        print url
        # put parents before children
        sort_by_date(comments)
        # prepare disqus thread
        s = urlparse.urlsplit(url)
        host = s.hostname
        path = s.path
        # get thread by url
        dsqthread = get_thread_by_url(url)
        print 'get_thread_by_url:'
        print dsqthread

def get_thread_by_url(url):
    params = copy(globalparams)
    return api.FetchUrl(API_URL % 'get_thread_by_url', parameters=params)

def dsq_import():
    dsq_setup()
    threads = parse_threads()
    ids = {}
    for thread in threads:
        url,comments = thread
        # put parents before children
        sort_by_date(comments)
        # prepare disqus thread
        s = urlparse.urlsplit(url)
        host = s.hostname
        path = s.path
        # get thread by url
        try:
            dsqthread = dsq.get_thread_by_url(dsqforum,url)
        except disqus.APIError:
            print 'Get thread by URL failed.'
            try:
                dsqthread = dsq.thread_by_identifier(dsqforum,title=thid+' comments',identifier=thid)['thread']
                dsq.update_thread(dsqforum,dsqthread,url=url)
            except disqus.APIError:
                print 'Can\'t create thread. Skipping this one.'
                continue
        for com in comments:
            print 'JSK Comment. Author: '+com['name']+' | IP: '+com['ip']
            try:
                dsqcom = dsq.create_post(dsqforum,
                                         dsqthread,
                                         com['msg'],
                                         com['name'].encode('utf-8'),
                                         com['email'],
                                         get_parent(com, ids),
                                         com['created'],
                                         com['url'],
                                         com['ip'])
                ids[com['guid']] = dsqcom.id
                print 'Disqus comment created: '+dsqcom.id+' (JSK id: '+com['guid']+')' 
            except disqus.APIError:
                print 'APIError in create_post.'
    print 'Processing complete.'

def get_parent(com, ids):
	if com['parent']:
		if com['parent'] in ids:
			return ids[com['parent']]
	return None

def my_key(comment):
    return comment['created']

def sort_by_date(posts):
    posts.sort(key=my_key)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'threadcheck':
            dsq_threadcheck()
