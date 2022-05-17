import a0
import click
from . import _util


@click.command()
@click.argument("topic", shell_complete=_util.autocomplete_topics("pubsub"))
@click.argument("payload")
@click.option("--header", "-h", multiple=True)
def cli(topic, payload, header):
    """Publish a message on a given topic."""
    header = list(kv.split("=", 1) for kv in header)
    a0.Publisher(topic).pub(a0.Packet(header, payload))
