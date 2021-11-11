import a0
import pytest
import threading
import time

pytestmark = pytest.mark.asyncio


def test_reader_writer():
    a0.File.remove("foo")
    file = a0.File("foo")

    w = a0.Writer(file)
    rs = a0.ReaderSync(file, a0.INIT_OLDEST, a0.ITER_NEXT)

    cv = threading.Condition()

    class State:
        payloads = []

    def callback(pkt):
        with cv:
            State.payloads.append(pkt.payload)
            cv.notify()

    r = a0.Reader(file, a0.INIT_OLDEST, a0.ITER_NEXT, callback)

    assert not rs.can_read()
    w.write("hello")
    assert rs.can_read()
    pkt = rs.read()
    assert pkt.payload == b"hello"
    assert pkt.headers == []
    assert not rs.can_read()

    w.push(a0.add_transport_seq_header())
    w2 = w.wrap(a0.add_writer_seq_header())

    w.write("aaa")
    w2.write("bbb")

    pkt = rs.read()
    assert pkt.payload == b"aaa"
    assert pkt.headers == [("a0_transport_seq", "1")]
    pkt = rs.read()
    assert pkt.payload == b"bbb"
    assert sorted(pkt.headers) == [("a0_transport_seq", "2"),
                                   ("a0_writer_seq", "0")]

    with cv:
        cv.wait_for(lambda: len(State.payloads) == 3)
    assert State.payloads == [b"hello", b"aaa", b"bbb"]

    def sleep_write(timeout, pkt):
        time.sleep(timeout)
        w.write(pkt)

    t = threading.Thread(target=sleep_write, args=(0.1, b"post_sleep"))
    t.start()
    assert rs.read_blocking().payload == b"post_sleep"
    t.join()

    t = threading.Thread(target=sleep_write, args=(0.1, b"post_sleep"))
    t.start()
    assert rs.read_blocking(timeout=0.2).payload == b"post_sleep"
    t.join()

    t = threading.Thread(target=sleep_write, args=(0.2, b"post_sleep"))
    t.start()
    with pytest.raises(RuntimeError, match="Connection timed out"):
        rs.read_blocking(timeout=a0.TimeMono.now() + 0.1)
    t.join()


async def test_aio_read():
    a0.File.remove("foo")
    file = a0.File("foo")

    w = a0.Writer(file)

    def thread_main():
        for i in range(5):
            time.sleep(0.1)
            w.write("keep going")
        w.write("done")

    t = threading.Thread(target=thread_main)
    t.start()

    assert (await a0.aio_read_one(file,
                                  a0.INIT_MOST_RECENT)).payload == b"keep going"

    cnt = 0
    async for pkt in a0.aio_read(file, a0.INIT_OLDEST, a0.ITER_NEXT):
        cnt += 1
        assert pkt.payload in [b"keep going", b"done"]
        if pkt.payload == b"done":
            break
    assert cnt == 6

    assert (await a0.aio_read_one(file, a0.INIT_MOST_RECENT)).payload == b"done"

    t.join()
