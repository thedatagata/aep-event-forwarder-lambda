# AWS Connect to Adobe Experience Platform Event Forwarder

This Lambda function forwards events from AWS Connect to Adobe Experience Platform with automatic token management through AWS Secrets Manager.

## Quick Start Guide for Non-Developers

This guide provides step-by-step instructions for setting up the necessary tools and deploying the AWS Lambda function, even if you have minimal coding experience.

## Part 1: Install Required Tools

### Installing Python

1. Brew install pyenv - *brew install pyenv*
2. Validate Installation - *pyenv --version*
3. Find available python versions - *pyenv install -l*
4. Install python3.11.3 - *pyenv install 3.11.3*
5. Install python3.9.6 - *pyenv install 3.9.6*
6. Set global version of python to 3.9.6 - *pyenv global 3.9.6*
7. Create a virtualenv for dev w/ 3.11.3 - *pyenv virtualenv 3.11.3 aws-dev*
8. Create a folder where you want to develop, navigate to that folder, and activate virtualenv - *pyenv activate aws-dev*
9. Verify correct pip - *pyenv which pip*
10. Clone the repo, navigate inside the project, and run - *pip install -r requirements.txt*
11. ???
12. profit

### 1. Install AWS CLI

The AWS Command Line Interface (CLI) allows you to interact with AWS services from the command line.

