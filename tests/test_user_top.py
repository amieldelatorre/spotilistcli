import pytest
import spotipy

import sptfy
import json
from commands import user_top


@pytest.fixture
def sptfy_mock():
    sptfy_obj = sptfy.Sptfy(
        spotify_client_id="something",
        spotify_client_secret="something_secret",
        spotify_redirect_uri="something"
    )
    return sptfy_obj


@pytest.mark.parametrize("args_list, exit_expected, expected_exit_code", [
    (["help"], True, 0),
    (["asdf"], True, 1),
    ([""], True, 1),
    (["artists"], False, 0),
    (["tracks"], False, 0),
])
def test_user_top_command(monkeypatch, capfd, sptfy_mock, args_list, exit_expected, expected_exit_code):
    monkeypatch.setattr("os.path.exists", lambda filepath: True)
    if exit_expected:
        with pytest.raises(SystemExit) as exit_wrapper:
            user_top.user_top_command(args_list, sptfy_mock)
        assert exit_wrapper.type == SystemExit
        assert exit_wrapper.value.code == expected_exit_code
    else:
        if args_list[0] == "artists":
            with open("tests/files/sptfy_current_user_top_artists_queries.json.test", "r") as file:
                data = json.load(file)
                monkeypatch.setattr(
                    spotipy.Spotify, "current_user_top_tracks",
                    lambda self, limit, offset, time_range: data
                )
                user_top.top_artists_subcommand(args_list[1:], sptfy_mock)
                out, err = capfd.readouterr()
                num_lines = len(out.split("\n"))
                assert num_lines == 11
        else:
            with open("tests/files/sptfy_current_user_top_tracks_queries.json.test", "r") as file:
                data = json.load(file)
                monkeypatch.setattr(
                    spotipy.Spotify, "current_user_top_tracks",
                    lambda self, limit, offset, time_range: data
                )
                user_top.top_tracks_subcommand(args_list[1:], sptfy_mock)
                out, err = capfd.readouterr()
                num_lines = len(out.split("\n"))
                assert num_lines == 11


@pytest.mark.parametrize("args_list, exit_expected, expected_exit_code", [
    (["--help"], True, 0),
    (["adf"], True, 2),
    (["--limit", "51"], True, 1),
    (["--limit", "0"], True, 1),
    (["--limit", "-1"], True, 1),
    (["--offset", "-1"], True, 1),
    (["--offset", "0"], False, 1),
    ([], False, 0),
])
def test_top_artists_subcommand(monkeypatch, capfd, sptfy_mock, args_list, exit_expected, expected_exit_code):
    with open("tests/files/sptfy_current_user_top_artists_queries.json.test", "r") as file:
        data = json.load(file)

    if exit_expected:
        with pytest.raises(SystemExit) as exit_wrapper:
            user_top.top_artists_subcommand(args_list, sptfy_mock)
        assert exit_wrapper.type == SystemExit
        assert exit_wrapper.value.code == expected_exit_code
    else:
        monkeypatch.setattr(
            spotipy.Spotify, "current_user_top_tracks",
            lambda self, limit, offset, time_range: data
        )
        user_top.top_artists_subcommand(args_list, sptfy_mock)
        out, err = capfd.readouterr()
        num_lines = len(out.split("\n"))
        assert num_lines == 11


@pytest.mark.parametrize("args_list, exit_expected, expected_exit_code", [
    (["--help"], True, 0),
    (["adf"], True, 2),
    (["--limit", "51"], True, 1),
    (["--limit", "0"], True, 1),
    (["--limit", "-1"], True, 1),
    (["--offset", "-1"], True, 1),
    (["--offset", "0"], False, 1),
    ([], False, 0),
])
def test_top_tracks_subcommand(monkeypatch, capfd, sptfy_mock, args_list, exit_expected, expected_exit_code):
    with open("tests/files/sptfy_current_user_top_tracks_queries.json.test", "r") as file:
        data = json.load(file)

    if exit_expected:
        with pytest.raises(SystemExit) as exit_wrapper:
            user_top.top_tracks_subcommand(args_list, sptfy_mock)
        assert exit_wrapper.type == SystemExit
        assert exit_wrapper.value.code == expected_exit_code
    else:
        monkeypatch.setattr(
            spotipy.Spotify, "current_user_top_tracks",
            lambda self, limit, offset, time_range: data
        )
        user_top.top_tracks_subcommand(args_list, sptfy_mock)
        out, err = capfd.readouterr()
        num_lines = len(out.split("\n"))
        assert num_lines == 11


@pytest.mark.parametrize("args_list, expected_num_errors", [
    (["--limit", "51"], 1),
    (["--limit", "0"], 1),
    (["--limit", "-1"], 1),
    (["--offset", "-1"], 1),
    (["--limit", "-1", "--offset", "-1"], 2),
    (["--limit", "0", "--offset", "-1"], 2),
    (["--limit", "51", "--offset", "-1"], 2),
    (["--offset", "0"], 0),
    ([], 0),
])
def test_get_user_top_args_errors(args_list, expected_num_errors):
    parser = user_top.get_user_top_parser()
    args = parser.parse_args(args_list)
    errors = user_top.get_user_top_args_errors(args)
    assert len(errors) == expected_num_errors
