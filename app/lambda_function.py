import asyncio

from main import run


def lambda_handler(event, context):
    asyncio.run(run())
    return {"statusCode": 200, "body": "Good news sent"}
