import setuptools
from pybind11.setup_helpers import Pybind11Extension
import subprocess

subprocess.run(
    ["make", "lib/libalephzero.a", "A0_EXT_YYJSON=1", "-j"],
    cwd="./alephzero",
    check=True,
)

module = Pybind11Extension(
    "alephzero_bindings",
    sources=["module.cc"],
    extra_compile_args=["-flto", "-O2"],
    extra_objects=["./alephzero/lib/libalephzero.a"],
    include_dirs=[
        "./alephzero/include/",
        "./alephzero/third_party/yyjson/src/",
    ],
    define_macros=[("A0_EXT_YYJSON", "1")],
)

setuptools.setup(name="alephzero",
                 version="0.3.14",
                 description="TODO: description",
                 author="Leonid Shamis",
                 author_email="leonid.shamis@gmail.com",
                 url="https://github.com/alephzero/py",
                 long_description="""TODO: long description""",
                 ext_modules=[module],
                 packages=setuptools.find_packages(where="./src"),
                 package_dir={"": "src"},
                 install_requires=[
                     "click>=8.0.3",
                     "jsonpointer>=2.1",
                     "websocket-client>=1.2.1",
                 ],
                 entry_points={
                     "console_scripts": ["a0 = a0.cli:main"],
                     "a0.cli.cmds": [
                         "cfg = a0.cli.cmds.cfg",
                         "log = a0.cli.cmds.log",
                         "prpc = a0.cli.cmds.prpc",
                         "pub = a0.cli.cmds.pub",
                         "pubsub = a0.cli.cmds.pubsub",
                         "rpc = a0.cli.cmds.rpc",
                         "sub = a0.cli.cmds.sub",
                     ],
                 })
