import a0
import json
import pytest
import threading
import time

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def cfg():
    # a0.File.remove(a0.env.topic_tmpl_cfg().replace("{topic}", "topic"))
    cfg = a0.Cfg("topic")
    cfg.write(
        json.dumps(
            {
                "foo": {
                    "a": "aaa",
                    "b": "bbb",
                },
                "bar": 3,
                "bat": [1, 2, 3],
            }
        )
    )
    yield cfg


def test_cfg_int(cfg):
    bar = a0.cfg("topic", "/bar", int)

    assert bar.read() == 3

    cfg.write(
        json.dumps(
            {
                "bar": 4,
                "foo": {
                    "a": "abc",
                    "b": "bcd",
                },
                "bat": [1, 2, 3],
            }
        )
    )

    assert bar.read() == 4

    bar.write(5)

    assert json.loads(cfg.read().payload.decode()) == {
        "bar": 5,
        "foo": {
            "a": "abc",
            "b": "bcd",
        },
        "bat": [1, 2, 3],
    }


def test_cfg_str(cfg):
    a = a0.cfg("topic", "/foo/a", str)

    assert a.read() == "aaa"

    cfg.write(
        json.dumps(
            {
                "bar": 4,
                "foo": {
                    "a": "abc",
                    "b": "bcd",
                },
                "bat": [1, 2, 3],
            }
        )
    )

    assert a.read() == "abc"

    a.write("bcd")

    assert json.loads(cfg.read().payload.decode()) == {
        "bar": 4,
        "foo": {
            "a": "bcd",
            "b": "bcd",
        },
        "bat": [1, 2, 3],
    }


def test_cfg_dict(cfg):
    foo = a0.cfg("topic", "/foo")
    assert foo.read() == {"a": "aaa", "b": "bbb"}

    foo = a0.cfg("topic", "/foo", dict)
    assert foo.read() == {"a": "aaa", "b": "bbb"}

    cfg.write(
        json.dumps(
            {
                "bar": 4,
                "foo": {
                    "a": "abc",
                    "b": "bcd",
                },
                "bat": [1, 2, 3],
            }
        )
    )

    assert foo.read() == {"a": "abc", "b": "bcd"}

    foo.write({"a": 0, "b": 1})

    assert json.loads(cfg.read().payload.decode()) == {
        "bar": 4,
        "foo": {
            "a": 0,
            "b": 1,
        },
        "bat": [1, 2, 3],
    }


def test_cfg_list(cfg):
    bat = a0.cfg("topic", "/bat")
    assert bat.read() == [1, 2, 3]

    bat = a0.cfg("topic", "/bat", list)
    assert bat.read() == [1, 2, 3]

    bat.write([1, 2, 3, 4])

    assert json.loads(cfg.read().payload.decode()) == {
        "bar": 3,
        "foo": {
            "a": "aaa",
            "b": "bbb",
        },
        "bat": [1, 2, 3, 4],
    }


def test_cfg_list_index(cfg):
    bat = a0.cfg("topic", "/bat/1")
    assert bat.read() == 2

    bat = a0.cfg("topic", "/bat/1", int)
    assert bat.read() == 2

    bat = a0.cfg("topic", "/bat/1", float)
    assert bat.read() == 2

    # https://datatracker.ietf.org/doc/html/rfc7386
    # If the patch is anything other than an object, the result will always be
    # to replace the entire target with the entire patch.  Also, it is not
    # possible to patch part of a target that is not an object, such as to
    # replace just some of the values in an array.

    bat.write(3)

    assert json.loads(cfg.read().payload.decode()) == {
        "bar": 3,
        "foo": {
            "a": "aaa",
            "b": "bbb",
        },
        "bat": [None, 3],
    }


def test_cfg_class(cfg):
    class Foo:
        def __init__(self, a, b):
            self.a = a
            self.b = b

        def tojson(self):
            return {"a": self.a, "b": self.b}

    foo_cfg = a0.cfg("topic", "/foo", Foo)
    foo = foo_cfg.read()

    assert type(foo) == Foo

    assert foo.a == "aaa"
    assert foo.b == "bbb"
    foo.a = "a"
    foo.b = "b"

    foo_cfg.write(foo)

    assert json.loads(cfg.read().payload.decode()) == {
        "bar": 3,
        "foo": {
            "a": "a",
            "b": "b",
        },
        "bat": [1, 2, 3],
    }

    foo.a = "aa"
    foo.b = "bb"
    foo_cfg.write({"a": foo.a, "b": foo.b})

    assert json.loads(cfg.read().payload.decode()) == {
        "bar": 3,
        "foo": {
            "a": "aa",
            "b": "bb",
        },
        "bat": [1, 2, 3],
    }


def test_cfg_write_if_empty():
    a0.File.remove(a0.env.topic_tmpl_cfg().replace("{topic}", "topic"))
    cfg = a0.Cfg("topic")
    assert cfg.write_if_empty("cfg 0")
    assert not cfg.write_if_empty("cfg 1")
    assert cfg.read().payload == b"cfg 0"
    cfg.write("cfg 2")
    assert cfg.read().payload == b"cfg 2"


def test_cfg_mergepatch(cfg):
    assert json.loads(cfg.read().payload) == {
        "bar": 3,
        "bat": [1, 2, 3],
        "foo": {"a": "aaa", "b": "bbb"},
    }
    cfg.mergepatch({"bar": 4})
    assert json.loads(cfg.read().payload) == {
        "bar": 4,
        "bat": [1, 2, 3],
        "foo": {"a": "aaa", "b": "bbb"},
    }


async def test_aio_cfg():
    a0.File.remove(a0.env.topic_tmpl_cfg().replace("{topic}", "topic"))
    cfg = a0.Cfg("topic")

    def thread_main():
        for _ in range(5):
            time.sleep(0.1)
            cfg.write("keep going")
        cfg.write("done")

    t = threading.Thread(target=thread_main)
    t.start()

    assert (await a0.aio_cfg_one("topic")).payload == b"keep going"

    cnt = 0
    async for pkt in a0.aio_cfg("topic"):
        cnt += 1
        assert pkt.payload in [b"keep going", b"done"]
        if pkt.payload == b"done":
            break
    assert cnt == 6

    assert (await a0.aio_cfg_one("topic")).payload == b"done"

    t.join()
