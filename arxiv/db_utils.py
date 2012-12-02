__all__ = [u"db", u"rdb"]

import os
import pymongo
import redis


server = os.environ.get(u"MONGO_SERVER", u"localhost")
port = int(os.environ.get(u"MONGO_PORT", 27017))
redis_server = os.environ.get(u"REDIS_SERVER", u"localhost")
redis_port = int(os.environ.get(u"REDIS_PORT", 27019))

db = pymongo.Connection(server, port).arxiv
rdb = redis.Redis(host=redis_server, port=redis_port)
