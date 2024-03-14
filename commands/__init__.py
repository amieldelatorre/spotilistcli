from .playlist import *
from .auth import *

top_level_command_args = {
    AUTH_COMMAND_NAME: auth_command,
    PLAYLIST_COMMAND_NAME: playlist_command
}


def get_usage() -> str:
    command_names = list(top_level_command_args.keys())
    return f"usage: spotiList {{help,{','.join(command_names)}}}"
