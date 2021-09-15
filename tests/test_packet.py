import a0


def test_packet():
    pkt = a0.Packet()
    assert len(pkt.id) == 36
    assert len(pkt.headers) == 0
    assert len(pkt.payload) == 0
    assert pkt.payload.decode() == ""

    pkt = a0.Packet("Hello, World!")
    assert len(pkt.id) == 36
    assert pkt.headers == []
    assert pkt.payload.decode() == "Hello, World!"

    pkt = a0.Packet(b"Hello, World!")
    assert len(pkt.id) == 36
    assert pkt.headers == []
    assert pkt.payload.decode() == "Hello, World!"

    pkt = a0.Packet([("foo", "bar"), ("aaa", "bbb")], b"Hello, World!")
    assert len(pkt.id) == 36
    assert sorted(pkt.headers) == [("aaa", "bbb"), ("foo", "bar")]
    assert pkt.payload == b"Hello, World!"

    assert pkt.payload_view == b"Hello, World!"
