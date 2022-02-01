import a0
import click
import signal


@click.command()
@click.argument("topic")
@click.option("--init",
              type=click.Choice(list(a0.ReaderInit.__members__),
                                case_sensitive=False),
              default=a0.ReaderInit.AWAIT_NEW.name)
@click.option("--iter",
              type=click.Choice(list(a0.ReaderIter.__members__),
                                case_sensitive=False),
              default=a0.ReaderIter.NEXT.name)
def cli(topic, init, iter):
    """Echo the messages logged on the given topic."""
    init = getattr(a0.ReaderInit, init.upper())
    iter = getattr(a0.ReaderIter, iter.upper())

    s = a0.Subscriber(topic, init, iter,
                      lambda pkt: print(pkt.payload.decode()))

    # Remove click SIGINT handler.
    signal.signal(signal.SIGINT, lambda *args: None)
    # Wait for SIGINT (ctrl+c).
    signal.pause()
