import a0
import click
import signal
import sys
from . import _util


@click.command()
@click.argument("topic", shell_complete=_util.autocomplete_topics("rpc"))
@click.argument("value")
@click.option("--header", "-h", multiple=True)
@click.option("--file", "-f", is_flag=True)
@click.option("--stdin", is_flag=True)
@click.option("--timeout", type=float)
def cli(topic, value, header, file, stdin, timeout):
    """Send an rpc on a given topic."""
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

    client = a0.RpcClient(topic)
    req = a0.Packet(header, payload)

    try:
        if timeout:
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            reply = client.send_blocking(req, timeout=timeout)
        else:
            reply = client.send_blocking(req)
        sys.stdout.buffer.write(reply.payload)
    except Exception:
        client.cancel(req.id)
