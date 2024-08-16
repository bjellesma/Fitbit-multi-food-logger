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

# load meals data from json file
with open('meals.json') as f:
    meals_data = json.load(f)

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

def make_api_request(url, method='get', headers=None, data=None, params=None):
    """
    Makes an API request and refreshes the token if necessary.
    """
    global access_token, refresh_token
    if not headers:
        headers = {}
    headers['Authorization'] = f'Bearer {access_token}'

    if method.lower() == 'get':
        response = requests.get(url, headers=headers, params=params)
    elif method.lower() == 'post':
        response = requests.post(url, headers=headers, json=data)

    if response.status_code == 401:  # Token expired
        access_token, refresh_token = refresh_access_token(refresh_token)
        if not access_token or not refresh_token:
            return {'error': 'Failed to refresh token.'}, 401

        headers['Authorization'] = f'Bearer {access_token}'
        if method.lower() == 'get':
            response = requests.get(url, headers=headers, params=params)
        elif method.lower() == 'post':
            response = requests.post(url, headers=headers, json=data)

    return response.json(), response.status_code

@app.route('/api/searchfoods/<query>', methods=['GET'])
def search_foods(query):
    url = f'https://api.fitbit.com/1/foods/search.json?query={query}'
    response, status_code = make_api_request(url)
    return jsonify(response), status_code

@app.route('/api/getmeal/<meal_id>', methods=['GET'])
def get_meal(meal_id):
    meal_id_str = str(meal_id)
    if meal_id_str in meals_data:
        return jsonify(meals_data[meal_id_str]), 200
    else:
        return jsonify({'error': 'Meal not found'}), 404

@app.route('/api/foodLogs/<date>', methods=['GET'])
def get_food_logs(date):
    data = request.args.get("data")
    url = f"https://api.fitbit.com/1/user/-/foods/log/date/{date}.json"
    response, status_code = make_api_request(url)
    if data == "summary":
        return jsonify(response.get('summary', {})), status_code
    return jsonify(response), status_code

@app.route('/api/log_food', methods=['POST'])
def log_food():
    entries = request.json
    food_logs = []
    for entry in entries:
        url = f"https://api.fitbit.com/1/user/-/foods/log.json?foodId={entry['foodId']}&mealTypeId={entry['mealTypeId']}&unitId={entry['unitId']}&amount={entry['amount']}&date={entry['date']}"
        response, status_code = make_api_request(url, method='post')
        if status_code != 201:
            return jsonify({'error': response}), status_code
        food_logs.append(response['foodLog'])
    return jsonify({'message': 'Logged food successfully.', 'food': food_logs}), 201

if __name__ == '__main__':
    app.run(debug=True)
