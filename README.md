# Detailed VS Code Deployment Guide

This guide provides step-by-step instructions for deploying the Adobe Experience Platform Event Forwarder Lambda function using VS Code's AWS Toolkit extension.

## Prerequisites

1. VS Code installed
2. AWS Toolkit extension installed
3. AWS credentials configured either as a profile or environment variables
4. AEP credentials saved in AWS Secrets Manager
5. Docker installed and running (for local testing)

## Local Testing

### Step 1: Configure AWS Credentials in VS Code

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS) to open the Command Palette
2. Type "AWS: Connect to AWS" and select it
3. Choose your AWS profile from the list

### Step 2: Test Locally

1. Open the Command Palette again
2. Type "AWS: Run SAM Application Locally" and select it
3. Select "API" option to start a local API Gateway
4. If prompted for the template file, select your `template.yaml`
5. Wait for Docker to initialize and the API to start (may take a minute)

### Step 3: Test with Postman

1. Open Postman or your preferred API testing tool
2. Create a new POST request to `http://127.0.0.1:3000/connect-event`
3. Set the Content-Type header to `application/json`
4. Add a test JSON payload in the request body:
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
5. Send the request and verify you receive a successful response

## Deployment to AWS

### Step 1: Deploy with AWS Toolkit

1. Open the VS Code Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Type "AWS: Deploy SAM Application" and select it
3. If prompted for the template file, select your `template.yaml`
4. Choose an S3 bucket for deployment, or create a new one
5. Enter a stack name (e.g., "aep-event-forwarder")
6. Select an AWS region 
7. Review the deployment parameters and confirm

![VS Code deployment wizard](https://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/images/sam-deploy-2.png)

### Step 2: Monitor Deployment

1. VS Code will show deployment progress in the OUTPUT panel
2. Wait for the "✅ Successfully deployed" message
3. The API Gateway endpoint URL will be displayed in the output

### Step 3: Test the Deployed Endpoint

1. Copy the API Gateway endpoint URL from the deployment output
2. Open Postman and create a POST request to this URL
3. Set the Content-Type header to `application/json`
4. Add a test JSON payload similar to the one used for local testing
5. Send the request and verify the Lambda is working in production

### Step 4: View Logs (Optional)

1. In VS Code, expand the AWS Explorer panel
2. Navigate to Lambda > Your Function Name
3. Right-click on the function and select "View Logs"
4. Choose a log stream to view execution logs

## Updating the Function

When you make changes to your function code:

1. Test locally using the steps above
2. Deploy again using "AWS: Deploy SAM Application"
3. Select the same stack name to update the existing deployment
4. Confirm the update

## Troubleshooting

### Common Issues

- **Deployment Fails**: Check your IAM permissions and that you have sufficient permissions to create CloudFormation stacks
- **Secret Access Issues**: Verify the Secrets Manager secret names match what's in your template
- **Testing Fails Locally**: Make sure Docker is running and that your AWS credentials have permission to access Secrets Manager
- **VS Code Not Showing AWS Resources**: Refresh your AWS Explorer panel or reconnect to AWS

### Viewing CloudFormation Errors

If deployment fails:

1. Open the AWS Explorer panel in VS Code
2. Navigate to AWS CloudFormation > Stacks
3. Right-click on your stack and select "View Stack Events"
4. Look for errors in the events list