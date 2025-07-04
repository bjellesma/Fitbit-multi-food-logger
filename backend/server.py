from flask import Flask, request, jsonify
import requests
import json
import os
import base64
from dotenv import load_dotenv
from flask_cors import CORS
from flask_caching import Cache
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Configure Flask-Caching
cache_config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300  # 5 minutes default
}
app.config.from_mapping(cache_config)
cache = Cache(app)

def make_fitbit_api_request(url, method='GET', headers=None, data=None, description=''):
    """
    Centralized function to make Fitbit API requests
    after a request is made, the function will check the response headers for rate limiting information
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

def clear_food_related_caches():
    """Clear caches related to food data when food logs are modified"""
    cache.delete_memoized(get_foods_cached)
    cache.delete_memoized(get_calories)

def clear_all_caches():
    """Clear all caches - useful for debugging or when tokens are refreshed"""
    cache.clear()

# Load environment variables
load_dotenv()
client_id = os.getenv('CLIENTID')
client_secret = os.getenv('CLIENTSECRET')

basic_token = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

# Global cache for units to reduce API calls
units_cache = None
units_cache_timestamp = None
CACHE_DURATION = 3600  # Cache for 1 hour

# Global cache for food search results
food_search_cache = {}
FOOD_SEARCH_CACHE_DURATION = 300  # Cache for 5 minutes

def get_cached_units():
    """Get units from cache or fetch from API if cache is expired"""
    global units_cache, units_cache_timestamp
    
    current_time = datetime.now().timestamp()
    
    # Return cached units if still valid
    if (units_cache and units_cache_timestamp and 
        current_time - units_cache_timestamp < CACHE_DURATION):
        return units_cache
    
    # Fetch fresh units from API
    units_data = make_fitbit_api_request("https://api.fitbit.com/1/foods/units.json", method='GET', description="fetching units")
    
    if units_data:
        units_cache = units_data
        units_cache_timestamp = current_time
        return units_data
    
    return None

def load_token(file_path, osvar):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            token_data = json.load(file)
            return token_data
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
    
    # Get request data
    data = request.json
    meal = int(data.get('meal', 0))
    meal_type = int(data.get('mealType', 0))
    date_option = int(data.get('dateOption', 1))
    
    # Use provided date if available, otherwise calculate based on option
    provided_date = data.get('date')
    if provided_date:
        current_date = provided_date
    else:
        # Calculate date based on option (fallback to server timezone)
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
        url = f"https://api.fitbit.com/1/user/-/foods/log.json?foodId={entry['foodId']}&mealTypeId={entry['mealTypeId']}&unitId={entry['unitId']}&amount={entry['amount']}&date={entry['date']}"
        result = make_fitbit_api_request(url, method='POST', description=f"logging food: {entry['name']}")
        
        if result is not None:
            clear_food_related_caches()  # Clear caches since food data changed
            logged_foods.append(entry['name'])
        else:
            failed_foods.append(f"{entry['name']}: Request failed")
    
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
        # If no date provided, use server's current date (fallback)
        target_date = datetime.now().strftime('%Y-%m-%d')
    
    # Call the cached function with the date parameter
    return get_foods_cached(target_date)

@cache.memoize(timeout=300)  # Cache for 5 minutes based on function arguments
def get_foods_cached(target_date):
    global access_token, refresh_token
    
    # Get foods logged for the date
    foods_url = f"https://api.fitbit.com/1/user/-/foods/log/date/{target_date}.json"
    foods_data = make_fitbit_api_request(foods_url, method='GET', description="fetching foods logged")
    
    if not foods_data:
        return jsonify({'error': 'Failed to fetch foods data'}), 500
    
    # Extract and format the foods
    foods = []
    if 'foods' in foods_data:
        for food in foods_data['foods']:
            foods.append({
                'id': food.get('logId'),  # Add the log ID for deletion
                'foodId': food.get('loggedFood', {}).get('foodId'),
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
    
    # Delete the food entry
    delete_url = f"https://api.fitbit.com/1/user/-/foods/log/{food_log_id}.json"
    success = make_fitbit_api_request(delete_url, method='DELETE', description="deleting food")
    
    if success:
        clear_food_related_caches()  # Clear caches since food data changed
        return jsonify({'message': 'Food deleted successfully'}), 200
    else:
        return jsonify({'error': 'Failed to delete food'}), 500

@app.route('/api/units/search', methods=['GET'])
@cache.memoize(timeout=600)  # Cache for 10 minutes based on search query
def search_units():
    global access_token, refresh_token
    
    # Get search query from request
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Get all units from cache or API
    units_data = get_cached_units()
    
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
    food_id = data.get('foodId')
    meal_type_id = data.get('mealTypeId')
    date = data.get('date')
    
    if None in (amount, unit_id, food_id, meal_type_id, date):
        return jsonify({'error': 'amount, unitId, foodId, mealTypeId, and date are required'}), 400
    
    # Step 1: Delete the old food log
    delete_url = f"https://api.fitbit.com/1/user/-/foods/log/{food_log_id}.json"
    delete_success = make_fitbit_api_request(delete_url, method='DELETE', description="deleting old food log for update")
    if not delete_success:
        return jsonify({'error': 'Failed to delete old food log'}), 500
    
    # Step 2: Create a new food log
    formatted_date = date
    if date and len(date) > 10:
        formatted_date = date[:10]  # Take only the date part if it includes time
    
    create_url = f"https://api.fitbit.com/1/user/-/foods/log.json?foodId={int(food_id)}&mealTypeId={int(meal_type_id)}&unitId={int(unit_id)}&amount={float(amount)}&date={formatted_date}"
    
    create_result = make_fitbit_api_request(create_url, method='POST', description="creating new food log for update")
    if create_result is not None:
        clear_food_related_caches()  # Clear caches since food data changed
        return jsonify({'message': 'Food updated (deleted and created) successfully', 'data': create_result}), 200
    else:
        return jsonify({'error': 'Failed to create new food log'}), 500

@app.route('/api/calories', methods=['GET'])
@cache.memoize(timeout=300)  # Cache for 5 minutes based on function arguments (days parameter)
def get_calories():
    global access_token, refresh_token
    
    # Get number of days from query parameter, default to 7
    days = int(request.args.get('days', 7))
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days-1)
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    # Fetch calories in and burned for the range
    calories_in_url = f"https://api.fitbit.com/1/user/-/foods/log/caloriesIn/date/{start_str}/{end_str}.json"
    calories_in_data = make_fitbit_api_request(calories_in_url, method='GET', description=f"calories consumed from {start_str} to {end_str}")
    print(f"DEBUG: calories_in_data for {start_str} to {end_str}: {calories_in_data}")
    
    calories_out_url = f"https://api.fitbit.com/1/user/-/activities/calories/date/{start_str}/{end_str}.json"
    calories_out_data = make_fitbit_api_request(calories_out_url, method='GET', description=f"calories burned from {start_str} to {end_str}")
    print(f"DEBUG: calories_out_data for {start_str} to {end_str}: {calories_out_data}")
    
    # Build a date-indexed dict for calories in
    calories_in_dict = {}
    if calories_in_data and isinstance(calories_in_data, dict):
        for entry in calories_in_data.get('foods-log-caloriesIn', []):
            calories_in_dict[entry.get('dateTime')] = entry.get('value', 0)
    
    # Build a date-indexed dict for calories burned
    calories_out_dict = {}
    if calories_out_data and isinstance(calories_out_data, dict):
        for entry in calories_out_data.get('activities-calories', []):
            calories_out_dict[entry.get('dateTime')] = entry.get('value', 0)
    
    # Build the result for each day in the range
    calories_data = []
    for i in range(days):
        target_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        calories_consumed = calories_in_dict.get(target_date, 0)
        calories_burned = calories_out_dict.get(target_date, 0)
        net_calories = int(calories_consumed) - int(calories_burned)
        calories_data.append({
            'date': target_date,
            'calories_consumed': calories_consumed,
            'calories_burned': calories_burned,
            'net_calories': net_calories
        })
    
    return jsonify({
        'days': days,
        'data': calories_data,
        'unit': 'calories'
    }), 200

@app.route('/api/foods/search', methods=['GET'])
@cache.memoize(timeout=300)  # Cache for 5 minutes based on search query
def search_foods():
    global access_token, refresh_token, food_search_cache
    
    # Get search query from request
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Check cache first
    current_time = datetime.now().timestamp()
    if query in food_search_cache:
        cached_data, cache_time = food_search_cache[query]
        if current_time - cache_time < FOOD_SEARCH_CACHE_DURATION:
            return jsonify({
                'query': query,
                'foods': cached_data,
                'total': len(cached_data),
                'cached': True
            }), 200
    
    # Search for foods using Fitbit API
    foods_url = f"https://api.fitbit.com/1/foods/search.json?query={query}"
    foods_data = make_fitbit_api_request(foods_url, method='GET', description="searching foods")
    
    if not foods_data:
        return jsonify({'error': 'Failed to fetch foods data'}), 500
    
    # Extract and format the foods
    foods = []
    if 'foods' in foods_data:
        # Get cached units once for all foods
        all_units = get_cached_units()
        units_map = {}
        if all_units:
            units_map = {unit['id']: unit for unit in all_units}
        
        for food in foods_data['foods']:
            # Get unit details for this food using cached data
            unit_details = []
            if 'units' in food and units_map:
                for unit_id in food['units']:
                    if unit_id in units_map:
                        unit_details.append({
                            'id': unit_id,
                            'name': units_map[unit_id]['name']
                        })
            
            foods.append({
                'id': food.get('foodId'),
                'name': food.get('name', 'Unknown'),
                'brand': food.get('brand', ''),
                'calories': food.get('calories', 0),
                'units': unit_details
            })
    
    # Cache the results
    food_search_cache[query] = (foods, current_time)
    
    return jsonify({
        'query': query,
        'foods': foods,
        'total': len(foods)
    }), 200

@app.route('/api/log_food_batch', methods=['POST'])
def log_food_batch():
    global access_token, refresh_token
    
    # Get request data
    data = request.json
    foods = data.get('foods', [])  # Array of food objects
    date_option = data.get('dateOption', 1)
    
    if not foods:
        return jsonify({'error': 'No foods provided'}), 400
    
    # Use provided date if available, otherwise calculate based on option
    provided_date = data.get('date')
    if provided_date:
        current_date = provided_date
    else:
        # Calculate date based on option (fallback to server timezone)
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
    
    logged_foods = []
    failed_foods = []
    
    # Log each food item in the batch
    for food in foods:
        food_id = food.get('foodId')
        meal_type = food.get('mealTypeId', 1)
        unit_id = food.get('unitId')
        amount = food.get('amount')
        
        if not all([food_id, unit_id, amount]):
            failed_foods.append(f"Invalid food data: {food}")
            continue
        
        url = f"https://api.fitbit.com/1/user/-/foods/log.json?foodId={food_id}&mealTypeId={meal_type}&unitId={unit_id}&amount={amount}&date={current_date}"
        result = make_fitbit_api_request(url, method='POST', description=f"logging batch food: {food.get('name', f'Food {food_id}')}")
        
        if result is not None:
            clear_food_related_caches()  # Clear caches since food data changed
            logged_foods.append(food.get('name', f'Food {food_id}'))
        else:
            failed_foods.append(f"{food.get('name', f'Food {food_id}')}: Request failed")
    
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

@app.route('/api/log_individual_food', methods=['POST'])
def log_individual_food():
    global access_token, refresh_token
    
    # Get request data
    data = request.json
    food_id = data.get('foodId')
    meal_type = data.get('mealTypeId', 1)
    unit_id = data.get('unitId')
    amount = data.get('amount')
    date_option = data.get('dateOption', 1)
    
    if not all([food_id, unit_id, amount]):
        return jsonify({'error': 'foodId, unitId, and amount are required'}), 400
    
    # Use provided date if available, otherwise calculate based on option
    provided_date = data.get('date')
    if provided_date:
        current_date = provided_date
    else:
        # Calculate date based on option (fallback to server timezone)
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
    
    # Log the individual food
    url = f"https://api.fitbit.com/1/user/-/foods/log.json?foodId={food_id}&mealTypeId={meal_type}&unitId={unit_id}&amount={amount}&date={current_date}"
    result = make_fitbit_api_request(url, method='POST', description="logging individual food")
    
    if result is not None:
        clear_food_related_caches()  # Clear caches since food data changed
        return jsonify({
            'message': 'Food logged successfully',
            'data': result
        }), 201
    else:
        return jsonify({'error': 'Failed to log food'}), 500

@app.route('/api/weight', methods=['GET'])
@cache.cached(timeout=300, key_prefix='weight')  # Cache for 5 minutes
def get_weight():
    global access_token, refresh_token
    
    # Get number of days from query parameter, default to 7
    days = int(request.args.get('days', 7))
    
    # Get weight data for the specified number of days
    weight_data = []
    
    for i in range(days):
        # Calculate date for each day (0 = today, 1 = yesterday, etc.)
        target_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # Get weight for this date
        weight_url = f"https://api.fitbit.com/1/user/-/body/log/weight/date/{target_date}/1d.json"
        weight_response = make_fitbit_api_request(weight_url, method='GET', description=f"weight for {target_date}")
        
        weight_value = None
        if weight_response and isinstance(weight_response, dict):
            weight_list = weight_response.get('weight', [])
            if weight_list:
                weight_value = weight_list[0].get('value', None)
        
        weight_data.append({
            'date': target_date,
            'weight': weight_value
        })
    
    # Reverse the list so most recent date is last
    weight_data.reverse()
    
    return jsonify({
        'days': days,
        'data': weight_data
    }), 200

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear all caches - useful for debugging or when data is stale"""
    try:
        clear_all_caches()
        return jsonify({'message': 'All caches cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to clear caches: {str(e)}'}), 500

@app.route('/api/cache/status', methods=['GET'])
def cache_status():
    """Get cache status information"""
    try:
        # This is a simple status check - in a real implementation you might want more details
        return jsonify({
            'message': 'Cache is active',
            'cache_type': app.config.get('CACHE_TYPE', 'Unknown'),
            'default_timeout': app.config.get('CACHE_DEFAULT_TIMEOUT', 'Unknown')
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get cache status: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
