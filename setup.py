import glob
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension

sources = ['module.cc'] + glob.glob('./alephzero/src/*.c*')
module = Pybind11Extension('alephzero_bindings',
                           sources=sources,
                           include_dirs=['./alephzero/include/'],
                           extra_compile_args=['-std=c++17', '-O3'])

setup(name='alephzero',
      version='0.2.5',
      description='TODO: description',
      author='Leonid Shamis',
      author_email='leonid.shamis@gmail.com',
      url='https://github.com/alephzero/py',
      long_description='''TODO: long description''',
      ext_modules=[module],
      py_modules=['a0'])
