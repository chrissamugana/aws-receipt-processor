import boto3
import os
import json
import logging
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        logger.info(f"Event: {json.dumps(event)}")
        
        # Extract bucket and key
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        logger.info(f"Processing file: {key} from bucket: {bucket}")
        
        # Run Textract AnalyzeExpense
        textract = boto3.client('textract')
        response = textract.analyze_expense(
            Document={'S3Object': {'Bucket': bucket, 'Name': key}}
        )
        
        logger.info(f"Textract response received with {len(response.get('ExpenseDocuments', []))} expense documents")
        
        # Parse & store result in DynamoDB
        ddb = boto3.resource('dynamodb')
        table = ddb.Table(os.environ['TABLE_NAME'])
        
        # Basic extraction from Textract response
        vendor = "Unknown"
        total = "0.00"
        
        # Extract vendor and total from Textract response
        if response.get('ExpenseDocuments'):
            expense_doc = response['ExpenseDocuments'][0]
            
            # Look for vendor information
            for field in expense_doc.get('SummaryFields', []):
                if field.get('Type', {}).get('Text') == 'VENDOR_NAME':
                    vendor = field.get('ValueDetection', {}).get('Text', 'Unknown')
                elif field.get('Type', {}).get('Text') == 'TOTAL':
                    total = field.get('ValueDetection', {}).get('Text', '0.00')
        
        # Store in DynamoDB
        table.put_item(Item={
            "receipt_id": key,
            "vendor": vendor,
            "total": total,
            "processed_at": context.aws_request_id
        })
        
        logger.info(f"Successfully processed receipt: {key}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Processed receipt successfully",
                "receipt_id": key,
                "vendor": vendor,
                "total": total
            })
        }
        
    except ClientError as e:
        logger.error(f"AWS service error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "AWS service error",
                "message": str(e)
            })
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        }