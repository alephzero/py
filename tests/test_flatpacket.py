import a0


def test_flatpacket_from_buffer():
    arena = a0.Arena(bytearray([0] * 4000), a0.Arena.Mode.SHARED)
    a0.Writer(arena).write("foo")

    class Capture:
        pass

    def fn(_, fpkt):
        assert fpkt.payload == b"foo"
        Capture.fpkt_memory_view = fpkt.memory_view
        Capture.fpkt_bytes = bytes(fpkt.memory_view)

    r = a0.ReaderSyncZeroCopy(arena, a0.INIT_OLDEST)
    r.read(fn)

    fpkt = a0.FlatPacket.from_buffer(Capture.fpkt_memory_view)
    assert fpkt.payload == b"foo"

    fpkt = a0.FlatPacket.from_buffer(Capture.fpkt_bytes)
    assert fpkt.payload == b"foo"

    frame_bytes = b"\x01\x00\x00\x00\x00\x00\x00\x00\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x008\x00\x00\x00\x00\x00\x00\x00F5C71FCC-8B80-4C2E-BD78-7F669E9591AA\x00\x00\x00\x00\x00\x00\x00\x00\x005\x00\x00\x00\x00\x00\x00\x00foo"
    frame = a0.Frame.from_buffer(frame_bytes)

    assert bytes(frame.memory_view) == frame_bytes
    fpkt = a0.FlatPacket.from_buffer(bytes(frame.data))
    assert fpkt.payload == b"foo"
