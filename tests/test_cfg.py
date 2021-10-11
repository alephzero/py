import a0
import json
import pytest


@pytest.fixture()
def cfg():
    cfg = a0.Cfg("topic")
    cfg.write(
        json.dumps({
            "foo": {
                "a": "aaa",
                "b": "bbb",
            },
            "bar": 3,
            "bat": [1, 2, 3],
        }))
    yield cfg


def test_cfg_int(cfg):
    bar = a0.cfg("topic", "/bar", int)

    assert bar == 3
    assert str(bar) == "3"

    cfg.write(
        json.dumps({
            "bar": 4,
            "foo": {
                "a": "abc",
                "b": "bcd",
            },
            "bat": [1, 2, 3],
        }))

    assert bar == 3

    a0.update_configs()

    assert bar == 4


def test_cfg_str(cfg):
    a = a0.cfg("topic", "/foo/a", str)

    assert a == "aaa"

    cfg.write(
        json.dumps({
            "bar": 4,
            "foo": {
                "a": "abc",
                "b": "bcd",
            },
            "bat": [1, 2, 3],
        }))

    assert a == "aaa"

    a0.update_configs()

    assert a == "abc"


def test_cfg_dict(cfg):
    foo = a0.cfg("topic", "/foo", dict)

    assert foo == {"a": "aaa", "b": "bbb"}

    cfg.write(
        json.dumps({
            "bar": 4,
            "foo": {
                "a": "abc",
                "b": "bcd",
            },
            "bat": [1, 2, 3],
        }))

    assert foo == {"a": "aaa", "b": "bbb"}

    a0.update_configs()

    assert foo == {"a": "abc", "b": "bcd"}


def test_cfg_list(cfg):
    val = a0.cfg("topic", "/bat")
    assert val == [1, 2, 3]

    val = a0.cfg("topic", "/bat", list)
    assert val == [1, 2, 3]


def test_cfg_class(cfg):

    class Foo:

        def __init__(self, a, b):
            self.a = a
            self.b = b

        def __str__(self):
            return f"Foo(a={self.a}, b={self.b})"

        def __len__(self):
            return len(self.a) + len(self.b)

        def bar(self):
            return 5

    foo = a0.cfg("topic", "/foo", Foo)

    assert (str(type(foo))
            == """<class 'a0.cfg(topic='topic', jptr='/foo', type_=Foo)'>""")

    assert foo.a == "aaa"
    assert foo.b == "bbb"
    assert str(foo) == "Foo(a=aaa, b=bbb)"
    assert len(foo) == 6  # type: ignore "__len__" is not present
    assert foo.bar() == 5

    cfg.write(
        json.dumps({
            "bar": 4,
            "foo": {
                "a": "abc",
                "b": "bcd",
            },
            "bat": [1, 2, 3],
        }))

    assert foo.a == "aaa"
    assert foo.b == "bbb"
    assert str(foo) == "Foo(a=aaa, b=bbb)"

    a0.update_configs()

    assert foo.a == "abc"
    assert foo.b == "bcd"
    assert str(foo) == "Foo(a=abc, b=bcd)"


def test_cfg_mergepatch(cfg):
    cfg = a0.Cfg("topic")
    assert json.loads(cfg.read().payload) == {
        "bar": 3,
        "bat": [1, 2, 3],
        "foo": {
            "a": "aaa",
            "b": "bbb"
        },
    }
    cfg.mergepatch({"bar": 4})
    assert json.loads(cfg.read().payload) == {
        "bar": 4,
        "bat": [1, 2, 3],
        "foo": {
            "a": "aaa",
            "b": "bbb"
        },
    }
