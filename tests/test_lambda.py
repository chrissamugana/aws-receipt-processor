import os
import boto3
from moto import mock_dynamodb, mock_textract
import pytest
from lambda import app

@mock_dynamodb
@mock_textract
def test_lambda_handler():
    os.environ['TABLE_NAME'] = 'ReceiptsTable'

    # Setup mock table
    ddb = boto3.client('dynamodb', region_name='eu-west-1')
    ddb.create_table(
        TableName='ReceiptsTable',
        KeySchema=[{'AttributeName': 'receipt_id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'receipt_id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )

    # Mock event
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "test-bucket"},
                    "object": {"key": "test.pdf"}
                }
            }
        ]
    }

    result = app.handler(event, None)
    assert result['statusCode'] == 200
