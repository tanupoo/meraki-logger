#!/usr/bin/env python

import asyncio
import aiopg
from copy import deepcopy
import motor.motor_asyncio
import pymongo.errors
from pymongo import ReturnDocument
import json
from datetime import datetime, timedelta
from dateutil.tz import gettz as dtgettz
from argparse import ArgumentParser

query_base = { "$and": [
    {
        "ev_type": "disassociation",
    }
    ]
}

select = {
        "_id": 0,
        "ts": 1,
        "reason": 1,
        "ev_type": 1,
        "ap_name": 1,
        "client_mac": 1,
        "identity": 1,
        }

sql_ins = """insert into deauth (
  ts, reason, ev_type, ap_name, client_mac, identity) values (
  %s, %s, %s, %s, %s, %s)"""

async def submit(pgconn, data):
    """
    data = {
    'ts': '2023-06-29T11:29:14.909003+09:00', 'ap_name': 'OpenRoamingTest',
    'ev_type': 'disassociation', 'client_mac': 'CA:A2:A6:xx:xx:xx',
    'reason': '2'}
    """
    cur = await pgconn.cursor()
    ts = data.get("ts", "")
    reason = data.get("reason", 0)
    ev_type = data.get("ev_type", "")
    ap_name = data.get("ap_name", "")
    client_mac = data.get("client_mac", "")
    identity = data.get("identity", "")
    await cur.execute(sql_ins,
                      (ts, reason, ev_type, ap_name, client_mac, identity))
    print(data)


async def do_main(opt):
    pgconn = await aiopg.connect(database=opt.pg_db_name,
                                 user=opt.pg_username,
                                 password=opt.pg_password,
                                 host='127.0.0.1')
    x_client = motor.motor_asyncio.AsyncIOMotorClient(
            opt.mongo_url, io_loop=opt.loop,
            serverSelectionTimeoutMS=2000)
    x_db = x_client[opt.mongo_db_name]
    x_tab = x_db[opt.mongo_table_name]
    tz = dtgettz(opt.tz)

    until = datetime.now(tz=dtgettz(opt.tz))
    since = until - timedelta(seconds=opt.interval)

    while True:
        query = deepcopy(query_base)
        query["$and"].extend([
            { "ts": { "$gte": since.isoformat() } },
            { "ts": { "$lt":  until.isoformat() } }
            ])
        print(query)
        try:
            async for r in x_tab.find(query, select).sort([("_ts",-1)]):
                await submit(pgconn, r)
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(e)
        # preparing for the next.
        until = since
        since = since - timedelta(seconds=opt.interval)
        await asyncio.sleep(.01)
    pgconn.close()

ap = ArgumentParser()
ap.add_argument("--mongo-url", action="store", dest="mongo_url",
                default="mongodb://localhost:27017",
                help="specify the mongodb's url.")
ap.add_argument("--mongo-dbcol", action="store", dest="mongo_db_col_name",
                default="fastdb/misc",
                help="specify the db and collection name. e.g. fastdb/misc")
ap.add_argument("--pg-db", action="store", dest="pg_db_name",
                default="syslog",
                help="specify the postgres db name.")
ap.add_argument("--pg-userpass", action="store", dest="pg_userpass",
                default="postgres:postgres",
                help="specify the postgres's user and password.")
ap.add_argument("-i", action="store", dest="interval",
                type=int, default=600,
                help="specify the interval to convert.")
opt = ap.parse_args()

opt.mongo_db_name, opt.mongo_table_name = opt.mongo_db_col_name.split("/")
opt.pg_username, opt.pg_password = opt.pg_userpass.split(":")

#
# main
#
loop = asyncio.new_event_loop()
loop.run_until_complete(do_main(opt))

