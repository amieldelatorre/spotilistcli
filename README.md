# SpotilistCLI
Small CLI tool to get playlist information from Spotify, written in Python.

## Prerequisits
1. Clone the repository
2. Create a developer account at https://developer.spotify.com/
3. Create a new app
4. Set an app name and description
5. Set the Redirect URI as `http://localhost:3000/callback`
6. Get the Client ID and Client Secret and put it in a `.env` file in the root directory of the cloned repository. The .env file should look like:

```Dotenv
SPOTIFY_CLIENT_ID=YOUR_CLIENT_ID
SPOTIFY_CLIENT_SECRET=YOUR_CLIENT_SECRET
SPOTIFY_REDIRECT_URI=http://localhost:3000/callback
```

## To run
Run these commands in your terminal at the root directory of the cloned .
```shell
python -m venv .venv
source ./venv/bin/activate
pip install -r requirements.txt
python3 app.py help
```
