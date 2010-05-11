#!/usr/bin/env python

"""Figures out which categories on News get the most traffic."""

__author__ = 'jue@jueseph.com (Jue Wang)'

import os
import sys
import pprint
import cPickle
import GChartWrapper
import gdata.analytics.client
import urlparse
import urllib2 as urllib
from datetime import datetime
from BeautifulSoup import BeautifulSoup

# globals
pp = pprint.PrettyPrinter(indent=2)
pprint = pp.pprint

def main():
    """Main function for this application."""
    get_top_categories()


def get_category_links(cachefile='links.cpickle',refresh=False):
    # delete cachefile to trigger a fresh parse
    if refresh:
        print 'Deleting cache file',cachefile
        try:
            os.remove(cachefile)
        except os.OSError:
            pass
    # load from cache if present
    try:
        links = cPickle.load(open(cachefile,'r'))
        print 'Cache file',cachefile,'loaded.'
    # fresh parse
    except IOError:
        page = urllib.urlopen('http://news.sciencemag.org/scienceinsider')
        soup = BeautifulSoup(page)
        tag = soup.find('div',{'id':'science-categories'})
        items = tag.findAll('li')
        links = []
        for item in items:
            links.append((item.a.string, 
                          urlparse.urlsplit(item.a['href'])[2]))
        cPickle.dump(links, open(cachefile,'w'))
    return links

def get_top_categories():
    # Configuration options.
    USERNAME = 'cremeglace'
    PASSWORD = 'ipcagEv6'
    TABLE_ID = 'ga:26242135' # news.sciencemag.org
    #TABLE_ID = 'ga:4887763'   # ScienceNOW
    SOURCE_APP_NAME = 'Google-segmentDemo-v1'
    START_DATE = '2010-02-01'
    END_DATE = '2010-05-10'

    # get tuples of categories, links
    categories = get_category_links()
    #pprint(links)

    my_client = gdata.analytics.client.AnalyticsClient(source=SOURCE_APP_NAME)
    my_client.client_login(
        USERNAME,
        PASSWORD,
        SOURCE_APP_NAME,
        service='analytics')

    # The query defining the date range and metrics to retrieve from the API.
    query_uri = gdata.analytics.client.DataFeedQuery({
        'ids': TABLE_ID,
        'start-date': START_DATE,
        'end-date': END_DATE,
        'metrics': 'ga:pageviews'})
    # submit query
    data = []
    for cat in categories:
        print cat[1]
        query_uri.query['segment'] = 'dynamic::ga:pagePath=~'+cat[1]
        api_data = my_client.GetDataFeed(query_uri)

        # extract data
        for entry in api_data.entry:
            views = entry.get_object('ga:pageviews').value
            data.append((cat[0],views))
            print 'Pageviews:',views

    for d in data:
        print d[0]+'\t'+d[1]

if __name__ == '__main__':
    main()
