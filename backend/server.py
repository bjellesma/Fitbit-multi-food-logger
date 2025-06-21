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
    print(f"DEBUG: Loading token from {file_path}")
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            token_data = json.load(file)
            print(f"DEBUG: Loaded token data from {file_path}: {token_data}")
            return token_data
    print(f"DEBUG: File {file_path} not found, checking environment variable {osvar}")
    return os.getenv(osvar) or None

def save_token(file_path, token):
    print(f"DEBUG: Saving token to {file_path}: {token}")
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
    print(f"DEBUG: Attempting to refresh access token...")
    print(f"DEBUG: Using refresh_token (first 20 chars): {refresh_token[:20] if refresh_token else 'None'}...")
    print(f"DEBUG: Client ID: {client_id}")
    print(f"DEBUG: Client Secret: {client_secret[:10] if client_secret else 'None'}...")
    
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
    
    print(f"DEBUG: Refresh request URL: {url}")
    print(f"DEBUG: Refresh request payload: {payload}")
    print(f"DEBUG: Refresh request headers: {headers}")
    
    response = requests.post(url, data=payload, headers=headers)
    print(f"DEBUG: Refresh response status: {response.status_code}")
    print(f"DEBUG: Refresh response body: {response.text}")
    
    if response.status_code == 200:
        new_tokens = response.json()
        print(f"DEBUG: Successfully got new tokens: {new_tokens}")
        save_token('access_token.json', {'access_token': new_tokens['access_token']})
        save_token('refresh_token.json', {'refresh_token': new_tokens['refresh_token']})
        return new_tokens['access_token'], new_tokens['refresh_token']
    else:
        print(f"DEBUG: Token refresh failed with status {response.status_code}")
        return None, None

