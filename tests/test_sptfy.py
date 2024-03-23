import json
import sptfy


def test_get_artists():
    with open("tests/files/test_get_artists_spotify_url_input_playlist.json.test", "r") as file:
        data = json.load(file)

    expected_results = [['string'], ['string', 'string', 'string'], []]
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

    expected_result = ["string1", "string2", "string3"]
    expected_num_processed = 3

    num_processed = 0
    for index, item in enumerate(data["items"]):
        if item is None or item["track"] is None:
            continue
        assert sptfy.get_spotify_url(item) == expected_result[index]
        num_processed += 1

    assert num_processed == expected_num_processed
