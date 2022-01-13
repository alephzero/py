import a0
import os
import pytest
import threading
import time


def test_rpc():
    a0.File.remove("foo.rpc.a0")
    assert not os.path.exists("/dev/shm/alephzero/foo.rpc.a0")

    cv = threading.Condition()

    class State:
        requests = []
        cancels = []
        replies = []

    def onrequest(req):
        with cv:
            State.requests.append(req.pkt.payload)
            if req.pkt.payload == b"reply":
                req.reply(b"reply")
            if req.pkt.payload.startswith(b"sleep"):
                time.sleep(0.2)
                req.reply(b"slept")
            cv.notify()

    def oncancel(id):
        with cv:
            State.cancels.append(id)
            cv.notify()

    server = a0.RpcServer("foo", onrequest, oncancel)
    assert os.path.exists("/dev/shm/alephzero/foo.rpc.a0")

    def onreply(pkt):
        with cv:
            State.replies.append(pkt.payload)
            cv.notify()

    client = a0.RpcClient("foo")
    client.send("reply", onreply)
    client.send("reply", onreply)
    pkt = a0.Packet("cancel")
    client.send(pkt, onreply)
    client.cancel(pkt.id)

    with cv:
        cv.wait_for(lambda: (len(State.requests) == 3 and len(State.cancels) ==
                             1 and len(State.replies) == 2))

    reply = client.send_blocking("sleep")
    assert reply.payload == b"slept"
    reply = client.send_blocking("sleep", timeout=a0.TimeMono.now() + 0.3)
    assert reply.payload == b"slept"
    with pytest.raises(RuntimeError, match="Connection timed out"):
        client.send_blocking("sleep", timeout=a0.TimeMono.now() + 0.1)

    assert client.send_fut("reply").result().payload == b"reply"
