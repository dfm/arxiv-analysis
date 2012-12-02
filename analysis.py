#!/usr/bin/env python


import os
import sys

try:
    import arxiv
    arxiv = arxiv
except ImportError:
    sys.path.append(os.path.join(os.path.abspath(__file__), u".."))
    import arxiv
    arxiv = arxiv


if __name__ == "__main__":
    arxiv.get_vocab()
