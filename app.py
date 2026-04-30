import os
import sys
import click
import commands
from spotipy.oauth2 import SpotifyOauthError
from log import logger


@click.group(help="A CLI tool to make a backup of the music you listen to on Spotify. "
                  "Creates a list of your playlists.")
def main():
    pass


if __name__ == "__main__":
    main.add_command(commands.auth.auth)
    main.add_command(commands.configure.configure)
    main.add_command(commands.playlist.playlist)
    main.add_command(commands.user_top.user_top)
    main.add_command(commands.validate.validate)
    main.add_command(commands.scrobble.scrobble)
    
    try:
        main()
    except SpotifyOauthError as e:
        logger.error(f"SpotifyOauthError {e.error}")
        logger.error(f"{e.error_description}")
        print("ERROR: check if the credentials in your .env file is valid!")
        sys.exit(1)
