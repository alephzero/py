import a0
import os
import pytest
import threading
import time


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

    assert not ss.can_read()
    p.pub("hello")
    assert ss.can_read()
    pkt = ss.read()
    assert pkt.payload == b"hello"
    assert sorted(k for k, _ in pkt.headers) == [
        "a0_time_mono",
        "a0_time_wall",
        "a0_transport_seq",
        "a0_writer_id",
        "a0_writer_seq",
    ]
    assert not ss.can_read()

    p.pub(a0.Packet([("key", "val")], "world"))

    pkt = ss.read()
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

    def sleep_write(timeout, pkt):
        time.sleep(timeout)
        p.pub(pkt)

    t = threading.Thread(target=sleep_write, args=(0.1, b"post_sleep"))
    t.start()
    assert ss.read_blocking().payload == b"post_sleep"
    t.join()

    t = threading.Thread(target=sleep_write, args=(0.1, b"post_sleep"))
    t.start()
    assert ss.read_blocking(timeout=a0.TimeMono.now() +
                            0.2).payload == b"post_sleep"
    t.join()

    t = threading.Thread(target=sleep_write, args=(0.2, b"post_sleep"))
    t.start()
    with pytest.raises(RuntimeError, match="Connection timed out"):
        ss.read_blocking(timeout=a0.TimeMono.now() + 0.1)
    t.join()
