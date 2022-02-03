import click
from . import _util


@click.group()
def cli():
    pass


@cli.command()
def ls():
    """List all pubsub topics."""
    for topic in _util.detect_topics("pubsub"):
        print(topic)
