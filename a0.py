from alephzero_bindings import *
import asyncio
import threading
import types


class aio_sub:

    def __init__(self, file, init_, iter_, loop=None):
        ns = types.SimpleNamespace()
        ns.loop = loop or asyncio.get_event_loop()
        ns.q = asyncio.Queue(1)
        ns.cv = threading.Condition()
        ns.closing = False

        # Note: To prevent cyclic dependencies, `callback` is NOT owned by
        # self.
        def callback(pkt_view):
            pkt = Packet(pkt_view)
            with ns.cv:
                if ns.closing:
                    return

                def onloop():
                    asyncio.ensure_future(ns.q.put(pkt))

                ns.loop.call_soon_threadsafe(onloop)
                ns.cv.wait()

        self._ns = ns
        self._sub = Subscriber(file, init_, iter_, callback)

    def __del__(self):
        with self._ns.cv:
            self._ns.closing = True
            self._ns.cv.notify()
        del self._sub  # Block until callback completes.

    def __aiter__(self):
        return self

    async def __anext__(self):
        pkt = await self._ns.q.get()
        with self._ns.cv:
            self._ns.cv.notify()
        return pkt


async def aio_sub_one(file, init_, loop=None):
    async for pkt in aio_sub(file, init_, ITER_NEXT, loop):
        return pkt


class AioRpcClient:

    def __init__(self, file, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._client = RpcClient(file)

    async def send(self, pkt):
        ns = types.SimpleNamespace()
        ns.fut = asyncio.Future(loop=self._loop)

        def callback(pkt_view):
            pkt = Packet(pkt_view)

            def onloop():
                ns.fut.set_result(pkt)

            self._loop.call_soon_threadsafe(onloop)

        self._client.send(pkt, callback)

        return await ns.fut
