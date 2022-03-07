from alephzero_bindings import *
from ._opts import *
import base64
import json
import threading
import websocket


class RemoteSubscriber:

    def __init__(
        self,
        remote_host,
        topic,
        callback,
        opts=None,
        init_=None,
        iter_=None,
        remote_port=24880,
        response_encoding="base64",
        scheduler="IMMEDIATE",
    ):
        addr = f"ws://{remote_host}:{remote_port}/wsapi/sub"
        opts = make_opts(opts, init_, iter_)
        handshake = {
            "topic": topic,
            "init": {
                INIT_AWAIT_NEW: "AWAIT_NEW",
                INIT_MOST_RECENT: "MOST_RECENT",
                INIT_OLDEST: "OLDEST",
            }[opts.init],
            "iter": {
                ITER_NEXT: "NEXT",
                ITER_NEWEST: "NEWEST",
            }[opts.iter],
            "response_encoding": response_encoding,
            "scheduler": scheduler,
        }

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
            while state.running:
                with state.cv:
                    try:
                        state.ws = websocket.create_connection(addr)
                        backoff = 0
                    except ConnectionError:
                        state.ws = None
                        backoff += 1
                        state.cv.wait(timeout=min(5, (2**backoff) / 1000))
                        continue

                state.ws.send(json.dumps(handshake))

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
                    headers = jmsg["headers"]
                    payload = jmsg["payload"]
                    if response_encoding == "base64":
                        payload = base64.b64decode(payload)

                    # Use sequence numbers to remove duplicates, in case of reconnects.
                    try:
                        seq_str = dict(headers).get("a0_transport_seq")
                        handshake["init"] = int(seq_str) + 1
                    except Exception:
                        continue

                    callback(Packet(headers, payload))

        self._thread = threading.Thread(target=_run, args=(self._state,))
        self._thread.start()

    def __del__(self):
        self._state.running = False
        with self._state.cv:
            if self._state.ws:
                self._state.ws.close()
            self._state.cv.notify()
        self._thread.join()
