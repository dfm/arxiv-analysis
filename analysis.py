import re
import datetime
import time

from collections import defaultdict
from xml.etree.ElementTree import ElementTree

import nltk
import requests


# ArXiv info.
url = "http://export.arxiv.org/oai2"
arXiv_header = {"Content-type": "application/x-www-form-urlencoded"}


# Regular expression to the find the resumption token.
resume_re = re.compile(".*<resumptionToken.*?>(.*?)</resumptionToken>.*")


# NLP setup.
strip_chars = r"""+$^_-*~@.,()[]{}<>`\|/"'=1234567890%?!#:; """
stopwords = [w.strip() for w in open("stopwords.txt")]
stemmer = nltk.stem.LancasterStemmer()


def get(date, max_tries=40):
    """
    Get listings from the ArXiv.

    ## Arguments

    * `date` (str): The start date for the listings. This should have the
      format `YYYY-MM-DD`.

    ## Returns

    * `results` (list): A list of the XML data (as strings) returned.

    """
    req = {"verb": "ListRecords", "from": date, "metadataPrefix": "arXiv"}

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


def analyse(data):
    pass


if __name__ == "__main__":
    listings = get((datetime.datetime.utcnow() - datetime.timedelta(1))
                .strftime("%Y-%m-%d"))
    for i, l in enumerate(listings):
        open("example-{0:d}.dat".format(i), "w").write(l)
