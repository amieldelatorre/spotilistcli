import argparse
import concurrent.futures
import json
import time
import sys
from datetime import datetime
from argparse import ArgumentParser
from typing import List, Callable, Optional
from sptfy import Sptfy, PlaylistNoSongs, PlaylistWithSongs, Song
from itertools import repeat
from helpers import get_obj_dict
from log import logger
from helpers import get_longest_string, get_command_usage, login_required


@login_required
def playlist_command(original_args: List[str], sptfy: Sptfy) -> None:
    if len(original_args) < 1:
        print(get_command_usage(
            command=PLAYLIST_COMMAND_NAME,
            subcommands=PLAYLIST_COMMAND_SUBCOMMANDS
        ))
        sys.exit(1)

    subcommand = original_args[0]

    if subcommand == "help":
        print(get_command_usage(
            command=PLAYLIST_COMMAND_NAME,
            subcommands=PLAYLIST_COMMAND_SUBCOMMANDS
        ))
        sys.exit(0)

    subcommand_function: Optional[Callable] = PLAYLIST_COMMAND_SUBCOMMANDS.get(subcommand, None)
    if subcommand_function is None:
        print(f"Unknown subcommand '{subcommand}', {get_command_usage(
            command=PLAYLIST_COMMAND_NAME,
            subcommands=PLAYLIST_COMMAND_SUBCOMMANDS
        )}")
        sys.exit(1)

    subcommand_function(
        args=original_args[1:],
        sptfy=sptfy
    )


def get_filename(sptfy: Sptfy) -> str:
    date = datetime.now()
    user_id = sptfy.get_user_id()
    filename = f"playlists-{user_id}-{date.strftime('%Y_%m_%dT%H_%M_%S')}.json"
    return filename


def download_playlists(args: List[str], sptfy: Sptfy) -> None:
    parser = get_playlist_download_parser()
    download_args = parser.parse_args(args)

    start = time.time()

    if download_args.filename is None:
        filename = get_filename(sptfy)
    elif download_args.filename.strip() == "":
        print(f"ERROR: Filename cannot be blank or null!")
        sys.exit(1)
    elif not download_args.filename.strip().endswith('.json'):
        print(f"ERROR: Filename must end with '.json'")
        sys.exit(1)
    else:
        filename = download_args.filename

    print(f"The filename will be {filename}")

    playlists_no_songs = sptfy.get_all_playlists_no_songs()
    logger.info(f'Number of playlists found: {len(playlists_no_songs)}')

    count = 0
    num_playlists = len(playlists_no_songs) + 1  # There is a +1 for liked songs
    playlists = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        tasks = executor.map(get_playlist_with_songs, playlists_no_songs, repeat(sptfy))
        for task in tasks:
            playlists.append(task)
            count += 1
            if download_args.show_progress:
                print(f"{count}/{num_playlists} completed")

    liked_songs = sptfy.get_saved_tracks_as_playlist()
    playlists.append(liked_songs)
    count += 1
    print(f"{count}/{num_playlists} completed")

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

    parser.add_argument(
        "--show-progress",
        action="store_true",
        help="Show how many have been completed out of the total amount",
        required=False,
        default=False
    )

    return parser


def get_playlist_show_parser() -> ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=f"{PLAYLIST_COMMAND_NAME} {PLAYLIST_SHOW_SUBCOMMAND}",
        description="Show all the songs from a playlist in Spotify"
    )

    parser.add_argument(
        "--playlist-id",
        action="store",
        help="The Id of the playlist to show",
        required=True
    )

    parser.add_argument(
        "--show-url",
        action="store_true",
        help="If the song urls should be shown when listing",
        required=False,
        default=False
    )

    parser.add_argument(
        "--show-artists",
        action="store_true",
        help="If the artists should be shown when listing",
        required=False,
        default=False
    )

    return parser


def list_playlists(args: List[str], sptfy: Sptfy) -> None:
    parser = get_playlist_list_parser()
    list_args = parser.parse_args(args)

    playlists_no_songs = sptfy.get_all_playlists_no_songs()
    longest_playlist_name = get_longest_string([playlist.name for playlist in playlists_no_songs])
    longest_playlist_id = get_longest_string([playlist.id for playlist in playlists_no_songs])

    for playlist in playlists_no_songs:
        print(f"{playlist.name:<{longest_playlist_name}}", end="")
        if list_args.show_id:
            print(f"\t{playlist.id:<{longest_playlist_id}}", end="")
        print()


def show_playlist(args: List[str], sptfy: Sptfy) -> None:
    parser = get_playlist_show_parser()
    show_args = parser.parse_args(args)

    if show_args.playlist_id is None or show_args.playlist_id.strip() == "":
        print("ERROR: Invalid playlist id, cannot be None or empty!")

    playlist_id = show_args.playlist_id.strip()
    if not sptfy.playlist_exists(playlist_id):
        print(f"ERROR: Playlist Id could not be found!")
        sys.exit(1)

    songs = sptfy.get_playlist_content(playlist_id)
    longest_song_name = get_longest_string([song.name for song in songs])
    longest_artists = get_longest_string([','.join(song.artists) for song in songs])
    longest_url = get_longest_string([song.spotify_url for song in songs])
    for song in songs:
        print(f"{song.name:<{longest_song_name}}", end="")
        if show_args.show_artists:
            print(f"\t{','.join(song.artists):<{longest_artists}}", end="")
        if show_args.show_url:
            print(f"\t{song.spotify_url:<{longest_url}}", end="")

        print()


def get_playlist_with_songs(playlist: PlaylistNoSongs, sptfy: Sptfy) -> PlaylistWithSongs:
    songs: List[Song] = sptfy.get_playlist_content(playlist_id=playlist.id)
    playlist_with_songs = PlaylistWithSongs(
        playlist=playlist,
        songs=songs
    )
    return playlist_with_songs


PLAYLIST_COMMAND_NAME = "playlist"
PLAYLIST_LIST_SUBCOMMAND = "list"
PLAYLIST_DOWNLOAD_SUBCOMMAND = "download"
PLAYLIST_SHOW_SUBCOMMAND = "show"
PLAYLIST_COMMAND_SUBCOMMANDS = {
    PLAYLIST_LIST_SUBCOMMAND: list_playlists,
    PLAYLIST_DOWNLOAD_SUBCOMMAND: download_playlists,
    PLAYLIST_SHOW_SUBCOMMAND: show_playlist,
}
