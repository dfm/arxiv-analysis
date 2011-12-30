#!/usr/bin/env python
# encoding: utf-8
"""
Get the listings from the last day as an XML file

"""

__all__ = ['get_recent_listings']

import re
import datetime
import time
import urllib
import httplib2

arXiv_url    = 'http://export.arxiv.org/oai2'
arXiv_header = {'Content-type': 'application/x-www-form-urlencoded'}

timedelta = datetime.timedelta(1)

resumption = re.compile(".*<resumptionToken.*?>(.*?)</resumptionToken>.*")

def get_recent_listings(out_fn='arXiv_recent', maxdepth=40):
    date = (datetime.datetime.utcnow()-timedelta).strftime("%Y-%m-%d")
    requestBody =        {'verb': 'ListRecords',
                          'from': date,
                'metadataPrefix': 'arXiv'}

    i = 0
    for j in xrange(maxdepth):
        print "Fetching list (iteration = %d)..."%i
        http = httplib2.Http()
        response, content = http.request(arXiv_url, 'POST', headers=arXiv_header,
                                        body=urllib.urlencode(requestBody))

        f = open(out_fn+".%d.xml"%i, "w")
        f.write(content)
        f.close()

        if response['status'] not in ['200', '503']:
            raise RuntimeError(response)
        if response['status'] == '503':
            waiting = int(response['retry-after'])
            print "Received 503... re-trying in %d seconds"%waiting
            time.sleep(waiting)
        else:
            resumptionToken = resumption.search(content)
            if resumptionToken is None:
                break
            resumptionToken = resumptionToken.groups()[0]
            print "resumptionToken = ", resumptionToken
            if resumptionToken == '':
                break
            requestBody = {'verb': 'ListRecords', 'resumptionToken': resumptionToken}

            print "Pausing to not swamp arXiv..."
            time.sleep(20)
            i += 1

    return response, i

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        print get_recent_listings(sys.argv[1])
    else:
        print get_recent_listings()

