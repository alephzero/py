import a0
import pytest


def test_constructor():
    pkt = a0.Packet()
    assert len(pkt.id) == 37
    assert len(pkt.headers) == 0
    assert len(pkt.payload) == 0
