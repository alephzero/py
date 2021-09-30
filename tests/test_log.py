import a0
import os
import threading


def test_logger():
    os.putenv("A0_TOPIC_TMPL_LOG", "alephzero/{topic}.log.a0")
    a0.File.remove("alephzero/foo.log.a0")
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

    listener = a0.LogListener("foo", a0.LogLevel.INFO, callback)

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
