import click

from .firefox import cli as firefox_cli
from .logger import LOG_LEVELS, configure_logging


@click.group()
@click.option(
    '-l', '--level',
    default='debug',
    type=click.Choice(LOG_LEVELS.keys()),
    help='Logging level.',
)
def cli(level):
    configure_logging(level)


cli.add_command(firefox_cli)
