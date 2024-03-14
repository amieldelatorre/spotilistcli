from log import logger
from typing import List
from sptfy import Sptfy


AUTH_COMMAND_NAME = "auth"
AUTH_COMMAND_SUBCOMMANDS = []


def auth_command(original_args: List[str], sptfy: Sptfy) -> None:
    sptfy.auth()