@app.route('/api/log_food', methods=['POST'])
def log_food():
    global access_token, refresh_token
    
    # Get request data
    data = request.json
    meal = int(data.get('meal', 0))
    meal_type = int(data.get('mealType', 0))
    date_option = int(data.get('dateOption', 1))
    
    # Calculate date based on option
    if date_option == 1:
        current_date = datetime.now().strftime('%Y-%m-%d')
    elif date_option == 2:
        current_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    elif date_option == 3:
        current_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    elif date_option == 4:
        current_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    else:
        current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Define the meals dictionary (same as log_food.py)
    meals = {
        1: [
            {
                "name": 'Protein Shake',
                "foodId": 22788636, # Protein Shake
                "mealTypeId": meal_type,
                "unitId": 301,    # Packets
                "amount": 2,
                "date": current_date
            },
            {
                "name": 'Milk (1%)',
                "foodId": 692771571, # Milk (1%)
                "mealTypeId": meal_type,
                "unitId": 91,    # Cups
                "amount": 2,
                "date": current_date
            },
        ],
        2: [
            {
                "name": 'Oatmeal',
                "foodId": 692777712, # Oatmeal
                "mealTypeId": meal_type,
                "unitId": 229,    # Packets
                "amount": 2,
                "date": current_date
            },
            {
                "name": 'Raisins',
                "foodId": 692772145, # Raisins
                "mealTypeId": meal_type,
                "unitId": 91,    # Cups
                "amount": .5,
                "date": current_date
            },
            {
                "name": 'Unsweetened Applesauce',
                "foodId": 692772244, # Unsweetened Applesauce
                "mealTypeId": meal_type,
                "unitId": 91,    # Cups
                "amount": 1.5,
                "date": current_date
            },
        ],
        3: [
            {
                "name": 'Zero Sugar Yogurt',
                "foodId": 804204232,
                "mealTypeId": meal_type,
                "unitId": 69,    # Container
                "amount": 1,
                "date": current_date
            },
            {
                "name": 'blueberries',
                "foodId": 82547,
                "mealTypeId": meal_type,
                "unitId": 91,    # Cups
                "amount": .33,
                "date": current_date
            }
        ],
        4: [
            {
                "name": 'Grapes',
                "foodId": 751876808,
                "mealTypeId": meal_type,
                "unitId": 148,    # Grapes
                "amount": 15,
                "date": current_date
            },
            {
                "name": 'Carrots',
                "foodId": 784706037,
                "mealTypeId": meal_type,
                "unitId": 226,    # oz
                "amount": 6,
                "date": current_date
            },
        ],
        5: [
            {
                "name": 'Soylent',
                "foodId": 761395165,
                "mealTypeId": meal_type,
                "unitId": 27,    # Container
                "amount": 1,
                "date": current_date
            },
        ],
        6: [
            {
                "name": 'Protein Bar',
                "foodId": 725735405,
                "mealTypeId": meal_type,
                "unitId": 17,    # Bar
                "amount": 1,
                "date": current_date
            },
            {
                "name": 'Banana',
                "foodId": 8100,
                "mealTypeId": meal_type,
                "unitId": 147,    # Bar
                "amount": 1,
                "date": current_date
            }
        ],
        7: [
            {
                "name": 'Pre Workout',
                "foodId": 798698937,
                "mealTypeId": meal_type,
                "unitId": 301,    # Container
                "amount": 1,
                "date": current_date
            },
        ],
        8: [
            {
                "name": 'Protein Shake',
                "foodId": 22788636, # Protein Shake
                "mealTypeId": meal_type,
                "unitId": 301,    # Packets
                "amount": 1,
                "date": current_date
            },
        ],
        9: [
            {
                "name": 'Protein Pasta',
                "foodId": 778450458,
                "mealTypeId": meal_type,
                "unitId": 226,    # Oz
                "amount": 3,
                "date": current_date
            },
            {
                "name": 'Chicken',
                "foodId": 787982016,
                "mealTypeId": meal_type,
                "unitId": 226,    # Oz
                "amount": 6,
                "date": current_date
            },
            {
                "name": 'Meat Sauce',
                "foodId": 82544,
                "mealTypeId": meal_type,
                "unitId": 91,  
                "amount": 1,
                "date": current_date
            },
            {
                "name": 'Parmasean Cheese',
                "foodId": 752199077,
                "mealTypeId": meal_type,
                "unitId": 364,    # Tsp
                "amount": 5,
                "date": current_date
            },
            {
                "name": 'Brocolli',
                "foodId": 82945,
                "mealTypeId": meal_type,
                "unitId": 304,    # Oz
                "amount": 1,
                "date": current_date
            },
        ],
    }
    
    # Get the selected meal entries
    if meal not in meals:
        return jsonify({'error': f'Invalid meal selection: {meal}'}), 400
    
    food_entries = meals[meal]
    logged_foods = []
    failed_foods = []
    
    # Log each food item in the meal
    for entry in food_entries:
        response = requests.post(
            f"https://api.fitbit.com/1/user/-/foods/log.json?foodId={entry['foodId']}&mealTypeId={entry['mealTypeId']}&unitId={entry['unitId']}&amount={entry['amount']}&date={entry['date']}",
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
        )
        
        if response.status_code == 201:
            logged_foods.append(entry['name'])
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
                    logged_foods.append(entry['name'])
                else:
                    failed_foods.append(f"{entry['name']}: {response.json()}")
            else:
                failed_foods.append(f"{entry['name']}: Failed to refresh token")
        else:
            failed_foods.append(f"{entry['name']}: {response.json()}")
    
    # Return results
    if failed_foods:
        return jsonify({
            'message': f"Logged {len(logged_foods)} foods successfully. Failed: {len(failed_foods)}",
            'logged_foods': logged_foods,
            'failed_foods': failed_foods,
            'date': current_date
        }), 207  # Multi-status
    else:
        return jsonify({
            'message': f"Successfully logged {len(logged_foods)} foods",
            'logged_foods': logged_foods,
            'date': current_date
        }), 201

