import a0
import os


def test_file():
    a0.File.remove("foo")

    file = a0.File("foo")
    assert len(file.arena.buf) == 16 * 1024 * 1024
    assert file.size == 16 * 1024 * 1024
    assert file.path == "/dev/shm/foo"
    assert file.fd > 3
    assert file.stat.st_size == 16 * 1024 * 1024

    path = file.path
    del file
    assert os.path.exists(path)
    a0.File.remove("foo")
    assert not os.path.exists(path)

    fileopts = a0.File.Options.DEFAULT()
    fileopts.create_options.size = 1024
    file = a0.File("foo", fileopts)
    assert len(file.arena.buf) == 1024
