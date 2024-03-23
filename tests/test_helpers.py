from helpers import null_or_empty
import pytest


class TestHelpers:
    @pytest.mark.parametrize("response, env_var_name, expected_result", [
        ("", "VAR", True),
        ("VALUE", "VAR", False)
    ])
    def test_null_or_empty(self, response, env_var_name, expected_result):
        response = null_or_empty(
            response=response,
            env_var_name=env_var_name
        )

        assert response == expected_result

