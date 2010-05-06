#! /usr/bin/env python
import sys
import cPickle
import urlparse
import pprint
import urllib2 as urllib
from GenericAPIWrapper import GenericAPIWrapper
from datetime import datetime
from BeautifulSoup import BeautifulStoneSoup
# globals
API_URL = "http://disqus.com/api/%s/"
API_VERSION = "1.1"
API_KEY = 'J02qcLb3NIgHS06Ow5CD5xEPXwyRuZjYBNPM4hVxf7pX01w3lcectGqlpPyMBcz5'
forum_api_key = None
forum_index = 0 
globalparams = {'api_version': API_VERSION,
                'user_api_key': API_KEY}
inputfile = 'hetnieuwewerkenblog.nl-comments.xml' 
api = GenericAPIWrapper(debug_level=0)
pp = pprint.PrettyPrinter(indent=4)
tab = '  '

def get_forum_api_key():
    params = globalparams.copy()
    url = API_URL % 'get_forum_list'
    data,headers = api.FetchUrl(url, parameters=params)
    forum = data['message'][forum_index]
    #pp.pprint(forum)
    params['forum_id'] = forum['id']
    params['filter'] = 'approved'
    url = API_URL % 'get_forum_api_key'
    data, headers = api.FetchUrl(url, parameters=params)
    global forum_api_key
    forum_api_key = data['message']
    print 'Forum',forum['name'],'('+forum['shortname']+')'

def parse_threads(refresh=False, cachefile='soup.cPickle'):
    if refresh:
        print 'Deleting cache file',cachefile
        try:
            os.remove(cachefile)
        except os.OSError:
            pass
    try:
        threads = cPickle.load(open(cachefile,'r'))
        print 'Threads loaded from cache',cachefile
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
        threads = process_threads(threads)
        cPickle.dump(threads, open(cachefile,'w'))
        print 'Parsed threads cached to',cachefile
    return threads

def process_threads(threads):
    """consolidate duplicate urls and translate ?p=# urls to prettified wp
    permalinks"""
    print 'Consolidating threads and resolving thread urls...'
    newthreads = {}
    nrenamed = 0
    for thread in threads:
        url,comments = thread
        if '/p=' in url:
            url = url.replace('/p=','/?p=')
            nrenamed += 1
        #print url
        url = get_wp_permalink(url)
        print url
        newthreads[url] = comments
    print len(threads),'threads consolidated to ',len(newthreads),'threads;',
    print nrenamed,'thread urls renamed.'
    return newthreads

def get_wp_permalink(url):
    response = urllib.urlopen(url)
    return response.geturl()

def dsq_threadcheck():
    get_forum_api_key()
    threads = parse_threads()
    ids = {}
    print 'Checking threads...'
    f = open('threadlog.txt','w')
    for url in threads:
        comments = threads[url]
        print url
        # put parents before children
        sort_by_date(comments)
        # prepare disqus thread
        s = urlparse.urlsplit(url)
        host = s.hostname
        path = s.path
        path = path.rstrip('/')
        if path == '':
            path = '/'
        # get thread by url
        data, headers = get_thread_by_url(url)
        dsqthread = data['message']
        print dsqthread
        print 'get_thread_by_url:'
        if dsqthread:
            #pp.pprint(data)
            id = dsqthread['id']
            identifier = dsqthread['identifier']
            print 'id:',
            pp.pprint(id)
            print 'identifier:',
            pp.pprint(identifier)
        else:
            print 'No thread found. Creating one...'
        break


def get_thread_by_url(url):
    params = globalparams.copy()
    params['url'] = url
    params['forum_api_key'] = forum_api_key
    return api.FetchUrl(API_URL % 'get_thread_by_url', parameters=params)

def dsq_import():
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
