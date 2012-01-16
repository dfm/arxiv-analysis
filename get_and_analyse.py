#!/usr/bin/env python

import sched
import time
from get_recent_listings import get_recent_listings
from analyse import analyse_listings

s = sched.scheduler(time.time, time.sleep)

def do_analysis():
    strt = time.time()
    tmp, n = get_recent_listings()
    analyse_listings(n=n+1)
    s.enter(24*60*60-(time.time()-strt), 1, do_analysis, ())
    s.run()

do_analysis()

