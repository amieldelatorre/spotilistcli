import argparse
import concurrent.futures
import json
import signal
import sys
import threading
from datetime import datetime
from argparse import ArgumentParser
from typing import List, Callable, Optional
from sptfy import Sptfy, PlaylistNoSongs, PlaylistWithSongs, Song
from ytmusic import YTM
from itertools import repeat
from helpers import get_obj_dict, time_taken
from log import logger
from helpers import get_longest_string, get_command_usage, login_required


@login_required
def playlist_command(original_args: List[str], sptfy: Sptfy) -> None:
    logger.debug("'playlist' command invoked")
    if len(original_args) < 1:
        print(get_command_usage(
            command=PLAYLIST_COMMAND_NAME,
            subcommands=PLAYLIST_COMMAND_SUBCOMMANDS
        ))
        sys.exit(1)

    subcommand = original_args[0]

    if subcommand == "help":
        logger.debug("'playlist' help command invoked")
        print(get_command_usage(
            command=PLAYLIST_COMMAND_NAME,
            subcommands=PLAYLIST_COMMAND_SUBCOMMANDS
        ))
        sys.exit(0)

    subcommand_function: Optional[Callable] = PLAYLIST_COMMAND_SUBCOMMANDS.get(subcommand, None)
    if subcommand_function is None:
        logger.debug(f"'playlist' '{subcommand}' subcommand not found")
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


