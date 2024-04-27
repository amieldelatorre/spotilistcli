import helpers
import pytest
from unittest.mock import mock_open, patch, call


@pytest.mark.parametrize("response, env_var_name, expected_result", [
    ("", "VAR", True),
    ("VALUE", "VAR", False)
])
def test_null_or_empty(response, env_var_name, expected_result):
    response = helpers.null_or_empty(
        response=response,
        env_var_name=env_var_name
    )

    assert response == expected_result


@pytest.mark.parametrize("getpass_list, input_patch, exit_expected, expected_exit_code, expected_result", [
    (iter(["", "something"]), "something", True, 1, None),
    (iter(["something", ""]), "something", True, 1, None),
    (iter(["something", "something"]), "", True, 1, None),
    (iter(["something", "something"]), "something", False, 0, helpers.EnvironmentVariables("something", "something", "something")),
])
def test_get_required_environment_variables_as_input(monkeypatch, getpass_list, input_patch, exit_expected, expected_exit_code,
                                                     expected_result):
    monkeypatch.setattr("getpass.getpass", lambda _: next(getpass_list))
    monkeypatch.setattr("builtins.input", lambda _: input_patch)
    if exit_expected:
        with pytest.raises(SystemExit) as wrapper_exit:
            helpers.get_required_environment_variables_as_input()
        assert wrapper_exit.type == SystemExit
        assert wrapper_exit.value.code == expected_exit_code
    else:
        result = helpers.get_required_environment_variables_as_input()
        assert expected_result == result


@pytest.mark.parametrize("env_vars_dict, exit_expected, expected_exit_code, expected_result", [
    ({
        helpers.SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR: "",
        helpers.SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR: "something",
        helpers.SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR: "something"
     }, True, 1, None),

    ({
        helpers.SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR: "something",
        helpers.SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR: "",
        helpers.SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR: "something"
    }, True, 1, None),

    ({
        helpers.SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR: "something",
        helpers.SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR: "something",
        helpers.SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR: ""
    }, True, 1, None),

    ({
        helpers.SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR: "something",
        helpers.SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR: "something",
        helpers.SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR: "something"
    }, False, 0, helpers.EnvironmentVariables("something", "something", "something")),
])
def test_get_required_environment_variables(monkeypatch, env_vars_dict, exit_expected, expected_exit_code,
                                            expected_result):
    for key in env_vars_dict.keys():
        monkeypatch.setenv(key, env_vars_dict[key])
    if exit_expected:
        with pytest.raises(SystemExit) as wrapper_exit:
            helpers.get_required_environment_variables()
        assert wrapper_exit.type == SystemExit
        assert wrapper_exit.value.code == expected_exit_code
    else:
        result = helpers.get_required_environment_variables()
        assert expected_result == result


def test_get_longest_string():
    strings = ["abcdefgh", "a", "abc", "ab", "abcdefghij", "abcde", "abcdef"]
    expected_length = 10
    result = helpers.get_longest_string(strings)
    assert result == expected_length


def test_command_usage():
    command = "command"
    subcommands = {
        "sumbcommand1": None,
        "sumbcommand2": None,
        "sumbcommand3": None,
        "sumbcommand4": None
    }

    expected = "usage: spotilistcli command {help,sumbcommand1,sumbcommand2,sumbcommand3,sumbcommand4}"
    result = helpers.get_command_usage(
        command=command,
        subcommands=subcommands
    )

    assert expected == result


@pytest.mark.parametrize("cache_file_exists, expected_exit_code", [
    (True, 0),
    (False, 1)
])
def test_login_required(monkeypatch, cache_file_exists, expected_exit_code):
    monkeypatch.setattr("os.path.exists", lambda _: cache_file_exists)

    @helpers.login_required
    def dummy():
        return "dummy"

    if cache_file_exists:
        assert dummy() == "dummy"
    else:
        with pytest.raises(SystemExit) as wrapper_exit:
            dummy()
        assert wrapper_exit.type == SystemExit
        assert wrapper_exit.value.code == expected_exit_code


def test_get_cache_file_path():
    result = helpers.get_cache_file_path()
    assert result.endswith(".cache")


def test_get_env_file_path():
    result = helpers.get_env_file_path()
    assert result.endswith(".env")


def test_get_obj_dict():
    expected = {
        "spotify_client_id": "something",
        "spotify_client_secret": "something",
        "spotify_redirect_uri": "something"
    }
    env_vars = helpers.EnvironmentVariables("something", "something", "something")

    assert helpers.get_obj_dict(env_vars) == expected


def test_environment_variables_class_write_to_file():
    filepath = "sptfy_temp/test_file.path"
    env_vars = helpers.EnvironmentVariables(
        spotify_client_id="spotify_client_id",
        spotify_client_secret="spotify_client_secret",
        spotify_redirect_uri="spotify_redirect_uri"
    )
    calls = [
        call(f"{helpers.SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR}=spotify_client_id\n"),
        call(f"{helpers.SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR}=spotify_client_secret\n"),
        call(f"{helpers.SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR}=spotify_redirect_uri\n")
    ]

    with patch("builtins.open", mock_open()) as mock:
        env_vars.write_to_file(filepath=filepath)
        mock.assert_called_once()
        write_mocked = mock()
        assert write_mocked.write.call_count == 3
        write_mocked.write.assert_has_calls(calls)
