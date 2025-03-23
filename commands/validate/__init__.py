import click
import commands.validate.youtube_urls

@click.group(help="Validate your generated playlists")
def validate():
    pass


validate.add_command(youtube_urls.youtube_urls)