**Windows:**
1. Download the MSI installer from [AWS CLI website](https://aws.amazon.com/cli/)
2. Run the downloaded MSI installer and follow the on-screen instructions
3. Open Command Prompt to verify installation:
   ```
   aws --version
   ```

**macOS:**
1. Install via Homebrew (recommended):
   ```
   brew install awscli
   ```
2. Or download the installer from the [AWS CLI website](https://aws.amazon.com/cli/)
3. Open Terminal to verify installation:
   ```
   aws --version
   ```

**Linux:**
1. Install using your package manager:
   ```
   # For Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install awscli

   # For Amazon Linux/RHEL
   sudo yum install awscli
   ```
2. Verify installation:
   ```
   aws --version
   ```

### 2. Configure AWS Credentials

After installing the AWS CLI, you need to configure it with your AWS credentials:

1. Get your AWS Access Key ID and Secret Access Key from your AWS administrator or the AWS Console
2. Open Terminal (macOS/Linux) or Command Prompt (Windows)
3. Run:
   ```
   aws configure
   ```
4. Enter your AWS Access Key ID, Secret Access Key, default region (e.g., us-east-1), and preferred output format (json)

Alternatively, you can create a named profile:
```
aws configure --profile your-profile-name
```

### 3. Install AWS SAM CLI

The AWS Serverless Application Model (SAM) CLI makes it easier to build and deploy serverless applications.

**Windows:**
1. Install Docker Desktop first from [Docker website](https://www.docker.com/products/docker-desktop)
2. Download the SAM CLI installer from [GitHub releases](https://github.com/aws/aws-sam-cli/releases)
3. Run the installer and follow the on-screen instructions
4. Open Command Prompt to verify installation:
   ```
   sam --version
   ```

**macOS:**
1. Install Docker Desktop first from [Docker website](https://www.docker.com/products/docker-desktop)
2. Install SAM CLI via Homebrew:
   ```
   brew tap aws/tap
   brew install aws-sam-cli
   ```
3. Verify installation:
   ```
   sam --version
   ```

**Linux:**
1. Install Docker first:
   ```
   # For Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io
   sudo systemctl start docker
   sudo systemctl enable docker
   ```
2. Download and install SAM CLI:
   ```
   wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
   unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
   sudo ./sam-installation/install
   ```
3. Verify installation:
   ```
   sam --version
   ```

### 4. Install VS Code and AWS Toolkit Extension

Visual Studio Code (VS Code) is a free, lightweight code editor.

1. Download and install VS Code from [Visual Studio Code website](https://code.visualstudio.com/)
2. Open VS Code
3. Click on the Extensions icon in the sidebar (or press Ctrl+Shift+X)
4. Search for "AWS Toolkit"
5. Click "Install" on the AWS Toolkit extension by Amazon

### 5. Install Python

This project requires Python 3.9 or newer.

**Windows:**
1. Download the Python installer from [Python.org](https://www.python.org/downloads/)
2. Run the installer, making sure to check "Add Python to PATH"
3. Open Command Prompt to verify installation:
   ```
   python --version
   ```

**macOS:**
1. Install via Homebrew:
   ```
   brew install python
   ```
2. Verify installation:
   ```
   python3 --version
   ```

**Linux:**
1. Install using your package manager:
   ```
   # For Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3 python3-pip
   ```
2. Verify installation:
   ```
   python3 --version
   ```

## Part 2: Setting Up the Project

### 1. Download the Project

1. Download this project as a ZIP file or clone it if you're familiar with Git
2. Extract the ZIP file to a location on your computer
3. Open VS Code
4. Click on "File" > "Open Folder" and select the extracted project folder

### 2. Set Up Python Environment

1. Open a Terminal in VS Code by clicking on "Terminal" > "New Terminal"
2. Create a virtual environment:
   ```
   # Windows
   python -m venv venv
   
   # macOS/Linux
   python3 -m venv venv
   ```
3. Activate the virtual environment:
   ```
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### 3. Store Credentials in AWS Secrets Manager

Create a secret in AWS Secrets Manager with your Adobe Experience Platform credentials:

1. Open the [AWS Secrets Manager Console](https://console.aws.amazon.com/secretsmanager/)
2. Click "Store a new secret"
3. Select "Other type of secret"
4. Enter your Adobe credentials in JSON format:
   ```json
   {
     "AEP_ENDPOINT": "https://dcs.adobedc.net/collection/your-collection-id",
     "IMS_ENDPOINT": "https://ims-na1.adobelogin.com/ims/token/v2",
     "CLIENT_ID": "your-client-id",
     "CLIENT_SECRET": "your-client-secret",
     "IMS_ORG": "your-org-id@AdobeOrg",
     "TECHNICAL_ACCOUNT_ID": "your-technical-account-id",
     "SCOPES": "openid,AdobeID,read_organizations,additional_info.projectedProductContext,session",
     "FLOW_ID": "your-flow-id",
     "SANDBOX_NAME": "your-sandbox-name"
   }
   ```
5. Click "Next"
6. Enter "aep-event-forwarder-creds" as the secret name
7. Complete the wizard to create the secret

Alternatively, you can use the AWS CLI:

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

## Part 3: Required AWS IAM Permissions

Before proceeding with deployment, ensure your AWS user has the following permissions:

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

Ask your AWS administrator to attach these permissions to your IAM user or role.

⚠️ **Permission Issues Note:** If you encounter `ROLLBACK_COMPLETE` states or IAM permission errors during deployment, ensure your AWS user has all the permissions listed above, particularly `iam:CreateRole` and `iam:TagRole` which are commonly missing.

## Part 4: Local Testing

### 1. Start Docker

Make sure Docker Desktop is running on your computer.

### 2. Test with SAM CLI

In VS Code's terminal:

```bash
# Build the application
sam build

# Start the local API (using a profile if configured)
sam local start-api --profile your-aws-profile

# Or using environment variables
AWS_ACCESS_KEY_ID=your-key AWS_SECRET_ACCESS_KEY=your-secret AWS_REGION=your-region sam local start-api
```

### 3. Test with Postman

1. Download and install [Postman](https://www.postman.com/downloads/)
2. Create a new POST request to http://127.0.0.1:3000/connect-event
3. Add a header: Content-Type = application/json
4. In the Body tab, select "raw" and "JSON"
5. Enter a test payload:
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
6. Click "Send" to test the function

## Part 5: Deployment with VS Code AWS Toolkit

### Deploy via AWS Toolkit Extension

1. In VS Code, press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS) to open the Command Palette
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

### Verifying Deployment

Once deployed, you'll see an output for the API Gateway endpoint URL. Test it with Postman:

1. Create a new POST request to the provided endpoint URL
2. Add a header: Content-Type = application/json 
3. Add the same JSON payload used for local testing
4. Click "Send" to test the deployed function

## Troubleshooting

### Permission Issues

- **Common Error**: "User is not authorized to perform iam:CreateRole"
  - **Solution**: Ask your AWS administrator to add the IAM permissions listed in Part 3
  
- **ROLLBACK_COMPLETE State**: If your stack is in this state, delete it using the AWS CLI or console before retrying deployment.

- **Tagging Permissions**: Make sure your user has `iam:TagRole` permission, which is often overlooked.

### Secret Access Issues

- **Error**: "Secrets Manager can't find the specified secret"
  - **Solution**: Make sure you've created the secret with the exact name "aep-event-forwarder-creds".

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

## Features

- Uses AWS Secrets Manager for secure credential storage
- Automatic token management with refresh handling
- Automatically retries requests when tokens expire
- Can be tested locally with AWS SAM
- Easily deployed with VS Code AWS Toolkit

## Customizing

- **Secret Names**: Change the environment variables in the template.yaml file
- **Event Structure**: Modify the lambda_handler function to adjust the event structure as needed
- **Token Management**: Adjust the token refresh logic in get_access_token() if needed