import a0
import click
import sys
from . import _util


@click.command()
@click.argument("topic", shell_complete=_util.autocomplete_topics("prpc"))
@click.argument("value")
@click.option("--header", "-h", multiple=True)
@click.option("--file", "-f", is_flag=True)
@click.option("--stdin", is_flag=True)
@click.option("--delim",
              type=click.Choice(["empty", "null", "newline"],
                                case_sensitive=False),
              default="newline",
              show_default=True)
def cli(topic, value, header, file, stdin, delim):
    """Send an prpc on a given topic."""
    if file and stdin:
        _util.fail("file and stdin are mutually exclusive")

    header = list(kv.split("=", 1) for kv in header)

    if file:
        payload = open(file, "rb").read()
    elif stdin:
        payload = sys.stdin.buffer.read()
    else:
        payload = value

    sep = {
        "empty": b"",
        "null": b"\0",
        "newline": b"\n",
    }[delim]

    stream = _util.StreamHelper()
    stream.install_sighandlers()

    def onprogress(pkt, done):
        try:
            sys.stdout.buffer.write(pkt.payload)
            sys.stdout.buffer.write(sep)
            sys.stdout.flush()
            if done:
                stream.shutdown()
        except BrokenPipeError:
            stream.shutdown()

    client = a0.PrpcClient(topic)
    client.connect(a0.Packet(header, payload), onprogress)

    stream.wait_shutdown()
