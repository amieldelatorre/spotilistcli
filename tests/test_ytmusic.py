import ytmusic
import pytest
import ytmusicapi
import sptfy
from ytmusic import YTMusicCache


@pytest.fixture
def ytm_mock():
    ytm_obj = ytmusic.YTM()
    return ytm_obj


@pytest.mark.parametrize("test_case", [
    {
        "name": "",
        "artists": [""],
        "search_results": [],
        "expected": None
    },
    {
        "name": "abcd",
        "artists": [""],
        "search_results": [{"title": "wxyz"}],
        "expected": None
    },
    {
        "name": "aBcd",
        "artists": [""],
        "search_results": [{}],
        "expected": None
    },
    {
        "name": "aBcd",
        "artists": [""],
        "search_results": [{"title": "ABCD", "videoId": "wxyz"}],
        "expected": "https://music.youtube.com/watch?v=wxyz"
    },
])
def test_search_youtube_music(monkeypatch, ytm_mock, test_case):
    name = test_case["name"]
    artists = test_case["artists"]
    search_results = test_case["search_results"]
    expected = test_case["expected"]

    monkeypatch.setattr(ytmusicapi.YTMusic, "search", lambda self, query, filter, limit: search_results)
    actual = ytm_mock.search_youtube_music(name, artists)

    assert actual == expected


@pytest.mark.parametrize("test_case", [
    {
        "song": sptfy.Song(
                name="A Song",
                artists=["Artist"],
                album=sptfy.Album(
                    name="An Album",
                    artists=["Artist"],
                    release_date="2001-01-01",
                    images=[
                        sptfy.AlbumImage(
                            url="https://example.invalid",
                            height=640,
                            width=640
                        )
                    ]
                ),
                track_number=1,
                disc_number=1,
                duration_ms=244000,
                external_ids=sptfy.ExternalIds("something", None, None),
                spotify_url="https://example.invalid",
                youtube_url=None
            ),
        "cache": {},
        "search_result": [],
        "expected_num_calls_to_search": 1,
        "expected_value": YTMusicCache(None, False, False),
    },
    {
        "song": sptfy.Song(
            name="A Song",
            artists=["Artist"],
            album=sptfy.Album(
                    name="An Album",
                    artists=["Artist"],
                    release_date="2001-01-01",
                    images=[
                        sptfy.AlbumImage(
                            url="https://example.invalid",
                            height=640,
                            width=640
                        )
                    ]
                ),
            track_number=1,
            disc_number=1,
            duration_ms=244000,
            external_ids=sptfy.ExternalIds("something", None, None),
            spotify_url="https://example.invalid",
            youtube_url=None
        ),
        "cache": {},
        "search_result": [{"title": "a song", "videoId": "1234"}],
        "expected_num_calls_to_search": 1,
        "expected_value": YTMusicCache("https://music.youtube.com/watch?v=1234", False, False),
    },
    {
        "song": sptfy.Song(
            name="A Song",
            artists=["Artist"],
            album=sptfy.Album(
                    name="An Album",
                    artists=["Artist"],
                    release_date="2001-01-01",
                    images=[
                        sptfy.AlbumImage(
                            url="https://example.invalid",
                            height=640,
                            width=640
                        )
                    ]
                ),
            track_number=1,
            disc_number=1,
            duration_ms=244000,
            external_ids=sptfy.ExternalIds("something", None, None),
            spotify_url="https://example.invalid",
            youtube_url=None
        ),
        "cache": {
            "https://example.invalid": YTMusicCache("https://music.youtube.com/watch?v=1234", False, False)
        },
        "search_result": [{"title": "a song", "videoId": "1234"}],
        "expected_num_calls_to_search": 0,
        "expected_value": YTMusicCache("https://music.youtube.com/watch?v=1234", False, False)
    },
    {
        "song": sptfy.Song(
            name="A Song",
            artists=["Artist"],
            album=sptfy.Album(
                    name="An Album",
                    artists=["Artist"],
                    release_date="2001-01-01",
                    images=[
                        sptfy.AlbumImage(
                            url="https://example.invalid",
                            height=640,
                            width=640
                        )
                    ]
                ),
            track_number=1,
            disc_number=1,
            duration_ms=244000,
            external_ids=sptfy.ExternalIds("something", None, None),
            spotify_url="https://example.invalid",
            youtube_url=None
        ),
        "cache": {
            "https://example.invalid": None
        },
        "search_result": [],
        "expected_num_calls_to_search": 0,
        "expected_value": None
    },
])
def test_get_youtube_url(monkeypatch, ytm_mock, test_case):
    song = test_case["song"]
    cache = test_case["cache"]
    search_result = test_case["search_result"]
    expected_num_calls_to_search = test_case["expected_num_calls_to_search"]
    expected_value = test_case["expected_value"]

    calls = 0
    def mocked_func(self, query, filter, limit):
        nonlocal calls
        calls += 1
        return search_result

    monkeypatch.setattr(ytmusicapi.YTMusic, "search", mocked_func)
    ytm_mock.cache = cache
    actual = ytm_mock.get_youtube_url(song)

    assert calls == expected_num_calls_to_search
    assert actual == expected_value


@pytest.mark.parametrize("test_case", [
    {
        "spotify_url": "https://example.invalid",
        "youtube_url": "https://music.youtube.com/watch?v=wxyz",
        "youtube_url_validated": False,
        "youtube_url_permanently_skip": False,
        "expected": {
            "https://example.invalid": YTMusicCache(youtube_url="https://music.youtube.com/watch?v=wxyz", youtube_url_validated=False, youtube_url_permanently_skip=False)
        }
    },
    {
        "spotify_url": "https://example.invalid",
        "youtube_url": "https://music.youtube.com/watch?v=wxyz",
        "youtube_url_validated": False,
        "youtube_url_permanently_skip": False,
        "expected": {
            "https://example.invalid": YTMusicCache(youtube_url="https://music.youtube.com/watch?v=wxyz",
                                                    youtube_url_validated=False,
                                                    youtube_url_permanently_skip=False)
        }
    }
])
def test_add_to_cache(ytm_mock, test_case):
    input_spotify_url = test_case["spotify_url"]
    input_youtube_url = test_case["youtube_url"]
    input_youtube_url_validated = test_case["youtube_url_validated"]
    input_youtube_url_permanently_skip = test_case["youtube_url_permanently_skip"]
    expected = test_case["expected"]

    ytm_mock.add_to_cache(input_spotify_url, input_youtube_url, input_youtube_url_validated, input_youtube_url_permanently_skip)

    assert ytm_mock.cache == expected
