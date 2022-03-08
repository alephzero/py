import a0
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


@cli.command()
@click.argument("topic", shell_complete=_util.autocomplete_topics("pubsub"))
def clear(topic):
    """Clear the pubsub topic."""
    t = a0.Transport(a0.File(a0.env.topic_tmpl_pubsub().format(topic=topic)))
    tlk = t.lock()
    tlk.clear()
