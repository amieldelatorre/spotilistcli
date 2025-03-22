import os
import click
from helpers import get_cache_file_path, time_taken
from log import logger
from helpers import login_required


@click.command()
@login_required
def logout() -> None:
    cache_filepath = get_cache_file_path()
    os.remove(cache_filepath)
    print("Logout successful!")
    logger.debug(f"Deleted f{cache_filepath} to logout")
