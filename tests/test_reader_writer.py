import a0
import threading


def test_reader_writer():
    a0.File.remove("foo")
    file = a0.File("foo")

    w = a0.Writer(file)
    rs = a0.ReaderSync(file, a0.INIT_OLDEST, a0.ITER_NEXT)

    cv = threading.Condition()
    pkt_cnt = 0
    def callback(pkt):
        with cv:
            nonlocal pkt_cnt
            pkt_cnt += 1
            cv.notify()

    r = a0.Reader(file, a0.INIT_OLDEST, a0.ITER_NEXT, callback)

    assert not rs.has_next()
    w.write("hello")
    assert rs.has_next()
    pkt = rs.next()
    assert pkt.payload == b"hello"
    assert pkt.headers == []
    assert not rs.has_next()

    w.push(a0.add_transport_seq_header())
    w2 = w.wrap(a0.add_writer_seq_header())

    w.write("aaa")
    w2.write("bbb")

    pkt = rs.next()
    assert pkt.payload == b"aaa"
    assert pkt.headers == [("a0_transport_seq", "1")]
    pkt = rs.next()
    assert pkt.payload == b"bbb"
    assert sorted(pkt.headers) == [("a0_transport_seq", "2"), ("a0_writer_seq", "0")]

    with cv:
        cv.wait_for(lambda: pkt_cnt >= 3)
