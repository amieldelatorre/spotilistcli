import os
import sys
import click
from sptfy import get_sptfy
from helpers import get_cache_file_path, time_taken
from log import logger


@click.command()
@time_taken
def login() -> None:
    logger.debug(f"'auth' 'login' subcommand invoked")
    cache_filepath = get_cache_file_path()

    sptfy = get_sptfy()
    login_result = sptfy.auth()
    if login_result:
        print("Login successful!")
        logger.debug(f"Login success")
    else:
        logger.debug(f"Login error")
        print("ERROR: Problems logging in.")
        if os.path.exists(cache_filepath):
            print(f"Please delete {cache_filepath} and try again.")
        print(f"\nIf problem persists check your .env file.")
        sys.exit(1)
