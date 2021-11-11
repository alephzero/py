from alephzero_bindings import *
import asyncio
import base64
import json
import jsonpointer
import threading
import types
import weakref
import websocket

#################
# Configuration #
#################


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


###########
# AsyncIO #
###########


class _aio_read_base:

    def __init__(self, generator_factory, loop=None):
        ns = types.SimpleNamespace()
        ns.loop = loop or asyncio.get_event_loop()
        ns.q = asyncio.Queue(1)
        ns.cv = threading.Condition()
        ns.closing = False

        # Note: To prevent cyclic dependencies, `callback` is NOT owned by
        # self.
        def callback(pkt):
            with ns.cv:
                if ns.closing:
                    return

                def onloop():
                    asyncio.ensure_future(ns.q.put(pkt))

                ns.loop.call_soon_threadsafe(onloop)
                ns.cv.wait()

        self._ns = ns
        self._reader = generator_factory(callback)

    def __del__(self):
        with self._ns.cv:
            self._ns.closing = True
            self._ns.cv.notify()
        del self._reader  # Block until callback completes.

    def __aiter__(self):
        return self

    async def __anext__(self):
        pkt = await self._ns.q.get()
        with self._ns.cv:
            self._ns.cv.notify()
        return pkt


def aio_read(arena, init_, iter_, loop=None):

    def factory(callback):
        return Reader(arena, init_, iter_, callback)

    return _aio_read_base(factory, loop)


async def aio_read_one(arena, init_, loop=None):
    async for pkt in aio_read(arena, init_, ITER_NEXT, loop):
        return pkt


def aio_sub(topic, init_, iter_, loop=None):

    def factory(callback):
        return Subscriber(topic, init_, iter_, callback)

    return _aio_read_base(factory, loop)


async def aio_sub_one(topic, init_, loop=None):
    async for pkt in aio_sub(topic, init_, ITER_NEXT, loop):
        return pkt


def aio_cfg(topic, loop=None):

    def factory(callback):
        return CfgWatcher(topic, callback)

    return _aio_read_base(factory, loop)


async def aio_cfg_one(topic, loop=None):
    async for pkt in aio_cfg(topic, loop):
        return pkt


class AioRpcClient:

    def __init__(self, topic, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._client = RpcClient(topic)

    async def send(self, pkt):
        ns = types.SimpleNamespace()
        ns.fut = asyncio.Future(loop=self._loop)

        def callback(pkt):

            def onloop():
                ns.fut.set_result(pkt)

            self._loop.call_soon_threadsafe(onloop)

        self._client.send(pkt, callback)

        return await ns.fut


##########
# Remote #
##########


class RemoteSubscriber:

    def __init__(
        self,
        remote_host,
        topic,
        init_,
        iter_,
        callback,
        remote_port=24880,
        response_encoding="base64",
        scheduler="IMMEDIATE",
    ):
        addr = f"ws://{remote_host}:{remote_port}/wsapi/sub"
        handshake = json.dumps(
            dict(
                topic=topic,
                init={
                    INIT_AWAIT_NEW: "AWAIT_NEW",
                    INIT_MOST_RECENT: "MOST_RECENT",
                    INIT_OLDEST: "OLDEST",
                }[init_],
                iter={
                    ITER_NEXT: "NEXT",
                    ITER_NEWEST: "NEWEST",
                }[iter_],
                response_encoding=response_encoding,
                scheduler=scheduler,
            ))

        # State is a container for mutable variables that are referenced from
        # within both the threaded run function and the destructor.
        class State:
            pass

        self._state = State()
        self._state.running = True
        self._state.cv = threading.Condition()
        self._state.ws = None

        # _run connects to the API, streams down the packets, and executes
        # the callback.
        #
        # _run CANNOT refer to self, or else the RemoteSubscriber reference
        # count will never go to zero and RemoteSubscriber will never be
        # shutdown.
        #
        # _run will auto-reconnect with exponential backoff.
        def _run(state):
            # backoff keeps track of the number of failed connection attempts.
            # It is reset when a connection is successful.
            backoff = 0
            # last_seq is used to prevent executing the callback with repeated
            # packets, if the connection is reset.
            last_seq = None
            while state.running:
                with state.cv:
                    try:
                        state.ws = websocket.create_connection(addr)
                        backoff = 0
                    except ConnectionRefusedError as err:
                        state.ws = None
                        backoff += 1
                        state.cv.wait(timeout=min(5, (2**backoff) / 1000))
                        continue

                state.ws.send(handshake)

                while True:
                    try:
                        msg = state.ws.recv()
                    except websocket.WebSocketConnectionClosedException:
                        # Remote API died.
                        break

                    if not msg:
                        # RemoteSubscriber went out of scope.
                        return

                    jmsg = json.loads(msg)
                    if response_encoding == "base64":
                        jmsg["payload"] = base64.b64decode(jmsg["payload"])

                    # Use sequence numbers to remove duplicates, in case of reconnects.
                    seq = [
                        v for k, v in jmsg["headers"] if k == "a0_transport_seq"
                    ]
                    if len(seq) != 1:
                        continue
                    try:
                        seq = int(seq[0])
                    except ValueError:
                        continue

                    if last_seq and seq <= last_seq:
                        continue
                    last_seq = seq

                    callback(Packet(jmsg["headers"], jmsg["payload"]))

        self._thread = threading.Thread(target=_run, args=(self._state,))
        self._thread.start()

    def __del__(self):
        self._state.running = False
        with self._state.cv:
            if self._state.ws:
                self._state.ws.close()
            self._state.cv.notify()
        self._thread.join()
