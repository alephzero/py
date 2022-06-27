import a0
import click
import sys
from . import _util


@click.command()
@click.argument("file", shell_complete=_util.autocomplete_files)
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
@click.option("--count", "-n", type=click.INT)
@click.option("--duration", "-t", type=_util.ClickDuration())
def cli(file, init, iter, delim, count=None, duration=None):
    """Echo the messages written on the given file."""
    init = getattr(a0.ReaderInit, init.upper())
    iter = getattr(a0.ReaderIter, iter.upper())

    sep = {
        "empty": b"",
        "null": b"\0",
        "newline": b"\n",
    }[delim]

    stream = _util.StreamHelper(count, duration)
    stream.install_sighandlers()

    def onpkt(pkt):
        try:
            sys.stdout.buffer.write(pkt.payload)
            sys.stdout.buffer.write(sep)
            sys.stdout.flush()
            stream.increment_count()
        except BrokenPipeError:
            stream.shutdown()

    reader = a0.Reader(a0.File(_util.abspath(file)), init, iter, onpkt)

    stream.wait_shutdown()
