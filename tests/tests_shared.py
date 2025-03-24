import pytest
import spotipy


@pytest.fixture
def patch_spotipy_me(monkeypatch):
    expected_query_return = {
        "display_name": "First Last",
        "external_urls": {
            "spotify": "https://example.invalid"
        },
        "href": "https://example.invalid",
        "id": "111111111111",
        "images": [
            {
                "url": "https://example.invalid",
                "height": 298,
                "width": 298
            },
            {
                "url": "https://example.invalid",
                "height": 298,
                "width": 298
            },
            {
                "url": "https://example.invalid",
                "height": 298,
                "width": 298
            }
        ],
        "type": "user",
        "uri": "spotify:user:111111111111",
        "followers": {
            "href": None,
            "total": 220
        }

    }
    monkeypatch.setattr(
        spotipy.Spotify, "me",
        lambda self: expected_query_return
    )

