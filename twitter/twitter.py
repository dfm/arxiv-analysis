#!/usr/bin/env python


from __future__ import print_function

import os
import time
import json
import requests
from requests.auth import OAuth1


url = u"https://stream.twitter.com/1/statuses/filter.json"

e = os.environ
client_key = e[u"TW_CLIENT_KEY"]
client_secret = e[u"TW_CLIENT_SECRET"]
user_key = e[u"TW_USER_KEY"]
user_secret = e[u"TW_USER_SECRET"]


def monitor(kw):
    wait = 0
    auth = OAuth1(client_key, client_secret, user_key, user_secret)
    while 1:
        try:
            try:
                r = requests.post(url, data={"track": kw}, auth=auth,
                                prefetch=False, timeout=90)
            except requests.exceptions.ConnectionError:
                print("request failed.")
                wait = min(wait + 0.25, 16)
            else:
                code = r.status_code
                print("{0} returned: {1}".format(url, code))
                if code == 200:
                    wait = 0
                    try:
                        for line in r.iter_lines():
                            if line:
                                tweet = json.loads(line)
                                fn = "tweets/{0}.json".format(tweet["id_str"])
                                with open(fn, "w") as f:
                                    f.write(line)
                    except requests.exceptions.Timeout:
                        print("request timed out.")
                    except Exception as e:
                        print("failed with {0}".format(e))
                elif code == 420:
                    if wait == 0:
                        wait = 60
                    else:
                        wait *= 2
                elif code in [401, 403, 404, 500]:
                    if wait == 0:
                        wait = 5
                    else:
                        wait = min(wait * 2, 320)
                else:
                    r.raise_for_status()
        except KeyboardInterrupt:
            print("Exiting.")
            break

        time.sleep(wait)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        kw = u",".join(sys.argv[1:])
    else:
        kw = u"arxiv"
    monitor(kw)
