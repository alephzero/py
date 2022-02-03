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
