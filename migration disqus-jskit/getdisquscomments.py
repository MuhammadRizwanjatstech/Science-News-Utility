#! /usr/bin/env python
import pprint
import sys
import simplejson as json
from GenericAPIWrapper import GenericAPIWrapper
from datetime import datetime

BASE_URL = "http://disqus.com/api/%s/"
API_VERSION = "1.1"

REQUEST_METHODS = {
"create_post": "POST",
"get_forum_list": "GET",
"get_forum_api_key": "GET",
"get_thread_list": "GET",
"get_num_posts": "GET",
"get_thread_by_url": "GET",
"get_thread_posts": "GET",
"thread_by_identifier": "POST",
"update_thread": "POST",
}

pp = pprint.PrettyPrinter(indent=4)
api = GenericAPIWrapper(debug_level=1)
def get_comments(dumpfile):
    # get forum
    forum_index = 1 # the forum (i.e. site) where you'll be putting comments
    params = {}
    params['user_api_key'] = 'J02qcLb3NIgHS06Ow5CD5xEPXwyRuZjYBNPM4hVxf7pX01w3lcectGqlpPyMBcz5' # danish guy's account api key
    #params['user_api_key'] = 'sgf7NKCcxNJwFqoFW53idFFSL5b4XzCQe7lzmX7UgShE3E7TrYGBjNxhzNTE1IBR'}
    params['api_version'] = API_VERSION
    url = BASE_URL % 'get_forum_list'
    data,headers = api.FetchUrl(url, parameters=params)
    forum = data['message'][forum_index]
    pp.pprint(forum)


    # get comments from forum
    url = BASE_URL % 'get_forum_posts'
    params['forum_id'] = forum['id']
    params['filter'] = 'approved'

    # only retrieve comments posted after this
    #since = datetime(2010, 3, 21, 16, 28, 56)
    since = datetime(1900, 3, 21, 16, 28, 56)
    # totallimit = 1500
    n = 50
    p = 1

    total = 0
    allposts = []

    #data = api.FetchUrl(url, parameters=params)
    #sys.exit()
    keeplooping = True
    # fetch all comments posted after 'since'
    while keeplooping:
        params['limit'] = n
        params['start'] = (p - 1) * n
        data,headers = api.FetchUrl(url, parameters=params)
        if data['succeeded']:
            posts = data['message']
            print len(posts), 'comments retrieved in this batch'
            if not posts:
                keeplooping = False

            for post in posts:
                created_at = datetime.strptime(post['created_at'], "%Y-%m-%dT%H:%M")
                print post['thread']['url']
                print post['created_at']

                if created_at < since: #if total > totallimit:
                    # Reached the limit post, stop fetching
                    keeplooping = False
                    print 'Earliest post encountered at',created_at
                    pp.pprint(post)
                    break
                else:
                    allposts.append(post)
                    total += 1
            p += 1
        else:
            print 'Data retrieval failed.'
            keeplooping = False

    print 'Dumping',total,'total posts to file:',filename
    f = open(dumpfile,'w')
    json.dump(allposts, f, indent=2*' ')

def process_threads():
    forum_index = 1 # the forum (i.e. site) where you'll be putting comments
    params = {}
    params['user_api_key'] = 'J02qcLb3NIgHS06Ow5CD5xEPXwyRuZjYBNPM4hVxf7pX01w3lcectGqlpPyMBcz5' # danish guy's account api key
    #params['user_api_key'] = 'sgf7NKCcxNJwFqoFW53idFFSL5b4XzCQe7lzmX7UgShE3E7TrYGBjNxhzNTE1IBR'}
    params['api_version'] = API_VERSION
    url = BASE_URL % 'get_forum_list'
    data,headers = api.FetchUrl(url, parameters=params)
    forum = data['message'][forum_index]
    pp.pprint(forum)


    # get comments from forum
    url = BASE_URL % 'get_forum_posts'
    params['forum_id'] = forum['id']
    params['filter'] = 'approved'


if __name__ == "__main__":
    if len(sys.argv) > 0:
        if sys.argv[1] == 'getcomments':
            filename = 'comments2.json'
            get_comments(filename)
        if sys.argv[1] == 'processthreads':
            process_threads()
