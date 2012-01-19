#!/usr/bin/env python
# encoding: utf-8
"""
Analyse the xml file of recent listings

"""

from collections import defaultdict

import datetime
import time
from xml.etree.ElementTree import ElementTree

import numpy as np

import nltk

import db

root_ns  = lambda x: './/{http://www.openarchives.org/OAI/2.0/}'+x
arxiv_ns = lambda x: './/{http://arxiv.org/OAI/arXiv/}'+x
fields = ['title', 'abstract', 'id', 'license', 'comments', 'report-no',
        'journal-ref', 'doi']
dates  = {'created': arxiv_ns('created'), 'updated': arxiv_ns('updated'),
        'datestamp': root_ns('datestamp')}
strip_chars = r"""+$^_-*~@.,()[]{}<>`\|/"'=1234567890%?!#:; """
stopwords = [w.strip() for w in open("stopwords.txt")] # nltk.corpus.stopwords.words('english')
stemmer = nltk.stem.LancasterStemmer()

def analyse_listings(fn='arXiv_recent', n=1):
    tree = ElementTree()
    for i in xrange(n):
        print "Analysing page:", i
        tree.parse(fn+".%d.xml"%i)
        records = tree.findall(root_ns('record'))
        for record in records:
            doc = {}
            for d in dates:
                el = record.find(dates[d])
                if el is not None:
                    doc[d] = datetime.datetime.strptime(el.text, '%Y-%m-%d')
            for f in fields:
                el = record.find(arxiv_ns(f))
                if el is not None:
                    doc[f] = el.text
            doc["categories"] = record.find(arxiv_ns("categories")).text.split()
            authors = record.find(arxiv_ns("authors"))
            doc["authors"] = []
            for a in authors.findall(arxiv_ns("author")):
                keyname   = a.find(arxiv_ns("keyname")).text
                tmpdoc = {"keyname": keyname}
                forenames = a.find(arxiv_ns("forenames"))
                if forenames is not None:
                    tmpdoc["forenames"] = forenames.text
                affil = a.find(arxiv_ns("affiliation"))
                if affil is not None:
                    tmpdoc["affiliation"] = affil.text
                doc["authors"].append(tmpdoc)
            doc = extract_features(doc)
            db.corpus.update({"_id": 0}, {"$inc": doc["vector"]}, upsert=True, safe=True)
            # push doc to MongoDB
            doc["_id"] = db.doc_counter()
            db.listings.update({"_id": doc["_id"]}, doc, upsert=True)

def extract_features(doc):
    if "abstract" not in doc or "title" not in doc:
        raise RuntimeError("'abstract' and 'title' need to be keywords in 'doc'")

    vector = defaultdict(int)
    tokens = nltk.wordpunct_tokenize(doc["abstract"] + " " + doc["title"])
    for w in tokens:#nltk.pos_tag(tokens):
        w = w.strip(strip_chars).lower()
        if w not in stopwords and "$" not in w:
            stem = stemmer.stem(w)
            if len(stem) > 1:
                vector[stem] += 1
    doc["vector"]  = vector

    count = 0
    for k in vector:
        count += vector[k]*vector[k]
    doc["vec_len"] = np.sqrt(count)
    return doc

if __name__ == '__main__':
    analyse_listings(n=1)

