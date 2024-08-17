from flask import Flask, request, jsonify
from collections import defaultdict
import requests
import json
import os
import base64
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime, timedelta
import time
from predict import predict_calories
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
        'client_secret': client_secret,
        'scope': 'activity nutrition heartrate location nutrition profile settings sleep social weight',
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
    elif method.lower() == 'delete':
        response = requests.delete(url, headers=headers, json=data)
    if response.status_code == 401:  # Token expired
        access_token, refresh_token = refresh_access_token(refresh_token)
        if not access_token or not refresh_token:
            return {'error': 'Failed to refresh token.'}, 401

        headers['Authorization'] = f'Bearer {access_token}'
        if method.lower() == 'get':
            response = requests.get(url, headers=headers, params=params)
        elif method.lower() == 'post':
            response = requests.post(url, headers=headers, json=data)

    if method.lower() == 'delete':
        res = response
    else:
        res = response.json()
    return res, response.status_code

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

@app.route('/api/delete_food/<log_id>', methods=['DELETE'])
def delete_food(log_id):
    food_logs = []
    url = f"https://api.fitbit.com/1/user/-/foods/log/{log_id}.json"
    response, status_code = make_api_request(url, method='delete')
    # 204 is the status code for successful deletion
    if status_code != 204: 
        return jsonify({'error': 'Unable to delete food'}), status_code
    return jsonify({'message': 'Deleted food successfully.'}), 201


@app.route('/api/activity/<activity_period>', methods=['GET'])
def get_activity(activity_period = '1y'):
    start_time = time.time()  # Start time tracking
    
    before_date = request.args.get("before_date")
    if not before_date:
        raise Exception("Please provide the before_date parameter.")

    # Fetch data from various endpoints
    steps_start = time.time()
    steps_response, _ = make_api_request(f"https://api.fitbit.com/1/user/-/activities/steps/date/{before_date}/{activity_period}.json")
    steps_duration = time.time() - steps_start
    print(f"Time taken for steps data: {steps_duration:.4f} seconds")

    activity_calories_start = time.time()
    activity_calories_response, _ = make_api_request(f"https://api.fitbit.com/1/user/-/activities/calories/date/{before_date}/{activity_period}.json")
    activity_calories_duration = time.time() - activity_calories_start
    print(f"Time taken for activity calories data: {activity_calories_duration:.4f} seconds")

    activity_zone_minutes_start = time.time()
    activity_zone_minutes_response, _ = make_api_request(f"https://api.fitbit.com/1/user/-/activities/heart/date/{before_date}/{activity_period}.json")
    activity_zone_minutes_duration = time.time() - activity_zone_minutes_start
    print(f"Time taken for activity zone minutes data: {activity_zone_minutes_duration:.4f} seconds")

    minutes_very_active_start = time.time()
    minutes_very_active_response, _ = make_api_request(f"https://api.fitbit.com/1/user/-/activities/minutesVeryActive/date/{before_date}/{activity_period}.json")
    minutes_very_active_duration = time.time() - minutes_very_active_start
    print(f"Time taken for very active minutes data: {minutes_very_active_duration:.4f} seconds")

    minutes_fairly_active_start = time.time()
    minutes_fairly_active_response, _ = make_api_request(f"https://api.fitbit.com/1/user/-/activities/minutesFairlyActive/date/{before_date}/{activity_period}.json")
    minutes_fairly_active_duration = time.time() - minutes_fairly_active_start
    print(f"Time taken for fairly active minutes data: {minutes_fairly_active_duration:.4f} seconds")

    # Parse the responses
    parse_start = time.time()
    steps_data = steps_response.get('activities-steps', [])
    activity_calories_data = activity_calories_response.get('activities-calories', [])
    activity_zone_minutes_data = activity_zone_minutes_response.get('activities-heart', [])
    minutes_very_active_data = minutes_very_active_response.get('activities-minutesVeryActive', [])
    # print(f'minutes_very_active_data: {minutes_very_active_data[-2]}')
    minutes_fairly_active_data = minutes_fairly_active_response.get('activities-minutesFairlyActive', [])
    # print(f'minutesFairlyActive: {minutes_fairly_active_data[-2]}')
    parse_duration = time.time() - parse_start
    print(f"Time taken to parse the data: {parse_duration:.4f} seconds")

    # Combine the data
    combine_start = time.time()
    combined_data = []
    for i in range(len(steps_data)):
        
        date = steps_data[i]['dateTime']
        steps = int(steps_data[i]['value'])
        activity_calories = int(activity_calories_data[i]['value'])
        activity_zone_data = activity_zone_minutes_data[i]['value']['heartRateZones']
        # Initialize variables to hold the minutes for each zone
        fat_burn_minutes = 0
        cardio_minutes = 0
        peak_minutes = 0
        # calc zone data
        for datum in activity_zone_data:
            if datum['name'] == 'Fat Burn':
                fat_burn_minutes = datum['minutes']
            elif datum['name'] == 'Cardio':
                cardio_minutes = datum['minutes'] * 2
            elif datum['name'] == 'Peak':
                peak_minutes = datum['minutes'] * 2
            zone_activity_minutes = fat_burn_minutes + cardio_minutes + peak_minutes

        combined_data.append({
            'dateTime': date,
            'steps': steps,
            'activityCalories': activity_calories,
            'zoneActivityMinutes': zone_activity_minutes,
        })
    combine_duration = time.time() - combine_start
    print(f"Time taken to combine the data: {combine_duration:.4f} seconds")

    total_duration = time.time() - start_time  # End time tracking
    print(f"Total time taken for the request: {total_duration:.4f} seconds")
    print(combined_data)
    return jsonify(combined_data), 200

@app.route('/api/predict/calories/<steps>/<activity_minutes>', methods=['POST'])
def post_predict_calories(steps, activity_minutes):
    data = request.json
    predict = predict_calories(data, steps, activity_minutes)
    return jsonify(predict), 200

if __name__ == '__main__':
    app.run(debug=True)
