import click
import commands.playlist.download
import commands.playlist.show
import commands.playlist.list
from helpers import login_required


@click.group(help="Playlist information")
@login_required
def playlist():
    pass


playlist.add_command(download.download)
playlist.add_command(show.show)
playlist.add_command(list.list)
