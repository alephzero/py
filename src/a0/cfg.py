from alephzero_bindings import *
import json
import jsonpointer
import threading
import weakref


class cfg:
    registry = []
    registry_mu = threading.Lock()

    def __init__(self, topic, jptr=None, type_=None):
        obj = {}
        object.__setattr__(self, "__obj", obj)

        def __get():
            tid = threading.get_ident()
            if tid not in obj:
                cfg_val = json.loads(Cfg(topic).read().payload.decode())
                if jptr is not None:
                    cfg_val = jsonpointer.resolve_pointer(cfg_val, jptr)

                if not type_:
                    obj[tid] = cfg_val
                elif type(cfg_val) == dict:
                    obj[tid] = type_(**cfg_val)
                elif type(cfg_val) == list:
                    obj[tid] = cfg_val if type_ == list else type_(*cfg_val)
                else:
                    obj[tid] = type_(cfg_val)

                object.__setattr__(self, "__obj", obj)
            return obj[tid]

        object.__setattr__(self, "__get", __get)

        with cfg.registry_mu:
            cfg.registry.append(weakref.ref(self))

    def __getattribute__(self, name):
        return getattr(object.__getattribute__(self, "__get")(), name)

    def __bool__(self):
        return bool(object.__getattribute__(self, "__get")())

    def __new__(cls, topic, jptr=None, type_=None):
        # fmt: off
        # yapf: disable
        special_methods = [
            "__abs__", "__add__", "__aenter__", "__aexit__", "__aiter__", "__and__", "__anext__",
            "__await__", "__bytes__", "__call__", "__ceil__", "__complex__", "__contains__",
            "__delattr__", "__delete__", "__delitem__", "__dir__", "__divmod__", "__enter__",
            "__eq__", "__exit__", "__float__", "__floor__", "__floordiv__", "__format__", "__ge__",
            "__get__", "__getitem__", "__gt__", "__hash__", "__iadd__", "__iand__",
            "__ifloordiv__", "__ilshift__", "__imatmul__", "__imod__", "__imul__", "__index__",
            "__int__", "__invert__", "__ior__", "__ipow__", "__irshift__", "__isub__", "__iter__",
            "__itruediv__", "__ixor__", "__le__", "__len__", "__length_hint__", "__lshift__",
            "__lt__", "__matmul__", "__missing__", "__mod__", "__mul__", "__ne__", "__neg__",
            "__new__", "__or__", "__pos__", "__pow__", "__radd__", "__rand__", "__rdivmod__",
            "__repr__", "__reversed__", "__rfloordiv__", "__rlshift__", "__rmatmul__", "__rmod__",
            "__rmul__", "__ror__", "__round__", "__rpow__", "__rrshift__", "__rshift__",
            "__rsub__", "__rtruediv__", "__rxor__", "__set__", "__setattr__", "__setitem__",
            "__str__", "__sub__", "__truediv__", "__trunc__", "__xor__",
        ]
        # yapf: enable
        # fmt: on

        def make_method(name):

            def method(self, *args, **kw):
                return getattr(object.__getattribute__(self, "__get")(),
                               name)(*args, **kw)

            return method

        namespace = {name: make_method(name) for name in special_methods}
        full_cls_args = [f"topic={repr(topic)}"]
        if jptr:
            full_cls_args.append(f"jptr={repr(jptr)}")
        if type_:
            full_cls_args.append(f"type_={type_.__name__}")
        full_cls = type(f"{cls.__name__}({', '.join(full_cls_args)})", (cls,),
                        namespace)

        self = object.__new__(full_cls)
        full_cls.__init__(self, topic, jptr, type_)
        return self


def update_configs():
    tid = threading.get_ident()
    with cfg.registry_mu:
        next_reg = []
        for weak_cfg in cfg.registry:
            cfg_ = weak_cfg()
            if not cfg_:
                continue
            next_reg.append(weak_cfg)
            obj = object.__getattribute__(cfg_, "__obj")
            if tid in obj:
                del obj[tid]
        cfg.registry = next_reg
