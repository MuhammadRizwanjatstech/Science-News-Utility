import twitter
import urllib2
import math
from sets import Set

username = 'sciencenow'
password = 'sc1encenew5'
api = twitter.Api(username=username, password=password)

me = api.GetUser('sciencenow')

# list of friends
print 'fetching list of friends...'
numpages = int(math.ceil(me.GetFriendsCount()/100.0))
friendpage = (api.GetFriends(page=x)
  for x in range(1,numpages+1))
friends = (y[z]
  for y in friendpage \
  for z in range(len(y)))

# list of followers
print 'fetching list of followers...'
numpages = int(math.ceil(me.GetFollowersCount()/100.0))
followerpage = (api.GetFollowers(page=x)
  for x in range(1,numpages+1))
followers = (y[z]
  for y in followerpage \
  for z in range(len(y)))

# compare followers to friends
print 'extracting friend usernames...'
friendNames = Set()
for friend in friends:
    friendNames.add(friend.screen_name)

print 'following all followers we are not already following:'
for follower in followers:
    if (not follower.screen_name in friendNames):
        print "attempting to follow " + follower.screen_name.encode('utf-8')
        try:
            api.CreateFriendship(follower.screen_name)
        except urllib2.HTTPError, e:
            print e
        except urllib2.URLError, e:
            print e
    else:
        print 'already following ' + follower.screen_name.encode('utf-8')
            
