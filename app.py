import os
import sys
from sptfy import Sptfy
from pathlib import Path
from commands import get_usage, top_level_command_args
from helpers import get_required_environment_variables


def main() -> None:
    if len(sys.argv) < 2:  # 2 because the file path is the first argument
        print(get_usage())
        exit(1)

    spotify_client_id, spotify_client_secret, spotify_redirect_url = get_required_environment_variables()

    sptfy = Sptfy(
        spotify_client_id=spotify_client_id,
        spotify_client_secret=spotify_client_secret,
        spotify_redirect_uri=spotify_redirect_url,
    )

    command = sys.argv[1]
    following_args = sys.argv[2:]

    if command == "help":
        print(get_usage())
        exit(0)

    command_function = top_level_command_args.get(command, None)
    if command_function is None:
        print(f"Unknown command '{command}', {get_usage()}")
        exit(1)

    command_function(
        original_args=following_args,
        sptfy=sptfy
    )


if __name__ == "__main__":
    main_script_path = Path(os.path.realpath(__file__))
    parent_dir = main_script_path.parent.absolute()
    os.chdir(parent_dir)
    main()
