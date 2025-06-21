#!/usr/bin/env python3
"""
Fitbit Token Generator
This script helps generate fresh access and refresh tokens for Fitbit API
"""

import requests
import json
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_tokens():
    client_id = os.getenv('CLIENTID')
    client_secret = os.getenv('CLIENTSECRET')
    
    if not client_id or not client_secret:
        print("ERROR: CLIENTID and CLIENTSECRET must be set in .env file")
        return
    
    print("=== Fitbit Token Generator ===")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:10]}...")
    print()
    
    # Use the known redirect URI
    redirect_uri = "http://localhost"
    print(f"Using redirect URI: {redirect_uri}")
    print()
    
    # Step 1: Generate authorization URL
    auth_url = f"https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={client_id}&scope=nutrition%20activity&redirect_uri={redirect_uri}"
    
    print("1. Open this URL in your browser to authorize the app:")
    print(f"   {auth_url}")
    print()
    print("2. After authorization, you'll be redirected to a URL like:")
    print(f"   {redirect_uri}?code=YOUR_AUTH_CODE")
    print()
    
    # Get authorization code from user
    auth_code = input("3. Enter the authorization code from the redirect URL: ").strip()
    
    if not auth_code:
        print("No authorization code provided. Exiting.")
        return
    
    # Clean the authorization code (remove any fragments like #_=_)
    auth_code = auth_code.split('#')[0]
    print(f"Using cleaned authorization code: {auth_code}")
    print()
    
    # Step 2: Exchange authorization code for tokens
    token_url = "https://api.fitbit.com/oauth2/token"
    basic_token = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': client_id,
        'redirect_uri': redirect_uri
    }
    
    headers = {
        'Authorization': f'Basic {basic_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    print("4. Exchanging authorization code for tokens...")
    
    response = requests.post(token_url, data=payload, headers=headers)
    
    if response.status_code == 200:
        tokens = response.json()
        print("✅ Successfully generated new tokens!")
        print()
        print("Token Information:")
        print(f"Access Token: {tokens['access_token'][:20]}...")
        print(f"Refresh Token: {tokens['refresh_token'][:20]}...")
        print(f"Expires In: {tokens['expires_in']} seconds")
        print()
        
        # Save tokens to files
        with open('access_token.json', 'w') as f:
            json.dump({'access_token': tokens['access_token']}, f)
        
        with open('refresh_token.json', 'w') as f:
            json.dump({'refresh_token': tokens['refresh_token']}, f)
        
        print("✅ Tokens saved to access_token.json and refresh_token.json")
        print()
        print("You can now restart your Flask server and test the endpoints!")
        
    else:
        print(f"❌ Failed to generate tokens. Status: {response.status_code}")
        print(f"Response: {response.text}")
        print()
        print("Common issues:")
        print("- Authorization code already used or expired")
        print("- Invalid client ID or secret")

if __name__ == "__main__":
    generate_tokens() 