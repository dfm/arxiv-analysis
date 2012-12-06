#!/usr/bin/env python

from __future__ import print_function

import os
import sys
import numpy as np

try:
    import arxiv
    arxiv = arxiv
except ImportError:
    sys.path.append(os.path.join(os.path.abspath(__file__), u".."))
    import arxiv
    arxiv = arxiv

from arxiv.db_utils import db


if __name__ == "__main__":
    cmd = sys.argv[1]

    if cmd == u"scrape":
        print(u"Scraping all the meta-data from the arxiv...")
        arxiv.get()

    if cmd == u"parse":
        print(u"Parsing the XML...")
        arxiv.parse()

    if cmd == u"build-vocab":
        print(u"Building the vocabulary list...")
        arxiv.build_vocab()

    if cmd == u"get-vocab":
        initial, N = 1000, 5000
        if len(sys.argv) >= 3:
            initial = int(sys.argv[2])
        elif len(sys.argv) >= 4:
            N = int(sys.argv[3])

        arxiv.get_vocab(initial=initial, N=N)

    if cmd in [u"run", u"results"]:
        fn = sys.argv[2]
        vocab = [l.strip() for l in open(fn)]

    if cmd == u"run":
        print(u"Running online LDA...")
        coll = db.abstracts
        coll.ensure_index(u"random")

        batch_size = 128
        ndocs = coll.count()
        ntopics = 100

        lda = arxiv.LDA(vocab, ntopics, ndocs, 1.0 / ntopics, 1.0 / ntopics,
                        1025.0, 0.8)

        iteration = 0
        while 1:
            docs = []
            ind = np.random.randint(ndocs - batch_size)
            cursor = coll.find({}, {u"abstract": 1, u"title": 1}) \
                         .sort(u"random").skip(ind)
            for i, d in enumerate(cursor):
                if i >= batch_size:
                    break
                if u"title" in d:
                    docs.append(d[u"title"] + u" " + d[u"abstract"])
            gamma, lam, bound = lda.update(docs)
            print(iteration, ind, np.exp(-bound))

            if iteration % 10 == 0:
                np.savetxt(u"lambda-{0}.txt".format(iteration), lam)

            iteration += 1

    if cmd == u"results":
        print(u"Displaying results...")
        fn = sys.argv[3]
        lam = np.loadtxt(fn)

        for i, l in enumerate(lam.T):
            l /= np.sum(l)
            tmp = sorted(zip(l, range(len(l))), key=lambda x: x[0],
                                                reverse=True)
            print(u"Topic {0}: ".format(i) +
                  u", ".join([u"{0} ({1:.1f})".format(vocab[t[1]], 100 * t[0])
                              for t in tmp[:10]]))
