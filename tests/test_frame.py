import a0


def test_frame_from_buffer():
    arena = a0.Arena(bytearray([0] * 4000), a0.Arena.Mode.SHARED)
    a0.Writer(arena).write("foo")

    class Capture:
        pass

    def fn(tlk, _):
        assert tlk.frame().seq == 1
        assert a0.FlatPacket.from_buffer(tlk.frame().data).payload == b"foo"

        Capture.frame_memory_view = tlk.frame().memory_view

    r = a0.ReaderSyncZeroCopy(arena, a0.INIT_OLDEST)
    r.read(fn)

    frame = a0.Frame.from_buffer(Capture.frame_memory_view)
    assert frame.seq == 1
    assert a0.FlatPacket.from_buffer(frame.data).payload == b"foo"
