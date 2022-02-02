# Aleph Zero: Python
[![CI](https://github.com/alephzero/py/workflows/CI/badge.svg)](https://github.com/alephzero/py/actions?query=workflow%3ACI)

See https://github.com/alephzero/alephzero for details

See https://github.com/alephzero/playground for examples.

## Install Instructions

```sh
pip install alephzero
```

## Example Publish

```py
import a0
p = a0.Publisher("topic")
p.pub("msg")
```

## Example Subscribe

```py
import a0
s = a0.Subscriber("topic", lambda pkt: print(pkt.payload))
```

## CLI

### Examples

Publish a message:
```sh
a0 pub topic msg
```

Subscribe to a topic:
```sh
a0 sub topic
```

Get more info:
```sh
a0 --help
```

Get more info for a command:
```sh
a0 cfg --help
```

### Auto-complete

Add the following snippet to your `~/.bashrc`:
```sh
eval "$(_A0_COMPLETE=bash_source a0)"
```

```sh
$ a0 <TAB><TAB>
cfg     log     prpc    pub     pubsub  rpc     sub
$ a0 cfg <TAB><TAB>
clear  echo   ls     set
```

### Custom Commands

The `a0` script searches for command plugins in three places:

1) pip installed entry-points with key `a0.cli.cmds`
2) `~/.config/alephzero/cli/cmds/`
3) `env[A0_CLI_CMDS_PATH]`

With (2) and (3), any python file in the path is expected to be a command file. The name of the file is the name of the command, for example `foo.py` will be triggered by the command line `a0 foo`. The file should export a symbol called `cli` which is either a `click.command` or `click.group`.

`env[A0_CLI_CMDS_PATH]` supports a colon separated list of paths.
