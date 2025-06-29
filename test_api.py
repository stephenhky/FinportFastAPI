import os
import requests
from requests_aws4auth import AWS4Auth
import boto3

# --- Configuration ---
# Replace with your API Gateway endpoint URL
# For example: 'https://xxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod'
API_GATEWAY_URL = os.environ.get('API_GATEWAY_URL', 'YOUR_API_GATEWAY_URL')

# AWS Credentials and Region
# If you are running this script from a machine with configured AWS CLI,
# boto3 will automatically use your default credentials and region.
# Otherwise, you can specify them here.
# For example, if you are using environment variables:
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
# AWS_SESSION_TOKEN = os.environ.get('AWS_SESSION_TOKEN') # Optional, for temporary credentials
# AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# If you need to manually specify credentials, uncomment and set these variables
# AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY_ID"
# AWS_SECRET_ACCESS_KEY = "YOUR_AWS_SECRET_ACCESS_KEY"
# AWS_REGION = "us-east-1"

# --- End of Configuration ---

def get_aws_auth():
    """
    Creates an AWS4Auth object for signing requests.
    It uses boto3 to find credentials in the standard locations
    (environment variables, ~/.aws/credentials, IAM role).
    """
    session = boto3.Session()
    credentials = session.get_credentials()
    
    if credentials is None:
        raise Exception("AWS credentials not found. Please configure your AWS CLI or set environment variables.")

    aws_auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        session.region_name or 'us-east-1',
        'execute-api',
        session_token=credentials.token
    )
    return aws_auth

def call_api():
    """
    Calls the API Gateway endpoint with AWSv4 signature authentication.
    """
    if API_GATEWAY_URL == 'YOUR_API_GATEWAY_URL':
        print("Please configure your API_GATEWAY_URL in the script or as an environment variable.")
        return

    try:
        auth = get_aws_auth()
        endpoint = f"{API_GATEWAY_URL}/"  # Calling the root/health check endpoint
        
        print(f"Calling endpoint: {endpoint}")
        
        response = requests.get(endpoint, auth=auth)
        
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(response.json())

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    call_api()