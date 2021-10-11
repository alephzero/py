import a0
import threading


def test_discovery():
    try:
        a0.File.remove_all("discovery_test")
    except Exception as _:
        pass

    a0.File("discovery_test/unused")
    a0.File.remove("discovery_test/unused")

    cv = threading.Condition()

    class State:
        paths = []

    def callback(path):
        with cv:
            State.paths.append(path)
            cv.notify()

    d = a0.Discovery("/dev/shm/discovery_test/**/*.a0", callback)

    a0.File("discovery_test/file.a0")
    a0.File("discovery_test/a/file.a0")
    a0.File("discovery_test/a/b/file.a0")
    a0.File("discovery_test/a/b/c/d/file.a0")
    a0.File("discovery_test/a/b/c/d/file2.a0")
    a0.File("discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file.a0")
    a0.File("discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file2.a0")
    a0.File("discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file3.a0")
    a0.File("discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file4.a0")
    a0.File("discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file5.a0")
    a0.File("discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file6.a0")
    a0.File("discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file7.a0")
    a0.File("discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file8.a0")

    with cv:
        cv.wait_for(lambda: len(State.paths) >= 13)

    d = None

    State.paths.sort()
    assert State.paths == [
        "/dev/shm/discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file.a0",
        "/dev/shm/discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file2.a0",
        "/dev/shm/discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file3.a0",
        "/dev/shm/discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file4.a0",
        "/dev/shm/discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file5.a0",
        "/dev/shm/discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file6.a0",
        "/dev/shm/discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file7.a0",
        "/dev/shm/discovery_test/a/b/c/d/e/f/g/h/i/j/k/l/m/file8.a0",
        "/dev/shm/discovery_test/a/b/c/d/file.a0",
        "/dev/shm/discovery_test/a/b/c/d/file2.a0",
        "/dev/shm/discovery_test/a/b/file.a0",
        "/dev/shm/discovery_test/a/file.a0",
        "/dev/shm/discovery_test/file.a0",
    ]
