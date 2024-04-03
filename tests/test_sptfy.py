import json
import spotipy
import pytest
import sptfy


@pytest.fixture
def sptfy_mock():
    sptfy_obj = sptfy.Sptfy(
        spotify_client_id="something",
        spotify_client_secret="something_secret",
        spotify_redirect_uri="something"
    )
    return sptfy_obj


def test_get_artists():
    with open("tests/files/test_get_artists_spotify_url_input_playlist.json.test", "r") as file:
        data = json.load(file)

    expected_results = [
        ['artist1'], ["artist2"], ["artist3"], ["artist4", "artist5", "artist6", "artist7", "artist8"], []
    ]
    expected_num_processed = len(expected_results)

    num_processed = 0
    for index, item in enumerate(data["items"]):
        if item is None or item["track"] is None:
            continue
        assert sptfy.get_artists(item) == expected_results[index]
        num_processed += 1

    assert num_processed == expected_num_processed


def test_get_spotify_url():
    with open("tests/files/test_get_artists_spotify_url_input_playlist.json.test", "r") as file:
        data = json.load(file)

    expected_result = [
        "https://example.invalid1", "https://example.invalid2", "https://example.invalid3",
        "https://example.invalid4", "https://example.invalid5"

    ]
    expected_num_processed = len(expected_result)

    num_processed = 0
    for index, item in enumerate(data["items"]):
        if item is None or item["track"] is None:
            continue
        assert sptfy.get_spotify_url(item) == expected_result[index]
        num_processed += 1

    assert num_processed == expected_num_processed


def test_get_all_playlists_no_songs(monkeypatch, sptfy_mock):
    with open("tests/files/sptfy_current_user_playlists_queries.json.test", "r") as file:
        data = json.load(file)
    data_iter = iter(data)

    monkeypatch.setattr(spotipy.Spotify, "current_user_playlists", lambda self, limit, offset: next(data_iter))
    playlists = sptfy_mock.get_all_playlists_no_songs()

    for playlist in playlists:
        assert type(playlist) is sptfy.PlaylistNoSongs
    assert len(playlists) == 118


def test_get_playlist_content(monkeypatch, sptfy_mock):
    with open("tests/files/sptfy_playlist_items_queries.json.test", "r") as file:
        data = json.load(file)
    data_iter = iter(data)

    monkeypatch.setattr(
        spotipy.Spotify, "playlist_items",
        lambda self, playlist_id, limit, offset, fields: next(data_iter)
    )
    playlist_items = sptfy_mock.get_playlist_content("something")

    for playlist_item in playlist_items:
        assert type(playlist_item) is sptfy.Song
    assert len(playlist_items) == 150


def test_get_saved_tracks_as_playlist(monkeypatch, sptfy_mock):
    with open("tests/files/sptfy_playlist_items_queries.json.test", "r") as file:
        data = json.load(file)
    data_iter = iter(data)

    monkeypatch.setattr(
        spotipy.Spotify, "current_user_saved_tracks",
        lambda self, limit, offset: next(data_iter)
    )
    liked_song_playlist = sptfy_mock.get_saved_tracks_as_playlist()
    assert type(liked_song_playlist) is sptfy.PlaylistWithSongs
    assert liked_song_playlist.total == 150


def test_get_user_id(monkeypatch, sptfy_mock):
    expected_query_return = {
        "display_name": "First Last",
        "external_urls": {
            "spotify": "https://example.invalid"
        },
        "href": "https://example.invalid",
        "id": "01234567890",
        "images": [
            {
                "url": "https://example.invalid",
                "height": 300,
                "width": 300
            },
            {
                "url": "https://example.invalid",
                "height": 300,
                "width": 300
            },
            {
                "url": "https://example.invalid",
                "height": 300,
                "width": 300
            }
        ],
        "type": "user",
        "uri": "spotify:user:01234567890",
        "followers": {
            "href": None,
            "total": 222
        }

    }

    monkeypatch.setattr(
        spotipy.Spotify, "me",
        lambda self: expected_query_return
    )
    user_id = sptfy_mock.get_user_id()

    assert user_id == expected_query_return["id"]


@pytest.mark.parametrize("playlist_exists", [
    True,
    False
])
def test_playlist_exists(monkeypatch, sptfy_mock, playlist_exists):

    def playlist_exists_playlist_not_found(self, playlist_id):
        raise spotipy.SpotifyException(
            http_status=400,
            code="123",
            msg="playlist not found"
        )

    if playlist_exists:
        monkeypatch.setattr(
            spotipy.Spotify, "playlist",
            lambda self, playlist_id: None
        )
        result = sptfy_mock.playlist_exists("1234567890")
        assert result is True
    else:
        monkeypatch.setattr(
            spotipy.Spotify, "playlist",
            playlist_exists_playlist_not_found
        )
        result = sptfy_mock.playlist_exists("1234567890")
        assert result is False


def test_get_user_top_artists(monkeypatch, sptfy_mock):
    with open("tests/files/sptfy_current_user_top_artists_queries.json.test", "r") as file:
        data = json.load(file)

    monkeypatch.setattr(
        spotipy.Spotify, "current_user_top_artists",
        lambda self, limit, offset, time_range: data
    )

    artists = sptfy_mock.get_user_top_artists()
    for artist in artists:
        assert type(artist) is sptfy.Artist


def test_get_user_top_tracks(monkeypatch, sptfy_mock):
    with open("tests/files/sptfy_current_user_top_tracks_queries.json.test", "r") as file:
        data = json.load(file)

    monkeypatch.setattr(
        spotipy.Spotify, "current_user_top_tracks",
        lambda self, limit, offset, time_range: data
    )

    songs = sptfy_mock.get_user_top_tracks()
    for song in songs:
        assert type(song) is sptfy.Song


def test_current_user_info(monkeypatch, sptfy_mock):
    user_data = {
        "display_name": "First Last",
        "external_urls": {
            "spotify": "https://example.invalid"
        },
        "href": "https://example.invalid",
        "id": "01234567890",
        "images": [
            {
                "url": "https://example.invalid",
                "height": 300,
                "width": 300
            },
            {
                "url": "https://example.invalid",
                "height": 300,
                "width": 300
            }
        ],
        "type": "user",
        "uri": "spotify:user:01234567890",
        "followers": {
            "href": None,
            "total": 111
        }
    }

    monkeypatch.setattr(
        spotipy.Spotify, "current_user",
        lambda self: user_data
    )

    user = sptfy_mock.get_current_user_info()

    assert type(user) is sptfy.User
    assert user.name == user_data["display_name"]
    assert user.id == user_data["id"]
    assert user.url == user_data["external_urls"]["spotify"]
