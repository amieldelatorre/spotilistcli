import json
import spotipy
import pytest
import sptfy
import helpers


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
