import click
import glob
import json

from typing import List, Dict, Set
from pathlib import Path
from sptfy import get_sptfy


@click.command(help="Scrobble extended listening to last.fm")
@click.option("--spotify-extended-listening-history-dir", required=True,
              help="Unzipped directory of the exported spotify extended listening history data")
@click.option("--unified-history-filename", default="unified_listening_history.json", 
              help="The file that will be read or generated that has collated all the Streaming_History_* files." \
                    "This will read the file if it exists, or create the file if missing")
@click.option("--track-db-filename", default="tracks_db.json", help="Local database of spotify track details")
def lastfm(
    spotify_extended_listening_history_dir: str,
    unified_history_filename: str,
    track_db_filename: str,
):
    unified_history = read_or_create_unified_history_file(spotify_extended_listening_history_dir, unified_history_filename)
    track_db = load_track_db(track_db_filename)
    tracks_missing_from_track_db = get_tracks_missing_from_track_db(unified_history, track_db)

    # print(len(tracks_missing_from_track_db))
    if len(tracks_missing_from_track_db) > 0:
        add_missing_tracks(tracks_missing_from_track_db, track_db, track_db_filename)


def add_missing_tracks(missing_tracks: Set[str], track_db: Dict, track_db_filename: str):
    sptfy = get_sptfy()
    missing_tracks_list = list(missing_tracks)

    for index in range(0, len(missing_tracks_list), 50):
        batch = missing_tracks_list[index : index + 50]

        tracks_data = sptfy.get_tracks(batch)

        for track in tracks_data:
            uri = track["uri"]
            track_db[uri] = track

        with open(track_db_filename, "w") as f:
            json.dump(track_db, f, indent=2, sort_keys=True)


def get_tracks_missing_from_track_db(unified_history: List[Dict], track_db: Dict) -> Set[str]:
    missing_tracks = set()
    for track in unified_history:
        if "spotify_track_uri" in track and track["spotify_track_uri"] is not None and track["spotify_track_uri"] not in track_db:
            missing_tracks.add(track["spotify_track_uri"])
    return missing_tracks


def load_track_db(track_db_filename: str) -> Dict:
    track_db_file = Path(track_db_filename)

    if track_db_file.exists():
        with open(track_db_file, "r") as f:
            track_db = json.load(f)
            return track_db
        
    return {}


def read_or_create_unified_history_file(spotify_extended_listening_history_dir: str, unified_history_filename: str) -> List[Dict]:
    unified_history_file = Path(unified_history_filename)

    if unified_history_file.exists():
        with open(unified_history_file, "r") as f:
            unified_history = json.load(f)
            return unified_history
    
    streaming_history_files = glob.glob(f"{spotify_extended_listening_history_dir}/Streaming_History*")
    streaming_history_files.sort()

    unified_data = []
    for filename in streaming_history_files:
        with open(filename, "r") as f:
            file_data = json.load(f)
            unified_data.extend(file_data)
    
    with open(unified_history_file, "w") as f:
        json.dump(unified_data, f, indent=2, sort_keys=True)
    return unified_data
