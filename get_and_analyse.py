#!/usr/bin/env python

from get_recent_listings import get_recent_listings
from analyse import analyse_listings

tmp, n = get_recent_listings()
analyse_listings(n=n+1)

