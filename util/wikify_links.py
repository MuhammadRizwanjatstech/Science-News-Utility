from BeautifulSoup import BeautifulSoup
import codecs

f=open('data.txt', 'r')
soup = BeautifulSoup(f)

links = soup.findAll(['a', 'p', 'h1', 'h2'])

for x in links:
    #if x.name == 'h2':
     #   print '====='+x.contents[0]+'======'
    if x.name == 'a':
        print '  * [[' + x['href'] + '|'+x.contents[0].encode('utf-8')+']]'
    else:
        print x.contents[0].encode('utf-8')
    #print '[['.x['href'].'|'.(x.contents)
