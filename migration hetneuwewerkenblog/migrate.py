#! /usr/bin/env python
import os
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
forum_id = None
forum_index = 0 
globalparams = {'api_version': API_VERSION,
                'user_api_key': API_KEY}
inputfile = 'hetnieuwewerkenblog.nl-comments.xml' 
api = GenericAPIWrapper(debug_level=0, input_encoding='utf-8')
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
    global forum_api_key, forum_id
    forum_api_key = data['message']
    forum_id = forum['id']
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
        comct = 0
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
                    # nonbreaking spaces
                    com['name'] = com['name'].replace(u'\xa0',' ')
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
            comct += len(comments)
            threads.append((link, comments))
        threads = process_threads(threads)
        cPickle.dump(threads, open(cachefile,'w'))
        print comct,'comments in',len(threads),'threads.'
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

def thread_by_identifier(identifier, title=''):
    params = globalparams.copy()
    params['identifier'] = identifier
    params['forum_api_key'] = forum_api_key
    params['title'] = title
    return api.FetchUrl(API_URL % 'thread_by_identifier', post_data=params)

def update_thread(id, title=None, allow_comments=None, slug=None, url=None):
    params = globalparams.copy()
    params['id'] = id
    params['forum_api_key'] = forum_api_key
    if title:
        params['title'] = title
    if allow_comments:
        params['allow_comments'] = allow_comments
    if slug:
        params['slug'] = slug
    if url:
        params['url'] = url
    return api.FetchUrl(API_URL % 'update_thread', post_data=params)

def create_post(thread_id, message, author_name, author_email, created_at=None,
                ip_address=None, author_url=None, parent_post=None, state=None):
    params = globalparams.copy()
    params['forum_api_key'] = forum_api_key
    params['thread_id'] = thread_id
    params['message'] = message
    params['author_name'] = author_name
    params['author_email'] = author_email
    if created_at:
        params['created_at'] = created_at
    if ip_address:
        params['ip_address'] = ip_address
    if author_url:
        params['author_url'] = author_url
    if parent_post:
        params['parent_post'] = parent_post
    if state:
        params['state'] = state
    return api.FetchUrl(API_URL % 'create_post', post_data=params)

def dsq_import():
    get_forum_api_key()
    threads = parse_threads()
    ids = {}
    print 'Importing comments to Disqus...'
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
        # get a thread to post to
        print 'Fetching thread',url
        data, headers = get_thread_by_url(url)
        dsqthread = data['message']
        #print dsqthread
        if dsqthread:
            #pp.pprint(data)
            id = dsqthread['id']
            identifier = dsqthread['identifier']
            print 'id:',
            pp.pprint(id)
            print 'identifier:',
            pp.pprint(identifier)
        else:
            print 'Get thread by URL failed. Creating by identifier instead...'
            data, headers = thread_by_identifier(path,title=url+' comments')
            dsqthread = data['message']
            if dsqthread:
                id = dsqthread['id']
                identifier = dsqthread['identifier']
                update_thread(id,url=url)
            else:
                print 'Create thread by identifier failed. Skipping this thread.'
                continue
        # now post the comments
        for com in comments:
            #print 'JSK Comment. Email:',com['email'].encode('utf-8'),'| IP:',com['ip']
            try:
                data, headers = create_post(id, 
                                        com['msg'].encode('utf-8'),
                                        com['name'].encode('utf-8'),
                                        com['email'].encode('utf-8'),
                                        parent_post=get_parent(com, ids), 
                                        created_at=com['created'].strftime('%Y-%m-%dT%H:%M'),
                                        author_url=com['url'],
                                        ip_address=com['ip'])
                dsqcom = data['message']
                if dsqcom:
                    ids[com['id']] = dsqcom['id']
                    print 'Disqus comment created: '+dsqcom['id']+' (JSK id: '+com['id']+')' 
                else:
                    'Comment creation failed. JSK id:',com['id']
            except urllib.HTTPError,e:
                print e
                print com
    print 'Processing complete.'

def get_all_comments():
    """Return list of all comments from Disqus account"""
    params = globalparams.copy()
    get_forum_api_key()
    params['forum_api_key'] = forum_api_key
    params['forum_id'] = forum_id
    # get all comment ids
    params['limit'] = 100
    params['start'] = 0
    params['filter'] = 'approved'
    params['exclude'] = 'killed'
    print 'Getting comments...'
    comments = []
    while 1:
        data, headers = api.FetchUrl(API_URL % 'get_forum_posts', 
                                     parameters=params,
                                     verbose=True)
        posts = data['message']
        #pp.pprint(posts)
        if posts:
            comments.extend(posts)
        else:
            break
        params['start'] += params['limit']
    print len(comments),'comments found.'
    return comments
   
def deleteall():
    """Deletes all comments in a forum. Use with caution."""
    ids = [x['id'] for x in get_all_comments()]
    print 'Deleting all comments...'
    # delete comments
    for id in ids:
        params = globalparams.copy()
        params['post_id'] = id
        params['action'] = 'kill'
        data, headers = api.FetchUrl(API_URL % 'moderate_post', post_data=params)
        if data['succeeded']:
            print 'Deleted comment',id
        else:
            'Failed to delete comment',id


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
        if sys.argv[1] == 'parse':
            parse_threads(refresh=True)
        if sys.argv[1] == 'import':
            dsq_import()
        if sys.argv[1] == 'delete':
            deleteall()
        if sys.argv[1] == 'getall':
            get_all_comments()
