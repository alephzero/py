from alephzero_bindings import *
from ._opts import *
import asyncio
import threading
import types


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


def aio_read(arena, *args, opts=None, init_=None, iter_=None, loop=None):
    opts = make_opts(*args, opts, init_, iter_)

    def factory(callback):
        return Reader(arena, opts, callback)

    return _aio_read_base(factory, loop)


async def aio_read_one(arena, *args, opts=None, init_=None, loop=None):
    opts = make_opts(*args, opts, init_)

    async for pkt in aio_read(arena, opts, loop):
        return pkt


def aio_sub(topic, *args, opts=None, init_=None, iter_=None, loop=None):
    opts = make_opts(*args, opts, init_, iter_)

    def factory(callback):
        return Subscriber(topic, opts, callback)

    return _aio_read_base(factory, loop)


async def aio_sub_one(topic, *args, opts=None, init_=None, loop=None):
    opts = make_opts(*args, opts, init_)

    async for pkt in aio_sub(topic, init_, opts, loop):
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
