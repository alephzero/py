import a0
import threading
import pytest
import time


class State:

    def __init__(self):
        self.detected_cnt = 0
        self.missed_cnt = 0

    def ondetected(self):
        self.detected_cnt += 1

    def onmissed(self):
        self.missed_cnt += 1


@pytest.fixture()
def test_shm():
    a0.Shm.unlink("/test.shm")
    yield a0.Shm("/test.shm")
    a0.Shm.unlink("/test.shm")


def test_shb_shbl_ehbl_ehb(test_shm):
    hb = a0.Heartbeat(test_shm, a0.Heartbeat.Options(freq=100))
    a0.Subscriber.read_one(test_shm, a0.INIT_MOST_RECENT)

    s = State()

    hbl = a0.HeartbeatListener(test_shm,
                               a0.HeartbeatListener.Options(min_freq=75),
                               s.ondetected, s.onmissed)

    time.sleep(1.0 / 50.0)

    del hbl

    assert s.detected_cnt == 1
    assert s.missed_cnt == 0


def test_shb_shbl_ehb_ehbl(test_shm):
    hb = a0.Heartbeat(test_shm, a0.Heartbeat.Options(freq=100))
    a0.Subscriber.read_one(test_shm, a0.INIT_MOST_RECENT)

    s = State()

    hbl = a0.HeartbeatListener(test_shm,
                               a0.HeartbeatListener.Options(min_freq=75),
                               s.ondetected, s.onmissed)

    time.sleep(1.0 / 50.0)

    assert s.detected_cnt == 1
    assert s.missed_cnt == 0

    del hb

    time.sleep(1.0 / 50.0)

    assert s.detected_cnt == 1
    assert s.missed_cnt == 1


def test_shbl_shb_ehb_ehbl(test_shm):
    s = State()

    hbl = a0.HeartbeatListener(test_shm,
                               a0.HeartbeatListener.Options(min_freq=75),
                               s.ondetected, s.onmissed)

    time.sleep(1.0 / 50.0)

    assert s.detected_cnt == 0
    assert s.missed_cnt == 0

    hb = a0.Heartbeat(test_shm, a0.Heartbeat.Options(freq=100))

    time.sleep(1.0 / 50.0)

    assert s.detected_cnt == 1
    assert s.missed_cnt == 0

    del hb

    time.sleep(1.0 / 50.0)

    assert s.detected_cnt == 1
    assert s.missed_cnt == 1


def test_ignore_old(test_shm):
    hb = a0.Heartbeat(test_shm, a0.Heartbeat.Options(freq=100))
    a0.Subscriber.read_one(test_shm, a0.INIT_MOST_RECENT)
    del hb

    time.sleep(1.0 / 50.0)

    # At this point, a heartbeat is written, but old.

    s = State()

    hbl = a0.HeartbeatListener(test_shm,
                               a0.HeartbeatListener.Options(min_freq=75),
                               s.ondetected, s.onmissed)

    time.sleep(1.0 / 50.0)

    assert s.detected_cnt == 0
    assert s.missed_cnt == 0

    hb = a0.Heartbeat(test_shm, a0.Heartbeat.Options(freq=100))

    time.sleep(1.0 / 50.0)

    assert s.detected_cnt == 1
    assert s.missed_cnt == 0


def test_async_close(test_shm):
    hb = a0.Heartbeat(test_shm, a0.Heartbeat.Options(freq=100))

    class NS:
        pass

    ns = NS()
    ns.init_event = threading.Event()
    ns.stop_event = threading.Event()
    ns.hbl = None

    def ondetected():
        assert ns.init_event.wait(timeout=1.0 / 50.0)

        def trigger_stop():
            ns.stop_event.set()

        ns.hbl.async_close(trigger_stop)

    ns.hbl = a0.HeartbeatListener(test_shm,
                                  a0.HeartbeatListener.Options(min_freq=75),
                                  ondetected, None)

    ns.init_event.set()
    assert ns.stop_event.wait(timeout=1.0 / 50.0)

    del ns.hbl
