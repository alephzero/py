import a0
import os


def test_pathglob():
    glob = a0.PathGlob("/dev/shm/a/foo.a0")
    assert glob.match("/dev/shm/a/foo.a0")
    assert not glob.match("/dev/shm/a/b/foo.a0")

    glob = a0.PathGlob("/dev/shm/*/foo.a0")
    assert glob.match("/dev/shm/a/foo.a0")
    assert not glob.match("/dev/shm/a/b/foo.a0")

    glob = a0.PathGlob("/dev/shm/*/*.a0")
    assert glob.match("/dev/shm/a/foo.a0")
    assert not glob.match("/dev/shm/a/b/foo.a0")

    glob = a0.PathGlob("/dev/shm/**/*.a0")
    assert glob.match("/dev/shm/a/foo.a0")
    assert glob.match("/dev/shm/a/b/foo.a0")

    glob = a0.PathGlob("/dev/shm/**/b/*.a0")
    assert not glob.match("/dev/shm/a/foo.a0")
    assert glob.match("/dev/shm/a/b/foo.a0")

    glob = a0.PathGlob("/dev/shm/**")
    assert glob.match("/dev/shm/foo.a0")

    glob = a0.PathGlob("/dev/shm/**/**/**/**/**/*******b***/*.a0")
    assert glob.match("/dev/shm/a/b/foo.a0")

    glob = a0.PathGlob("/dev/shm/**/*.a0")
    assert glob.match("/dev/shm/foo.a0")

    glob = a0.PathGlob("foo.a0")
    assert glob.match("/dev/shm/alephzero/foo.a0")
    assert not glob.match("/foo.a0")
    assert glob.match("foo.a0")

    glob = a0.PathGlob("**/*.a0")
    assert glob.match("a/foo.a0")
    assert glob.match("a/b/foo.a0")
    assert glob.match("/dev/shm/alephzero/a/foo.a0")
    assert glob.match("/dev/shm/alephzero/a/b/foo.a0")
    assert not glob.match("/foo/bar/a/foo.a0")
    assert not glob.match("/foo/bar/a/b/foo.a0")

    os.environ["A0_ROOT"] = "/foo/bar"
    glob = a0.PathGlob("**/*.a0")
    assert glob.match("a/foo.a0")
    assert glob.match("a/b/foo.a0")
    assert not glob.match("/dev/shm/alephzero/a/foo.a0")
    assert not glob.match("/dev/shm/alephzero/a/b/foo.a0")
    assert glob.match("/foo/bar/a/foo.a0")
    assert glob.match("/foo/bar/a/b/foo.a0")
    del os.environ["A0_ROOT"]
