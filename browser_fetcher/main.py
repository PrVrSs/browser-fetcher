import click

from browser_fetcher.firefox import cli as firefox_cli


@click.group()
def cli():
    pass


cli.add_command(firefox_cli)
