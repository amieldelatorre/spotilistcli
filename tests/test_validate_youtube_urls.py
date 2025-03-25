import json
import os.path
import tempfile
from tempfile import tempdir
import pytest

from commands.validate.youtube_urls import (load_playlists_file, get_songs_to_validate,
                                            get_songs_to_validate_iterator, update_validated_song,
                                            overwrite_youtube_url, is_valid_youtube_music_url)
from sptfy import Song, PlaylistWithSongs, PlaylistNoSongs


def test_load_playlists_file():
    filename = "tests/files/validate_youtube_urls_input.json.test"
    actual = load_playlists_file(filename)

    assert len(actual) == 119


def test_get_songs_to_validate():
    filename = "tests/files/validate_youtube_urls_input.json.test"
    playlists = load_playlists_file(filename)
    expected = {
        "https://example01.invalid": Song(
            name="A Song",
            artists=[
                "Artist"
            ],
            spotify_url="https://example01.invalid",
            youtube_url="https://music.youtube.com/watch?v=01",
            youtube_url_validated=False,
        ),
        "https://example02.invalid": Song(
            name="A Song",
            artists=[
                "Artist",
                "Artist2"
            ],
            spotify_url="https://example02.invalid",
            youtube_url="https://music.youtube.com/watch?v=02",
            youtube_url_validated=False,
        ),
        "https://example03.invalid": Song(
            name="A Song",
            artists=[
                "Artist"
            ],
            spotify_url="https://example03.invalid",
            youtube_url="https://music.youtube.com/watch?v=03",
            youtube_url_validated=False,
        ),
        "https://example.invalid": Song(
            name="A Song",
            artists=[
                "Artist",
            ],
            spotify_url="https://example.invalid",
            youtube_url=None,
            youtube_url_validated=False,
        ),
    }


    actual = get_songs_to_validate(playlists)

    assert len(actual) == 4
    assert actual == expected


def test_get_songs_to_validate_iterator():
    test_input = {
        "https://example01.invalid": Song(
            name="A Song",
            artists=[
                "Artist"
            ],
            spotify_url="https://example01.invalid",
            youtube_url="https://music.youtube.com/watch?v=01",
            youtube_url_validated=False,
        ),
        "https://example02.invalid": Song(
            name="A Song",
            artists=[
                "Artist",
                "Artist2"
            ],
            spotify_url="https://example02.invalid",
            youtube_url="https://music.youtube.com/watch?v=02",
            youtube_url_validated=False,
        ),
        "https://example03.invalid": Song(
            name="A Song",
            artists=[
                "Artist"
            ],
            spotify_url="https://example03.invalid",
            youtube_url="https://music.youtube.com/watch?v=03",
            youtube_url_validated=False,
        ),
        "https://example.invalid": Song(
            name="A Song",
            artists=[
                "Artist",
                "Artist2"
            ],
            spotify_url="https://example.invalid",
            youtube_url="https://music.youtube.com/watch?v=wxyz",
            youtube_url_validated=False,
        ),
    }

    iterator = get_songs_to_validate_iterator(test_input)
    num_next = 0
    while True:
        try:
            next(iterator)
            num_next += 1
        except StopIteration:
            break

    assert num_next == 4


def test_update_validated_song():
    filename = "tests/files/validate_youtube_urls_input.json.test"
    playlists = load_playlists_file(filename)
    tmpdir = tempfile.mkdtemp()
    temp_file = os.path.join(tmpdir, "test.json")

    test_case = ["https://example01.invalid", "https://example02.invalid", "https://example03.invalid"]
    for valid in test_case:
        playlists = update_validated_song(playlists, valid, temp_file)


    with open(temp_file) as file:
        actual = json.load(file)

    with open("tests/files/validate_youtube_urls_expected_update_validated_songs.json.test") as file:
        expected = json.load(file)

    assert actual == expected


def test_overwrite_youtube_url():
    input_playlists = [
        PlaylistWithSongs(PlaylistNoSongs(
            id="somethingAb1234Af9D9Cb",
            name="A Playlist",
            total=2,
            spotify_playlist_url="https://example.invalid",
            owner_spotify_id="111111111111"
        ), songs=[
           Song(
               name="A song",
               artists=["Artist"],
               spotify_url="https://example.invalid",
               youtube_url="https://music.youtube.com/watch?v=wxyz"
           ),
            Song(
                name="A song",
                artists=["Artist"],
                spotify_url="https://example2.invalid",
                youtube_url="https://music.youtube.com/watch?v=abcd"
            )
        ]),
        PlaylistWithSongs(PlaylistNoSongs(
            id="somethingAb1234Af9D9Cb",
            name="A Playlist",
            total=2,
            spotify_playlist_url="https://example.invalid",
            owner_spotify_id="111111111111"
        ), songs=[
            Song(
                name="A song",
                artists=["Artist"],
                spotify_url="https://example.invalid",
                youtube_url="https://music.youtube.com/watch?v=wxyz"
            ),
            Song(
                name="A song",
                artists=["Artist"],
                spotify_url="https://example2.invalid",
                youtube_url="https://music.youtube.com/watch?v=abcd"
            )
        ])
    ]
    input_spotify_url = "https://example.invalid"
    input_youtube_url = "https://music.youtube.com/watch?v=1234"
    expected = [
        PlaylistWithSongs(PlaylistNoSongs(
            id="somethingAb1234Af9D9Cb",
            name="A Playlist",
            total=2,
            spotify_playlist_url="https://example.invalid",
            owner_spotify_id="111111111111"
        ), songs=[
            Song(
                name="A song",
                artists=["Artist"],
                spotify_url="https://example.invalid",
                youtube_url="https://music.youtube.com/watch?v=1234"
            ),
            Song(
                name="A song",
                artists=["Artist"],
                spotify_url="https://example2.invalid",
                youtube_url="https://music.youtube.com/watch?v=abcd"
            )
        ]),
        PlaylistWithSongs(PlaylistNoSongs(
            id="somethingAb1234Af9D9Cb",
            name="A Playlist",
            total=2,
            spotify_playlist_url="https://example.invalid",
            owner_spotify_id="111111111111"
        ), songs=[
            Song(
                name="A song",
                artists=["Artist"],
                spotify_url="https://example.invalid",
                youtube_url="https://music.youtube.com/watch?v=1234"
            ),
            Song(
                name="A song",
                artists=["Artist"],
                spotify_url="https://example2.invalid",
                youtube_url="https://music.youtube.com/watch?v=abcd"
            )
        ])
    ]

    actual = overwrite_youtube_url(input_playlists, input_spotify_url, input_youtube_url)

    assert actual == expected


@pytest.mark.parametrize("url, expected", [
    ("https://music.youtube.com/watch?v=1234", True),
    ("http://music.youtube.com/watch?v=1234", True),
    ("htts://music.youtube.com/watch?v=1234", False),
    ("music.youtube.com/watch?v=1234", False),
    ("music.youtube.com/watch", False),
    ("music.youtube.com", False),
    ("music", False)
])
def test_is_valid_url(url, expected):
    actual = is_valid_youtube_music_url(url)
    assert actual == expected

