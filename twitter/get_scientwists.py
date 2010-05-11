import urllib2
from BeautifulSoup import BeautifulSoup
import twitter
import math
from UnicodeWriter import UnicodeWriter

# fetch list of scientwists' screennames
page = open("scientwists.htm")
soup = BeautifulSoup(page)

scientwists = soup.findAll('div', {"class" : 'scientwist'})
screennames = [sn.a.contents[0].encode('utf-8')
    for sn in scientwists]

#print screennames

# fetch rest of info from twitter, and write to spreadsheet
api = twitter.Api(username='sciencenow', password='sc1encenew5')
outfile = open('scientwists.csv', 'w')
csvout = UnicodeWriter(outfile, 'excel')

# column labels on first row
row = [
    'Screen Name',
    'Name',
    'Location',
    'Description',
    'Followers']
csvout.writerow(row)

for user in screennames:
    print user
    try:
        f = api.GetUser(user)
        """print 'screenname: ' + `f.GetScreenName()`
        print 'name: ' + `f.GetName()`
        print 'location: ' + `f.GetLocation()`
        print 'description: ' + `f.GetDescription()`
        print 'followers: ' + `f.GetFollowersCount()`"""
    except (urllib2.HTTPError, urllib2.URLError):
        continue;
    
    row = [f.GetScreenName(),
        f.GetName(),
        f.GetLocation(),
        f.GetDescription(),
        `f.GetFollowersCount()`]
    
    # Remove null entries
    for i in range(len(row)):
        if (row[i] == None):
            row[i] = 'None'
    
    csvout.writerow(row)
    
outfile.close()
