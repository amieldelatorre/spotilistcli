import os
import sys
from sptfy import Sptfy
from dotenv import load_dotenv
from commands import playlist
from helpers import get_usage


def main():
    if len(sys.argv) < 2:  # 2 because the file path is the first argument
        print(get_usage())
        exit(1)

    load_dotenv()
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

    sptfy = Sptfy(
        spotify_client_id=SPOTIFY_CLIENT_ID,
        spotify_client_secret=SPOTIFY_CLIENT_SECRET,
        spotify_redirect_uri=SPOTIFY_REDIRECT_URI,
    )

    command = sys.argv[1]
    following_args = sys.argv[2:]
    match command:
        case playlist.PLAYLIST_COMMAND_NAME:
            playlist.playlist_command(
                original_args=following_args,
                sptfy=sptfy
            )
        case 'help':
            print(get_usage())
        case _:
            print(f"Unknown command '{command}', {get_usage()}")
            exit(1)


if __name__ == "__main__":
    main()
