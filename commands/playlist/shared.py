from typing import List
from log import logger
from sptfy import PlaylistNoSongs


def filter_playlists(user_id: str, playlists: List[PlaylistNoSongs], filter_owned: bool) -> List[PlaylistNoSongs]:
    logger.debug("Filtering playlists")
    if not any([filter_owned]):
        return playlists

    filtered_playlists = []

    owned_playlists = []
    if filter_owned:
        owned_playlists = [playlist for playlist in playlists if playlist.owner_spotify_id == user_id]
    filtered_playlists.extend(owned_playlists)

    return filtered_playlists
