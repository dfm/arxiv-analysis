from __future__ import print_function

__all__ = [u"parse"]

import os
import re
import random
from datetime import datetime
import xml.etree.cElementTree as ET
from multiprocessing import Pool

from .db_utils import db


record_tag = u".//{http://www.openarchives.org/OAI/2.0/}record"
ns_re = re.compile(r"\{(?:.*?)\}(.*)")
date_fmt = u"%a, %d %b %Y %H:%M:%S %Z"

comma_and = r"(?:,* and )|(?:,\s*)"
ca_re = re.compile(comma_and)
au_re = re.compile(r"(.+?)(?:" + comma_and + "|(?:\s*$))")

affil_re = re.compile(r"(.*?)(?:\((.*)\)|$)")
affils_re = re.compile(r"\(([0-9]+)\) (.*?)(?=(?:,*\s*\()|\))")


server = os.environ.get(u"MONGO_SERVER", "localhost")
port = int(os.environ.get(u"MONGO_PORT", 27017))


def parse_one(f):
    print(u"Starting: {0}".format(f))
    coll = db.abstracts

    tree = ET.parse(f)
    root = tree.getroot()
    for i, r in enumerate(root.findall(record_tag)):
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
                    txt = [c.strip() for c in txt.split()]
                elif k == u"authors":
                    spl = txt.replace(u"\n", u"").split(u"((")
                    if len(spl) > 1:
                        if len(spl) > 2:
                            spl = [spl[0], u"(".join(spl[1:])]
                        authors, affils = spl
                        affils = dict(affils_re.findall(u"(" + affils))
                    else:
                        authors, affils = txt, {}
                    authors = [affil_re.findall(a.strip())[0]
                                            for a in au_re.findall(authors)]
                    doc[u"authors"] = []
                    for a in authors:
                        if len(a[1]) > 0 and a[1][0] in u"1234567890":
                            doc[u"authors"].append({u"name": a[0],
                                    u"affil": ", ".join([affils.get(af.strip(),
                                                                    af.strip())
                                        for af in ca_re.split(a[1])])})
                        else:
                            doc[u"authors"].append({u"name": a[0],
                                u"affil": a[1].strip()})

                    k = u"authors_raw"

                doc[k] = txt

        # Add a random number for selecting random documents later.
        doc[u"random"] = random.random()
        coll.insert(doc)

    print(u"Finished {0}".format(f))


def parse(fns):
    p = Pool()
    p.map(parse_one, list(fns))


if __name__ == "__main__":
    import sys
    parse(sys.argv[1:])
