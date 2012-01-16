# encoding: utf-8
"""
Database connections

"""

import numpy as np

import pymongo
import config

# The characters used to generate the unique ids for the papers
char_inds = range(ord('0'), ord('9')+1) + range(ord('A'), ord('Z')+1) \
        + range(ord('a'), ord('z')+1)
chars = [chr(c) for c in char_inds]
nchars = len(chars)

# MongoDB backend server
db = pymongo.Connection(config.SERVER, config.PORT)[config.DATABASE]
if config.USERNAME != 'None':
    db.authenticate(config.USERNAME,config.PASSWORD)

# listings
listings = db["listings"]
listings.ensure_index("created")
listings.ensure_index("updated")
listings.ensure_index("id")
listings.ensure_index("title")
listings.ensure_index("categories")

# corpus
corpus = db["corpus"]
norms = corpus.find_one({"_id": 0})
# Warning: not at all "thread" safe!
def doc_counter():
    _id = corpus.find_one({"_id": 1})
    if _id is None:
        _id = ['0']
    else:
        _id = list(_id["counter"])[::-1]
    for i, c in enumerate(_id):
        indx = chars.index(c)
        indx += 1
        if indx < nchars:
            _id[i] = chars[indx]
            break
        else:
            _id[i] = '0'
            if i == len(_id)-1:
                _id.append('0')
    _id = ''.join(_id[::-1])
    corpus.update({"_id": 1}, {"_id": 1, "counter": _id}, upsert=True, safe=True)
    return _id

# users
users = db["users"]
users.ensure_index("email", unique=True)

def doc_dot(doc1, doc2):
    v1, v2 = doc1["vector"], doc2["vector"]
    l1, l2 = doc1["vec_len"], doc2["vec_len"]
    if l1 > l2:
        v1,v2 = v2,v1

    res = 0.0
    for k in v1:
        if k in v2:
            res += v1[k]*v2[k]

    return res/l1/l2

def all_dots(doc, q={}, f={}):
    f["vector"]  = 1
    f["vec_len"] = 1
    doc = doc
    docs  = [d for d in db.listings.find(q, f)]
    dists = [doc_dot(doc2,doc) for doc2 in docs]
    return docs, dists

def normalize(doc):
    vec = doc["vector"]
    vec_len = 0.0

    for k in vec:
        vec[k] /= float(norms[k])
        vec_len += vec[k]**2

    doc["vector"], doc["vec_len"] = vec, np.sqrt(vec_len)
    return doc

