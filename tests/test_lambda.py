import os
import boto3
from moto import mock_dynamodb2  
import pytest
from unittest.mock import patch
from receipt_lambda import app  # your lambda app module

@mock_dynamodb2
def test_lambda_handler():
    os.environ['TABLE_NAME'] = 'ReceiptsTable'

    # Setup mock DynamoDB table
    ddb = boto3.client('dynamodb', region_name='eu-west-1')
    ddb.create_table(
        TableName='ReceiptsTable',
        KeySchema=[{'AttributeName': 'receipt_id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'receipt_id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )

    # Mock event as per your lambda trigger
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

    # Patch boto3 client for textract since moto does NOT support Textract mocks
    with patch('boto3.client') as mock_boto_client:
        mock_textract = mock_boto_client.return_value
        mock_textract.analyze_document.return_value = {
            "Blocks": [{"BlockType": "LINE", "Text": "Sample receipt text"}]
        }

        # Call your lambda handler
        result = app.handler(event, None)

    assert result['statusCode'] == 200

