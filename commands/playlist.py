import argparse
import concurrent.futures
import json
import time
from datetime import datetime
from argparse import ArgumentParser
from typing import List
from sptfy import Sptfy, PlaylistNoSongs, PlaylistWithSongs, Song
from itertools import repeat
from helpers import get_obj_dict
from log import logger


PLAYLIST_COMMAND_NAME = "playlist"
PLAYLIST_COMMAND_SUBCOMMANDS = ["list", "download"]


def get_playlist_parser() -> ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PLAYLIST_COMMAND_NAME,
        description="Show/Download playlist data from Spotify"
    )

    parser.add_argument(
        "--id",
        action="store",
        help="Specify a playlist id and shows it's items. If a playlist id is not specified it will grab all playlists "
             "names",
        required=False
    )

    return parser


def playlist_command(original_args: List[str], sptfy: Sptfy):
    if len(original_args) < 1:
        print(f"\tusage: {PLAYLIST_COMMAND_NAME} {','.join(PLAYLIST_COMMAND_SUBCOMMANDS)}")
        exit(1)

    subcommand = original_args[0]
    if subcommand not in PLAYLIST_COMMAND_SUBCOMMANDS:
        print(f"\tUnknown subcommand '{subcommand}', usage: {PLAYLIST_COMMAND_NAME}"
              f" {','.join(PLAYLIST_COMMAND_SUBCOMMANDS)}")
        exit(1)

    date = datetime.now()
    start = time.time()
    playlists_no_songs = sptfy.get_all_playlists_no_songs()
    logger.info(f'Number of playlists found: {len(playlists_no_songs)}')

    if subcommand == "list":
        print(*playlists_no_songs, sep="\n")
    elif subcommand == "download":
        filename = f"playlists-{date.strftime('%d_%m_%YT%H_%M_%S')}.json"
        print(f"The filename will be {filename}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            playlists = list(executor.map(get_playlist_with_songs, playlists_no_songs, repeat(sptfy)))

        with open(filename, 'w') as file:
            logger.info(f"Writing to file '{filename}' in the local directory")
            file.write(json.dumps(playlists, default=get_obj_dict))

        end = time.time()
        time_taken = end - start
        logger.info(f"Number of playlists processed: {len(playlists)}")
        logger.info(f"Time taken: {round(time_taken, 2)} seconds")


def get_playlist_with_songs(playlist: PlaylistNoSongs, sptfy: Sptfy) -> PlaylistWithSongs:
    songs: List[Song] = sptfy.get_playlist_content(playlist_id=playlist.id)
    playlist_with_songs = PlaylistWithSongs(
        playlist=playlist,
        songs=songs
    )
    return playlist_with_songs
