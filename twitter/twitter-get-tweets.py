#! /usr/bin/env python
import twitter
import pickle
import urllib2
            
api = twitter.Api(username='sciencenow', password='sc1encenew5')
me = api.GetUser('sciencenow')

rpp = 50    # max = 100
filename = 'results.pickle'

allresults = [] 

currpage = 1
while 1:
    try:
        print 'Fetching results for',str((currpage-1)*rpp+1),'to',str(currpage*rpp)+':',
        results = api.GetUserTimeline(count=rpp, page=currpage)
        print str(len(results))+' results.'
        if len(results) > 0:
            allresults.extend(results)
            currpage += 1
        else:
            break
    except urllib2.HTTPError, e:
        print e
        break
print len(allresults), 'tweets retrieved.'

print 'Saving data as', filename

pickle.dump(allresults, open(filename,'w'))
