# Fitbit Multi Food Editor

A web application for logging food entries to Fitbit with a modern React frontend and Flask backend.

## Prerequisites

- Python 3.10 or higher
- Node.js and npm
- Fitbit Developer Account with API credentials

## Setup Instructions

### 1. Get Fitbit API Credentials

1. Go to [Fitbit Developer Portal](https://dev.fitbit.com/)
2. Create a new app and get your `CLIENT_ID` and `CLIENT_SECRET`
3. Generate your access and refresh tokens
4. Create a `.env` file in the `backend` directory with your credentials:

```env
CLIENTID=your_client_id_here
CLIENTSECRET=your_client_secret_here
```

### 2. Configure Tokens

1. Copy the sample token files:
   ```bash
   cp backend/access-token-sample.json backend/access-token.json
   cp backend/refresh-token-sample.json backend/refresh-token.json
   ```

2. Replace the placeholder values in these files with your actual Fitbit tokens:
   - `backend/access-token.json` - Your Fitbit access token
   - `backend/refresh-token.json` - Your Fitbit refresh token

### 3. Install Dependencies

#### Backend Setup
```bash
cd backend
pipenv install
```

#### Frontend Setup
```bash
cd frontend
npm install
```

## Running the Application

### Start the Backend Server
```bash
cd backend
pipenv run server
```
The Flask server will start on `http://localhost:5000`

### Start the Frontend Development Server
```bash
cd frontend
npm start
```
The React app will start on `http://localhost:3000`

### Access the Application
Open your browser and navigate to `http://localhost:3000` to use the Fitbit Multi Food Editor.

## Project Structure

- `backend/` - Flask API server
- `frontend/` - React web application
- `log_food.py` - Standalone food logging script
- `search_food.py` - Standalone food search script
- `search_units.py` - Standalone unit search script

## Troubleshooting

- Make sure both servers are running simultaneously
- Verify your Fitbit tokens are valid and properly configured
- Check that all dependencies are installed correctly
- Ensure your `.env` file contains the correct Fitbit API credentials

### Token Issues

If you get a 401 error or "Refresh token invalid" message, your tokens have expired. To generate new tokens:

1. **Run the token generator:**
   ```bash
   cd backend
   pipenv run python generate_tokens.py
   ```

2. **Follow the prompts:**
   - Open the authorization URL in your browser
   - Authorize your Fitbit app
   - Copy the authorization code from the redirect URL
   - Paste it into the terminal

3. **Restart your server:**
   ```bash
   pipenv run server
   ```

The script will automatically save new tokens to the correct files and you can immediately test your endpoints again.

## CLI

### search for food

```bash
python3 search_food.py
```

### log food

```bash
python3 log_food.py
```
