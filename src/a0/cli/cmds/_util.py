import a0
import click
import datetime
import glob
import os
import re
import signal
import sys
import threading


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


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


class ClickDuration(click.ParamType):
    name = "duration"

    def convert(self, value, param, ctx):
        if isinstance(value, datetime.timedelta):
            return value

        if isfloat(value):
            return datetime.timedelta(seconds=float(value))

        pattern = r'^((?P<hours>[\.\d]+?)h)?((?P<minutes>[\.\d]+?)m)?((?P<seconds>[\.\d]+?)s)?$'

        parts = re.match(pattern, value)
        if parts is None:
            self.fail(
                f"{value!r} is not valid. Use something like '1m3s', '63s', or '63'",
                param, ctx)

        return datetime.timedelta(
            **{
                key: float(group_val)
                for key, group_val in parts.groupdict().items()
                if group_val
            })

    def __repr__(self) -> str:
        return "Duration"


class StreamHelper:

    def __init__(self, max_count=None, duration=None):
        self.max_count = max_count
        self.timeout = duration.total_seconds() if duration else None

        self.cv = threading.Condition()
        self.count = 0
        self.closing = False

    def shutdown(self):
        with self.cv:
            self.closing = True
            self.cv.notify()

    def increment_count(self):
        with self.cv:
            self.count += 1
            if self.max_count is not None and self.count >= self.max_count:
                self.shutdown()

    def wait_shutdown(self):
        with self.cv:
            self.cv.wait_for(lambda: self.closing, timeout=self.timeout)

    def install_sighandlers(self):

        def onsigint(*args, **kwargs):
            with self.cv:
                self.closing = True
                self.cv.notify()

        signal.signal(signal.SIGINT, onsigint)
