#! /usr/bin/env python
import pprint
import sys
import re
import simplejson as json
import cookielib
import urllib2
from BeautifulSoup import BeautifulStoneSoup
from GenericAPIWrapper import GenericAPIWrapper
from datetime import datetime

pp = pprint.PrettyPrinter(indent=4)
api = GenericAPIWrapper(debug_level=1)

post_comment_url = 'http://js-kit.com/comment.put'
del_comment_url = 'http://js-kit.com/comment.del'

filename = 'comments.json'

# admin login cookie
admin_ck = cookielib.Cookie(version=0, 
                      name='jsKitUser',
                      port=None,
                      port_specified=False,
                      value='GFoyM4l1Zwv9T5RxZm47ZTXG33MRF5ZSRYoBCyn_YSmvzVspcEvzHg--',
                      domain='.js-kit.com', 
                      domain_specified=True, 
                      domain_initial_dot=True,
                      path='/', 
                      path_specified=True, 
                      secure=False, 
                      expires=None,
                      discard=False,
                      comment=None,
                      comment_url=None,
                      rest=None,
                      rfc2109=False
                     )

# hash for storing dsq -> jsk id mappings
ids = {}

def get_parent_id(com):
	global ids
	if com['parent_post']:
		if com['parent_post'] in ids:
			return ids[com['parent_post']]
	return None

def reorder_parentsfirst(posts):
    posts = posts[:]
    out = list()
    orphaned = list()
    i = 0
    while len(posts) > 0:
        #dprint('i='+str(i)+', len(jskcomments)='+str(len(jskcomments)))
        com = posts[i]
        p_id = com['parent_post']
        if p_id: # search for parent and set i to its index
            #dprint('Parent id: '+p_id)
            found = False

            for j, par in enumerate(posts):
                #dprint('j='+str(j))
                #dprint('Match? '+par['guid'])
                if par['id'] == p_id:
                    i = j
                    found = True
                    break

            found2 = False
            for k, par in enumerate(out):
                if par['id'] == p_id:
                    found2 = True
                    break
            if not found and not found2:
                print 'Parent',p_id,'not found in comments.'
                orphaned.append(com)

            if not found:
                out.append(com)
                del posts[i]
                i = 0

        else:	# no parent, ok to remove element and put into new list
            out.append(com)
            del posts[i]
            i = 0
    return out,orphaned

def my_key(comment):
    return datetime.strptime(comment['created_at'], "%Y-%m-%dT%H:%M")

def sort_by_date(posts):
    posts.sort(key=my_key)

def post_comments_from_file():
    '''Read comments from a pickle file and post the comments on JS-Kit, taking
    care to preserve threading where parent IDs are indicated.'''
    global ids, admin_ck
    comments = json.load(open(filename,'r'))
    print 'Making sure comments are in order of parents first (sorting by date/time)...'
    #comments, orphaned = reorder_parentsfirst(comments)
    sort_by_date(comments)

    print 'Preparing to post',len(comments),'comments...'
    root = 'http://news.sciencemag.org' #'http://newsdev.jueseph.com'
    # regular expression for extrating comment ids
    idre = re.compile(r'\'(jsid-\d+-\d+)\'', re.M)
    urlre = re.compile(r'http://news.sciencemag.org[^/]*(/[^?]*)\?*')
    for i,com in enumerate(comments):
        if com['is_anonymous']:
            author = com['anonymous_author']
            name = author['name']
        else:
            author = com['author']
            name = author['display_name']
        email = author['email']
        created_at = com['created_at']
        ip = com['ip_address']
        msg = com['message']
        url = com['thread']['url']
        # article path, i.e. /sciencenow/2010/04/basename.html
        path = urlre.search(url).groups()[0]

        # post comment
        print 'Posting comment',i+1
        url = root + path
        params = {'tid':'jst-1',
                  'js-CmtName' : name,
                  'js-CmtText' : msg,
                  'js-CmtEmail' : email,
                  'ref' : url
                 }
        parent = get_parent_id(com)
        if parent:
            params['js-CmtParentID'] = parent

        response, headers = api.FetchUrl(post_comment_url, 
                                         parameters=params, 
                                         #dry_run=True,
                                         convert_data=False,
                                         no_cache=True,
                                         auth_cookie=None)
        if response:
            print 'Response'
            print response
            # hash the id of the returned comment
            m = idre.search(response)
            if m:
                id = m.groups()[0]
            else:
                print 'No id returned'
                id = None
            ids[com['id']] = id
            print 'Posted in',url
            print 'id:',id,' (jsk),',com['id'],'(dsq)',
            if parent:
                print '\tparent:',parent,'(jsk)',
            print '\nname:',name.encode('utf-8'),'\temail:',email,'\n'
        else:
            print 'No response from server'

        #break # debug -- only post first comment


def delete_comment(ref, id):
    global admin_ck
    # for deleting comments
    params = {'ref' : ref,
              'id' : id,
              'jx' : '0'}
    return api.FetchUrl(del_comment_url,
                        parameters=params,
                        convert_data=False,
                        #dry_run=True, # for debugging
                        no_cache=True,
                        auth_cookie=admin_ck)

def delete_rss_comments():
    '''Get comments out of RSS feed and delete all of them.'''
    while 1:
        # fetch rss comments
        rss,headers = api.FetchUrl('http://js-kit.com/rss/newsdev.jueseph.com',
                           convert_data=False)
        print 'Response header:'
        print headers
        soup = BeautifulStoneSoup(rss)
        comments = soup.findAll('item')
        if comments:
            for com in comments:
                ref, id = com.guid.contents[0].split('#')
                delete_comment(ref,id)
        else:
            break

def delete_all_comments():
    '''Reads an import log and deletes all comments referenced in there by url,
    id'''
    filename = 'log.post.final.txt'
    f = open(filename,'r')
    idre = re.compile(r'jsid-\d+-\d+')
    urlre = re.compile(r'Posted in (http://newsdev.jueseph.com[^/]*/[^?\n]*)\?*')
    pairs = []
    while f:
        line = f.readline()
        if not line:
            break
        url = urlre.search(line)
        if url:
            url = url.groups()[0]
            line = f.readline()
            if line:
                id = idre.search(line)
                if id:
                    id = id.group()
                    pairs.append((url,id))
            # end of file
            else:
                break
    f.close()

    print 'Deleting',len(pairs),'comments...'
    for pair in pairs:
        url,id = pair
        delete_comment(url,id)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'deleteall':
            delete_all_comments()
        if sys.argv[1] == 'deleterss':
            delete_rss_comments()
        elif sys.argv[1] == 'postall':
            post_comments_from_file()
