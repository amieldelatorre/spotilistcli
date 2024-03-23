import os
import argparse
import sys
from typing import List, Optional, Callable
from sptfy import Sptfy
from helpers import get_command_usage, login_required, get_cache_file_path
from spotipy.oauth2 import SpotifyOauthError


def auth_command(original_args: List[str], sptfy: Sptfy) -> None:
    if len(original_args) < 1:
        print(get_command_usage(
            command=AUTH_COMMAND_NAME,
            subcommands=AUTH_COMMAND_SUBCOMMANDS
        ))
        sys.exit(1)

    subcommand = original_args[0]

    if subcommand == "help":
        print(get_command_usage(
            command=AUTH_COMMAND_NAME,
            subcommands=AUTH_COMMAND_SUBCOMMANDS
        ))
        sys.exit(0)

    subcommand_function: Optional[Callable] = AUTH_COMMAND_SUBCOMMANDS.get(subcommand, None)
    if subcommand_function is None:
        print(f"Unknown subcommand '{subcommand}', {get_command_usage(
            command=AUTH_COMMAND_NAME, 
            subcommands=AUTH_COMMAND_SUBCOMMANDS
        )}")
        sys.exit(1)

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


@login_required
def current_user(args: List[str], sptfy: Sptfy) -> None:
    parser = get_current_user_parser()
    current_user_args = parser.parse_args(args)

    user = sptfy.get_current_user_info()

    print(f"{user.name}", end="")
    if current_user_args.show_id:
        print(f"\t{user.id}", end="")
    if current_user_args.show_url:
        print(f"\t{user.url}", end="")


def get_current_user_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=f"{AUTH_COMMAND_NAME} {AUTH_CURRENT_USER_SUBCOMMAND}",
        description="Show current user info"
    )

    parser.add_argument(
        "--show-id",
        action="store_true",
        help="If user Id should be shown",
        required=False,
        default=False
    )

    parser.add_argument(
        "--show-url",
        action="store_true",
        help="If user profile url should be shown",
        required=False,
        default=False
    )

    return parser


AUTH_COMMAND_NAME = "auth"
AUTH_LOGIN_SUBCOMMAND = "login"
AUTH_LOGOUT_SUBCOMMAND = "logout"
AUTH_CURRENT_USER_SUBCOMMAND = "current-user"
AUTH_COMMAND_SUBCOMMANDS = {
    AUTH_LOGIN_SUBCOMMAND: login,
    AUTH_LOGOUT_SUBCOMMAND: logout,
    AUTH_CURRENT_USER_SUBCOMMAND: current_user
}
