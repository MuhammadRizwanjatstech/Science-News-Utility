import twitter
import math
import codecs, csv, cStringIO

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
            
api = twitter.Api(username='sciencenow', password='sc1encenew5')

me = api.GetUser('sciencenow')
numpages = int(math.ceil(me.GetFollowersCount()/100.0))
followerpage = (api.GetFollowers(page=x)
  for x in range(1,numpages+1))
myfollower = (y[z]
  for y in followerpage \
  for z in range(len(y)))
outfile = open('followers.csv', 'w')
csvout = UnicodeWriter(outfile, 'excel')

# column labels on first row
row = [
    'Screen Name',
    'Name',
    'Location',
    'Description',
    'Followers']
csvout.writerow(row)


for f in myfollower:
    """print 'screenname: ' + `f.GetScreenName()`
    print 'name: ' + `f.GetName()`
    print 'location: ' + `f.GetLocation()`
    print 'description: ' + `f.GetDescription()`
    print 'followers: ' + `f.GetFollowersCount()`"""
    
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
