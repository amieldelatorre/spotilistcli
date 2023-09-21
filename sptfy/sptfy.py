import spotipy
import json
from spotipy.oauth2 import SpotifyOAuth
from dataclasses import dataclass
from typing import List, Dict
from log import logger


@dataclass
class Song:
    name: str
    artists: List[str]
    spotify_url: str

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True
        )

    def __repr__(self):
        return f"{self.name}"


@dataclass
class PlaylistNoSongs:
    id: str
    name: str
    total: int
    external_url: str

    def __repr__(self):
        return f"{self.name}"


@dataclass
class PlaylistWithSongs(PlaylistNoSongs):
    songs: List[Song]

    def __init__(self, playlist: PlaylistNoSongs, songs: List[Song]):
        self.id = playlist.id
        self.name = playlist.name
        self.total = playlist.total
        self.external_url = playlist.external_url
        self.songs = songs

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True
        )


def get_artists(song: Dict) -> List[str]:
    artists = []

    if song["track"]["artists"] is None:
        return artists
    artists = [artist["name"] for artist in song["track"]["artists"]]
    return artists


def get_spotify_url(song: Dict) -> str:
    spotify_url = 'None'
    if 'spotify' not in song['track']['external_urls']:
        return spotify_url
    spotify_url = song['track']['external_urls']["spotify"]
    return spotify_url


class Sptfy:
    def __init__(self, spotify_client_id, spotify_client_secret, spotify_redirect_uri):
        logger.info(f"Authenticating with spotify")
        auth_manager = SpotifyOAuth(
            open_browser=True,
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            redirect_uri=spotify_redirect_uri,
            scope="playlist-read-private,playlist-read-collaborative,user-library-read"
        )

        self.spotify = spotipy.Spotify(
            auth_manager=auth_manager
        )

    def get_all_playlists_no_songs(self, limit=50, offset=0) -> List[PlaylistNoSongs]:
        logger.info(f"Retrieving all playlists")
        playlists = []

        while True:
            query = self.spotify.current_user_playlists(
                limit=limit,
                offset=offset
            )
            for item in query['items']:
                playlist = PlaylistNoSongs(
                    id=item['id'],
                    name=item['name'],
                    total=item['tracks']['total'],
                    external_url=item['external_urls']['spotify']
                )
                playlists.append(playlist)
            if query['next'] is not None:
                offset += limit
            else:
                break
        return playlists

    def get_playlist_content(self, playlist_id: str, limit=100, offset=0):
        logger.debug(f"Retrieving contents for playlist '{playlist_id}'")
        songs = []
        while True:
            query = self.spotify.playlist_items(
                playlist_id=playlist_id,
                limit=limit,
                offset=offset,
                fields="items(track(name,artists(name),external_urls(spotify))),next"
            )

            for item in query["items"]:
                if item is None or item["track"] is None:
                    continue

                artists = get_artists(item)
                spotify_url = get_spotify_url(item)
                song = Song(
                    name=item["track"]["name"],
                    artists=artists,
                    spotify_url=spotify_url
                )
                songs.append(song)

            if query['next'] is not None:
                offset += limit
            else:
                break
        return songs

    def get_saved_tracks_as_playlist(self, limit=20, offset=0) -> PlaylistWithSongs:
        logger.debug(f"Retrieving saved tracks for user")

        songs = []
        while True:
            query = self.spotify.current_user_saved_tracks(
                limit=limit,
                offset=offset,
            )

            for item in query["items"]:
                if item is None or item["track"] is None:
                    continue

                artists = get_artists(item)
                spotify_url = get_spotify_url(item)
                song = Song(
                    name=item["track"]["name"],
                    artists=artists,
                    spotify_url=spotify_url
                )
                songs.append(song)

            if query['next'] is not None:
                offset += limit
            else:
                break

        playlist = PlaylistWithSongs(
            PlaylistNoSongs(
                id="liked_songs",
                name="Liked Songs",
                total=len(songs),
                external_url="None"
            ),
            songs=songs
        )
        return playlist

