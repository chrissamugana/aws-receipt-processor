# 📥 AWS Receipt Processing System

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

