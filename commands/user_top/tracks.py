import click
from .consts import VALID_TIME_RANGE
from sptfy import get_sptfy
from helpers import time_taken, get_longest_string
from log import logger


@click.command()
@click.option("--limit", type=click.IntRange(1, 50),
              default=10, help="Maximum number of items to return")
@click.option("--offset", type=click.IntRange(min=0),
              default=0, help="The index of the first item to return")
@click.option("--time-range", type=click.Choice(VALID_TIME_RANGE, case_sensitive=True),
              default=VALID_TIME_RANGE[0], help="Time frame to compute for the data")
@time_taken
def tracks(limit, offset, time_range) -> None:
    logger.debug(f"Retrieving top tracks")
    logger.debug(f"Getting user top tracks with input: limit {limit}, "
                 f"offset {offset}, time_range {time_range}")

    sptfy = get_sptfy()
    songs = sptfy.get_user_top_tracks(
        limit=limit,
        offset=offset,
        time_range=time_range
    )

    logger.debug(f"Showing songs and artists")
    longest_song_name = get_longest_string([song.name for song in songs])
    longest_artists_name = get_longest_string([','.join(song.artists) for song in songs])
    for song in songs:
        print(f"{song.name:<{longest_song_name}}\t{','.join(song.artists):<{longest_artists_name}}")