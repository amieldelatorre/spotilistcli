# SpotilistCLI
Small CLI tool to get playlist information from Spotify, written in Python.

## Prerequisites
1. Clone the repository
2. Create a developer account at https://developer.spotify.com/
3. Create a new app
4. Set an app name and description
5. Set the Redirect URI as `http://127.0.0.1:3000/callback`
6. Get the Client ID and Client Secret and put it in a `.env` file in `~/.config/spotilistcli`. The .env file should look like:

```Dotenv
SPOTIFY_CLIENT_ID=YOUR_CLIENT_ID
SPOTIFY_CLIENT_SECRET=YOUR_CLIENT_SECRET
SPOTIFY_REDIRECT_URI=http://127.0.0.1:3000/callback
```

OR, once the executable has been downloaded or the project has been setup with the requirements installed, you can run `spotilistcli configure` to create the `.env` file interactively.

## Downloading the executable
The latest executables can be found here: https://github.com/amieldelatorre/spotilistcli/releases/latest. After downloading and unpacking, create a shortcut (Windows) or soft links (linux/macos).

```bash
# Example of adding a symbolic link to the /usr/local/bin directory
ln -s /full/path/to/file/spotilistcli/spotilistcli /usr/local/bin/spotilistcli
# spotilistcli/spotilistcli (directory/actual executable)
```

The first run of the package may be slow as it will unpack the bundled dependencies, however, subsequent runs will be faster.

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
pyinstaller --hidden-import http.server --hidden-import commands.playlist --add-data=commands:commands --onedir --name spotilistcli app.py
spotilistcli help
```

## Downloading all playlists with a youtube URL cache from a previous download
```bash
python app.py playlist download --show-progress --with-youtube-url --with-youtube-url-cache-from <previous_filename> --with-youtube-url-cache-unvalidated --filter-owned
```

## Validating youtube URLs in downloaded file
```bash
python app.py validate youtube-urls --input-filename <filename>
```
