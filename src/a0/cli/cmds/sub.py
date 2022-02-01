import a0
import click
import signal
import sys


@click.command()
@click.argument("topic")
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

    def onpkt(pkt):
        sys.stdout.buffer.write(pkt.payload)
        sys.stdout.buffer.write(sep)
        sys.stdout.flush()

    s = a0.Subscriber(topic, init, iter, onpkt)

    # Remove click SIGINT handler.
    signal.signal(signal.SIGINT, lambda *args: None)
    # Wait for SIGINT (ctrl+c).
    signal.pause()
