import a0
import click
import sys


@click.command()
@click.argument("topic")
@click.option("--header", "-h", multiple=True)
@click.option("--value")
@click.option("--file", "-f")
@click.option("--stdin", is_flag=True)
@click.option("--empty", is_flag=True)
def cli(topic, header, value, file, stdin, empty):
    """Publish a message on a given topic."""
    selected = [opt for opt in [value, file, stdin, empty] if opt]
    if not selected:
        print("One of value, file, stdin, and empty are required",
              file=sys.stderr)
        sys.exit(-1)

    if len(selected) > 1:
        print("value, file, stdin, and empty are mutually exclusive",
              file=sys.stderr)
        sys.exit(-1)

    header = list(kv.split("=", 1) for kv in header)

    if value:
        pass
    elif file:
        value = open(file, "rb").read()
    elif stdin:
        value = sys.stdin.read()
    elif empty:
        value = ""

    a0.Publisher(topic).pub(a0.Packet(header, value))
