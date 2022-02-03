import a0
import click
import json
import jsonpointer
from . import _util


@click.group()
def cli():
    pass


@cli.command()
def ls():
    """List all topics with configs."""
    for topic in _util.detect_topics("cfg"):
        print(topic)


@cli.command()
@click.argument("topic", shell_complete=_util.autocomplete_topics("cfg"))
@click.argument("key", nargs=-1)
@click.option("--json", "format", flag_value="json", default=True)
@click.option("--list", "format", flag_value="list")
def echo(topic, key, format):
    """Echo the config for the given topic and keys."""
    try:
        cfg = json.loads(a0.Cfg(topic).read().payload)
    except Exception:
        cfg = {}

    if key:
        queried_cfg = {}
        for k in key:
            if k.startswith("/"):
                ptr = jsonpointer.JsonPointer(k)
                cfg_level = queried_cfg
                for part in ptr.parts[:-1]:
                    if part not in cfg_level:
                        cfg_level[part] = {}
                    cfg_level = cfg_level[part]
                ptr.set(queried_cfg, ptr.get(cfg))
            else:
                queried_cfg[k] = cfg.get(k)
        cfg = queried_cfg

    if format == "list":

        def walk(prefix, node):
            for key, val in node.items():
                name = f"{prefix}/{key}"
                if type(val) == dict:
                    walk(name, val)
                else:
                    print(f'"{name}" = {json.dumps(val)}')

        walk("", cfg)
    elif format == "json":
        print(json.dumps(cfg, indent=2))


@cli.command()
@click.argument("topic", shell_complete=_util.autocomplete_topics("cfg"))
@click.argument("kv", nargs=-1)
def set(topic, kv):
    """Set the config for the given topic and keys."""
    kv = dict([arg.split("=", 1) for arg in kv])
    for key, val in kv.items():
        try:
            val = json.loads(val)
        except Exception:
            pass

        mergepatch = {key: val}
        if key[0] == "/":
            parts = key.split("/")
            mergepatch = {parts[-1]: val}
            for part in parts[1:-1][::-1]:
                mergepatch = {part: mergepatch}

        a0.Cfg(topic).mergepatch(mergepatch)


@cli.command()
@click.argument("topic", shell_complete=_util.autocomplete_topics("cfg"))
@click.argument("key", nargs=-1)
def clear(topic, key):
    """Clear the config for the given topic and keys."""
    if not key:
        a0.Cfg(topic).write("{}")
        return

    for k in key:
        mergepatch = {k: None}
        if k[0] == "/":
            parts = k.split("/")
            mergepatch = {parts[-1]: None}
            for part in parts[1:-1][::-1]:
                mergepatch = {part: mergepatch}

        a0.Cfg(topic).mergepatch(mergepatch)
