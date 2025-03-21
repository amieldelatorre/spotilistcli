import pytest
import tempfile
import sptfy
import spotipy
import json
import os
from datetime import datetime
from commands import playlist


FROZEN_TIME = datetime(2024, 4, 3, 21, 2, 0)


@pytest.fixture
def sptfy_mock():
    sptfy_obj = sptfy.Sptfy(
        spotify_client_id="something",
        spotify_client_secret="something_secret",
        spotify_redirect_uri="something"
    )
    return sptfy_obj


@pytest.fixture
def patch_datetime_now(monkeypatch):
    class MockedDateTime(datetime):
        @classmethod
        def now(cls):
            return FROZEN_TIME

    monkeypatch.setattr(
        "commands.playlist.datetime",
        MockedDateTime
    )


def test_get_filename(monkeypatch, sptfy_mock, patch_datetime_now):
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

    actual = playlist.get_filename(sptfy_mock)

    assert actual == "playlists-01234567890-2024_04_03T21_02_00.json"


def test_get_playlist_with_songs(monkeypatch, sptfy_mock):
    with open("tests/files/sptfy_playlist_items_queries.json.test", "r") as file:
        data = json.load(file)
    data_iter = iter(data)

    monkeypatch.setattr(
        spotipy.Spotify, "playlist_items",
        lambda self, playlist_id, limit, offset, fields: next(data_iter)
    )

    playlist_no_song = sptfy.PlaylistNoSongs(
        id="somethingAb1234Af9D9Cb",
        name="A Playlist",
        total=347,
        spotify_playlist_url="https://example.invalid"
    )

    actual = playlist.get_playlist_with_songs(playlist_no_song, sptfy_mock)

    assert actual.total == 347


@pytest.mark.parametrize("args_list, playlist_found, expected_outputs, exit_expected, expected_exit_code", [
    (
        ["--playlist-id", "somethingAb1234Af9D9Cb"],
        True,
        ["A Track"],
        False,
        0,
    ),
    (
        ["--playlist-id", "somethingAb1234Af9D9Cb", "--show-url"],
        True,
        ["A Track\thttps://example.invalid"],
        False,
        0,
    ),
    (
        ["--playlist-id", "somethingAb1234Af9D9Cb", "--show-artists"],
        True,
        ["A Track\tartist", "A Track\tartist,artist "],
        False,
        0,
    ),
    (
        ["--playlist-id"],
        True,
        [],
        True,
        2,
    ),
    (
        ["--playlist-id", "somethingAb1234Af9D9Cb"],
        False,
        [],
        True,
        1,
    )
])
def test_show_playlist(monkeypatch, capfd, sptfy_mock,
                       args_list, playlist_found, expected_outputs, exit_expected, expected_exit_code):
    with open("tests/files/sptfy_playlist_items_queries.json.test", "r") as file:
        data = json.load(file)
    data_iter = iter(data)

    monkeypatch.setattr(
        spotipy.Spotify, "playlist_items",
        lambda self, playlist_id, limit, offset, fields: next(data_iter)
    )

    monkeypatch.setattr(
        sptfy.Sptfy, "playlist_exists",
        lambda self, playlist_id: playlist_found
    )
    if exit_expected:
        with pytest.raises(SystemExit) as exit_wrapper:
            playlist.show_playlist(args_list, sptfy_mock)
        assert exit_wrapper.type == SystemExit
        assert exit_wrapper.value.code == expected_exit_code
    else:
        playlist.show_playlist(args_list, sptfy_mock)
        out, err = capfd.readouterr()
        num_lines = len(out.split("\n"))
        assert num_lines == 151
        for expected_output in expected_outputs:
            assert expected_output in out


@pytest.mark.parametrize("args_list, expected_outputs", [
    (
        [],
        ["Playlist Name"]
    ),
    (
        ["--show-id"],
        ["Playlist Name\tsomethingAb1234Af9D9Cb"]
    ),
])
def test_list_playlists(monkeypatch, capfd, sptfy_mock, args_list, expected_outputs):
    with open("tests/files/sptfy_current_user_playlists_queries.json.test", "r") as file:
        data = json.load(file)
    data_iter = iter(data)

    monkeypatch.setattr(spotipy.Spotify, "current_user_playlists", lambda self, limit, offset: next(data_iter))

    playlist.list_playlists(args_list, sptfy_mock)
    out, err = capfd.readouterr()
    num_lines = len(out.split("\n"))
    assert num_lines == 119
    for expected_output in expected_outputs:
        assert expected_output in out


def test_download_playlists_fail_filename(sptfy_mock):
    args_list = ["--filename", "does_not_end_in_dot_json"]

    with pytest.raises(SystemExit) as exit_wrapper:
        playlist.download_playlists(args_list, sptfy_mock)
    assert exit_wrapper.type == SystemExit
    assert exit_wrapper.value.code == 1


@pytest.fixture
def patch_get_all_playlists_no_songs(monkeypatch, sptfy_mock):
    with open("tests/files/sptfy_current_user_playlists_queries.json.test", "r") as file:
        data = json.load(file)
    data_iter = iter(data)

    monkeypatch.setattr(spotipy.Spotify, "current_user_playlists", lambda self, limit, offset: next(data_iter))
    # playlists = sptfy_mock.get_all_playlists_no_songs()
    #
    # monkeypatch.setattr(
    #     sptfy.Sptfy, "get_all_playlists_no_songs",
    #     lambda self: playlists
    # )


@pytest.fixture
def patch_get_playlist_with_songs(monkeypatch):
    playlist_no_songs = sptfy.PlaylistNoSongs(
        id="somethingAb1234Af9D9Cb",
        name="A Playlist",
        total=2,
        spotify_playlist_url="https://example.invalid"
    )

    songs = [
        sptfy.Song(
            name="A Song",
            artists=["Artist"],
            spotify_url="https://example.invalid",
            youtube_url=None
        ),
        sptfy.Song(
            name="A Song",
            artists=["Artist", "Artist2"],
            spotify_url="https://example.invalid",
            youtube_url=None
        )
    ]
    playlist_with_songs = sptfy.PlaylistWithSongs(
        playlist=playlist_no_songs,
        songs=songs
    )

    monkeypatch.setattr(
        playlist, "get_playlist_with_songs",
        lambda playlist_with_no_song, sptfy_arg: playlist_with_songs
    )


@pytest.fixture
def patch_get_saved_tracks_as_playlist(monkeypatch):
    with open("tests/files/sptfy_playlist_items_queries.json.test", "r") as file:
        data = json.load(file)
    data_iter = iter(data)

    monkeypatch.setattr(
        spotipy.Spotify, "current_user_saved_tracks",
        lambda self, limit, offset: next(data_iter)
    )


def test_download_playlists(monkeypatch, capfd, sptfy_mock,
                            patch_get_all_playlists_no_songs, patch_get_playlist_with_songs,
                            patch_get_saved_tracks_as_playlist):
    tmpdir = tempfile.mkdtemp()
    temp_file = os.path.join(tmpdir, "test.json")
    args_list = ["--filename", temp_file]

    playlist.download_playlists(args_list, sptfy_mock)

    with open(temp_file) as file:
        actual = json.load(file)

    with open("tests/files/expected_download_playlist.json.test") as file:
        expected = json.load(file)

    assert actual == expected

