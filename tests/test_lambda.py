import sys
import os
import boto3
import pytest
from moto import mock_aws
from unittest.mock import patch

# Add the parent directory to Python path so it can find receipt_lambda folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Now import from receipt_lambda/app.py
from receipt_lambda.app import handler

@mock_aws
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
    
    # Patch boto3.client for textract since moto does NOT support Textract mocks
    with patch('receipt_lambda.app.boto3.client') as mock_boto_client:
        # Mock textract client
        mock_textract = mock_boto_client.return_value
        mock_textract.analyze_expense.return_value = {
            "ExpenseDocuments": [
                {
                    "Blocks": [{"BlockType": "LINE", "Text": "Sample receipt text"}]
                }
            ]
        }
        
        # Create a real DynamoDB resource for moto to handle
        real_ddb_resource = boto3.resource('dynamodb', region_name='eu-west-1')
        
        # Patch boto3.resource to return the real resource for DynamoDB
        with patch('receipt_lambda.app.boto3.resource', return_value=real_ddb_resource):
            # Call your lambda handler
            result = handler(event, None)
            
            # Add your assertions here
            assert result is not None
            # Add more specific assertions based on what your handler should return