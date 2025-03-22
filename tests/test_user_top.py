import pytest
import spotipy
from click.testing import CliRunner

import sptfy
import json
import commands


@pytest.fixture
def sptfy_mock():
    sptfy_obj = sptfy.Sptfy(
        spotify_client_id="something",
        spotify_client_secret="something_secret",
        spotify_redirect_uri="something"
    )
    return sptfy_obj


@pytest.mark.parametrize("args_list, exit_expected, expected_exit_code", [
    (["--help"], True, 0),
    (["asdf"], True, 2),
    ([""], True, 2),
    (["artists"], False, 0),
    (["tracks"], False, 0),
])
def test_user_top_command(monkeypatch, sptfy_mock, args_list, exit_expected, expected_exit_code):
    runner = CliRunner()

    monkeypatch.setattr("os.path.exists", lambda filepath: True)
    if exit_expected:
        result = runner.invoke(commands.user_top.user_top, args_list)
        assert result.exit_code == expected_exit_code
    else:
        if args_list[0] == "artists":
            with open("tests/files/sptfy_current_user_top_artists_queries.json.test", "r") as file:
                data = json.load(file)
                monkeypatch.setattr(
                    spotipy.Spotify, "current_user_top_artists",
                    lambda self, limit, offset, time_range: data
                )
                result = runner.invoke(commands.user_top.user_top, args_list)
                num_lines = len(result.stdout.split("\n"))
                assert num_lines == 11
        else:
            with open("tests/files/sptfy_current_user_top_tracks_queries.json.test", "r") as file:
                data = json.load(file)
                monkeypatch.setattr(
                    spotipy.Spotify, "current_user_top_tracks",
                    lambda self, limit, offset, time_range: data
                )
                result = runner.invoke(commands.user_top.user_top, args_list)
                num_lines = len(result.stdout.split("\n"))
                assert num_lines == 11


@pytest.mark.parametrize("args_list, exit_expected, expected_exit_code", [
    (["--help"], True, 0),
    (["adf"], True, 2),
    (["--limit", "51"], True, 2),
    (["--limit", "0"], True, 2),
    (["--limit", "-1"], True, 2),
    (["--offset", "-1"], True, 2),
    (["--time-range", "short"], True, 2),
    (["--time--range", "medium_terms"], True, 2),
    (["--time-range", "short_term"], False, 0),
    (["--offset", "0"], False, 1),
    ([], False, 0),
])
def test_top_artists_subcommand(monkeypatch, sptfy_mock, args_list, exit_expected, expected_exit_code):
    runner = CliRunner()

    with open("tests/files/sptfy_current_user_top_tracks_queries.json.test", "r") as file:
        data = json.load(file)

    if exit_expected:
        result = runner.invoke(commands.user_top.artists, args_list)
        assert result.exit_code == expected_exit_code
    else:
        monkeypatch.setattr(
            spotipy.Spotify, "current_user_top_artists",
            lambda self, limit, offset, time_range: data
        )
        result = runner.invoke(commands.user_top.artists, args_list)
        num_lines = len(result.stdout.split("\n"))
        assert num_lines == 11


@pytest.mark.parametrize("args_list, exit_expected, expected_exit_code", [
    (["--help"], True, 0),
    (["adf"], True, 2),
    (["--limit", "51"], True, 2),
    (["--limit", "0"], True, 2),
    (["--limit", "-1"], True, 2),
    (["--offset", "-1"], True, 2),
    (["--time-range", "short"], True, 2),
    (["--time--range", "medium_terms"], True, 2),
    (["--time-range", "short_term"], False, 0),
    (["--offset", "0"], False, 1),
    ([], False, 0),
])
def test_top_tracks_subcommand(monkeypatch, sptfy_mock, args_list, exit_expected, expected_exit_code):
    runner = CliRunner()

    with open("tests/files/sptfy_current_user_top_tracks_queries.json.test", "r") as file:
        data = json.load(file)

    if exit_expected:
        result = runner.invoke(commands.user_top.tracks, args_list)
        assert result.exit_code == expected_exit_code
    else:
        monkeypatch.setattr(
            spotipy.Spotify, "current_user_top_tracks",
            lambda self, limit, offset, time_range: data
        )
        result = runner.invoke(commands.user_top.tracks, args_list)
        num_lines = len(result.stdout.split("\n"))
        assert num_lines == 11
