markdown
Copy
Edit
# 📥 AWS Serverless Receipt Processing System

This project is a fully serverless receipt processing system built with **AWS CDK (Python)**. It automatically processes uploaded receipt images by extracting key information and emailing the results back to the user.

## 🔧 Key Features

- **S3 Bucket**: Users upload receipts here. Uploading triggers the processing pipeline.
- **AWS Lambda**: Uses Amazon **Textract** to extract text from receipts, parses the data, and stores it in DynamoDB.
- **DynamoDB**: Stores structured metadata for analytics, querying, or auditing.
- **SES (Simple Email Service)**: Sends extracted receipt summaries back to the user’s email.
- **Infrastructure as Code**: Entire architecture is managed using AWS CDK with Python.
- **CI/CD**: GitHub Actions workflow automates synthesis and validation on every push.

---

## 📁 Project Structure

aws-receipt-processor/
├── README.md
├── .gitignore
├── .github/
│ └── workflows/
│ └── ci.yml
├── cdk/
│ ├── app.py
│ ├── cdk.json
│ ├── requirements.txt
│ └── receipt_app/
│ └── receipt_stack.py
├── lambda/
│ ├── app.py
│ ├── parse_utils.py
│ ├── email_template.html
│ └── requirements.txt
├── tests/
│ ├── test_handler.py
│ └── test_utils.py

markdown
Copy
Edit

---

## 🚀 How It Works

1. **User uploads a receipt** image to S3.
2. **S3 Event** triggers the Lambda function.
3. **Lambda**:
   - Uses **Textract** to extract text.
   - Parses key data like merchant, total, date.
   - Stores parsed data in **DynamoDB**.
   - Renders email with **Jinja2** and sends it via **SES**.
4. **User receives email** with the receipt summary.

---

## 📦 Tech Stack

- **AWS CDK (Python)**
- **Lambda**
- **Textract**
- **S3**
- **SES**
- **DynamoDB**
- **GitHub Actions**
- **Boto3 + Jinja2**

---
