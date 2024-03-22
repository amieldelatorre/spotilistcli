import os
from dotenv import load_dotenv
from typing import Dict, List


def get_obj_dict(obj) -> Dict:
    return obj.__dict__


def get_required_environment_variables() -> (str, str, str):
    spotify_client_id_env_variable_str = "SPOTIFY_CLIENT_ID"
    spotify_client_secret_env_variable_str = "SPOTIFY_CLIENT_SECRET"
    spotify_redirect_uri_env_variable_str = "SPOTIFY_REDIRECT_URI"

    load_dotenv()

    spotify_client_id = os.getenv(spotify_client_id_env_variable_str, default=None)
    spotify_client_secret = os.getenv(spotify_client_secret_env_variable_str, default=None)
    spotify_redirect_url = os.getenv(spotify_redirect_uri_env_variable_str, default=None)

    missing_environment_variables = []
    if spotify_client_id is None:
        missing_environment_variables.append(spotify_client_id_env_variable_str)
    if spotify_client_secret is None:
        missing_environment_variables.append(spotify_client_secret_env_variable_str)
    if spotify_redirect_url is None:
        missing_environment_variables.append(spotify_redirect_uri_env_variable_str)

    if len(missing_environment_variables) > 0:
        print(f"ERROR: The following environment variable(s) are missing:")
        for env_var in missing_environment_variables:
            print(f"\t- {env_var}")
        exit(1)

    return spotify_client_id, spotify_client_secret, spotify_redirect_url


def get_longest_string(strings: List[str]) -> int:
    curr_longest_len = 0
    for string in strings:
        if len(string) > curr_longest_len:
            curr_longest_len = len(string)

    return curr_longest_len


def get_command_usage(command: str, subcommands: Dict) -> str:
    command_names = list(subcommands.keys())
    return f"usage: spotiList {command} {{help,{','.join(command_names)}}}"
