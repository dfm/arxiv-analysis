import os
from collections import defaultdict


punct = u".,?![]{}();:\"'=$<>\\/|%^&#`"

# Load in the list of stop words.
stopfn = os.path.join(os.path.dirname(os.path.abspath(__file__)), u"stops.txt")
stops = [line.strip() for line in open(stopfn)]


def tokenize_document(txt, vocab=None):
    tokens = [t.lower().strip(punct) for t in txt.split()]
    if vocab is None:
        return [t for t in tokens if t not in stops and len(t) > 2]

    d = defaultdict(int)
    for t in tokens:
        if t in vocab:
            d[unicode(vocab.index(t))] += 1
    return d
