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
        "identity": 1,
        }

async def do_main(opt, query):
    x_client = motor.motor_asyncio.AsyncIOMotorClient(
            opt.mongo_url, io_loop=opt.loop,
            serverSelectionTimeoutMS=2000)
    x_db = x_client[opt.mongo_db_name]
    x_tab = x_db[opt.mongo_table_name]

    try:
        async for r in x_tab.find(query, select).sort([("_ts",-1)]):
            print(r)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print(e)

from argparse import ArgumentParser
ap = ArgumentParser()
ap.add_argument("-u", action="store", dest="mongo_url",
                default="mongodb://localhost:27017",
                help="specify the mongodb's url.")
ap.add_argument("-c", action="store", dest="mongo_db_col_name",
                default="fastdb/misc",
                help="specify the db and collection name. e.g. fastdb/misc")
ap.add_argument("-a", action="store_true", dest="all_data",
                help="specify to show all.")
ap.add_argument("-e", action="store_true", dest="some_event",
                help="specify to show some events.")
ap.add_argument("-r", action="store", dest="range",
                default="today",
                help="specify the range to show. all, today, or a number.")
opt = ap.parse_args()

opt.mongo_db_name, opt.mongo_table_name = opt.mongo_db_col_name.split("/")

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

if opt.range == "all":
    pass
else:
    if opt.range == "today":
        dt = datetime.now(tz=dtgettz("Asia/Tokyo"))
        since = datetime(dt.year, dt.month, dt.day, 0, 0,
                        tzinfo=dtgettz("Asia/Tokyo"))
        until = since + timedelta(days=1)
    else:
        seconds = float(opt.range)
        until = datetime.now(tz=dtgettz("Asia/Tokyo"))
        since = until - timedelta(seconds=seconds)
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
opt.loop = asyncio.new_event_loop()
opt.loop.run_until_complete(do_main(opt, query))
