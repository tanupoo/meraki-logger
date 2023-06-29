from fastapi import FastAPI, Request, HTTPException
from fastapi import status as httpcode
import motor.motor_asyncio
import json
from dateutil import parser as dtparser

def api(config):

    logger = config.logger

    app = FastAPI()

    x_client = motor.motor_asyncio.AsyncIOMotorClient(
            config.mongo_url, io_loop=config.loop,
            serverSelectionTimeoutMS=2000)
    x_db = x_client[config.mongo_db_name]
    x_tab = x_db[config.mongo_table_name]

    #
    # API
    #
    @app.post(
        "/post",
        response_description="POST",
        status_code=httpcode.HTTP_201_CREATED,
        )
    async def post_log(request: Request):
        try:
            in_json = await request.json()
        except json.decoder.JSONDecodeError as e:
            msg = f"JSON parse error: {str(e)}"
            logger.error(msg)
            return HTTPException(
                    status_code=httpcode.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={ "detail": msg })
        except Exception as e:
            msg = str(e)
            logger.error(msg)
            return HTTPException(
                    status_code=httpcode.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={ "detail": msg })
        if config.enable_debug:
            logger.debug(f"IN_JSON={in_json}")
        # check the timestamp.
        ts = in_json.get("ts")
        if ts is None:
            msg = f"ts doesn't exist."
            logger.error(msg)
            return HTTPException(
                    status_code=httpcode.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={ "detail": msg })
        # create _ts as the timestamp for mongo.
        try:
            in_json["_ts"] = dtparser.parse(ts)
        except dtparser._parser.ParserError as e:
            msg = str(e)
            logger.error(msg)
            return HTTPException(
                    status_code=httpcode.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={ "detail": msg })
        # post the info.
        logger.debug(f"insert_one: trying: {in_json}")
        try:
            result = await x_tab.insert_one(in_json)
        except Exception as e:
            msg = str(e)
            logger.error(msg)
            return HTTPException(
                    status_code=httpcode.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={ "detail": msg })
        #
        logger.debug(f"RET: id={result.inserted_id} ack={result.acknowledged} "
                    f"data={in_json}")
        # if needed, copy in_data again to avoid leaking "_id".
        if result.acknowledged == True:
            return { "status": "OK" }
        else:
            logger.error(f"{result}")
            return HTTPException(
                    status_code=httpcode.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={ "detail": "error on submit" } )

    return app

