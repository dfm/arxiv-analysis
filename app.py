#!/usr/bin/env python
# encoding: utf-8
"""
ArXiv Reader app

"""

import flask

# configure flask
import config
app = flask.Flask(__name__)
app.config.from_object(config)

@app.route('/')
def index():
    return "Nothing to see here..."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

