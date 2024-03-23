import os
import getpass
from pathlib import Path
from sys import exit
from dotenv import load_dotenv
from typing import Dict, List, Callable
from dataclasses import dataclass


SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR = "SPOTIFY_CLIENT_ID"
SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR = "SPOTIFY_CLIENT_SECRET"
SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR = "SPOTIFY_REDIRECT_URI"


@dataclass
class EnvironmentVariables:
    spotify_client_id: str
    spotify_client_secret: str
    spotify_redirect_uri: str


def get_obj_dict(obj) -> Dict:
    return obj.__dict__


def null_or_empty(response: str, env_var_name) -> None:
    if response is None or response == "":
        print(f"ERROR: '{env_var_name}' cannot be null or empty!")
        exit(1)


def get_required_environment_variables_as_input() -> EnvironmentVariables:
    spotify_client_id = getpass.getpass(f"{SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR}: ").strip()
    null_or_empty(spotify_client_id, SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR)

    spotify_client_secret = getpass.getpass(f"{SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR}: ").strip()
    null_or_empty(spotify_client_secret, SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR)

    spotify_redirect_uri = input(f"{SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR}: ").strip()
    null_or_empty(spotify_redirect_uri, SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR)

    env_vars = EnvironmentVariables(
        spotify_client_id=spotify_client_id,
        spotify_client_secret=spotify_client_secret,
        spotify_redirect_uri=spotify_redirect_uri
    )

    return env_vars


def get_required_environment_variables() -> EnvironmentVariables:
    load_dotenv()

    spotify_client_id = os.getenv(SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR, default=None)
    spotify_client_secret = os.getenv(SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR, default=None)
    spotify_redirect_uri = os.getenv(SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR, default=None)

    missing_environment_variables = []
    if spotify_client_id is None:
        missing_environment_variables.append(SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR)
    if spotify_client_secret is None:
        missing_environment_variables.append(SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR)
    if spotify_redirect_uri is None:
        missing_environment_variables.append(SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR)

    if len(missing_environment_variables) > 0:
        print(f"ERROR: The following environment variable(s) are missing:")
        for env_var in missing_environment_variables:
            print(f"\t- {env_var}")
        print("Please run: spotilist configure")
        exit(1)

    env_vars = EnvironmentVariables(
        spotify_client_id=spotify_client_id,
        spotify_client_secret=spotify_client_secret,
        spotify_redirect_uri=spotify_redirect_uri
    )

    return env_vars


def get_longest_string(strings: List[str]) -> int:
    curr_longest_len = 0
    for string in strings:
        if len(string) > curr_longest_len:
            curr_longest_len = len(string)

    return curr_longest_len


def get_command_usage(command: str, subcommands: Dict) -> str:
    command_names = list(subcommands.keys())
    return f"usage: spotiList {command} {{help,{','.join(command_names)}}}"


def get_cache_file_path() -> str:
    # Depends on app.py changing the working directory to the main script's directory
    cache_filename = ".cache"
    working_directory = Path(os.getcwd())
    cache_filepath = os.path.join(working_directory, cache_filename)

    return cache_filepath


def login_required(func) -> Callable:
    def wrapper(*args, **kwargs) -> None:
        cache_filepath = get_cache_file_path()

        if os.path.exists(cache_filepath):
            func(*args, **kwargs)
        else:
            print("Not currently logged in!")
            print("Please log in with: `spotilist auth login`")
            exit(1)

    return wrapper


def get_env_file_path() -> str:
    # Depends on app.py changing the working directory to the main script's directory
    env_filename = ".env"
    working_directory = Path(os.getcwd())
    env_filepath = os.path.join(working_directory, env_filename)

    return env_filepath
