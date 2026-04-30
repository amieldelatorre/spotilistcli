import click
from . import lastfm


@click.group(help="Scrobble extended listening history data to a destination")
def scrobble():
    pass


scrobble.add_command(lastfm.lastfm)
