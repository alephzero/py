import a0
import pytest


def test_arena_constructor():
    bytes_ = bytes([0] * 4000)

    a0.Arena(bytes_, a0.Arena.Mode.READONLY)
    with pytest.raises(BufferError, match="Object is not writable."):
        a0.Arena(bytes_, a0.Arena.Mode.SHARED)

    bytearray_ = bytearray(bytes_)
    a0.Arena(bytearray_, a0.Arena.Mode.SHARED)


def test_arena_keep_alive():

    def make_arena():
        bytes_ = bytearray([0] * 4000)
        bytes_[3] = 4
        return a0.Arena(bytes_, a0.Arena.Mode.SHARED)

    arena = make_arena()
    assert arena.buf[3] == 4


def test_arena_buf_keep_alive():

    def make_arena_buf():
        bytes_ = bytearray([0] * 4000)
        bytes_[3] = 4
        return a0.Arena(bytes_, a0.Arena.Mode.SHARED).buf

    buf = make_arena_buf()
    assert buf[3] == 4
