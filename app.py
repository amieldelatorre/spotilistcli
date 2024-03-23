import os
import sys
from sys import exit
from sptfy import Sptfy
from commands import get_usage, top_level_command_args
from helpers import get_required_environment_variables, get_parent_dir
from commands import configure


def main() -> None:
    if len(sys.argv) < 2:  # 2 because the file path is the first argument
        print(get_usage())
        exit(1)

    command = sys.argv[1]
    following_args = sys.argv[2:]

    if command == "help":
        print(get_usage())
        exit(0)
    elif command == configure.CONFIGURE_COMMAND_NAME:
        configure.configure_command()
        exit(0)

    env_vars = get_required_environment_variables()
    sptfy = Sptfy(
        spotify_client_id=env_vars.spotify_client_id,
        spotify_client_secret=env_vars.spotify_client_secret,
        spotify_redirect_uri=env_vars.spotify_redirect_uri,
    )

    command_function = top_level_command_args.get(command, None)
    if command_function is None:
        print(f"Unknown command '{command}', {get_usage()}")
        exit(1)

    command_function(
        original_args=following_args,
        sptfy=sptfy
    )


if __name__ == "__main__":
    parent_dir = get_parent_dir()
    os.chdir(parent_dir)

    main()
