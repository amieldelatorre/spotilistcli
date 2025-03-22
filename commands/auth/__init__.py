import click
from .login import login
from .logout import logout
from .current_user import current_user


@click.group(help="Authentication options")
def auth():
    pass


auth.add_command(login)
auth.add_command(logout)
auth.add_command(current_user)