@time_taken
def download_playlists(args: List[str], sptfy: Sptfy) -> None:
    logger.debug(f"'playlist' 'download' subcommand invoked")
    parser = get_playlist_download_parser()
    download_args = parser.parse_args(args)

    logger.debug(f"Retrieve or validate filename")
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

    logger.debug(f"Retrieve list of playlists without songs")
    playlists_no_songs = sptfy.get_all_playlists_no_songs()
    logger.info(f'Number of playlists found: {len(playlists_no_songs)}')

    num_playlists = len(playlists_no_songs) + 1  # There is a +1 for liked songs
    playlists = get_playlists_with_songs(
        num_playlists=num_playlists,
        playlists_no_songs=playlists_no_songs,
        sptfy=sptfy,
        show_progress=download_args.show_progress
    )

    if download_args.with_youtube_url:
        modify_playlists_with_songs_youtube_url(playlists, download_args.show_progress,
                                                download_args.with_youtube_url_cache_from,
                                                download_args.with_youtube_url_cache_unvalidated)

    with open(filename, 'w') as file:
        logger.info(f"Writing to file '{filename}' in the local directory")
        file.write(json.dumps(playlists, default=get_obj_dict))
        logger.info(f"Number of playlists processed: {len(playlists)} (There is a +1 for liked songs)")

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

    parser.add_argument(
        "--with-youtube-url",
        action="store_true",
        help="Find and search for the Youtube Music URL",
        required=False,
        default=False
    )

    parser.add_argument(
        "--with-youtube-url-cache-from",
        action="store",
        help="Preload the cache with Youtube URLs from a previously generated file. Null entries will be skipped and not loaded. Only takes effect when the `--with-youtube-url` flag is used.",
        required=False,
        default=None
    )

    parser.add_argument(
        "--with-youtube-url-cache-unvalidated",
        action="store_true",
        help="Use unvalidated Youtube URLs from previously generated file. Only takes effect when the `--with-youtube-url-cache-from` flag is used.",
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


@time_taken
def list_playlists(args: List[str], sptfy: Sptfy) -> None:
    parser = get_playlist_list_parser()
    list_args = parser.parse_args(args)

    logger.debug(f"Retrieve playlist names")
    playlists_no_songs = sptfy.get_all_playlists_no_songs()
    longest_playlist_name = get_longest_string([playlist.name for playlist in playlists_no_songs])
    longest_playlist_id = get_longest_string([playlist.id for playlist in playlists_no_songs])

    logger.debug(f"Showing playlist names")
    if list_args.show_id:
        logger.debug(f"Showing playlist Ids")
    for playlist in playlists_no_songs:
        print(f"{playlist.name:<{longest_playlist_name}}", end="")
        if list_args.show_id:
            print(f"\t{playlist.id:<{longest_playlist_id}}", end="")
        print()


@time_taken
def show_playlist(args: List[str], sptfy: Sptfy) -> None:
    parser = get_playlist_show_parser()
    show_args = parser.parse_args(args)

    if show_args.playlist_id is None or show_args.playlist_id.strip() == "":
        print("ERROR: Invalid playlist id, cannot be None or empty!")

    logger.debug(f"Validate playlist id")
    playlist_id = show_args.playlist_id.strip()
    if not sptfy.playlist_exists(playlist_id):
        print(f"ERROR: Playlist Id could not be found!")
        sys.exit(1)

    logger.debug(f"Retrieve playlist")
    songs = sptfy.get_playlist_content(playlist_id)
    longest_song_name = get_longest_string([song.name for song in songs])
    longest_artists = get_longest_string([','.join(song.artists) for song in songs])
    longest_url = get_longest_string([song.spotify_url for song in songs])

    logger.debug(f"Showing playlist contents")
    if show_args.show_artists:
        logger.debug(f"Showing song artists")
    if show_args.show_url:
        logger.debug(f"Showing song urls")

    for song in songs:
        print(f"{song.name:<{longest_song_name}}", end="")
        if show_args.show_artists:
            print(f"\t{','.join(song.artists):<{longest_artists}}", end="")
        if show_args.show_url:
            print(f"\t{song.spotify_url:<{longest_url}}", end="")

        print()


def get_playlist_with_songs(playlist: PlaylistNoSongs, sptfy: Sptfy) -> PlaylistWithSongs:
    logger.debug(f"Retrieve song for playlist")
    songs: List[Song] = sptfy.get_playlist_content(playlist_id=playlist.id)
    playlist_with_songs = PlaylistWithSongs(
        playlist=playlist,
        songs=songs
    )
    return playlist_with_songs


def get_playlists_with_songs(num_playlists: int, playlists_no_songs: List[PlaylistNoSongs], sptfy: Sptfy,
                             show_progress: True) -> List[PlaylistWithSongs]:
    count = 0
    playlists = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        logger.debug(f"Retrieve playlists with their songs")
        tasks = executor.map(get_playlist_with_songs, playlists_no_songs, repeat(sptfy))
        for task in tasks:
            playlists.append(task)
            count += 1
            if show_progress:
                print(f"Downloaded playlists: {count}/{num_playlists} completed")

    logger.debug(f"Retrieve liked songs")
    liked_songs = sptfy.get_saved_tracks_as_playlist()
    playlists.append(liked_songs)
    count += 1
    print(f"Downloaded playlists: {count}/{num_playlists} completed")

    return playlists


def modify_playlists_with_songs_youtube_url(playlists: List[PlaylistWithSongs], show_progress: bool,
                                            youtube_url_cache_file: Optional[str],
                                            use_unvalidated_url_from_youtube_url_cache: bool):
    logger.debug("Adding youtube urls to songs")
    ytm = YTM()
    if youtube_url_cache_file is not None:
        preload_youtube_url_cache(ytm, youtube_url_cache_file, use_unvalidated_url_from_youtube_url_cache)

    interrupt_event = threading.Event()
    def signal_handler(signum, frame):
        logger.warning("Interrupt signal received, processing may be incomplete")
        interrupt_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    count = 0
    num_playlists = len(playlists)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        logger.debug(f"Retrieve playlists with their songs")
        tasks = executor.map(add_youtube_url_to_songs, playlists, repeat(ytm), repeat(interrupt_event))
        try:
            for task in tasks:
                count += 1
                if show_progress:
                    print(f"Added Youtube URL for playlists' songs: {count}/{num_playlists} completed")
        except KeyboardInterrupt:
            interrupt_event.set()
        finally:
            return


def add_youtube_url_to_songs(playlist: PlaylistWithSongs, ytm: YTM, interrupt_event: threading.Event):
    logger.debug(f"add youtube urls for playlist '{playlist.id}'")
    for song in playlist.songs:
        if interrupt_event.is_set():
            logger.warning(f"interrupted playlist '{playlist.name}")
            return playlist
        song.youtube_url = ytm.get_youtube_url(song)


def preload_youtube_url_cache(ytm: YTM, filename: str, use_unvalidated_url: bool):
    print("Preloading youtube url cache")
    if use_unvalidated_url:
        print("`--with-youtube-url-cache-unvalidated` flag used, adding unvalidated URLs to cache")
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        songs = []
        for item in data:
            item_songs = item["songs"]
            for item_song in item_songs:
                song_name = item_song["name"]
                song_artists = item_song["artists"]
                song_spotify_url = item_song["spotify_url"]
                song_youtube_url = item_song["youtube_url"]
                song_youtube_url_validated = item_song["youtube_url_validated"]

                songs.append(Song(
                    name=song_name,
                    artists=song_artists,
                    spotify_url=song_spotify_url,
                    youtube_url=song_youtube_url,
                    youtube_url_validated=song_youtube_url_validated
                ))

        for song in songs:
            if song.youtube_url is None:
                continue
            if song.youtube_url_validated or use_unvalidated_url:
                ytm.add_to_cache(song.spotify_url, song.youtube_url)

    except FileNotFoundError:
        logger.error(f"file: {filename} could not be found")
        sys.exit(1)


PLAYLIST_COMMAND_NAME = "playlist"
PLAYLIST_LIST_SUBCOMMAND = "list"
PLAYLIST_DOWNLOAD_SUBCOMMAND = "download"
PLAYLIST_SHOW_SUBCOMMAND = "show"
PLAYLIST_COMMAND_SUBCOMMANDS = {
    PLAYLIST_LIST_SUBCOMMAND: list_playlists,
    PLAYLIST_DOWNLOAD_SUBCOMMAND: download_playlists,
    PLAYLIST_SHOW_SUBCOMMAND: show_playlist,
}
