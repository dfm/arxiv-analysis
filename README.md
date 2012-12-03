# ArXiv analysis

Run [online variational LDA](http://arxiv.org/abs/1206.7051v1) on all the
abstracts from the arXiv. The implementation is based on [Matt Hoffman's
GPL licensed code](http://www.cs.princeton.edu/~mdhoffma/).

## Usage

You'll need a [`mongod`](http://www.mongodb.org/) instance running on
the port given by the environment variable `MONGO_PORT` and a
[`redis-server`](http://redis.io/) instance running on the port given by
the `REDIS_PORT` environment variable.

The code depends on the Python packages: `numpy`, `scipy`, `requests`,
`pymongo` and `redis`.

* `mkdir abstracts`
* `./analysis.py scrape abstracts` — scrapes all the metadata from the arXiv
  [OAI interface](http://arxiv.org/help/oa/index) and saves the raw XML
  responses as `abstracts/raw-*.xml`. This takes a _long time_ because of
  the arXiv's flow control policies. It took me approximately 6 hours.
* `./analysis.py parse abstracts/raw-*.xml` — parses the raw responses and
  saves the abstracts to a MongoDB database called `arxiv` in the collection
  called `abstracts`.
* `./analysis.py build-vocab` — counts all the words in the corpus removing
  anything with less than 3 characters and removing any stop words.
* `./analysis.py get-vocab 100 5000 > vocab.txt` — lists the vocabulary
  skipping the first 100 most popular words and keeping 5000 words total.
* `./analysis.py run vocab.txt` — runs online variational LDA by randomly
  selecting articles from the database. The topic distributions are stored
  in the `lambda-*.txt` files. This will run forever so just kill it whenever
  you feel like it.
* `./analysis.py vocab.txt lambda-100.txt` — list the topics and their most
  common words at step 100.
