import a0
import os
import pytest
import threading
import time

pytestmark = pytest.mark.asyncio


def test_pubsub():
    a0.File.remove("foo.pubsub.a0")
    assert not os.path.exists("/dev/shm/alephzero/foo.pubsub.a0")

    p = a0.Publisher("foo")
    ss = a0.SubscriberSync("foo", a0.INIT_OLDEST)
    assert os.path.exists("/dev/shm/alephzero/foo.pubsub.a0")

    cv = threading.Condition()

    class State:
        payloads = []

    def callback(pkt):
        with cv:
            State.payloads.append(pkt.payload)
            cv.notify()

    s = a0.Subscriber("foo", a0.INIT_OLDEST, callback)

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
    assert ss.read_blocking(timeout=0.2).payload == b"post_sleep"
    t.join()

    t = threading.Thread(target=sleep_write, args=(0.2, b"post_sleep"))
    t.start()
    with pytest.raises(RuntimeError, match="Connection timed out"):
        ss.read_blocking(timeout=a0.TimeMono.now() + 0.1)
    t.join()


async def test_aio_sub():
    a0.File.remove("foo.pubsub.a0")

    p = a0.Publisher("foo")

    def thread_main():
        for i in range(5):
            time.sleep(0.1)
            p.pub("keep going")
        p.pub("done")

    t = threading.Thread(target=thread_main)
    t.start()

    assert (await a0.aio_sub_one("foo",
                                 a0.INIT_MOST_RECENT)).payload == b"keep going"

    cnt = 0
    async for pkt in a0.aio_sub("foo", a0.INIT_OLDEST):
        cnt += 1
        assert pkt.payload in [b"keep going", b"done"]
        if pkt.payload == b"done":
            break
    assert cnt == 6

    assert (await a0.aio_sub_one("foo", a0.INIT_MOST_RECENT)).payload == b"done"

    t.join()
