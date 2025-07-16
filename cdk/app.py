#!/usr/bin/env python3
import os

import aws_cdk as cdk

from receipt_app.receipt_stack import ReceiptStack  # ✅ Custom stack class

app = cdk.App()

# ✅ Instantiate your stack (use a descriptive name for clarity)
ReceiptStack(
    app, 
    "ReceiptProcessorStack",
    # Optional: Define env if you want to lock this to a specific account/region
    # env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))
)

app.synth()
