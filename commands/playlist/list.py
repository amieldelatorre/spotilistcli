import click

from helpers import time_taken, get_longest_string
from log import logger
from sptfy import get_sptfy


@click.command()
@click.option("--show-id", default=False, is_flag=True, help="If the playlist Ids should be shown when listing")
@time_taken
def list(show_id: bool) -> None:
    logger.debug(f"Retrieve playlist names")

    sptfy = get_sptfy()

    playlists_no_songs = sptfy.get_all_playlists_no_songs()
    longest_playlist_name = get_longest_string([playlist.name for playlist in playlists_no_songs])
    longest_playlist_id = get_longest_string([playlist.id for playlist in playlists_no_songs])

    logger.debug(f"Showing playlist names")
    if show_id:
        logger.debug(f"Showing playlist Ids")
    for playlist in playlists_no_songs:
        print(f"{playlist.name:<{longest_playlist_name}}", end="")
        if show_id:
            print(f"\t{playlist.id:<{longest_playlist_id}}", end="")
        print()
