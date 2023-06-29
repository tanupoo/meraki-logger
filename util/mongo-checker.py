import motor.motor_asyncio
import pymongo.errors
from pymongo import ReturnDocument
import json
from datetime import datetime, timedelta
from dateutil.tz import gettz as dtgettz
import asyncio

select = {
        "_id": 0,
        "ts": 1,
        "reason": 1,
        "ev_type": 1,
        "ap_name": 1,
        "client_mac": 1,
        "identifier": 1,
        }

async def do_main(config, query):
    client = motor.motor_asyncio.AsyncIOMotorClient(
            "localhost", 27017,
            serverSelectionTimeoutMS=2000)
    col = client["fastdb"]["misc"]
    try:
        async for r in col.find(query, select).sort([("_ts",-1)]):
            print(r)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print(e)

from argparse import ArgumentParser
ap = ArgumentParser()
ap.add_argument("-a", action="store_true", dest="all_data",
                help="specify to show all.")
ap.add_argument("-e", action="store_true", dest="some_event",
                help="specify to show some events.")
opt = ap.parse_args()

query = { "$and": [] }
if opt.some_event:
    query["$and"].append({
            "ev_type": { "$in": [
                "disassociation",
                "8021x_radius_timeout",
                "8021x_client_deauth",
                "8021x_deauth"
                ]
            }
        })
else:
    query["$and"].append({
            "ev_type": "disassociation"
        })

if not opt.all_data:
    until = datetime.now(tz=dtgettz("Asia/Tokyo"))
    since = until - timedelta(seconds=600)
    query["$and"].extend([
        {
            "ts": { "$gte": since.isoformat() }
        },
        {
            "ts": { "$lt":  until.isoformat() }
        }
        ])

#
# main
#
loop = asyncio.new_event_loop()
loop.run_until_complete(do_main(config, query))
