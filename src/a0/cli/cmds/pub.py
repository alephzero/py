import a0
import click
import sys
from . import _util


@click.command()
@click.argument("topic", shell_complete=_util.autocomplete_topics("pubsub"))
@click.argument("value")
@click.option("--header", "-h", multiple=True)
@click.option("--file", "-f", is_flag=True)
@click.option("--stdin", is_flag=True)
def cli(topic, value, header, file, stdin):
    """Publish a message on a given topic."""
    if file and stdin:
        print("file and stdin are mutually exclusive", file=sys.stderr)
        sys.exit(-1)

    header = list(kv.split("=", 1) for kv in header)

    if file:
        payload = open(file, "rb").read()
    elif stdin:
        payload = sys.stdin.buffer.read()
    else:
        payload = value

    a0.Publisher(topic).pub(a0.Packet(header, payload))
