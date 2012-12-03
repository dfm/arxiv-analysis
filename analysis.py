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

    if cmd in [u"run", u"results"]:
        fn = os.path.join(os.path.dirname(os.path.abspath(arxiv.__file__)),
                          u"vocab.txt")
        vocab = [l.strip() for l in open(fn)]

    if sys.argv[1] == u"run":
        coll = db.abstracts
        coll.ensure_index(u"random")

        batch_size = 128
        ndocs = coll.count()
        ntopics = 100

        lda = arxiv.LDA(vocab, ntopics, ndocs, 1.0 / ntopics, 1.0 / ntopics,
                        1024.0, 0.7)

        iteration = 0
        while 1:
            docs = []
            ind = np.random.randint(ndocs - batch_size)
            docs = [d[u"title"] + u" " + d[u"abstract"] for d in
                            coll.find({}, {u"abstract": 1, u"title": 1})
                                .sort(u"random").skip(ind).limit(batch_size)]
            gamma, lam, bound = lda.update(docs)
            print(iteration, np.exp(-bound))

            if iteration % 10 == 0:
                np.savetxt(u"lambda-{0}.txt".format(iteration), lam)

            iteration += 1

    if cmd == u"results":
        fn = sys.argv[2]
        lam = np.loadtxt(fn)

        for i, l in enumerate(lam):
            l /= np.sum(l)
            tmp = sorted(zip(l, range(len(l))), key=lambda x: x[0],
                                                reverse=True)
            print(u"Topic {0}:".format(i))
            for i in range(50):
                t = tmp[i]
                print(u"{0:20s} --- {1:.4f}".format(vocab[t[1]], t[0]))
            print()
