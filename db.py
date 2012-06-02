__all__ = ["records", "corpus"]

import os
import pymongo

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
corpus = db["corpus"]
