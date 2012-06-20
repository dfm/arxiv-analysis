__all__ = ["records", "corpus"]

import os
import pymongo
from pymongo.errors import OperationFailure

# The characters used to generate the unique ids for the papers
char_inds = range(ord('0'), ord('9')+1) + range(ord('A'), ord('Z')+1) \
        + range(ord('a'), ord('z')+1)
chars = [chr(c) for c in char_inds]
nchars = len(chars)

# Info for the MongoDB server.
server = os.environ.get("ARXIV_IO_MONGO_SERVER", "localhost")
port = int(os.environ.get("ARXIV_IO_MONGO_PORT", 27017))
database = os.environ.get("ARXIV_IO_MONGO_DB", "arxivio")
user = os.environ.get("ARXIV_IO_MONGO_USER", None)
pw = os.environ.get("ARXIV_IO_MONGO_PASS", None)


# Connect to the database.
db = pymongo.Connection(server, port)[database]
if user is not None:
    db.authenticate(user, pw)


# Records collection.
records = db["records"]
records.ensure_index("authors")
records.ensure_index("categories")
records.ensure_index("datestamp")
records.ensure_index("nversions")

# Corpus.
# _id: 0 - The corpus word vector.
# _id: 1 - Next update.
# _id: 2 - Counter.
corpus = db["corpus"]
counter_id = 2


def doc_counter():
    _id = corpus.find_one({"_id": counter_id})
    if _id is None:
        _id = ["0"]
    else:
        _id = list(_id["counter"])[::-1]
    for i, c in enumerate(_id):
        indx = chars.index(c)
        indx += 1
        if indx < nchars:
            _id[i] = chars[indx]
            break
        else:
            _id[i] = "0"
            if i == len(_id) - 1:
                _id.append("0")
    _id = "".join(_id[::-1])
    try:
        corpus.update({"_id": counter_id},
                {"_id": counter_id, "counter": _id},
                upsert=True, safe=True)
    except OperationFailure:
        print("Counter failure!")
        return doc_counter()
    return _id
