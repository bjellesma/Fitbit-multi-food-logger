import requests
import json
import os
import base64
from dotenv import load_dotenv
from datetime import datetime

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

# load token data from json files
access_token_data = load_token('access_token.json', 'ACCESSTOKEN')
refresh_token_data = load_token('refresh_token.json', 'REFRESHTOKEN')

# load tokens
access_token = access_token_data['access_token']
refresh_token = refresh_token_data['refresh_token']

if not access_token or not refresh_token:
    raise Exception("Tokens are missing. Please provide valid access and refresh tokens.")

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

def create_food(entry, access_token=access_token):
    return requests.post(
        f"https://api.fitbit.com/1/user/-/foods/log.json?foodId={entry['foodId']}&mealTypeId={entry['mealTypeId']}&unitId={entry['unitId']}&amount={entry['amount']}&date={entry['date']}",
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    )

# Get the current date in yyyy-MM-dd format
current_date = datetime.now().strftime('%Y-%m-%d')

food_entries = []
# Prompt the user for meal and meal type, converting the input to integers
meal = int(input("What do you want to add?\n 1=morning shake \n 2=oatmeal pie\n 3=Yogurt \n 4=Grapes/Carrots \n 5=Soylent \n 6=Granola \n 7=Preworkout \n 8=Post workout \n 9=Chicken and Pasta \n >"))
meal_type = int(input("When did you eat this?\n 1=Breakfast \n 2=morning shake \n 3=Lunch\n 4=Afternoon Snack \n 5=Dinner \n >"))

# Define the meals in a dictionary
meals = {
    1: [
        {
            "name": 'Protein Shake',
            "foodId": 22788636, # Protein Shake
            "mealTypeId": meal_type,
            "unitId": 301,    # Packets
            "amount": 2,
            "date": current_date  # Use the current date
        },
        {
            "name": 'Milk (1%)',
            "foodId": 692771571, # Milk (1%)
            "mealTypeId": meal_type,
            "unitId": 91,    # Cups
            "amount": 2,
            "date": current_date  # Use the current date
        },
    ],
    2: [
        {
            "name": 'Oatmeal',
            "foodId": 692777712, # Oatmeal
            "mealTypeId": meal_type,
            "unitId": 229,    # Packets
            "amount": 2,
            "date": current_date  # Use the current date
        },
        {
            "name": 'Raisins',
            "foodId": 692772145, # Raisins
            "mealTypeId": meal_type,
            "unitId": 91,    # Cups
            "amount": .5,
            "date": current_date  # Use the current date
        },
        {
            "name": 'Unsweetened Applesauce',
            "foodId": 692772244, # Unsweetened Applesauce
            "mealTypeId": meal_type,
            "unitId": 91,    # Cups
            "amount": 1.5,
            "date": current_date  # Use the current date
        },
    ],
    3: [
        {
            "name": 'Zero Sugar Yogurt',
            "foodId": 804204232,
            "mealTypeId": meal_type,
            "unitId": 69,    # Container
            "amount": 1,
            "date": current_date  # Use the current date
        },
    ],
    4: [
        {
            "name": 'Grapes',
            "foodId": 751876808,
            "mealTypeId": meal_type,
            "unitId": 148,    # Grapes
            "amount": 15,
            "date": current_date  # Use the current date
        },
        {
            "name": 'Carrots',
            "foodId": 784706037,
            "mealTypeId": meal_type,
            "unitId": 226,    # oz
            "amount": 6,
            "date": current_date  # Use the current date
        },
    ],
    5: [
        {
            "name": 'Soylent',
            "foodId": 761395165,
            "mealTypeId": meal_type,
            "unitId": 27,    # Container
            "amount": 1,
            "date": current_date  # Use the current date
        },
    ],
    6: [
        {
            "name": 'Protein Bar',
            "foodId": 725735405,
            "mealTypeId": meal_type,
            "unitId": 17,    # Bar
            "amount": 1,
            "date": current_date  # Use the current date
        },
    ],
    7: [
        {
            "name": 'Pre Workout',
            "foodId": 798698937,
            "mealTypeId": meal_type,
            "unitId": 301,    # Container
            "amount": 1,
            "date": current_date  # Use the current date
        },
    ],
    8: [
        {
            "name": 'Protein Shake',
            "foodId": 22788636, # Protein Shake
            "mealTypeId": meal_type,
            "unitId": 301,    # Packets
            "amount": 1,
            "date": current_date  # Use the current date
        },
    ],
    9: [
        {
            "name": 'Protein Pasta',
            "foodId": 778450458,
            "mealTypeId": meal_type,
            "unitId": 226,    # Oz
            "amount": 3,
            "date": current_date  # Use the current date
        },
        {
            "name": 'Chicken',
            "foodId": 787982016,
            "mealTypeId": meal_type,
            "unitId": 226,    # Oz
            "amount": 6,
            "date": current_date  # Use the current date
        },
        {
            "name": 'Meat Sauce',
            "foodId": 82544,
            "mealTypeId": meal_type,
            "unitId": 91,  
            "amount": 1,
            "date": current_date  # Use the current date
        },
        {
            "name": 'Parmasean Cheese',
            "foodId": 752199077,
            "mealTypeId": meal_type,
            "unitId": 364,    # Tsp
            "amount": 5,
            "date": current_date  # Use the current date
        },
        {
            "name": 'Brocolli',
            "foodId": 82945,
            "mealTypeId": meal_type,
            "unitId": 304,    # Oz
            "amount": 1,
            "date": current_date  # Use the current date
        },
    ],
}

# Add the selected meal to the food entries
if meal in meals:
    food_entries.extend(meals[meal])
else:
    print(f'Input not recognized. Exiting.')
for entry in food_entries:
    # Print the request data for debugging
    response = create_food(entry=entry)
    if response.status_code == 201:
        print(f"Logged food {entry['name']} successfully.")
    elif response.status_code == 401:  # Unauthorized, token might be expired
        print("Token expired, refreshing token...")
        access_token, refresh_token = refresh_access_token(refresh_token)
        if access_token and refresh_token:
            response = create_food(entry=entry, access_token=access_token)
            if response.status_code == 201:
                print(f"Logged food {entry['name']} successfully after refreshing token.")
            else:
                print(f"Error logging food {entry['name']} after refreshing token: {response.content}")
    else:
        print(f"Error logging food {entry['name']} with {current_date}: {response.content}")