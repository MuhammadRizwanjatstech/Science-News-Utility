#! /usr/bin/env python
import twitter
import pickle
from datetime import datetime
import sys
import pprint

filename = 'results.pickle'
            
def print_basic_info(pickle_filename):
    mentions = pickle.load(open(pickle_filename, 'r'))
    ct = 1
    for m in mentions:
        print ct
        ct += 1
        print m.user.screen_name
        print m.created_at
        print m.text.encode('utf-8')

def print_search_data(pickle_filename):
    allresults = pickle.load(open(pickle_filename, 'r'))

    datehist = {}
    for query in allresults:
        print 'Query:',query
        results = allresults[query]
        datehist[query] = {}
        for m in results:
            #created = datetime.strptime(m.created_at, "%a %b %d %H:%M:%S +0000 %Y")
            created = datetime.strptime(m['created_at'], "%a, %d %b %Y %H:%M:%S +0000")
            datehist[query].setdefault(created.strftime('%Y-%m-%d'), []).append(m)

        for key in sorted(datehist[query].iterkeys()):
            print key+',', len(datehist[query][key])
    """
    pp = pprint.PrettyPrinter(indent=4)
    for m in mentions:
        pp.pprint(m)
    """

def print_get_data(pickle_filename):
    results = pickle.load(open(pickle_filename, 'r'))

    datehist = {}
    for m in results:
        created = datetime.strptime(m.created_at, "%a %b %d %H:%M:%S +0000 %Y")
        datehist.setdefault(created.strftime('%Y-%m-%d'), []).append(m)

    for key in sorted(datehist.iterkeys()):
        print key+',', len(datehist[key])
    """
    pp = pprint.PrettyPrinter(indent=4)
    for m in mentions:
        pp.pprint(m)
    """


def main():
    print_get_data(filename)
        
if __name__ == '__main__':
    status = main()
    sys.exit(status)

