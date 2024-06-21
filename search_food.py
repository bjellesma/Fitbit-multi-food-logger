import requests

access_token = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1BLNzMiLCJzdWIiOiI4NFpKUE0iLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJ3bnV0IiwiZXhwIjoxNzE4OTIyODg2LCJpYXQiOjE3MTg4OTQwODZ9.e02Z7jv9NtrtPNZRXsRW_y3udLr7cbpruk6AfMCyNMs'
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
