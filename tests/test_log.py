import a0
import os
import threading


def test_logger():
    a0.File.remove("foo.log.a0")
    assert not os.path.exists("/dev/shm/alephzero/foo.log.a0")

    logger = a0.Logger("foo")
    assert os.path.exists("/dev/shm/alephzero/foo.log.a0")

    cv = threading.Condition()

    class State:
        msgs = []

    def callback(pkt):
        with cv:
            hdrs = dict(pkt.headers)
            State.msgs.append([hdrs["a0_log_level"], pkt.payload])
            cv.notify()

    qos = a0.Reader.Qos(a0.INIT_AWAIT_NEW, a0.ITER_NEXT)
    listener = a0.LogListener("foo", a0.LogLevel.INFO, qos, callback)

    logger.crit("crit")
    logger.err("err")
    logger.warn("warn")
    logger.info("info")
    logger.dbg("dbg")

    with cv:
        cv.wait_for(lambda: len(State.msgs) == 4)
    assert State.msgs == [
        ["CRIT", b"crit"],
        ["ERR", b"err"],
        ["WARN", b"warn"],
        ["INFO", b"info"],
    ]
