#!/usr/bin/env python

import sched
import time
import datetime
from get_recent_listings import get_recent_listings
from analyse import analyse_listings

s = sched.scheduler(time.time, time.sleep)

def do_analysis():
    strt = time.time()
    tmp, n = get_recent_listings()
    analyse_listings(n=n+1)

    d = datetime.datetime.now()
    if d.hour == 21:
        d += datetime.timedelta(days=1)
    d = d.replace(hour=21, minute=0, second=0)
    t = time.mktime(d.timetuple())

    s.enterabs(t, 1, do_analysis, ())
    print "Queue:"
    print "------"
    print s.queue
    s.run()

do_analysis()

