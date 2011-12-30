import os

e = os.environ

DEBUG      = e['DEBUG'].lower() == 'y'
SECRET_KEY = e.get('SECRET_KEY', 'develop')

USERNAME   = e['ARXIV_USER']
PASSWORD   = e['ARXIV_PASS']
DATABASE   = e['ARXIV_DB']
SERVER     = e['ARXIV_SERVER']
PORT       = int(e['ARXIV_PORT'])
SENDGRID_USERNAME = e['SENDGRID_USERNAME']
SENDGRID_PASSWORD = e['SENDGRID_PASSWORD']
REDIS_SERVER = e['REDIS_SERVER']
REDIS_PASS   = e['REDIS_PASS']
REDIS_PORT   = int(e['REDIS_PORT'])

categories = sorted(["astro-ph", "cond-mat", "gr-qc", "hep-ex", "hep-lat", "hep-ph",
        "hep-th", "math-ph", "nucl-ex", "nucl-th", "physics", "quant-ph", "math",
        "nlin", "cs", "q-bio", "q-fin", "stat"])

subjects   = [{"category": "astro-ph", "subjects": ["CO", "EP", "GA", "HE", "IM", "SR"]},
        {"category": "cond-mat",
            "subjects": ["dis-nn", "mtrl-sci", "mes-hall", "other", "quant-gas",
                           "soft", "stat-mech", "str-el", "supr-con"]},
        {"category": "physics",
            "subjects": ["acc-ph", "ao-ph", "atom-ph", "atm-clus", "bio-ph",
                "chem-ph", "class-ph", "comp-ph", "data-an", "flu-dyn", "gen-ph",
                "geo-ph", "hist-ph", "ins-det", "med-ph", "optics", "ed-ph",
                "soc-ph", "plasm-ph", "pop-ph", "space-ph"]},
        {"category": "math",
            "subjects": ["AG", "AT", "AP", "CT", "CA", "CO", "AC", "CV", "DG",
                "DS", "FA", "GM", "GN", "GT", "GR", "HO", "IT", "KT", "LO", "MP",
                "MG", "NT", "NA", "OA", "OC", "PR", "QA", "RT", "RA", "SP", "ST",
                "SG"]},
        {"category": "nlin",
            "subjects": ["AO", "CG", "CD", "SI", "PS"]},
        {"category": "cs",
            "subjects": ["AI", "CL", "CC", "CE", "CG", "GT", "CV", "CY", "CR",
                "DS", "DB", "DL", "DM", "DC", "ET", "FL", "GL", "GR", "AR", "HC",
                "IR", "IT", "LG", "LO", "MS", "MA", "MM", "NI", "NE", "NA", "OS",
                "OH", "PF", "PL", "RO", "SI", "SE", "SD", "SC", "SY"]},
        {"category": "q-bio",
            "subjects": ["BM", "CB", "GN", "MN", "NC", "OT", "PE", "QM", "SC", "TO"]},
        {"category": "q-fin",
            "subjects": ["CP", "GN", "PM", "PR", "RM", "ST", "TR"]},
        {"category": "stat",
            "subjects": ["AP", "CO", "ML", "ME", "OT", "TH"]}]

