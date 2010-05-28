#! /usr/bin/env python
"""Extracts Movable Type comments from backup dump and prints a data file in a
format for submission to JS-Kit tech support to migrate into JS-Kit"""

import pprint
import sys
import re
import operator
import simplejson as json
from datetime import datetime
from BeautifulSoup import BeautifulStoneSoup, Tag, CData, ProcessingInstruction, NavigableString

pp = pprint.PrettyPrinter(indent=2)
infile = 'si 20100427 backup.xml'#'test.xml' 
outfile = 'out.txt'
dumpfile = 'comments.json'

def get_entry_url(entrytag):
    """Given a BS Tag that represents an entry, returns the url that should be
    associated with the entry."""
    root = 'http://news.sciencemag.org'
    date = entrytag['authored_on']
    year = date[:4]
    month = date[4:6]
    basename = entrytag['basename']
    basename = basename.replace('_','-')
    stem = '/scienceinsider/'+year+'/'+month+'/'+basename+'.html'
    return root+stem, stem

def process(filename):
    print 'Parsing XML in',filename
    soup = BeautifulStoneSoup(open(filename,'r'))
    print 'Finding entry tags...'
    entries = soup.findAll('entry')
    urls = {}
    print len(entries),'entries found.\nDetermining entry URLs...'
    for entry in entries:
        id = entry['id']
        urls[id] = get_entry_url(entry)
        #print id,":",urls[id]
    print 'Finding comment tags...'
    comments = soup.findAll('comment')
    print len(comments), 'comments found.'
    print 'Extracting comment data and matching to URLs...'
    threads = {}
    for com in comments:
        outcom = {}
        outcom['id'] = com['id']
        outcom['url'],outcom['uniq'] = urls[com['entry_id']]
        outcom['author'] = com.get('author', 'Anonymous')
        outcom['email'] = com.get('email',None)
        date = com['created_on']
        #print date
        date = datetime(int(date[:4]),
                        int(date[4:6]),
                        int(date[6:8]),
                        int(date[8:10]),
                        int(date[10:12]),
                        int(date[12:14]))
        outcom['created_on'] = date.strftime('%Y-%m-%d %H:%M:%S')
        outcom['ip'] = com['ip']
        outcom['text'] = com.text
        threads.setdefault(outcom['uniq'],[]).append(outcom)
    print 'Dumping extracted comments to',dumpfile
    json.dump(threads,open(dumpfile,'w'))
    print 'Done.'
    
def showdump():
    comments = json.load(open(dumpfile,'r'))
    if comments:
        pp.pprint(comments)

def format_wp(outfile):
    # extract list of threads
    threads = json.load(open(dumpfile,'r'))
    # set up xml output
    f = open(outfile,'w')
    soup = BeautifulStoneSoup()
    soup.append(ProcessingInstruction('xml version="1.0" encoding="UTF-8'))
    rss = Tag(soup, 'rss',
              [('version','2.0'),
               ('xmlns:excerpt','http://wordpress.org/export/1.0/excerpt/'),
               ('xmlns:content','http://purl.org/rss/1.0/modules/content/'),
               ('xmlns:wfw','http://wellformedweb.org/CommentAPI/'),
               ('xmlns:dc','http://purl.org/dc/elements/1.1/'),
               ('xmlns:wp','http://wordpress.org/export/1.0/')])
    soup.append(rss)
    channel = Tag(soup, 'channel')
    clink = Tag(soup, 'link')
    clink.append('http://news.sciencemag.org/scienceinsider')
    rss.append(channel)
    channel.append(clink)
    print 'Reformatting comments in',len(threads),'threads from json into xml...'
    # print threads in descending order of date
    threads = sorted(threads.iteritems(), key=operator.itemgetter(0))
    ncom = 0
    for uniq,thread in threads:
        item = Tag(soup,'item')
        channel.append(item)
        title = Tag(soup,'title')
        title.append('Comments for '+thread[0]['url'])
        link = Tag(soup,'link')
        link.append(thread[0]['url'])
        guid = Tag(soup, 'guid', [('isPermaLink','false')])
        guid.append(thread[0]['url'])
        id = Tag(soup,'wp:post_id')
        id.append(thread[0]['uniq'])
        item.append(title)
        item.append(link)
        item.append(guid)
        item.append(id)
        for comment in thread:
            ctag = Tag(soup, 'wp:comment')
            id = Tag(soup,'wp:comment_id')
            id.append(comment['id'])
            author = Tag(soup,'wp:comment_author')
            author.append(CData(comment['author']))
            email = Tag(soup,'wp:comment_author_email')
            if comment['email']:
                email.append(comment['email'])
            ip = Tag(soup,'wp:comment_author_ip')
            ip.append(comment['ip'])
            date = Tag(soup,'wp:comment_date')
            date.append(comment['created_on'])
            dategmt = Tag(soup,'wp:post_date_gmt')
            dategmt.append(comment['created_on'])
            text = Tag(soup,'wp:comment_content')
            text.append(CData(comment['text']))
            status = Tag(soup,'wp:comment_approved')
            status.append('1')
            type = Tag(soup,'wp:comment_type')
            parent = Tag(soup,'wp:comment_parent')
            parent.append('0')
            user = Tag(soup,'wp:comment_user_id')
            user.append('0')

            item.append(ctag)
            ctag.append(id)
            ctag.append(author)
            ctag.append(email)
            ctag.append(ip)
            ctag.append(date)
            ctag.append(dategmt)
            ctag.append(text)
            ctag.append(status)
            ctag.append(type)
            ctag.append(parent)
            ctag.append(user)
            ncom += 1
    print 'Outputted',ncom,'comments.'
    print_soup(f,soup)


def print_soup(os, soup):
    indent = ''
    tab = '    '
    def print_soup_r(os,node,indent):
        if isinstance(node,Tag):
            children = node.contents
            os.write(indent+'<'+node.name)
            for attr in node.attrs:
                os.write(' '+attr[0]+'="'+attr[1]+'"')
            os.write('>')
            if children:
                if len(children) > 1 or not isinstance(children[0],NavigableString):
                    os.write('\n')
                for child in children:
                    print_soup_r(os,child,indent+tab)
                if len(children) > 1 or not isinstance(children[0],NavigableString):
                    os.write(indent)
            os.write('</'+node.name+'>\n')
        elif isinstance(node,ProcessingInstruction):
            os.write(indent+str(node)+'\n')
        else:
            os.write(str(node))
    children = soup.contents
    for child in children:
        print_soup_r(os,child,indent)

if __name__ == '__main__':
    if len(sys.argv) > 0:
        if sys.argv[1] == 'process':
            process(infile)
        if sys.argv[1] == 'showdump':
            showdump()
        if sys.argv[1] == 'output':
            format_wp('out.xml')
