#! /usr/bin/env python

"""module docstring"""

# imports
import os
import sys
import re
from BeautifulSoup import BeautifulStoneSoup, Tag

# constants
DATAPATH = 'data/327/March/19 March--5972/final_xml/'

# classes
class HighWireXMLReformatter:
    def __init__(self):
        pass

    def set_input(self, path, filter=None):
        self._filenames = list()
        # default filter accepts all filenames
        if not filter:
            filter = re.compile('.*')
        # assume (for now) that this is a directory containing xml files
        filenames = os.listdir(path)
        # don't process unwanted files
        for i,fn in enumerate(filenames):
            if filter.match(fn):
                self._filenames.append(path+fn)

    def parse(self, replfilter=None, replstr=None):
        if not self._filenames:
            print 'Please set the input file first'
            return
        # build list of article tag items
        self._articles = []
        for fn in self._filenames:
            if replfilter:
                file = open(fn,'r')
                filtered = replfilter.sub(replstr,file.read())
                soup = BeautifulStoneSoup(filtered)
            else:
                soup = BeautifulStoneSoup(open(fn,'r'))
            articles = soup.findAll('article');
            if articles:
                self._articles.extend(articles)

    def output(self, filename, os=sys.stdout):
        if self._articles == None:
            print 'Please parse file(s) first'
            return
        elif not self._articles:
            print 'No articles detected in parse file.'
            return
        osoup = BeautifulStoneSoup()
        channel = Tag(osoup, 'channel', [('id', '1')])
        osoup.append(channel)
        # journal meta (extract from first article)
        article = self._articles[0]
        jtitle = Tag(osoup, 'title')
        jtitle.append('Science Magazine')
        jhomepage = Tag(osoup, 'homepage')
        jhomepage.append('http://www.sciencemag.org/content/current')
        pubdate = article.find('pub-date')
        jpubdate = Tag(osoup, 'pubDate')
        jpubdate.append('%(year)s-%(month)s-%(day)s' % 
                        {'year' : pubdate.year.contents[0],
                         'month' : pubdate.month.contents[0],
                         'day' : pubdate.day.contents[0]})
        jvolume = article.find('volume')
        jissue = article.find('issue')
        jcoverimg = Tag(osoup, 'image', [('type', 'cover'),
                                         ('url','http://coverurl')])
        channel.append(jtitle)
        channel.append(jhomepage)
        channel.append(jpubdate)
        channel.append(jvolume)
        channel.append(jissue)
        channel.append(jcoverimg)

        # article meta
        sectiondict = {}
        for article in self._articles:
            # item, fpage
            fpagetag = article.find('fpage')
            fpage = fpagetag.contents[0]
            try:
                subpage = fpagetag['seq']
            except KeyError, msg:
                subpage = ''
            item = Tag(osoup, 'item', [('fpage',fpage),
                                        ('subpage',subpage)])
            # title
            atitle = article.find('article-title')
            atitle.name = 'title'
            # pubdate
            pubdate = article.find('pub-date')
            apubdate = Tag(osoup, 'pubDate')
            apubdate.append('%(year)s-%(month)s-%(day)s' % 
                            {'year' : pubdate.year.contents[0],
                             'month' : pubdate.month.contents[0],
                             'day' : pubdate.day.contents[0]})
            # overline
            overline = article.find('subj-group', 
                                   {'subj-group-type' : 'heading' }
                                  ).subject.contents[0]
            aoverline = Tag(osoup, 'overline')
            aoverline.append(overline)
            # authors
            contribs = article.findAll('contrib')
            acontribs = Tag(osoup, 'authors')
            for c in contribs:
                ctype = c['contrib-type']
                fname = c.find('given-names').contents[0]
                lname = c.find('surname').contents[0]
                acontrib = Tag(osoup, ctype)
                afname = Tag(osoup, 'fname')
                afname.append(fname)
                alname = Tag(osoup, 'lname')
                alname.append(lname)
                acontrib.append(alname)
                acontrib.append(afname)
                acontribs.append(acontrib)
            # summary
            teaser = article.find('abstract', {'abstract-type':'teaser'})
            if not teaser:
                teaser = ''
            asummary = Tag(osoup, 'summary')
            asummary.append(teaser)
            # text
            abody = article.find('body')
            try:
                abody.name = 'text'
            except AttributeError:
                abody = Tag(osoup, 'text')
            # images
            aimages = Tag(osoup, 'images')
            aimage = Tag(osoup, 'image')
            aimage.append('test image')
            aimages.append(aimage)
            # links
            alinks = Tag(osoup, 'links')
            alinkabs = Tag(osoup, 'link', [('type','abstract')])
            alinkabs.append('abstract url')
            alinkfull = Tag(osoup, 'link', [('type','full')])
            alinkfull.append('full url')
            alinks.append(alinkabs)
            alinks.append(alinkfull)
            # categories
            acats = Tag(osoup, 'categories')
            cats = article.findAll('subj-group', {'subj-group-type' : 'field'})
            for cat in cats:
                acat = Tag(osoup, 'category')
                acat.append(cat.subject.contents[0])
                acats.append(acat)
            # section
            sectionname = article.find('subj-group', 
                                   {'subj-group-type' : 'article-type' }
                                  ).subject.contents[0]
            if sectionname in sectiondict:
                section = sectiondict[sectionname]
            else:
                section = Tag(osoup, 'section', [('id','#'), 
                                                 ('title', sectionname)])
                sectiondict[sectionname] = section
                channel.append(section)
            # build item
            item.append(atitle)
            item.append(apubdate)
            item.append(aoverline)
            item.append(acontribs)
            item.append(asummary)
            item.append(abody)
            item.append(aimages)
            item.append(alinks)
            item.append(acats)
            section.append(item)
        print >>os, osoup.prettify()

    def pprint(self, os, osoup):
        tab = '    '
        def pprint_r(os, root, indent):
            try:
                children = root.contents
                for child in children:
                    pprint_r(os, child, indent+tab)
            except AttributeError:
                print >>os, indent, root
        pprint_r(os, osoup, '')

def main():
    pass

if __name__ == '__main__':
    status = main()
    sys.exit(status)
