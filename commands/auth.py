import os
from pathlib import Path
from typing import List, Optional, Callable
from sptfy import Sptfy
from helpers import get_command_usage


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


def logout(args: List[str], sptfy: Sptfy) -> None:
    # Depends on app.py changing the working directory to the main script's directory
    cache_filename = ".cache"
    main_script_path = Path(os.getcwd())
    cache_filepath = os.path.join(main_script_path, cache_filename)

    if os.path.exists(cache_filepath):
        os.remove(cache_filepath)
        print("Logout successful!")
    else:
        print("Not currently logged in!")


AUTH_COMMAND_NAME = "auth"
AUTH_LOGIN_SUBCOMMAND = "login"
AUTH_LOGOUT_SUBCOMMAND = "logout"
AUTH_COMMAND_SUBCOMMANDS = {
    AUTH_LOGIN_SUBCOMMAND: login,
    AUTH_LOGOUT_SUBCOMMAND: logout
}
