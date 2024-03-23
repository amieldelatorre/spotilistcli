# SpotilistCLI
Small CLI tool to get playlist information from Spotify, written in Python.

## Prerequisites
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

OR, once the executable has been downloaded or the project has been setup with the requirements installed, you can run `spotilist configure` to create the `.env` file interactively.

## Downloading the executable
The latest executables can be found here: https://github.com/amieldelatorre/spotilistcli/releases/latest

## Running
Run these commands in your terminal at the root directory of the cloned .
```shell
python -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
python3 app.py help
```

## Building an executable / binary
```shell
python -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --hidden-import http.server --hidden-import commands.playlist --add-data=commands:commands --onefile --name spotilistcli app.py
# Then move the .env file to the dist/ directory or one of it's parent directories
spotilistcli help
```