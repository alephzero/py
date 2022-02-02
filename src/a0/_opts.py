from alephzero_bindings import *


def make_opts(*args):
    opts = Reader.Options()
    for arg in args:
        if isinstance(arg, Reader.Options):
            opts = arg
        elif isinstance(arg, Reader.Init):
            opts.init = arg
        elif isinstance(arg, Reader.Iter):
            opts.iter = arg
    return opts
