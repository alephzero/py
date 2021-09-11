from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension
import subprocess
import os

subprocess.run(
    ["make", "lib/libalephzero.a", "-j"],
    cwd="./alephzero",
    check=True,
    env=dict(
        os.environ,
        A0_C_CONFIG_USE_YYJSON="0",
        A0_CXX_CONFIG_USE_NLOHMANN="0",
    ),
)

module = Pybind11Extension(
    "alephzero_bindings",
    sources=["module.cc"],
    extra_objects=["./alephzero/lib/libalephzero.a"],
    include_dirs=["./alephzero/include/"],
)

setup(
    name="alephzero",
    version="0.3.0",
    description="TODO: description",
    author="Leonid Shamis",
    author_email="leonid.shamis@gmail.com",
    url="https://github.com/alephzero/py",
    long_description="""TODO: long description""",
    ext_modules=[module],
    py_modules=["a0"],
)
