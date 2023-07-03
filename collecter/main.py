import asyncio
import aiopg
from copy import deepcopy
import motor.motor_asyncio
import pymongo.errors
from pymongo import ReturnDocument
import json
from datetime import datetime, timedelta
from dateutil.tz import gettz as dtgettz

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


async def do_main(config):
    pgconn = await aiopg.connect(database=config.pg_db_name,
                                 user=config.pg_username,
                                 password=config.pg_password,
                                 host="127.0.0.1")
    x_client = motor.motor_asyncio.AsyncIOMotorClient(
            config.mongo_url, io_loop=config.loop,
            serverSelectionTimeoutMS=2000)
    x_db = x_client[config.mongo_db_name]
    x_tab = x_db[config.mongo_table_name]
    tz = dtgettz(config.tz)

    since = datetime.now(tz=tz)

    while True:
        await asyncio.sleep(config.interval)

        until = datetime.now(tz=tz)
        query = deepcopy(query_base)
        query["$and"].extend([
            { "ts": { "$gte": since.isoformat() } },
            { "ts": { "$lt":  until.isoformat() } }
            ])
        try:
            async for r in x_tab.find(query, select).sort([("_ts",-1)]):
                await submit(pgconn, r)
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(e)
        # copy *until* to *since* for the next.
        since = until
    pgconn.close()

