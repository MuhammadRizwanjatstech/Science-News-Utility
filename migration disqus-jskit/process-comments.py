#! /usr/bin/env python
import pprint
import sys
import simplejson as json
from datetime import datetime

pp = pprint.PrettyPrinter(indent=4)

f = open('comments.json','r')
allposts = json.load(f)
"""
if post['is_anonymous']:
    pp.pprint(post['anonymous_author'])
else:
    pp.pprint(post['author'])
"""
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

def display_parents(posts):
    for post in posts:
        id = post['id']
        pid = post['parent_post']
        print 'id:',id,'\tpid:',pid,'\tts:',post['created_at']

def my_key(comment):
    return datetime.strptime(comment['created_at'], "%Y-%m-%dT%H:%M")

def sort_by_date(posts):
    posts.sort(key=my_key)

def main():
    sort_by_date(allposts)
    reordered = allposts
    #reordered,orphaned = reorder_parentsfirst(allposts)
    #pickle.dump(reordered,open('reordered.pickle','w'))
    #pickle.dump(reordered,open('orphaned.pickle','w'))
    display_parents(reordered)

# Running this module
if __name__ == '__main__':
    status = main()
    sys.exit(status)

