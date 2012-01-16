import os

e = os.environ

DEBUG      = e['DEBUG'].lower() == 'y'
SECRET_KEY = e.get('SECRET_KEY', 'develop')

USERNAME   = e['ARXIV_USER']
PASSWORD   = e['ARXIV_PASS']
DATABASE   = e['ARXIV_DB']
SERVER     = e['ARXIV_SERVER']
PORT       = int(e['ARXIV_PORT'])

