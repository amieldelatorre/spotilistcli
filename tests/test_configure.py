import pytest

import helpers
from commands import configure
from unittest.mock import mock_open, patch, call


@pytest.mark.parametrize("getpass_list, input_list, exit_expected, expected_exit_code, path_exists", [
    (["", "something"], ["yes", "something"], True, 1, True),
    (["something", ""], ["yes", "something"], True, 1, True),
    (["something", "something"], ["yes", ""], True, 1, True),
    (["something", "something"], ["yes", "something"], False, 0, True),
    (["something", "something"], ["n", "something"], True, 0, True),
    (["something", "something"], ["y", "something"], True, 0, True),
    (["something", "something"], ["something"], False, 0, False),
])
def test_configure_command(
        monkeypatch, getpass_list, input_list, exit_expected, expected_exit_code, path_exists):
    getpass_iter = iter(getpass_list)
    input_iter = iter(input_list)

    monkeypatch.setattr("os.path.exists", lambda filepath: path_exists)
    monkeypatch.setattr("getpass.getpass", lambda _: next(getpass_iter))
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    if exit_expected:
        with pytest.raises(SystemExit) as wrapper_exit:
            configure.configure_command()
            assert wrapper_exit.type == SystemExit
            assert wrapper_exit.value.code == expected_exit_code
    else:
        calls = [
            call(f"{helpers.SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR}={getpass_list[0]}\n"),
            call(f"{helpers.SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR}={getpass_list[0]}\n")
        ]

        if len(input_list) == 1:
            calls.append(call(f"{helpers.SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR}={input_list[0]}\n"))
        else:
            calls.append(call(f"{helpers.SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR}={input_list[1]}\n"))

        with patch("builtins.open", mock_open()) as mock:
            configure.configure_command()
            mock.assert_called_once()
            write_mocked = mock()
            assert write_mocked.write.call_count == 3
            write_mocked.write.assert_has_calls(calls)
