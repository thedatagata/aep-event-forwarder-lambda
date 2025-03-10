import os
import json
import logging
import boto3
import requests
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize clients
secretsmanager = boto3.client('secretsmanager')

# Constants
AEP_CREDENTIALS_SECRET_NAME = os.environ.get('AEP_CREDENTIALS_SECRET_NAME', 'aep-event-forwarder-creds')
ACCESS_TOKEN_SECRET_NAME = os.environ.get('ACCESS_TOKEN_SECRET_NAME', 'adobe-access-token')

def get_aep_credentials():
    """
    Retrieve Adobe Experience Platform credentials from Secrets Manager
    """
    logger.info("Retrieving AEP credentials from Secrets Manager")
    try:
        response = secretsmanager.get_secret_value(SecretId=AEP_CREDENTIALS_SECRET_NAME)
        credentials = json.loads(response['SecretString']) 
        print(credentials)
        logger.info("Successfully retrieved AEP credentials")
        return credentials
    except ClientError as e:
        logger.error(f"Error retrieving AEP credentials: {str(e)}")
        raise

def get_access_token(force_refresh=False):
    """
    Retrieve a valid access token from Secrets Manager or generate a new one if needed
    
    Args:
        force_refresh (bool): If True, force generate a new token regardless of expiry
    """
    if not force_refresh:
        try:
            # Try to get the existing token from Secrets Manager
            response = secretsmanager.get_secret_value(SecretId=ACCESS_TOKEN_SECRET_NAME)
            token_secret = json.loads(response['SecretString'])
            
            # Check if token is still valid (with 5-minute buffer)
            if 'expiry' in token_secret and datetime.now() < datetime.fromisoformat(token_secret['expiry']) - timedelta(minutes=5):
                logger.info("Using existing token from Secrets Manager")
                return token_secret['access_token']
            
            logger.info("Token expired, generating new token")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info("Token secret not found, will create new one")
            else:
                logger.error(f"Error accessing Secrets Manager: {str(e)}")
                raise
    else:
        logger.info("Force refreshing token due to explicit request or token validation failure")
    
    # Generate new token
    new_token = generate_new_token()
    return new_token

def generate_new_token():
    """
    Generate a new access token from Adobe IMS
    """
    logger.info("Generating new Adobe access token")
    
    # Get credentials from Secrets Manager
    credentials = get_aep_credentials()
    
    data = {
        "grant_type": "client_credentials",
        "client_id": credentials.get("CLIENT_ID"),
        "client_secret": credentials.get("CLIENT_SECRET"),
        "scope": credentials.get("SCOPES")
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(
            credentials.get("IMS_ENDPOINT"),
            headers=headers,
            data=data,
            timeout=10.0
        )
        
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get('access_token')
        expires_in = token_data.get('expires_in', 86400)  # Default to 24 hours if not provided
        
        # Calculate expiry time
        expiry = datetime.now() + timedelta(seconds=expires_in)
        
        # Store token in Secrets Manager
        secret_payload = {
            'access_token': access_token,
            'expiry': expiry.isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        try:
            secretsmanager.create_secret(
                Name=ACCESS_TOKEN_SECRET_NAME,
                SecretString=json.dumps(secret_payload)
            )
            logger.info("Created new access token secret")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceExistsException':
                secretsmanager.update_secret(
                    SecretId=ACCESS_TOKEN_SECRET_NAME,
                    SecretString=json.dumps(secret_payload)
                )
                logger.info("Updated existing access token secret")
            else:
                raise
        
        return access_token
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error generating token: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")
        raise

def send_to_aep(event_data, access_token, retry_attempt=0):
    """
    Send event data to Adobe Experience Platform
    
    Args:
        event_data: The event data to send to AEP
        access_token: The Adobe access token to use for authentication
        retry_attempt: Internal counter to prevent infinite retry loops
    """
    # Get credentials from Secrets Manager
    credentials = get_aep_credentials()
    
    aep_endpoint = credentials.get("AEP_ENDPOINT") 
    flow_id = credentials.get("FLOW_ID")
    sandbox_name = credentials.get("SANDBOX_NAME") 

    url = aep_endpoint
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'x-adobe-flow-id': flow_id,
        'x-sandbox-name': sandbox_name
    }
    
    logger.info(f"Sending data to AEP URL: {url}")
    
    try:
        response = requests.post(url, json=event_data, headers=headers)
        
        # Handle 401 errors which may indicate an expired token
        if response.status_code == 401 and retry_attempt == 0:
            try:
                error_data = response.json()
                error_type = error_data.get("type", "")
                error_title = error_data.get("title", "")
                
                # Check if this is a token expiration error
                if ("token expired" in error_title.lower() or 
                    "authorization token expired" in error_title.lower() or
                    "EXEG-0503-401" in error_type):
                    
                    logger.info("Access token expired. Generating a new token and retrying.")
                    
                    # Force generate a new token
                    new_token = get_access_token(force_refresh=True)
                    
                    # Retry the request with the new token (only retry once to avoid infinite loops)
                    return send_to_aep(event_data, new_token, retry_attempt=1)
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                logger.error(f"Error parsing 401 response: {str(e)}")
                # Continue with normal error handling if we can't parse the response
        
        # For all other cases, proceed as normal
        response.raise_for_status()
        logger.info(f"Successfully sent event to AEP: {response.status_code}")
        
        try:
            return response.json()
        except json.JSONDecodeError:
            logger.info("Response was not JSON, returning text")
            return {"responseText": response.text}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending to AEP: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        raise

def lambda_handler(event, context):
    """
    Lambda handler for processing events and forwarding to AEP
    """
    logger.info("Received event")
    
    try:
        # Handle API Gateway events
        if isinstance(event, dict) and 'body' in event:
            try:
                if event['body']:
                    # If body is a string (which it should be from API Gateway), parse it
                    if isinstance(event['body'], str):
                        event = json.loads(event['body'])
                    else:
                        event = event['body']
            except json.JSONDecodeError as e:
                logger.error(f"Could not parse event body as JSON: {str(e)}")
                return {
                    'statusCode': 400,
                    'body': json.dumps({'message': 'Invalid JSON in request body'})
                }
        
        # Get access token
        try:
            access_token = get_access_token()
        except Exception as e:
            logger.error(f"Failed to get access token: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Failed to authenticate with Adobe API'})
            }
        
        # Send event to AEP
        try:
            aep_response = send_to_aep(event, access_token)
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Event successfully forwarded to AEP',
                    'aepResponse': aep_response
                })
            }
        except Exception as e:
            logger.error(f"Failed to send event to AEP: {str(e)}")
            return {
                'statusCode': 502,
                'body': json.dumps({'message': 'Failed to send event to Adobe Experience Platform'})
            }
    
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error processing event: {str(e)}'})
        }