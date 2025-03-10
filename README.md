# AWS Connect to Adobe Experience Platform Event Forwarder

This Lambda function forwards events from AWS Connect to Adobe Experience Platform with automatic token management through AWS Secrets Manager.

## Features

- Uses AWS Secrets Manager for secure credential storage
- Automatic token management with refresh handling
- Automatically retries requests when tokens expire
- Can be tested locally with AWS SAM
- Easily deployed with VS Code AWS Toolkit

## Setup

### 1. Required AWS IAM Permissions

Before proceeding, ensure your AWS user has the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PutRolePolicy",
                "iam:PassRole",
                "iam:TagRole",
                "cloudformation:CreateStack",
                "cloudformation:CreateChangeSet",
                "cloudformation:ExecuteChangeSet",
                "cloudformation:DescribeStacks",
                "cloudformation:DescribeStackEvents",
                "cloudformation:GetTemplateSummary",
                "lambda:CreateFunction",
                "lambda:GetFunction",
                "lambda:AddPermission",
                "lambda:UpdateFunctionCode",
                "apigateway:POST",
                "apigateway:PUT",
                "apigateway:GET",
                "s3:CreateBucket",
                "s3:PutObject",
                "s3:GetObject",
                "secretsmanager:CreateSecret",
                "secretsmanager:GetSecretValue",
                "secretsmanager:PutSecretValue",
                "secretsmanager:UpdateSecret"
            ],
            "Resource": "*"
        }
    ]
}
```

⚠️ **Permission Issues Note:** If you encounter `ROLLBACK_COMPLETE` states or IAM permission errors during deployment, ensure your AWS user has all the permissions listed above, particularly `iam:CreateRole` and `iam:TagRole` which are commonly missing.

### 2. Store Credentials in Secrets Manager

Create a secret in AWS Secrets Manager with your Adobe Experience Platform credentials:

```bash
aws secretsmanager create-secret \
  --name aep-event-forwarder-creds \
  --secret-string '{
    "AEP_ENDPOINT": "https://dcs.adobedc.net/collection/your-collection-id",
    "IMS_ENDPOINT": "https://ims-na1.adobelogin.com/ims/token/v2",
    "CLIENT_ID": "your-client-id",
    "CLIENT_SECRET": "your-client-secret",
    "IMS_ORG": "your-org-id@AdobeOrg",
    "TECHNICAL_ACCOUNT_ID": "your-technical-account-id",
    "SCOPES": "openid,AdobeID,read_organizations,additional_info.projectedProductContext,session",
    "FLOW_ID": "your-flow-id",
    "SANDBOX_NAME": "your-sandbox-name"
  }' \
  --profile your-aws-profile
```

## Local Testing

### 1. Install Prerequisites

- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Docker](https://www.docker.com/products/docker-desktop)
- [VS Code with AWS Toolkit extension](https://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/setup-toolkit.html)

### 2. Configure AWS Credentials

Set up your AWS credentials either by:

- Configuring a profile: `aws configure --profile your-profile-name`
- Setting environment variables:
  ```bash
  export AWS_ACCESS_KEY_ID=your-access-key
  export AWS_SECRET_ACCESS_KEY=your-secret-key
  export AWS_REGION=your-region
  ```

### 3. Test with SAM CLI

```bash
# Build the application
sam build

# Start the local API
sam local start-api --profile your-aws-profile

# Or using environment variables
AWS_ACCESS_KEY_ID=your-key AWS_SECRET_ACCESS_KEY=your-secret AWS_REGION=your-region sam local start-api
```

### 4. Test with Postman

1. Send a POST request to http://127.0.0.1:3000/connect-event
2. Set Content-Type header to application/json
3. Include a JSON payload in the body

Example payload:
```json
{
  "order_id": "XU7L020O9M59VQ4S98",
  "order_time": "2023-08-05T06:23:23Z",
  "order_total": "69.69",
  "customer_id": "64a85c39fc13ae36aebeed8c",
  "customer_email": "customer@example.com",
  "customer_name": "John Doe"
}
```

## Deployment with VS Code AWS Toolkit

### 1. Open Project in VS Code

Open the project folder in VS Code:

```bash
code .
```

### A. Deploy via AWS Toolkit Extension (Recommended)

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS) to open the Command Palette
2. Type "AWS: Connect to AWS" and select it
3. Choose your AWS profile
4. Type "AWS: Deploy SAM Application" and select it
5. Follow the deployment wizard:
   - **Template File**: Choose your `template.yaml`
   - **Deployment Method**: Choose "Deploy to production with CloudFormation"
   - **S3 Bucket**: Choose or create a bucket for deployment artifacts
   - **Stack Name**: Enter a unique name (e.g., "aep-connect-event-forwarder")
   - **Parameters**: Choose "Just specify the required parameters"
   - **Capabilities**: Confirm required capabilities
   - Wait for deployment to complete

⚠️ **Common Issue: ROLLBACK_COMPLETE State**
If your deployment fails and the stack is in ROLLBACK_COMPLETE state, you need to delete it before retrying:

```bash
aws cloudformation delete-stack --stack-name your-stack-name
aws cloudformation wait stack-delete-complete --stack-name your-stack-name
```

Then try the deployment again with a new stack name.

### B. Deploy via SAM CLI

Alternatively, you can deploy using the SAM CLI:

```bash
sam build
sam deploy --guided --profile your-profile
```

### 4. Verify Deployment

Once deployed, you'll see an output for the API Gateway endpoint URL. Test it with Postman:

1. Send a POST request to the endpoint (e.g., https://xmzbly0q45.execute-api.us-east-1.amazonaws.com/Prod/connect-event/)
2. Set Content-Type header to application/json
3. Include a JSON payload in the body

## Troubleshooting

### Permission Issues

- **Common Error**: "User is not authorized to perform iam:CreateRole"
  - **Solution**: Add IAM permissions listed in the "Required AWS IAM Permissions" section
  
- **ROLLBACK_COMPLETE State**: If your stack is in this state, delete it using the AWS CLI or console before retrying deployment.

- **Tagging Permissions**: Make sure your user has `iam:TagRole` permission, which is often overlooked.

### Secret Access Issues

- **Error**: "Secrets Manager can't find the specified secret"
  - **Solution**: Make sure you've created the secret with the exact name used in your template parameters.

- **Error**: "User is not authorized to perform secretsmanager:GetSecretValue"
  - **Solution**: Ensure your AWS user and Lambda execution role have Secrets Manager permissions.

### Testing Issues

- **Local Testing Fails**: Ensure Docker is running and that your AWS credentials have permission to access Secrets Manager.

- **401 Errors from Adobe**: The function will automatically retry once with a fresh token, but verify your Adobe credentials are correct.

## How It Works

1. Lambda receives an event from API Gateway
2. Credentials are retrieved securely from AWS Secrets Manager
3. Access token is retrieved from cache or generated if needed
4. Event is forwarded to Adobe Experience Platform
5. If token expires, a new one is automatically generated and the request is retried
6. Lambda returns the AEP response to the caller

## Customizing

- **Secret Names**: Change the environment variables in the template.yaml file
- **Event Structure**: Modify the lambda_handler function to adjust the event structure as needed
- **Token Management**: Adjust the token refresh logic in get_access_token() if needed