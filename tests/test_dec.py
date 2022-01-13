import a0
import threading


def test_dec():

    cv = threading.Condition()
    payloads = []

    @a0.dec.sub("foo")
    def foo(pkt):
        with cv:
            payloads.append(pkt.payload)
            cv.notify()

    @a0.dec.sub
    def bar(pkt):
        with cv:
            payloads.append(pkt.payload)
            cv.notify()

    @a0.dec.sub("bar")
    def bar2(pkt):
        with cv:
            payloads.append(pkt.payload)
            cv.notify()

    a0.dec.start_all()

    foo_pub = a0.Publisher("foo")
    foo_pub.pub("hello")

    bar_pub = a0.Publisher("bar")
    bar_pub.pub("world")

    with cv:
        cv.wait_for(lambda: len(payloads) == 3)
    assert sorted(payloads) == [b"hello", b"world", b"world"]
