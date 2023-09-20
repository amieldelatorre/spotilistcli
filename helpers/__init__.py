from commands import playlist


def get_usage():
    return f"usage: SpotiList {{help,{playlist.PLAYLIST_COMMAND_NAME}}}"


def get_obj_dict(obj):
    return obj.__dict__
