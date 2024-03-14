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


def playlist_command(original_args: List[str], sptfy: Sptfy):
    if len(original_args) < 1:
        print(get_playlist_command_usage())
        exit(1)

    subcommand = original_args[0]

    if subcommand == "help":
        print(get_playlist_command_usage())
        exit(0)

    subcommand_function = PLAYLIST_COMMAND_SUBCOMMANDS.get(subcommand, None)
    if subcommand_function is None:
        print(f"Unknown subcommand '{subcommand}', {get_playlist_command_usage()}")
        exit(1)

    subcommand_function(
        args=original_args[1:],
        sptfy=sptfy
    )


def get_longest_title_length(playlists_no_songs: List[PlaylistNoSongs]) -> int:
    curr_longest_len = 0
    for playlist in playlists_no_songs:
        if len(playlist.name) > curr_longest_len:
            curr_longest_len = len(playlist.name)

    return curr_longest_len


def get_filename(sptfy: Sptfy) -> str:
    date = datetime.now()
    user_id = sptfy.get_user_id()
    filename = f"playlists-{user_id}-{date.strftime('%d_%m_%YT%H_%M_%S')}.json"
    return filename


def download_playlists(args: List[str], sptfy: Sptfy) -> None:
    parser = get_playlist_download_parser()
    download_args = parser.parse_args(args)

    start = time.time()

    if download_args.filename is None:
        filename = get_filename(sptfy)
    elif download_args.filename.strip() == "":
        print(f"ERROR: Filename cannot be blank or null!")
        exit(1)
    elif not download_args.filename.strip().endswith('.json'):
        print(f"ERROR: Filename must end with '.json'")
        exit(1)
    else:
        filename = download_args.filename

    print(f"The filename will be {filename}")


    playlists_no_songs = sptfy.get_all_playlists_no_songs()
    logger.info(f'Number of playlists found: {len(playlists_no_songs)}')

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        playlists = list(executor.map(get_playlist_with_songs, playlists_no_songs, repeat(sptfy)))

    liked_songs = sptfy.get_saved_tracks_as_playlist()
    playlists.append(liked_songs)

    with open(filename, 'w') as file:
        logger.info(f"Writing to file '{filename}' in the local directory")
        file.write(json.dumps(playlists, default=get_obj_dict))
        logger.info(f"Number of playlists processed: {len(playlists)} (There is a +1 for liked songs)")

    end = time.time()
    time_taken = end - start
    logger.info(f"Time taken: {round(time_taken, 2)} seconds")
    print("Finished!")


def get_playlist_list_parser() -> ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=f"{PLAYLIST_COMMAND_NAME} {PLAYLIST_LIST_SUBCOMMAND}",
        description="Show playlist data from Spotify"
    )

    parser.add_argument(
        "--show-id",
        action="store_true",
        help="If the playlist Ids should be shown when listing",
        required=False,
        default=False
    )

    return parser


def get_playlist_download_parser() -> ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=f"{PLAYLIST_COMMAND_NAME} {PLAYLIST_DOWNLOAD_SUBCOMMAND}",
        description="Download playlist data from Spotify"
    )

    parser.add_argument(
        "--filename",
        action="store",
        help="The filename desired",
        required=False,
        default=None
    )

    return parser


def list_playlists(args: List[str], sptfy: Sptfy) -> None:
    parser = get_playlist_list_parser()
    list_args = parser.parse_args(args)

    playlists_no_songs = sptfy.get_all_playlists_no_songs()
    longest_length = get_longest_title_length(playlists_no_songs)

    for playlist in playlists_no_songs:
        print(f"{playlist.name:>{longest_length}}\t", end="")
        if list_args.show_id:
            print(f"{playlist.id}", end="")
        print()


def get_playlist_with_songs(playlist: PlaylistNoSongs, sptfy: Sptfy) -> PlaylistWithSongs:
    songs: List[Song] = sptfy.get_playlist_content(playlist_id=playlist.id)
    playlist_with_songs = PlaylistWithSongs(
        playlist=playlist,
        songs=songs
    )
    return playlist_with_songs


def get_playlist_command_usage():
    command_names = list(PLAYLIST_COMMAND_SUBCOMMANDS.keys())
    return f"usage: spotiList {PLAYLIST_COMMAND_NAME} {{help,{','.join(command_names)}}}"


PLAYLIST_COMMAND_NAME = "playlist"
PLAYLIST_LIST_SUBCOMMAND = "list"
PLAYLIST_DOWNLOAD_SUBCOMMAND = "download"
PLAYLIST_COMMAND_SUBCOMMANDS = {
    PLAYLIST_LIST_SUBCOMMAND: list_playlists,
    PLAYLIST_DOWNLOAD_SUBCOMMAND: download_playlists,
}
