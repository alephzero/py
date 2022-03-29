from a0._jptr import *
import pytest


def test_jptr_get():
    # RFC Tests
    obj = {
        "foo": ["bar", "baz"],
        "": 0,
        "a/b": 1,
        "c%d": 2,
        "e^f": 3,
        "g|h": 4,
        "i\\j": 5,
        'k"l': 6,
        " ": 7,
        "m~n": 8,
    }

    assert jptr_get(obj, "") == obj
    assert jptr_get(obj, "/foo") == ["bar", "baz"]
    assert jptr_get(obj, "/foo/0") == "bar"
    assert jptr_get(obj, "/") == 0
    assert jptr_get(obj, "/a~1b") == 1
    assert jptr_get(obj, "/c%d") == 2
    assert jptr_get(obj, "/e^f") == 3
    assert jptr_get(obj, "/g|h") == 4
    assert jptr_get(obj, "/i\\j") == 5
    assert jptr_get(obj, '/k"l') == 6
    assert jptr_get(obj, "/ ") == 7
    assert jptr_get(obj, "/m~0n") == 8

    # Invalid tests
    with pytest.raises(KeyError):
        jptr_get({}, "/a")

    with pytest.raises(IndexError):
        jptr_get([0], "/1")

    # Array index tests
    assert jptr_get([0, 1, 2], "/0") == 0
    assert jptr_get([0, 1, 2], "/2") == 2
    assert jptr_get([0, 1, 2], "/-") == 2


def test_jptr_set():
    with pytest.raises(ValueError) as err:
        jptr_set({}, "", "foo")
    assert str(err.value) == "JSON Pointer cannot set root object"

    with pytest.raises(TypeError):
        jptr_set(None, "/", "foo")

    with pytest.raises(TypeError):
        jptr_set("abc", "/", "foo")

    with pytest.raises(TypeError):
        jptr_set(5, "/", "foo")

    obj = {"a": "b"}
    jptr_set(obj, "/a", "c")
    assert obj == {"a": "c"}

    obj = {"a": "b"}
    jptr_set(obj, "/c/d", "e")
    assert obj == {"a": "b", "c": {"d": "e"}}

    obj = {"a": "b"}
    jptr_set(obj, "/c/d", None)
    assert obj == {"a": "b", "c": {"d": None}}

    obj = []
    jptr_set(obj, "/0/a/0", "b")
    assert obj == [{"a": ["b"]}]

    obj = ["a"]
    jptr_set(obj, "/2/b/-", "c")
    assert obj == ["a", None, {"b": ["c"]}]
    jptr_set(obj, "/2/b/-", "d")
    assert obj == ["a", None, {"b": ["c", "d"]}]

    with pytest.raises(ValueError) as err:
        jptr_set({"a": "b"}, "/0/2", "d")
    assert str(err.value) == "JSON Object cannot be indexed by a number"

    with pytest.raises(ValueError) as err:
        jptr_set({"a": "b"}, "/-/2", "d")
    assert str(err.value) == "JSON Object cannot be indexed by a number"

    with pytest.raises(ValueError) as err:
        jptr_set(["a"], "/a", "d")
    assert str(err.value) == "JSON Array cannot be indexed by a string"

    obj = {"a": "b"}
    jptr_set(obj, '/"-"/2', "d")
    assert obj == {"a": "b", "-": [None, None, "d"]}

    obj = {"a": "b"}
    jptr_set(obj, '/"-"/"2"', "d")
    assert obj == {"a": "b", "-": {"2": "d"}}

    obj = {"a": "b"}
    jptr_set(obj, '/"-"/""2"', "d")
    assert obj == {"a": "b", "-": {'"2': "d"}}
