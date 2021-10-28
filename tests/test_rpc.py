import a0
import os
import threading


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
            if req.pkt.payload.decode() == "reply":
                req.reply(b"reply")
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
