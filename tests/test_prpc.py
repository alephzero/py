import a0
import os
import threading


def test_prpc():
    os.putenv("A0_TOPIC_TMPL_PRPC", "alephzero/{topic}.prpc.a0")
    a0.File.remove("alephzero/foo.prpc.a0")
    assert not os.path.exists("/dev/shm/alephzero/foo.prpc.a0")

    cv = threading.Condition()

    class State:
        connects = []
        replies = []
        done = False

    def onconnect(conn):
        State.connects.append(conn.pkt.payload)
        conn.send("progress", False)
        conn.send("progress", False)
        conn.send("progress", False)
        conn.send("progress", False)
        conn.send("progress", True)

    server = a0.PrpcServer("foo", onconnect, lambda id: None)
    assert os.path.exists("/dev/shm/alephzero/foo.prpc.a0")

    def onprogress(pkt, done):
        State.replies.append(pkt.payload)
        if done:
            with cv:
                State.done = True
                cv.notify()

    client = a0.PrpcClient("foo")
    client.connect("connect", onprogress)

    with cv:
        cv.wait_for(lambda: State.done)
        assert len(State.connects) == 1 and len(State.replies) == 5
