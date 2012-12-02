from __future__ import print_function

__all__ = [u"build_vocab", u"get_vocab"]

import os
import sys
from multiprocessing import Pool

from .db_utils import db, rdb

punct = u".,?![]{}();:\"'=$<>\\/|%^&#"

# Load in the list of stop words.
stopfn = os.path.join(os.path.dirname(os.path.abspath(__file__)), u"stops.txt")
stops = [line.strip() for line in open(stopfn)]


def process_one(doc):
    if doc.get(u"title", None) is None:
        return

    if doc.get(u"random", 0.0) > 0.99:
        sys.stdout.write(u".")
        sys.stdout.flush()

    txt = doc[u"title"] + doc[u"abstract"]
    tokens = [t.lower().strip(punct) for t in txt.split()]
    tokens = [t for t in tokens if t not in stops and len(t) > 2]

    pipe = rdb.pipeline()
    for t in tokens:
        pipe.zincrby(u"vocab", t, 1)
    pipe.execute()


def build_vocab():
    rdb.flushall()
    coll = db.abstracts

    print(u"Fetching a list of documents from mongo...")
    docs = list(coll.find({}, {u"title": 1, u"abstract": 1, u"random": 1}))

    print(u"Processing. This will take a while. Watch the grass grow...")
    pool = Pool()
    pool.map(process_one, docs)


def get_vocab(initial=100, N=5000):
    for w in rdb.zrevrange(u"vocab", initial, initial + N):
        print(w)
