import a0
import os
import threading


def test_pubsub():
    a0.File.remove("foo.pubsub.a0")
    assert not os.path.exists("/dev/shm/alephzero/foo.pubsub.a0")

    p = a0.Publisher("foo")
    ss = a0.SubscriberSync("foo", a0.INIT_OLDEST, a0.ITER_NEXT)
    assert os.path.exists("/dev/shm/alephzero/foo.pubsub.a0")

    cv = threading.Condition()

    class State:
        payloads = []

    def callback(pkt):
        with cv:
            State.payloads.append(pkt.payload)
            cv.notify()

    s = a0.Subscriber("foo", a0.INIT_OLDEST, a0.ITER_NEXT, callback)

    assert not ss.has_next()
    p.pub("hello")
    assert ss.has_next()
    pkt = ss.next()
    assert pkt.payload == b"hello"
    assert sorted(k for k, _ in pkt.headers) == [
        "a0_time_mono",
        "a0_time_wall",
        "a0_transport_seq",
        "a0_writer_id",
        "a0_writer_seq",
    ]
    assert not ss.has_next()

    p.pub(a0.Packet([("key", "val")], "world"))

    pkt = ss.next()
    assert pkt.payload == b"world"
    assert sorted(k for k, _ in pkt.headers) == [
        "a0_time_mono",
        "a0_time_wall",
        "a0_transport_seq",
        "a0_writer_id",
        "a0_writer_seq",
        "key",
    ]

    with cv:
        cv.wait_for(lambda: len(State.payloads) == 2)
    assert State.payloads == [b"hello", b"world"]