@app.route('/api/foods', methods=['GET'])
def get_foods():
    global access_token, refresh_token
    
    # Get date from query parameter, default to today
    date_param = request.args.get('date')
    if date_param:
        target_date = date_param
    else:
        target_date = datetime.now().strftime('%Y-%m-%d')
    
    def make_fitbit_request(url, description):
        """Helper function to make Fitbit API requests with token refresh handling"""
        global access_token, refresh_token
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print(f"DEBUG: Got 401 for {description}, attempting token refresh...")
            access_token, refresh_token = refresh_access_token(refresh_token)
            if access_token and refresh_token:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json()
        
        return None
    
    # Get foods logged for the date
    foods_url = f"https://api.fitbit.com/1/user/-/foods/log/date/{target_date}.json"
    foods_data = make_fitbit_request(foods_url, "foods logged")
    
    if not foods_data:
        return jsonify({'error': 'Failed to fetch foods data'}), 500
    
    # Extract and format the foods
    foods = []
    if 'foods' in foods_data:
        for food in foods_data['foods']:
            foods.append({
                'id': food.get('logId'),  # Add the log ID for deletion
                'name': food.get('loggedFood', {}).get('name', 'Unknown'),
                'mealType': food.get('loggedFood', {}).get('mealTypeId', 0),
                'amount': food.get('loggedFood', {}).get('amount', 0),
                'unit': food.get('loggedFood', {}).get('unit', {}).get('name', ''),
                'calories': food.get('loggedFood', {}).get('calories', 0),
                'time': food.get('loggedFood', {}).get('logDate', '')
            })
    
    return jsonify({
        'date': target_date,
        'foods': foods,
        'total_foods': len(foods)
    }), 200

@app.route('/api/foods/<food_log_id>', methods=['DELETE'])
def delete_food(food_log_id):
    global access_token, refresh_token
    
    def make_fitbit_request(url, description):
        """Helper function to make Fitbit API requests with token refresh handling"""
        global access_token, refresh_token
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.delete(url, headers=headers)
        
        if response.status_code == 204:  # Success for DELETE
            return True
        elif response.status_code == 401:
            print(f"DEBUG: Got 401 for {description}, attempting token refresh...")
            access_token, refresh_token = refresh_access_token(refresh_token)
            if access_token and refresh_token:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                response = requests.delete(url, headers=headers)
                if response.status_code == 204:
                    return True
        
        return False
    
    # Delete the food entry
    delete_url = f"https://api.fitbit.com/1/user/-/foods/log/{food_log_id}.json"
    success = make_fitbit_request(delete_url, "delete food")
    
    if success:
        return jsonify({'message': 'Food deleted successfully'}), 200
    else:
        return jsonify({'error': 'Failed to delete food'}), 500

@app.route('/api/units/search', methods=['GET'])
def search_units():
    global access_token, refresh_token
    
    # Get search query from request
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    def make_fitbit_request(url, description):
        """Helper function to make Fitbit API requests with token refresh handling"""
        global access_token, refresh_token
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print(f"DEBUG: Got 401 for {description}, attempting token refresh...")
            access_token, refresh_token = refresh_access_token(refresh_token)
            if access_token and refresh_token:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json()
        
        return None
    
    # Get all units from Fitbit API
    units_url = "https://api.fitbit.com/1/foods/units.json"
    units_data = make_fitbit_request(units_url, "units")
    
    if not units_data:
        return jsonify({'error': 'Failed to fetch units data'}), 500
    
    # Filter units by search query
    matching_units = []
    for unit in units_data:
        if query in unit.get('name', '').lower() or query in unit.get('plural', '').lower():
            matching_units.append({
                'id': unit.get('id'),
                'name': unit.get('name'),
                'plural': unit.get('plural')
            })
    
    return jsonify({
        'query': query,
        'units': matching_units,
        'total': len(matching_units)
    }), 200

