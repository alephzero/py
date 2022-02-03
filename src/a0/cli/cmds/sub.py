import a0
import click
import signal
import sys
from . import _util


@click.command()
@click.argument("topic", shell_complete=_util.autocomplete_topics("pubsub"))
@click.option("--init",
              type=click.Choice(list(a0.ReaderInit.__members__),
                                case_sensitive=False),
              default=a0.ReaderInit.AWAIT_NEW.name,
              show_default=True)
@click.option("--iter",
              type=click.Choice(list(a0.ReaderIter.__members__),
                                case_sensitive=False),
              default=a0.ReaderIter.NEXT.name,
              show_default=True)
@click.option("--delim",
              type=click.Choice(["empty", "null", "newline"],
                                case_sensitive=False),
              default="newline",
              show_default=True)
def cli(topic, init, iter, delim):
    """Echo the messages published on the given topic."""
    init = getattr(a0.ReaderInit, init.upper())
    iter = getattr(a0.ReaderIter, iter.upper())

    sep = {
        "empty": b"",
        "null": b"\0",
        "newline": b"\n",
    }[delim]

    # Remove click SIGINT handler.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    class State:
        sub = None

    def onpkt(pkt):
        try:
            sys.stdout.buffer.write(pkt.payload)
            sys.stdout.buffer.write(sep)
            sys.stdout.flush()
        except BrokenPipeError:
            State.sub = None

    State.sub = a0.Subscriber(topic, init, iter, onpkt)

    # Wait for SIGINT (ctrl+c).
    signal.pause()
