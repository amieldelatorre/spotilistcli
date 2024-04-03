import argparse
import sys
from typing import List, Optional, Callable
from sptfy import Sptfy
from helpers import get_longest_string, get_command_usage, login_required, time_taken
from log import logger


@login_required
def user_top_command(original_args: List[str], sptfy: Sptfy) -> None:
    logger.debug(f"'user-top' command invoked")
    if len(original_args) < 1:
        print(get_command_usage(
            command=USER_TOP_COMMAND_NAME,
            subcommands=USER_TOP_COMMAND_SUBCOMMANDS
        ))
        sys.exit(1)

    subcommand = original_args[0]
    if subcommand == "help":
        logger.debug("'user-top' help command invoked")
        print(get_command_usage(
            command=USER_TOP_COMMAND_NAME,
            subcommands=USER_TOP_COMMAND_SUBCOMMANDS
        ))
        sys.exit(0)

    subcommand_function: Optional[Callable] = USER_TOP_COMMAND_SUBCOMMANDS.get(subcommand, None)
    if subcommand_function is None:
        logger.debug(f"'user-top' '{subcommand}' subcommand not found")
        print(f"Unknown subcommand '{subcommand}', {get_command_usage(
            command=USER_TOP_COMMAND_NAME,
            subcommands=USER_TOP_COMMAND_SUBCOMMANDS
        )}")
        sys.exit(1)

    subcommand_function(
        args=original_args[1:],
        sptfy=sptfy
    )


@time_taken
def top_artists_subcommand(args: List[str], sptfy: Sptfy) -> None:
    logger.debug(f"Retrieving top artists")
    parser = get_user_top_parser()
    top_artists_args = parser.parse_args(args)

    arg_errors = get_user_top_args_errors(top_artists_args)
    if len(arg_errors) > 0:
        logger.debug(f"{len(arg_errors)} errors found, exiting program")
        for err in arg_errors:
            print(err)
        sys.exit(1)

    logger.debug(f"{len(arg_errors)} errors found, continuing")
    logger.debug(f"Getting user top artists with input: limit {top_artists_args.limit}, "
                 f"offset {top_artists_args.offset}, time_range {top_artists_args.time_range}")

    artists = sptfy.get_user_top_artists(
        limit=top_artists_args.limit,
        offset=top_artists_args.offset,
        time_range=top_artists_args.time_range
    )

    logger.debug(f"Showing artists")
    longest_artist_name = get_longest_string([artist.name for artist in artists])
    for artist in artists:
        print(f"{artist.name:<{longest_artist_name}}")


@time_taken
def top_tracks_subcommand(args: List[str], sptfy: Sptfy) -> None:
    logger.debug(f"Retrieving top tracks")
    parser = get_user_top_parser()
    top_tracks_args = parser.parse_args(args)

    arg_errors = get_user_top_args_errors(top_tracks_args)
    if len(arg_errors) > 0:
        logger.debug(f"{len(arg_errors)} errors found, exiting program")
        for err in arg_errors:
            print(err)
        sys.exit(1)

    logger.debug(f"{len(arg_errors)} errors found, continuing")
    logger.debug(f"Getting user top tracks with input: limit {top_tracks_args.limit}, "
                 f"offset {top_tracks_args.offset}, time_range {top_tracks_args.time_range}")

    songs = sptfy.get_user_top_tracks(
        limit=top_tracks_args.limit,
        offset=top_tracks_args.offset,
        time_range=top_tracks_args.time_range
    )

    logger.debug(f"Showing songs and artists")
    longest_song_name = get_longest_string([song.name for song in songs])
    longest_artists_name = get_longest_string([','.join(song.artists) for song in songs])
    for song in songs:
        print(f"{song.name:<{longest_song_name}}\t{','.join(song.artists):<{longest_artists_name}}")


def get_user_top_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=f"{USER_TOP_COMMAND_NAME} {'|'.join(list(USER_TOP_COMMAND_SUBCOMMANDS.keys()))}",
        description="Show user top data"
    )

    parser.add_argument(
        "--limit",
        action="store",
        help="Maximum number of items to return",
        required=False,
        default=10
    )

    parser.add_argument(
        "--offset",
        action="store",
        help="The index of the first item to return",
        required=False,
        default=0
    )

    parser.add_argument(
        "--time-range",
        action="store",
        help=f"Time frame to compute for the data",
        choices=VALID_TIME_RANGE,
        required=False,
        default=VALID_TIME_RANGE[0]
    )

    return parser


def get_user_top_args_errors(args: argparse.Namespace) -> List[str]:
    logger.debug(f"Validating arguments passed")
    errors = []

    # Validate limit
    if type(args.limit) is int or args.limit.isdigit():
        limit = int(args.limit)
        if limit <= 0 or limit >= 51:
            errors.append("ERROR: limit provided is not a positive integer greater than 0 and less than or equal to 50")
    elif not args.limit.isdigit():
        errors.append("ERROR: limit provided is not a positive integer greater than 0")

    # Validate offset
    if type(args.offset) is int or args.offset.isdigit():
        offset = int(args.offset)
        if offset < 0:
            errors.append("ERROR: offset provided is not a positive integer")
    elif not args.offset.isdigit():
        errors.append("ERROR: offset provided is not a positive integer")

    return errors


VALID_TIME_RANGE = ["short_term", "medium_term", "long_term"]
USER_TOP_COMMAND_NAME = "user-top"
USER_TOP_ARTISTS_SUBCOMMAND = "artists"
USER_TOP_TRACKS_SUBCOMMAND = "tracks"
USER_TOP_COMMAND_SUBCOMMANDS = {
    USER_TOP_ARTISTS_SUBCOMMAND: top_artists_subcommand,
    USER_TOP_TRACKS_SUBCOMMAND: top_tracks_subcommand,
}