@app.route('/api/foods/<food_log_id>', methods=['PUT'])
def update_food(food_log_id):
    global access_token, refresh_token
    
    # Get update data from request
    data = request.json
    amount = data.get('amount')
    unit_id = data.get('unitId')
    
    if amount is None or unit_id is None:
        return jsonify({'error': 'Amount and unitId are required'}), 400
    
    def make_fitbit_request(url, payload, description):
        """Helper function to make Fitbit API requests with token refresh handling"""
        global access_token, refresh_token
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.put(url, json=payload, headers=headers)
        
        if response.status_code == 200:  # Success for PUT
            return response.json()
        elif response.status_code == 401:
            print(f"DEBUG: Got 401 for {description}, attempting token refresh...")
            access_token, refresh_token = refresh_access_token(refresh_token)
            if access_token and refresh_token:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                response = requests.put(url, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()
        
        return None
    
    def find_unit_id_by_name(unit_name):
        """Helper function to find unit ID by name"""
        global access_token, refresh_token
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        units_url = "https://api.fitbit.com/1/foods/units.json"
        response = requests.get(units_url, headers=headers)
        
        if response.status_code == 200:
            units_data = response.json()
            for unit in units_data:
                if unit.get('name', '').lower() == unit_name.lower() or unit.get('plural', '').lower() == unit_name.lower():
                    return unit.get('id')
        elif response.status_code == 401:
            # Try with refreshed token
            access_token, refresh_token = refresh_access_token(refresh_token)
            if access_token and refresh_token:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                response = requests.get(units_url, headers=headers)
                if response.status_code == 200:
                    units_data = response.json()
                    for unit in units_data:
                        if unit.get('name', '').lower() == unit_name.lower() or unit.get('plural', '').lower() == unit_name.lower():
                            return unit.get('id')
        
        return None
    
    # Handle unit ID or unit name
    final_unit_id = unit_id
    if isinstance(unit_id, str) and not unit_id.isdigit():
        # It's a unit name, find the corresponding ID
        found_unit_id = find_unit_id_by_name(unit_id)
        if found_unit_id is None:
            return jsonify({'error': f'Unit "{unit_id}" not found'}), 400
        final_unit_id = found_unit_id
    
    # Update the food entry
    update_url = f"https://api.fitbit.com/1/user/-/foods/log/{food_log_id}.json"
    payload = {
        'amount': amount,
        'unitId': int(final_unit_id)
    }
    
    result = make_fitbit_request(update_url, payload, "update food")
    
    if result:
        return jsonify({'message': 'Food updated successfully', 'data': result}), 200
    else:
        return jsonify({'error': 'Failed to update food'}), 500

@app.route('/api/calories', methods=['GET'])
def get_calories():
    global access_token, refresh_token
    
    # Debug: Log current tokens
    
    # Get current date in YYYY-MM-DD format
    today = datetime.now().strftime('%Y-%m-%d')
    
    def make_fitbit_request(url, description):
        """Helper function to make Fitbit API requests with token refresh handling"""
        global access_token, refresh_token
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print(f"DEBUG: Got 401 for {description}, attempting token refresh...")
            access_token, refresh_token = refresh_access_token(refresh_token)
            if access_token and refresh_token:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json()
        
        return None
    
    # Get calories consumed
    calories_in_url = f"https://api.fitbit.com/1/user/-/foods/log/caloriesIn/date/{today}/1d.json"
    calories_in_data = make_fitbit_request(calories_in_url, "calories consumed")
    
    # Get calories burned
    calories_out_url = f"https://api.fitbit.com/1/user/-/activities/calories/date/{today}/1d.json"
    calories_out_data = make_fitbit_request(calories_out_url, "calories burned")
    
    # Extract values
    calories_consumed = 0
    if calories_in_data:
        calories_data = calories_in_data.get('foods-log-caloriesIn', [])
        if calories_data:
            calories_consumed = calories_data[0].get('value', 0)
    
    calories_burned = 0
    if calories_out_data:
        calories_data = calories_out_data.get('activities-calories', [])
        if calories_data:
            calories_burned = calories_data[0].get('value', 0)
    
    # Calculate net calories
    net_calories = int(calories_consumed) - int(calories_burned)
    
    return jsonify({
        'date': today,
        'calories_consumed': calories_consumed,
        'calories_burned': calories_burned,
        'net_calories': net_calories,
        'unit': 'calories'
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
