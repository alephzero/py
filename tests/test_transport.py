import a0
import contextlib
import pytest
import threading
import time


def test_transport():
    a0.File.remove("foo")
    file = a0.File("foo")

    w = a0.Writer(file)
    w.write("aaa")
    w.write("bbb")
    w.write("ccc")

    transport = a0.Transport(file)
    tlk = transport.lock()

    assert not tlk.empty()

    tlk.jump_head()
    assert tlk.iter_valid()
    assert a0.FlatPacket(tlk.frame()).payload == b"aaa"

    tlk.jump_tail()
    assert tlk.iter_valid()
    assert a0.FlatPacket(tlk.frame()).payload == b"ccc"

    tlk.jump_head()
    assert tlk.has_next()
    tlk.step_next()
    assert tlk.iter_valid()
    assert a0.FlatPacket(tlk.frame()).payload == b"bbb"

    tlk.jump_tail()
    assert tlk.has_prev()
    tlk.step_prev()
    assert tlk.iter_valid()
    assert a0.FlatPacket(tlk.frame()).payload == b"bbb"

    @contextlib.contextmanager
    def thread_sleep_write(pkt, timeout):

        def sleep_write(pkt, timeout):
            time.sleep(timeout)
            w.write(pkt)

        t = threading.Thread(target=sleep_write, args=(pkt, timeout))
        t.start()
        yield
        t.join()

    tlk.jump_tail()

    with thread_sleep_write("ddd", timeout=0.1):
        tlk.wait(tlk.has_next)
        tlk.step_next()
        assert a0.FlatPacket(tlk.frame()).payload == b"ddd"

    with thread_sleep_write("eee", timeout=0.1):
        tlk.wait(tlk.has_next, timeout=0.2)
        tlk.step_next()
        assert a0.FlatPacket(tlk.frame()).payload == b"eee"

    with thread_sleep_write("fff", timeout=0.2):
        with pytest.raises(RuntimeError, match="Connection timed out"):
            tlk.wait(tlk.has_next, timeout=0.1)
        # Note we need to release the lock here.
        # The wait returned, having reacquired the lock.
        # The thread needs to acquire the lock to do the write.
        tlk = None
