# cdk/receipt_app/receipt_stack.py
from aws_cdk import (
    Stack,
    aws_s3 as s3,
)
from constructs import Construct

class ReceiptStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # minimal resource so synth/bootstrap can run
        s3.Bucket(self, "ReceiptUploadBucket")

