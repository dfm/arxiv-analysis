import os
import nltk
import nltk.corpus
import pymongo

server = os.environ.get(u"MONGO_SERVER", u"localhost")
port = int(os.environ.get(u"MONGO_PORT", 27017))

stemmer = nltk.PorterStemmer()
stops = nltk.corpus.stopwords.words(u"english") + u".,?![]{}();:\"'"


def process():
    db = pymongo.Connection(server, port).arxiv
    coll = db.abstracts
    doc = coll.find_one()
    txt = doc["title"] + doc[u"abstract"]
    tokens = [(stemmer.stem(t), t) for t in nltk.word_tokenize(txt)
                                   if t not in stops]
    print tokens


if __name__ == "__main__":
    process()
