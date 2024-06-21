import requests

access_token = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1BLNzMiLCJzdWIiOiI4NFpKUE0iLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJ3bnV0IiwiZXhwIjoxNzE4OTIyODg2LCJpYXQiOjE3MTg4OTQwODZ9.e02Z7jv9NtrtPNZRXsRW_y3udLr7cbpruk6AfMCyNMs'
headers = {
    'Authorization': f'Bearer {access_token}'
}

# Make the API request
response = requests.get(
    'https://api.fitbit.com/1/foods/units.json',
    headers=headers
)

if response.status_code == 200:
    units = response.json()
    print(f"Available Measurement Units: {units}")
    for unit in units:
        print(f"Unit ID: {unit['id']} - Name: {unit['name']} - Plural: {unit['plural']}")
else:
    print(f"Error: {response.json()}")