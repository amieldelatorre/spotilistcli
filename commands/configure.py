import os
import getpass
from dataclasses import dataclass
from sys import exit
from typing import List
from sptfy import Sptfy
from helpers import (get_env_file_path, SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR, SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR,
                     SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR, ENVIRONMENT_ENV_VARIABLE_STR)


@dataclass
class EnvironmentVariables:
    spotify_client_id: str
    spotify_client_secret: str
    spotify_redirect_uri: str
    environment: str


def configure_command() -> None:
    env_filepath = get_env_file_path()

    if os.path.exists(env_filepath):
        response = input(".env file exists. Do you want to carry on and overwrite it? (only 'yes' is accepted) ")
        if response != "yes":
            print("Aborting command")
            exit(0)

    env_vars = get_environment_variables()
    with open(env_filepath, "w") as file:
        file.write(f"{SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR}={env_vars.spotify_client_id}\n")
        file.write(f"{SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR}={env_vars.spotify_client_secret}\n")
        file.write(f"{SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR}={env_vars.spotify_redirect_uri}\n")
        file.write(f"{ENVIRONMENT_ENV_VARIABLE_STR}={env_vars.environment}\n")

    print(f"\nConfiguration successful! .env has been populated at {env_filepath}.")
    print("Login with: spotilistcli auth login")


def get_environment_variables() -> EnvironmentVariables:
    spotify_client_id = getpass.getpass(f"{SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR}: ").strip()
    null_or_empty(spotify_client_id, SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR)

    spotify_client_secret = getpass.getpass(f"{SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR}: ").strip()
    null_or_empty(spotify_client_secret, SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR)

    spotify_redirect_uri = input(f"{SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR}: ").strip()
    null_or_empty(spotify_redirect_uri, SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR)

    environment = input(f"{ENVIRONMENT_ENV_VARIABLE_STR}: ").strip()
    null_or_empty(environment, ENVIRONMENT_ENV_VARIABLE_STR)

    env_vars = EnvironmentVariables(
        spotify_client_id=spotify_client_id,
        spotify_client_secret=spotify_client_secret,
        spotify_redirect_uri=spotify_redirect_uri,
        environment=environment
    )

    return env_vars


def null_or_empty(response: str, env_var_name) -> None:
    if response is None or response == "":
        print(f"ERROR: '{env_var_name}' cannot be null or empty!")
        exit(1)


CONFIGURE_COMMAND_NAME = "configure"
