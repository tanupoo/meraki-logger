import sys
sys.path.insert(0, "../syslog")

from parser import parser
from argparse import ArgumentParser
import requests
import json

ap = ArgumentParser()
ap.add_argument("syslog_file", help="specify a log filename.")
ap.add_argument("-n", action="store_true", dest="noharm",
                help="no harm, no change.")
opt = ap.parse_args()

n = 0

def submit(data):
    global n
    url = "http://localhost:65515/post"
    headers = {"content-type": "application/json"}
    ret = requests.post(url, data=json.dumps(data), headers=headers)
    if not ret.ok:
        print(f"ERROR: {ret.status_code} {ret.reason}")
    else:
        n += 1

p = parser(embed_syslog=False)
with open(opt.syslog_file) as fd:
    for line in fd:
        ev_one = p.parse(line)
        if ev_one:
            if opt.noharm:
                print(ev_one)
            else:
                submit(ev_one)

print(f"nb_post: {n}")
