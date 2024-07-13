from flask import Flask, request, jsonify
import requests
import json
import os
import base64
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()
client_id = os.getenv('CLIENTID')
client_secret = os.getenv('CLIENTSECRET')

basic_token = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

def load_token(file_path, osvar):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return os.getenv(osvar) or None

def save_token(file_path, token):
    with open(file_path, 'w') as file:
        json.dump(token, file)

# Load token data from json files
access_token = load_token('access_token.json', 'ACCESSTOKEN')['access_token']
refresh_token = load_token('refresh_token.json', 'REFRESHTOKEN')['refresh_token']

# todo how do we ask users to do this
# todo might be easier to ask for this on the frontend
if not access_token or not refresh_token:
    raise Exception("Tokens are missing. Please provide valid access and refresh tokens.")

def refresh_access_token(refresh_token):
    url = "https://api.fitbit.com/oauth2/token"
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }
    headers = {
        'Authorization': f'Basic {basic_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        new_tokens = response.json()
        save_token('access_token.json', {'access_token': new_tokens['access_token']})
        save_token('refresh_token.json', {'refresh_token': new_tokens['refresh_token']})
        return new_tokens['access_token'], new_tokens['refresh_token']
    else:
        return None, None

@app.route('/api/log_food', methods=['POST'])
def log_food():
    global access_token, refresh_token
    # todo is this coming from the request body
    entry = request.json
    response = requests.post(
        f"https://api.fitbit.com/1/user/-/foods/log.json?foodId={entry['foodId']}&mealTypeId={entry['mealTypeId']}&unitId={entry['unitId']}&amount={entry['amount']}&date={entry['date']}",
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    )
    if response.status_code == 201:
        return jsonify({'message': f"Logged food {entry['name']} successfully."}), 201
    elif response.status_code == 401:  # Unauthorized, token might be expired
        access_token, refresh_token = refresh_access_token(refresh_token)
        if access_token and refresh_token:
            response = requests.post(
                f"https://api.fitbit.com/1/user/-/foods/log.json?foodId={entry['foodId']}&mealTypeId={entry['mealTypeId']}&unitId={entry['unitId']}&amount={entry['amount']}&date={entry['date']}",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
            )
            if response.status_code == 201:
                return jsonify({'message': f"Logged food {entry['name']} successfully after refreshing token."}), 201
            else:
                return jsonify({'error': response.json()}), response.status_code
        else:
            return jsonify({'error': 'Failed to refresh token.'}), 401
    else:
        return jsonify({'error': response.json()}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
