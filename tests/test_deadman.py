import a0
import pytest
import os


def test_deadman():
    a0.File.remove("foo.deadman")
    assert not os.path.exists("/dev/shm/alephzero/foo.deadman")

    d = a0.Deadman("foo")
    assert os.path.exists("/dev/shm/alephzero/foo.deadman")

    assert not d.state().is_taken

    assert d.try_take()

    s = d.state()
    assert s.is_taken
    assert s.is_owner

    assert d.try_take()
    assert d.state().is_taken

    d.release()

    assert not d.state().is_taken

    d.take()

    s = d.state()
    assert s.is_taken
    assert s.is_owner

    # with pytest.raises(RuntimeError) as err:
    #     d.take(0.1)
    # assert str(err.value) == "Resource deadlock avoided"

    d.release()

    assert not d.state().is_taken
