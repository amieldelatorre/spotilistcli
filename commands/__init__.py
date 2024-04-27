from .playlist import *
from .auth import *
from .user_top import *

top_level_command_args = {
    AUTH_COMMAND_NAME: auth_command,
    PLAYLIST_COMMAND_NAME: playlist_command,
    USER_TOP_COMMAND_NAME: user_top_command
}


def get_usage() -> str:
    command_names = list(top_level_command_args.keys())
    return f"usage: spotilistcli {{help,configure,{','.join(command_names)}}}"
