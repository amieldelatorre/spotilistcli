import click
from helpers import login_required
from .download import download
from .show import show
from .list import list


@click.group(help="Playlist information")
@login_required
def playlist():
    pass


playlist.add_command(download)
playlist.add_command(show)
playlist.add_command(list)
