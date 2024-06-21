import requests

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
                
else:
    print(f"Error: {response.json()}")
