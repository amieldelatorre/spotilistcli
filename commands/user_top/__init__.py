import click
from helpers import login_required
from .artists import artists
from .tracks import tracks

@click.group(help="Current user's top tracks and artists")
@login_required
def user_top():
    pass


user_top.add_command(artists)
user_top.add_command(tracks)
