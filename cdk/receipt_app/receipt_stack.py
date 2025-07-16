from aws_cdk import (
    Stack,
    Duration,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_dynamodb as ddb
)
from constructs import Construct

class ReceiptProcessorStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

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

        table = ddb.Table(self, "ReceiptsTable",
            partition_key=ddb.Attribute(name="receipt_id", type=ddb.AttributeType.STRING),
            encryption=ddb.TableEncryption.AWS_MANAGED
        )

        lambda_role = iam.Role(self, "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonTextractFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSESFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        lambda_fn = _lambda.Function(
            self, "ReceiptProcessorHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.main",
            code=_lambda.Code.from_asset("../receipt_lambda"),
            role=lambda_role,
            timeout=Duration.seconds(30)
        )
