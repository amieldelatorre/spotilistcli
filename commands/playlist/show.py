import sys
import click
from helpers import time_taken, get_longest_string
from log import logger
from sptfy import get_sptfy


@click.command()
@click.option("--playlist-id", required=True, help="The Id of the playlist to show")
@click.option("--show-url", default=False, is_flag=True, help="If the song urls should be shown when listing")
@click.option("--show-artists", default=False, is_flag=True, help="If the artists should be shown when listing")
@time_taken
def show(playlist_id: str, show_url: bool, show_artists: bool):
    if playlist_id is None or playlist_id.strip() == "":
        print("ERROR: Invalid playlist id, cannot be None or empty!")

    sptfy = get_sptfy()

    logger.debug(f"Validate playlist id")
    playlist_id = playlist_id.strip()
    if not sptfy.playlist_exists(playlist_id):
        print(f"ERROR: Playlist Id could not be found!")
        sys.exit(1)

    logger.debug(f"Retrieve playlist")
    songs = sptfy.get_playlist_content(playlist_id)
    longest_song_name = get_longest_string([song.name for song in songs])
    longest_artists = get_longest_string([','.join(song.artists) for song in songs])
    longest_url = get_longest_string([song.spotify_url for song in songs])

    logger.debug(f"Showing playlist contents")
    if show_artists:
        logger.debug(f"Showing song artists")
    if show_url:
        logger.debug(f"Showing song urls")

    for song in songs:
        print(f"{song.name:<{longest_song_name}}", end="")
        if show_artists:
            print(f"\t{','.join(song.artists):<{longest_artists}}", end="")
        if show_url:
            print(f"\t{song.spotify_url:<{longest_url}}", end="")

        print()