import os
from sys import exit
from pathlib import Path
from typing import List, Optional, Callable
from sptfy import Sptfy
from helpers import get_command_usage, login_required, get_cache_file_path


def auth_command(original_args: List[str], sptfy: Sptfy) -> None:
    if len(original_args) < 1:
        print(get_command_usage(
            command=AUTH_COMMAND_NAME,
            subcommands=AUTH_COMMAND_SUBCOMMANDS
        ))
        exit(1)

    subcommand = original_args[0]

    if subcommand == "help":
        print(get_command_usage(
            command=AUTH_COMMAND_NAME,
            subcommands=AUTH_COMMAND_SUBCOMMANDS
        ))
        exit(0)

    subcommand_function: Optional[Callable] = AUTH_COMMAND_SUBCOMMANDS.get(subcommand, None)
    if subcommand_function is None:
        print(f"Unknown subcommand '{subcommand}', {get_command_usage(
            command=AUTH_COMMAND_NAME, 
            subcommands=AUTH_COMMAND_SUBCOMMANDS
        )}")
        exit(1)

    subcommand_function(
        args=original_args[1:],
        sptfy=sptfy
    )


def login(args: List[str], sptfy: Sptfy) -> None:
    sptfy.auth()
    print("Login successful!")


@login_required
def logout(args: List[str], sptfy: Sptfy) -> None:
    cache_filepath = get_cache_file_path()
    os.remove(cache_filepath)
    print("Logout successful!")


AUTH_COMMAND_NAME = "auth"
AUTH_LOGIN_SUBCOMMAND = "login"
AUTH_LOGOUT_SUBCOMMAND = "logout"
AUTH_COMMAND_SUBCOMMANDS = {
    AUTH_LOGIN_SUBCOMMAND: login,
    AUTH_LOGOUT_SUBCOMMAND: logout
}
