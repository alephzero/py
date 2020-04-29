import a0


def test_constructor():
    pkt = a0.Packet()
    assert len(pkt.id) == 36
    assert len(pkt.headers) == 0
    assert len(pkt.payload) == 0
