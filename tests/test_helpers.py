import helpers
import pytest


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
