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
refresh_token = refresh_token_data['refresh_token']headers = {
    'Authorization': f'Bearer {access_token}'
}

# Make the API request
response = requests.get(
    'https://api.fitbit.com/1/foods/units.json',
    headers=headers
)

if response.status_code == 200:
    units = response.json()
    for unit in units:
        print(f"Unit ID: {unit['id']} - Name: {unit['name']} - Plural: {unit['plural']}")
else:
    print(f"Error: {response.json()}")