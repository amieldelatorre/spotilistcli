import concurrent.futures
import json
import signal
import sys
import threading
import click
from itertools import repeat
from typing import List, Optional
from helpers import time_taken, get_obj_dict
from log import logger
from sptfy import Sptfy, get_sptfy, PlaylistWithSongs, PlaylistNoSongs, Song
from datetime import datetime

from ytmusic import YTM


@click.command()
@click.option("--filename", default=None, help="The filename desired")
@click.option("--show-progress", default=False, is_flag=True,
              help="Show how many have been completed out of the total amount")
@click.option("--with-youtube-url", default=False, is_flag=True, help="Find and search for the Youtube Music URL")
@click.option("--with-youtube-url-cache-from", default=None,
              help="Preload the cache with Youtube URLs from a previously generated file. Null entries will be "
                   "skipped and not loaded. Only takes effect when the `--with-youtube-url` flag is used.")
@click.option("--with-youtube-url-cache-unvalidated", default=False, is_flag=True,
              help="Use unvalidated Youtube URLs from previously generated file. Only takes effect when the "
                   "`--with-youtube-url-cache-from` flag is used.")
@time_taken
def download(filename: str, show_progress: bool, with_youtube_url: bool, with_youtube_url_cache_from: str,
             with_youtube_url_cache_unvalidated: bool) -> None:
    logger.debug(f"'playlist' 'download' subcommand invoked")

    sptfy = get_sptfy()
    logger.debug(f"Retrieve or validate filename")
    if filename is None:
        filename = get_filename(sptfy)
    elif filename.strip() == "":
        print(f"ERROR: Filename cannot be blank or null!")
        sys.exit(1)
    elif not filename.strip().endswith('.json'):
        print(f"ERROR: Filename must end with '.json'")
        sys.exit(1)
    else:
        filename = filename

    print(f"The filename will be {filename}")

    logger.debug(f"Retrieve list of playlists without songs")
    playlists_no_songs = sptfy.get_all_playlists_no_songs()
    logger.info(f'Number of playlists found: {len(playlists_no_songs)}')

    num_playlists = len(playlists_no_songs) + 0  # There is a +1 for liked songs
    playlists = get_playlists_with_songs(
        num_playlists=num_playlists,
        playlists_no_songs=playlists_no_songs,
        sptfy=sptfy,
        show_progress=show_progress
    )

    if with_youtube_url:
        modify_playlists_with_songs_youtube_url(playlists, show_progress,
                                                with_youtube_url_cache_from,
                                                with_youtube_url_cache_unvalidated)

    with open(filename, 'w') as file:
        logger.info(f"Writing to file '{filename}' in the local directory")
        file.write(json.dumps(playlists, default=get_obj_dict))
        logger.info(f"Number of playlists processed: {len(playlists)} (There is a +0 for liked songs)")

    print("Finished!")


def get_filename(sptfy: Sptfy) -> str:
    date = datetime.now()
    user_id = sptfy.get_user_id()
    filename = f"playlists-{user_id}-{date.strftime('%Y_%m_%dT%H_%M_%S')}.json"
    return filename


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


def get_playlist_with_songs(playlist: PlaylistNoSongs, sptfy: Sptfy) -> PlaylistWithSongs:
    logger.debug(f"Retrieve song for playlist")
    songs: List[Song] = sptfy.get_playlist_content(playlist_id=playlist.id)
    playlist_with_songs = PlaylistWithSongs(
        playlist=playlist,
        songs=songs
    )
    return playlist_with_songs


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
        cache_value = ytm.get_youtube_url(song)
        song.youtube_url = cache_value.youtube_url
        song.youtube_url_validated = cache_value.youtube_url_validated


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
                ytm.add_to_cache(song.spotify_url, song.youtube_url, song.youtube_url_validated)

    except FileNotFoundError:
        logger.error(f"file: {filename} could not be found")
        sys.exit(1)
