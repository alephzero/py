import a0
import click
import glob
import os


@click.group()
def cli():
    pass


@cli.command()
def ls():
    """List all pubsub topics."""
    files = glob.glob(os.path.join(a0.env.root(), "**/*.pubsub.a0"),
                      recursive=True)
    for file in files:
        file = os.path.relpath(file, a0.env.root())
        file = file[:-len(".pubsub.a0")]
        print(file)
