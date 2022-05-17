import a0
import click
from . import _util


@click.command()
@click.argument("file", shell_complete=_util.autocomplete_files)
@click.argument("payload")
@click.option("--header", "-h", multiple=True)
@click.option("--add_standard_headers", is_flag=True)
def cli(file, payload, header, add_standard_headers):
    """Write a message on a given file."""
    header = list(kv.split("=", 1) for kv in header)

    w = a0.Writer(a0.File(_util.abspath(file)))
    if add_standard_headers:
        w.push(a0.add_standard_headers())
    w.write(a0.Packet(header, payload))
