#!/usr/bin/env python

import time
import datetime
from get_recent_listings import get_recent_listings
from analyse import analyse_listings

def get_time():
    d = datetime.datetime.now()
    if d.hour >= 21:
        d += datetime.timedelta(days=1)
    d = d.replace(hour=21, minute=0, second=0)
    t = time.mktime(d.timetuple())
    return t

def do_analysis():
    tmp, n = get_recent_listings()
    analyse_listings(n=n+1)

# while True:
#     do_analysis()
#     dt = get_time()-time.time()
#     print "delay: ",dt
#     time.sleep(dt)

