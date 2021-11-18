from setuptools import setup
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

setup(
    name="alephzero",
    version="0.3.10",
    description="TODO: description",
    author="Leonid Shamis",
    author_email="leonid.shamis@gmail.com",
    url="https://github.com/alephzero/py",
    long_description="""TODO: long description""",
    ext_modules=[module],
    py_modules=["a0"],
    install_requires=[
        "jsonpointer>=2.1",
        "websocket-client>=1.2.1",
    ],
)
