from aws_cdk import (
    Stack,
    Duration,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    aws_s3_notifications as s3_notifications,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
    aws_kms as kms,
    aws_lambda_destinations as destinations,
    CfnOutput
)
from constructs import Construct

class ReceiptProcessorStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # KMS Key for encryption
        kms_key = kms.Key(self, "ReceiptProcessorKey",
            description="KMS key for Receipt Processor encryption",
            enable_key_rotation=True
        )

        # Your original S3 bucket with lifecycle rules
        upload_bucket = s3.Bucket(self, "ReceiptUploadBucket",
            versioned=True,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=kms_key,
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

        # Your original DynamoDB table with enhanced features
        table = dynamodb.Table(self, "ReceiptsTable",
            partition_key=dynamodb.Attribute(name="receipt_id", type=dynamodb.AttributeType.STRING),
        )

        # Dead Letter Queue for failed Lambda executions
        dead_letter_queue = sqs.Queue(self, "ReceiptProcessorDLQ",
            encryption=sqs.QueueEncryption.KMS,
            encryption_master_key=kms_key,
            retention_period=Duration.days(14)
        )

        # SNS Topic for alerts
        alert_topic = sns.Topic(self, "ReceiptProcessorAlerts",
            display_name="Receipt Processor Alerts",
            master_key=kms_key
        )

        # Add email subscription (replace with your email)
        alert_topic.add_subscription(
            subscriptions.EmailSubscription("henates781@simerm.com")
        )

        # Your original Lambda role with same permissions
        lambda_role = iam.Role(self, "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonTextractFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSESFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        # Enhanced Lambda function with your same configuration
        lambda_fn = _lambda.Function(
            self, "ReceiptProcessorHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.handler",
            code=_lambda.Code.from_asset("../receipt_lambda"),
            role=lambda_role,
            timeout=Duration.seconds(300),  # Increased for Textract processing
            memory_size=512,  # Increased for better performance
            environment={
                "TABLE_NAME": table.table_name,
                "BUCKET_NAME": upload_bucket.bucket_name,
                "KMS_KEY_ID": kms_key.key_id
            },
            dead_letter_queue=dead_letter_queue,
            on_failure=destinations.SnsDestination(alert_topic)
        )

        # Your original S3 event notification
        upload_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.LambdaDestination(lambda_fn)
        )

        # Your original permissions
        table.grant_read_write_data(lambda_fn)
        upload_bucket.grant_read(lambda_fn)

        # Additional permissions for enhanced features
        kms_key.grant_encrypt_decrypt(lambda_fn)
        alert_topic.grant_publish(lambda_fn)

        # CloudWatch Alarms
        lambda_errors_alarm = cloudwatch.Alarm(self, "LambdaErrorsAlarm",
            metric=lambda_fn.metric_errors(
                period=Duration.minutes(5),
                statistic="Sum"
            ),
            threshold=1,
            evaluation_periods=1,
            alarm_description="Lambda function errors"
        )

        lambda_duration_alarm = cloudwatch.Alarm(self, "LambdaDurationAlarm",
            metric=lambda_fn.metric_duration(
                period=Duration.minutes(5),
                statistic="Average"
            ),
            threshold=Duration.seconds(60).to_seconds(),
            evaluation_periods=2,
            alarm_description="Lambda function duration is too high"
        )

        # FIXED: Correct method name for DLQ messages
        dlq_messages_alarm = cloudwatch.Alarm(self, "DLQMessagesAlarm",
            metric=dead_letter_queue.metric_approximate_number_of_messages_visible(
                period=Duration.minutes(5),
                statistic="Sum"
            ),
            threshold=1,
            evaluation_periods=1,
            alarm_description="Messages in dead letter queue"
        )

        # Add alarms to SNS topic
        lambda_errors_alarm.add_alarm_action(
            cloudwatch_actions.SnsAction(alert_topic)
        )
        lambda_duration_alarm.add_alarm_action(
            cloudwatch_actions.SnsAction(alert_topic)
        )
        dlq_messages_alarm.add_alarm_action(
            cloudwatch_actions.SnsAction(alert_topic)
        )

        # CloudWatch Dashboard
        dashboard = cloudwatch.Dashboard(self, "ReceiptProcessorDashboard",
            dashboard_name="ReceiptProcessor"
        )

        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Lambda Metrics",
                left=[
                    lambda_fn.metric_invocations(),
                    lambda_fn.metric_errors(),
                    lambda_fn.metric_duration()
                ],
                width=12
            ),
            cloudwatch.SingleValueWidget(
                title="DLQ Messages",
                metrics=[dead_letter_queue.metric_approximate_number_of_messages_visible()],
                width=12
            )
        )

        # Outputs
        CfnOutput(self, "BucketName", value=upload_bucket.bucket_name)
        CfnOutput(self, "TableName", value=table.table_name)
        CfnOutput(self, "DashboardURL", 
            value=f"https://{self.region}.console.aws.amazon.com/cloudwatch/home?region={self.region}#dashboards:name=ReceiptProcessor"
        )