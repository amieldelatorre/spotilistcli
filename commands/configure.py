import os
import sys
from log import logger
from helpers import (get_env_file_path, get_required_environment_variables_as_input, SPOTIFY_CLIENT_ID_ENV_VARIABLE_STR,
                     SPOTIFY_CLIENT_SECRET_ENV_VARIABLE_STR, SPOTIFY_REDIRECT_URI_ENV_VARIABLE_STR)


def configure_command() -> None:
    logger.debug("'configure' command invoked")
    env_filepath = get_env_file_path()

    if os.path.exists(env_filepath):
        logger.debug(f"{env_filepath} exists")
        response = input(".env file exists. Do you want to carry on and overwrite it? (only 'yes' is accepted) ")
        if response != "yes":
            logger.debug(f"Aborting the configuration of env file")
            print("Aborting command")
            sys.exit(0)

    logger.debug(f"{env_filepath} does not exist, continuing and retrieving as input")
    env_vars = get_required_environment_variables_as_input()
    env_vars.write_to_file(env_filepath)
    print(f"\nConfiguration successful! .env has been populated at {env_filepath}.")
    print("Login with: spotilistcli auth login")


CONFIGURE_COMMAND_NAME = "configure"
