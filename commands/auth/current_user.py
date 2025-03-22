import click
from sptfy import get_sptfy
from helpers import login_required
from log import logger

@click.command
@click.option("--show-id", default=False, help="Show the user's spotify Id")
@click.option("--show-url", default=False, help="Show the user's spotify profile URL")
@login_required
def current_user(show_id, show_url) -> None:
    logger.debug(f"Retrieving current user public info")

    sptfy = get_sptfy()
    user = sptfy.get_current_user_info()
    logger.debug(f"Showing user name")
    print(f"{user.name}", end="")
    if show_id:
        logger.debug(f"Showing user Id")
        print(f"\t{user.id}", end="")
    if show_url:
        logger.debug(f"Showing user url")
        print(f"\t{user.url}", end="")