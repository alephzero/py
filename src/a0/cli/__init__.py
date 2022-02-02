import click
import pkg_resources
import os
import sys
from importlib.machinery import SourceFileLoader


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(-1)


@click.group()
def cli():
    pass


def main():
    known_cmds = set()

    def add_cmd(name, module):
        if name in known_cmds:
            fail(f"multiple commands named '{name}'")
        known_cmds.add(name)
        if not hasattr(module, "cli"):
            fail(f"no cli entry point in '{name}'")
        cli.add_command(module.cli, name)

    for cmd in pkg_resources.iter_entry_points("a0.cli.cmds"):
        add_cmd(cmd.name, cmd.load())

    def load_cmds_from(dirpath):
        for filename in os.listdir(dirpath):
            name, ext = os.path.splitext(filename)
            if name.startswith("_") or ext != ".py":
                continue
            filepath = os.path.join(dirpath, filename)
            add_cmd(name, SourceFileLoader(name, filepath).load_module())

    env_path = os.environ.get("A0_CLI_CMDS_PATH")
    if env_path:
        for i, path in enumerate(env_path.split(":")):
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                fail(
                    f"Path doesn't exist: Env['A0_CLI_CMDS_PATH'][{i}]='{path}'"
                )
            load_cmds_from(path)

    local_path = os.path.expanduser("~/.config/alephzero/cli/cmds/")
    if os.path.exists(local_path):
        load_cmds_from(local_path)

    cli()


if __name__ == "__main__":
    main()
