import boto3
import os
import json

def handler(event, context):
    print("Event:", json.dumps(event))

    # Extract bucket and key
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    # Run Textract AnalyzeExpense
    textract = boto3.client('textract')
    response = textract.analyze_expense(
        Document={'S3Object': {'Bucket': bucket, 'Name': key}}
    )

    # Parse & store result in DynamoDB (placeholder logic)
    ddb = boto3.resource('dynamodb')
    table = ddb.Table(os.environ['TABLE_NAME'])
    table.put_item(Item={
        "receipt_id": key,
        "vendor": "TODO",
        "total": "TODO"
    })

    # Send email via SES (optional, add later)

    return {
        "statusCode": 200,
        "body": "Processed receipt"
    }
