import a0
import click
import glob
import os
import signal
import sys


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(-1)


@click.group()
def cli():
    pass


@cli.command()
def ls():
    """List all topics with logs."""
    files = glob.glob(os.path.join(a0.env.root(), "**/*.log.a0"),
                      recursive=True)
    for file in files:
        file = os.path.relpath(file, a0.env.root())
        file = file[:-len(".log.a0")]
        print(file)


@cli.command()
@click.argument("topic")
@click.option("--level",
              type=click.Choice(list(a0.LogLevel.__members__),
                                case_sensitive=False),
              default=a0.LogLevel.INFO.name,
              show_default=True)
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
def echo(topic, level, init, iter):
    """Echo the messages logged on the given topic."""
    level = getattr(a0.LogLevel, level.upper())
    init = getattr(a0.ReaderInit, init.upper())
    iter = getattr(a0.ReaderIter, iter.upper())

    # Remove click SIGINT handler.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    ll = a0.LogListener(topic, level, init, iter,
                        lambda pkt: print(pkt.payload.decode()))

    # Wait for SIGINT (ctrl+c).
    signal.pause()


@cli.command()
@click.argument("topic")
def clear(topic):
    """Clear the log history for the given topic."""
    t = a0.Transport(a0.File(f"{topic}.log.a0"))
    tl = t.lock()
    tl.clear()
