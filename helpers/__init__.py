import os
import getpass
import sys
import __main__
import time
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Callable
from dataclasses import dataclass
from log import logger


SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR = "SPOTIFY_CLIENT_ID"
SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR = "SPOTIFY_CLIENT_SECRET"
SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR = "SPOTIFY_REDIRECT_URI"


@dataclass
class EnvironmentVariables:
    spotify_client_id: str
    spotify_client_secret: str
    spotify_redirect_uri: str

    def __eq__(self, other):
        return type(self) is type(other) and \
            self.spotify_client_id == other.spotify_client_id and \
            self.spotify_client_secret == other.spotify_client_secret and \
            self.spotify_redirect_uri == other.spotify_redirect_uri

    def write_to_file(self, filepath):
        logger.debug(f"Writing environment variables to {filepath}, creating directory if it does not exist")

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as file:
            file.write(f"{SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR}={self.spotify_client_id}\n")
            file.write(f"{SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR}={self.spotify_client_secret}\n")
            file.write(f"{SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR}={self.spotify_redirect_uri}\n")


def get_obj_dict(obj) -> Dict:
    return obj.__dict__


def null_or_empty(response: str, env_var_name) -> bool:
    if response is None or response == "":
        print(f"ERROR: '{env_var_name}' cannot be null or empty!")
        return True
    return False


def get_required_environment_variables_as_input() -> EnvironmentVariables:
    logger.debug(f"Retrieving required environment variables as input")
    spotify_client_id = getpass.getpass(f"{SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR}: ").strip()
    if null_or_empty(spotify_client_id, SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR):
        sys.exit(1)

    spotify_client_secret = getpass.getpass(f"{SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR}: ").strip()
    if null_or_empty(spotify_client_secret, SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR):
        sys.exit(1)

    spotify_redirect_uri = input(f"{SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR}: ").strip()
    if null_or_empty(spotify_redirect_uri, SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR):
        sys.exit(1)

    env_vars = EnvironmentVariables(
        spotify_client_id=spotify_client_id,
        spotify_client_secret=spotify_client_secret,
        spotify_redirect_uri=spotify_redirect_uri
    )

    return env_vars


def get_required_environment_variables() -> EnvironmentVariables:
    logger.debug(f"Retrieving required environment variables")
    load_dotenv(dotenv_path=get_env_file_path())

    spotify_client_id = os.getenv(SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR, default=None)
    spotify_client_secret = os.getenv(SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR, default=None)
    spotify_redirect_uri = os.getenv(SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR, default=None)

    missing_environment_variables = []
    if spotify_client_id is None or spotify_client_id.strip() == "":
        missing_environment_variables.append(SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR)
    if spotify_client_secret is None or spotify_client_secret.strip() == "":
        missing_environment_variables.append(SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR)
    if spotify_redirect_uri is None or spotify_redirect_uri.strip() == "":
        missing_environment_variables.append(SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR)

    if len(missing_environment_variables) > 0:
        print(f"ERROR: The following environment variable(s) are missing:")
        for env_var in missing_environment_variables:
            print(f"\t- {env_var}")
        print("Please run: spotilistcli configure")
        sys.exit(1)

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
    return f"usage: spotilistcli {command} {{help,{','.join(command_names)}}}"


def get_cache_file_path() -> str:
    cache_filepath = os.path.join(str(Path.home()), ".config", "spotilistcli", ".cache")
    cache_abs_filepath = os.path.abspath(cache_filepath)

    return cache_abs_filepath


def login_required(func) -> Callable:
    def wrapper(*args, **kwargs) -> None:
        cache_filepath = get_cache_file_path()

        if os.path.exists(cache_filepath):
            logger.debug(f"{cache_filepath} exists and going to function")
            return func(*args, **kwargs)
        else:
            logger.debug(f"{cache_filepath} does not exist")
            print("Not currently logged in!")
            print("Please log in with: spotilistcli auth login")
            sys.exit(1)

    return wrapper


def get_env_file_path() -> str:
    env_filepath = os.path.join(str(Path.home()), ".config", "spotilistcli", ".env")
    env_abs_filepath = os.path.abspath(env_filepath)

    return env_abs_filepath


def get_parent_dir() -> Path:
    # Get parent dir and switch the working directory
    # When run as an executable, the working directory is a temp folder,
    # using this we can get the folder of the actual file
    if getattr(sys, 'frozen', False):
        executable_path = Path(sys.executable)
        parent_dir = executable_path.parent.absolute()
    else:
        main_script_path = Path(os.path.realpath(__main__.__file__))
        parent_dir = main_script_path.parent.absolute()
    return parent_dir


def time_taken(func) -> Callable:
    def wrapper(*args, **kwargs) -> None:
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        duration = end - start
        logger.info(f"Time taken: {round(duration, 2)} seconds")

    return wrapper
