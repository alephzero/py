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
    for cmd_res in pkg_resources.iter_entry_points("a0.cli.cmds"):
        cmd = cmd_res.load()
        cli.add_command(cmd.cli, cmd_res.name)

    def load_cmds_from(dirpath):
        for filename in os.listdir(dirpath):
            name, ext = os.path.splitext(filename)
            if name.startswith("_") or ext != ".py":
                continue
            filepath = os.path.join(dirpath, filename)
            cmd = SourceFileLoader(name, filepath).load_module()
            cli.add_command(cmd.cli, name)

    env_path = os.environ.get("A0_CLI_CMDS_PATH")
    if env_path:
        env_path = os.path.expanduser(env_path)
        if not os.path.exists(env_path):
            fail(f"Path doesn't exist: Env['A0_CLI_CMDS_PATH']='{env_path}'")
        load_cmds_from(env_path)

    local_path = os.path.expanduser("~/.config/alephzero/cli/cmds/")
    if os.path.exists(local_path):
        load_cmds_from(local_path)

    cli()


if __name__ == "__main__":
    main()
