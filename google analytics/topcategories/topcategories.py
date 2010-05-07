#!/usr/bin/env python

"""Figures out which categories on News get the most traffic."""

__author__ = 'jue@jueseph.com (Jue Wang)'

import sys
import pprint
import GChartWrapper
import gdata.analytics.client
from datetime import datetime

# globals
pp = pprint.PrettyPrinter(indent=2)

def main():
    """Main function for this application."""
    get_top_categories()


def get_top_categories():
    # Configuration options.
    USERNAME = 'cremeglace'
    PASSWORD = 'ipcagEv6'
    #TABLE_ID = 'ga:26242135' # news.sciencemag.org
    TABLE_ID = 'ga:4887763'   # ScienceNOW
    SOURCE_APP_NAME = 'Google-segmentDemo-v1'

    my_client = gdata.analytics.client.AnalyticsClient(source=SOURCE_APP_NAME)
    my_client.client_login(
        USERNAME,
        PASSWORD,
        SOURCE_APP_NAME,
        service='analytics')

    # The query defining the date range and metrics to retrieve from the API.
    query_uri = gdata.analytics.client.DataFeedQuery({
        'ids': TABLE_ID,
        'start-date': '2009-11-01',
        'end-date': '2009-12-01',
        'metrics': 'ga:pageviews'})
    api_data = my_client.GetDataFeed(query_uri)
    for entry in api_data.entry:
        print entry.get_object('ga:pageviews').value

if __name__ == '__main__':
    main()
