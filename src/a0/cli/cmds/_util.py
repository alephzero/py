import a0
import glob
import os
import sys


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(-1)


def detect_topics(protocol):
    topics = []
    detected = glob.glob(os.path.join(a0.env.root(), f"**/*.{protocol}.a0"),
                         recursive=True)
    for abspath in detected:
        relpath = os.path.relpath(abspath, a0.env.root())
        topic = relpath[:-len(f".{protocol}.a0")]
        topics.append(topic)
    return topics


def autocomplete_topics(protocol):

    def fn(ctx, param, incomplete):
        return [
            topic for topic in detect_topics(protocol)
            if topic.startswith(incomplete)
        ]

    return fn


def abspath(path):
    if path.startswith("./"):
        return os.path.abspath(path)
    return os.path.abspath(os.path.join(a0.env.root(),
                                        os.path.expanduser(path)))


def autocomplete_files(ctx, param, incomplete):
    abspath_prefix = abspath(incomplete)
    detected = glob.glob(abspath_prefix + "*") + glob.glob(
        abspath_prefix + "**/*.a0", recursive=True)
    return [path for path in detected if path.endswith(".a0")]
