import os
import re
from datetime import datetime
import xml.etree.cElementTree as ET

import pymongo


record_tag = u".//{http://www.openarchives.org/OAI/2.0/}record"
ns_re = re.compile(r"\{(?:.*?)\}(.*)")
date_fmt = u"%a, %d %b %Y %H:%M:%S %Z"


server = os.environ.get(u"MONGO_SERVER", "localhost")
port = int(os.environ.get(u"MONGO_PORT", 27017))


def parse(fns):
    db = pymongo.Connection(server, port).arxiv
    for f in fns:
        tree = ET.parse(f)
        root = tree.getroot()
        for r in root.findall(record_tag):
            doc = {}
            for el in r.iter():
                txt = el.text
                if txt is None:
                    for k, v in el.attrib.iteritems():
                        doc[unicode(k.lower())] = unicode(v)
                elif txt.strip() != u"":
                    k = unicode(ns_re.search(el.tag).groups()[0].lower())
                    txt = unicode(txt.strip())
                    if k == u"date":
                        txt = datetime.strptime(txt, date_fmt)
                    elif k == u"categories":
                        txt = [c.strip() for c in txt.split(u",")]
                    doc[k] = txt
            print doc


if __name__ == "__main__":
    import sys
    import glob

    fns = glob.glob(sys.argv[1])
    parse(fns)
