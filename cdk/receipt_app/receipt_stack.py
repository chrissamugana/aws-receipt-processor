from aws_cdk import (
    Stack,
    Duration,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_dynamodb as ddb
)
from constructs import Construct


class ReceiptProcessorStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # 🔹 S3 Bucket for uploads
        upload_bucket = s3.Bucket(self, "ReceiptUploadBucket",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            lifecycle_rules=[
                s3.LifecycleRule(
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(30)
                        )
                    ]
                )
            ]
        )

        # 🔹 DynamoDB Table for storing metadata
        table = ddb.Table(self, "ReceiptsTable",
            partition_key=ddb.Attribute(name="receipt_id", type=ddb.AttributeType.STRING),
            encryption=ddb.TableEncryption.AWS_MANAGED
        )

        # 🔹 IAM Role for Lambda
        lambda_role = iam.Role(self, "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonTextractFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSESFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        # 🔹 Lambda Function to process receipt
        lambda_fn = _lambda.Function(self, "ReceiptProcessorFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.main",
            code=_lambda.Code.from_asset("../lambda"),
            role=lambda_role,
            environment={
                "TABLE_NAME": table.table_name,
                "BUCKET_NAME": upload_bucket.bucket_name
            }
        )

        # 🔹 Trigger Lambda on S3 upload
        upload_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.LambdaDestination(lambda_fn)
        )




