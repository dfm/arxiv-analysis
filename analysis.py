import re
import datetime
import time

from collections import defaultdict
import xml.etree.cElementTree as ElementTree

import nltk
import requests

import db


# ArXiv info.
url = "http://export.arxiv.org/oai2"
arXiv_header = {"Content-type": "application/x-www-form-urlencoded"}


# Regular expression to the find the resumption token.
resume_re = re.compile(".*<resumptionToken.*?>(.*?)</resumptionToken>.*")


# NLP setup.
strip_chars = r"""+$^_-*~@.,()[]{}<>`\|/"'=1234567890%?!#:; """
stopwords = [w.strip() for w in open("stopwords.txt")]
stemmer = nltk.stem.LancasterStemmer()


# Hackish XML parsing hacks.
root_ns = lambda x: ".//{http://www.openarchives.org/OAI/2.0/}" + x
arxiv_ns = lambda x: ".//{http://arxiv.org/OAI/arXivRaw/}" + x
strip_ns = re.compile("{0}(.*)".format(arxiv_ns("")[3:]))


# The list of fields to grab from the XML.
fields = ["title", "abstract", "id", "license", "comments", "report-no",
          "journal-ref", "doi", "submitter", "authors", "categories",
          "acm-class"]


# The datetime format for the versions.
version_dt_fmt = "%a, %d %b %Y %H:%M:%S GMT"


# Category conversions.
cat_conv = {"hep-th": "hep.th", "hep-ex": "hep.ex", "hep-lat": "hep.lat",
        "hep-ph": "hep.ph", "nucl-ex": "nucl.ex", "nucl-th": "nucl.th"}


# Author list regular expressions.
au_split = re.compile(",|(?:\\band\\b)")


def build_vector(txt):
    """Build a word vector from a string of text."""
    # Tokenize the text.
    tokens = [t.strip(strip_chars).lower()
            for t in nltk.wordpunct_tokenize(txt)]

    # Ignore the stopwords.
    tokens = [stemmer.stem(t) for t in tokens if t not in stopwords]

    # Build the vector.
    vec = defaultdict(int)
    norm = 0.0
    for t in tokens:
        if len(t) > 0:
            vec[t] += 1
            norm += 1.0

    return vec


def analyse(record):
    """Analyse a record dictionary and return it."""
    # Parse the categories.
    cats = record.pop("categories", "").split()
    record["categories"] = []

    # Do the category conversions.
    for c in cats:
        record["categories"].append(cat_conv.get(c, c))

    # Parse the author list.
    record["authors"] = au_split.split(record["authors"])

    # Build the word vector from the title and abstract.
    vec = build_vector(" ".join([record["title"], record["abstract"]]))
    record["word_vector"] = vec

    # Sort the versions.
    record["versions"] = sorted(record["versions"], key=lambda r: r["date"])
    record["nversions"] = len(record["versions"])

    # Set the datestamp to the most recent version.
    record["datestamp"] = record["versions"][-1]["date"]

    # Set up the ids.
    record["_id"] = record.pop("id")

    # Update the database.
    db.records.update({"_id": record["_id"]}, record, upsert=True)

    # Update the corpus word vector.
    db.corpus.update({"_id": 0}, {"$inc": vec}, upsert=True)

    return record


def get(date, max_tries=40):
    """
    Get listings from the ArXiv.

    ## Arguments

    * `date` (str): The start date for the listings. This should have the
      format `YYYY-MM-DD`.

    ## Returns

    * `results` (list): A list of the XML data (as strings) returned.

    """
    req = {"verb": "ListRecords", "from": date, "metadataPrefix": "arXivRaw"}

    results = []

    for j in xrange(max_tries):
        print("Fetching pass {0:d}...".format(j))

        # Send the request.
        r = requests.post(url, data=req)

        # Handle the response.
        code = r.status_code

        if code == 503:
            # Asked to retry
            to = int(r.headers["retry-after"])
            print("Got 503. Retrying after {0:d} seconds.".format(to))
            time.sleep(to)
        elif code == 200:
            # Everything's OK.
            content = r.text
            print("Received {0:d} characters.".format(len(content)))
            results.append(content)

            # Look for a resumption token.
            token = resume_re.search(content)

            print("Resumption token: {0}.".format(token))

            # If there isn't one, we're all done.
            if token == "" or token is None:
                break

            # If there is a resumption token, rebuild the request.
            req = {"verb": "ListRecords", "resumptionToken": token}

            # Pause so as not to get banned.
            to = 20
            print("Sleeping for {0:d} seconds so as not to get banned."
                    .format(to))
            time.sleep(to)
        else:
            # Wha happen'?
            r.raise_for_status()

    return results


def parse(data):
    records = []

    # Parse the XML string.
    tree = ElementTree.fromstring(data)
    record_list = tree.findall(root_ns("record"))
    for record in record_list:
        doc = {}

        # Loop over the children.
        for n in record.find(root_ns("metadata")).find(arxiv_ns("arXivRaw")):
            tag = strip_ns.findall(n.tag)[0]
            if tag not in ["version"]:
                doc[tag] = n.text

        # Get the datestamp.
        el = record.find(root_ns("datestamp"))
        if el is not None:
            doc["datestamp"] = datetime.datetime.strptime(el.text, "%Y-%m-%d")

        # Parse the versions.
        versions = record.findall(arxiv_ns("version"))
        doc["versions"] = []
        for v in versions:
            el = v.find(arxiv_ns("date"))
            if el is not None:
                rev = v.get("version")
                d = datetime.datetime.strptime(el.text, version_dt_fmt)
                doc["versions"].append({"version": rev, "date": d})

        # Parse the tags.
        for f in fields:
            el = record.find(arxiv_ns(f))
            if el is not None:
                doc[f] = el.text

        records.append(doc)

    return records


def do_analysis(force=False, delta=1):
    now = datetime.datetime.now()

    # See when the next update was scheduled.
    next_update = db.corpus.find_one({"_id": 1})
    if next_update is not None:
        date = next_update["date"]

        # Make sure that we've passed the date of the next update.
        if not force and now < date:
            dt = time.mktime(date.timetuple()) - time.time()
            print("Too soon! Waiting {0:.4f} seconds.".format(dt))
            return dt
    else:
        date = now

    print("Starting an analysis run {0}.".format(now))
    print("The start date is set to {0}.".format(date))

    date -= datetime.timedelta(days=delta)

    # Get the records.
    rs = map(parse, get(date.strftime("%Y-%m-%d")))
    records = []
    for r in rs:
        records += r

    if len(records) > 0:
        print("Got {0:d} records.".format(len(records)))

        # Run the analysis.
        start = time.time()
        map(analyse, records)
        print("Analysis took {0:.3f} seconds".format(time.time() - start))
    else:
        print("No records returned")

    # Update the next update schedule.
    now += datetime.timedelta(days=1)
    now = now.replace(hour=0, minute=0, second=0)
    db.corpus.update({"_id": 1}, {"_id": 1, "date": now}, upsert=True)

    dt = time.mktime(now.timetuple()) - time.time()
    print("Next update scheduled for {0} ({1:.4f} seconds from now)."
            .format(now, dt))

    return dt


if __name__ == "__main__":
    import sys

    if "--force" in sys.argv:
        dt = do_analysis(force=True)
    elif len(sys.argv) == 2:
        dt = do_analysis(force=True, delta=int(sys.argv[1]))

    while True:
        dt = do_analysis()
        time.sleep(dt)
