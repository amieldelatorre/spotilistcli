import json
import sptfy


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
