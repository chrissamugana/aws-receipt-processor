#!/usr/bin/env python3
import aws_cdk as cdk
from receipt_app.receipt_stack import ReceiptProcessorStack

app = cdk.App()
ReceiptProcessorStack(app, "ReceiptProcessorStack", env=cdk.Environment(
    region="eu-west-1"
))
app.synth()

