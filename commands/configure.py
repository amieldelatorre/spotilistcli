import os
import sys
from helpers import (get_env_file_path, get_required_environment_variables_as_input, SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR,
                     SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR, SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR)


def configure_command() -> None:
    env_filepath = get_env_file_path()

    if os.path.exists(env_filepath):
        response = input(".env file exists. Do you want to carry on and overwrite it? (only 'yes' is accepted) ")
        if response != "yes":
            print("Aborting command")
            sys.exit(0)

    env_vars = get_required_environment_variables_as_input()
    with open(env_filepath, "w") as file:
        file.write(f"{SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR}={env_vars.spotify_client_id}\n")
        file.write(f"{SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR}={env_vars.spotify_client_secret}\n")
        file.write(f"{SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR}={env_vars.spotify_redirect_uri}\n")

    print(f"\nConfiguration successful! .env has been populated at {env_filepath}.")
    print("Login with: spotilistcli auth login")


CONFIGURE_COMMAND_NAME = "configure"
