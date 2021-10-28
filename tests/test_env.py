import a0
import contextlib
import os


@contextlib.contextmanager
def scoped_env(**kwargs):
    old_env = dict(os.environ)
    os.environ.update(kwargs)
    yield
    os.environ.clear()
    os.environ.update(old_env)


def test_env():
    assert a0.env.root() == "/dev/shm/alephzero"
    assert a0.env.topic() is None

    with scoped_env(A0_ROOT="/dev/shm/tmp", A0_TOPIC="test"):
        assert a0.env.root() == "/dev/shm/tmp"
        assert a0.env.topic() == "test"
