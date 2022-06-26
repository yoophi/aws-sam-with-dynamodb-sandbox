from random import random

import boto3
import json
import os
from ulid import ULID

from botocore.exceptions import ClientError
from loguru import logger

REGION = os.environ.get("REGION")
AWS_ENV = os.environ.get("AWS_ENV")
DEV_ENV = os.environ.get("DEV_ENV")

if AWS_ENV == "AWS_SAM_LOCAL":
    endpoint = None
    if DEV_ENV == "OSX":
        endpoint = "http://docker.for.mac.localhost:8000/"
    elif DEV_ENV == "Windows":
        endpoint = "http://docker.for.window.localhost:8000/"
    else:
        endpoint = "http://127.0.0.1:8000"

    dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint)
else:
    dynamodb = boto3.resource("dynamodb")

USER_TABLE_NAME = (
    os.environ.get("LOCAL_USER_TABLE")
    if AWS_ENV == "AWS_SAM_LOCAL"
    else os.environ.get("USER_TABLE")
)

sample_table = dynamodb.Table(USER_TABLE_NAME)
print((USER_TABLE_NAME, REGION, AWS_ENV, DEV_ENV))

sample_data = [
    {
        "Id": str(ULID()),
        "PublicAddress": f'{random()}'
    }
    for _ in range(10000)
]


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    try:
        # When the list of items in the batch contains duplicates, Amazon DynamoDB
        # rejects the request. By default, the batch_writer keeps duplicates.
        with sample_table.batch_writer() as batch:
            for item in sample_data:
                batch.put_item(Item=item)
                logger.info('batch.put_item: ok')
        logger.info("Put data into %s.", sample_table.name)
    except ClientError as error:
        if error.response['Error']['Code'] == 'ValidationException':
            logger.info(
                "Got expected exception when trying to put duplicate records into the "
                "archive table.")
        else:
            logger.exception(
                "Got unexpected exception when trying to put duplicate records into "
                "the archive table.")
            raise
    except Exception as error:
        logger.exception('Exception occurred')

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
            }
        ),
    }
