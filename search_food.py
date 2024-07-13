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

headers = {
    'Authorization': f'Bearer {access_token}'
}

query = input("Enter the food item to search for: ")
response = requests.get(
    f'https://api.fitbit.com/1/foods/search.json?query={query}',
    headers=headers
)

if response.status_code == 200:
    res = response.json()
    for food in res['foods']:
        print(f"Name: {food['name']} - ID: {food['foodId']} - Brand: {food['brand']} - Calories: {food['calories']} - Units: {food['units']}")
elif response.status_code == 401:
    print("Token expired, refreshing token...")
    access_token, refresh_token = refresh_access_token(refresh_token)
    if access_token and refresh_token:
        response = requests.get(
            f'https://api.fitbit.com/1/foods/search.json?query={query}',
            headers=headers
        )
        if response.status_code == 201:
            print(f"Name: {food['name']} - ID: {food['foodId']} - Brand: {food['brand']} - Calories: {food['calories']} - Units: {food['units']}")
        else:
            print(f"Error searching after refreshing token: {response.content}")
else:
    print(f"Error: {response.json()}")
