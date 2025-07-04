import os
import requests
import json
import base64
from dotenv import load_dotenv

# get env variables
load_dotenv()
client_id = os.getenv('CLIENTID')
client_secret = os.getenv('CLIENTSECRET')

basic_token = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

def load_token(file_path, osvar):
    # osvar is used 
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return os.getenv('CLIENTID') or None

def save_token(file_path, token):
    with open(file_path, 'w') as file:
        json.dump(token, file)

# Function to refresh the access token
def refresh_access_token(refresh_token):
    url = "https://api.fitbit.com/oauth2/token"
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }
    # note that we need to use the base token which should never expire
    headers = {
        'Authorization': f'Basic {basic_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, data=payload, headers=headers)
    # if success, save new tokens
    if response.status_code == 200:
        new_tokens = response.json()
        save_token('access_token.json', {'access_token': new_tokens['access_token']})
        save_token('refresh_token.json', {'refresh_token': new_tokens['refresh_token']})
        return new_tokens['access_token'], new_tokens['refresh_token']
    else:
        print("Failed to refresh token:", response.json())
        return None, None

# load token data from json files
access_token_data = load_token('access_token.json', 'ACCESSTOKEN')
refresh_token_data = load_token('refresh_token.json', 'REFRESHTOKEN')

# load tokens
access_token = access_token_data['access_token']
refresh_token = refresh_token_data['refresh_token']

def make_fitbit_api_request(url, method='GET', headers=None, data=None, description=''):
    """
    Centralized function to make Fitbit API requests with rate limiting logging
    """
    global access_token, refresh_token
    
    if headers is None:
        headers = {}
    
    # Add authorization header
    headers['Authorization'] = f'Bearer {access_token}'
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
    
    # Make the request
    if method.upper() == 'GET':
        response = requests.get(url, headers=headers)
    elif method.upper() == 'POST':
        response = requests.post(url, headers=headers, data=data)
    elif method.upper() == 'PUT':
        response = requests.put(url, headers=headers, data=data)
    elif method.upper() == 'DELETE':
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    # Log rate limiting information
    rate_limit = response.headers.get('Fitbit-Rate-Limit-Limit')
    rate_remaining = response.headers.get('Fitbit-Rate-Limit-Remaining')
    rate_reset = response.headers.get('Fitbit-Rate-Limit-Reset')
    
    print(f"[Fitbit API] {description}")
    print(f"  Rate limit: {rate_limit}")
    print(f"  Remaining: {rate_remaining}")
    print(f"  Reset time: {rate_reset}")
    print(f"  Status: {response.status_code}")
    
    # Handle different response status codes
    if response.status_code in [200, 201, 204]:
        if response.status_code == 204:  # No content for DELETE
            return True
        return response.json()
    elif response.status_code == 401:
        # Token expired, try to refresh
        print(f"[Fitbit API] Token expired, attempting refresh...")
        access_token, refresh_token = refresh_access_token(refresh_token)
        if access_token and refresh_token:
            # Retry the request with new token
            headers['Authorization'] = f'Bearer {access_token}'
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, data=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            # Log rate limiting info for retry
            rate_limit = response.headers.get('Fitbit-Rate-Limit-Limit')
            rate_remaining = response.headers.get('Fitbit-Rate-Limit-Remaining')
            rate_reset = response.headers.get('Fitbit-Rate-Limit-Reset')
            
            print(f"[Fitbit API] Retry {description}")
            print(f"  Rate limit: {rate_limit}")
            print(f"  Remaining: {rate_remaining}")
            print(f"  Reset time: {rate_reset}")
            print(f"  Status: {response.status_code}")
            
            if response.status_code in [200, 201, 204]:
                if response.status_code == 204:
                    return True
                return response.json()
    
    # If we get here, the request failed
    print(f"[Fitbit API] Request failed: {response.status_code} - {response.text}")
    return None

query = input("Enter the food item to search for: ")
result = make_fitbit_api_request(
    f'https://api.fitbit.com/1/foods/search.json?query={query}',
    method='GET',
    description="searching foods"
)

if result:
    for food in result['foods']:
        print(f"Name: {food['name']} - ID: {food['foodId']} - Brand: {food['brand']} - Calories: {food['calories']} - Units: {food['units']}")
else:
    print("Error searching for foods")
