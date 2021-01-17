import glob
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension

sources = ['module.cc']
headers = []
for directory in [
        './alephzero/include', './alephzero/include/a0', './alephzero/src'
]:
    for extension in ['c', 'cpp']:
        sources += glob.glob(f'{directory}/*.{extension}')
    for extension in ['h', 'hpp']:
        headers += glob.glob(f'{directory}/*.{extension}')

module = Pybind11Extension('alephzero_bindings',
                           sources=sources,
                           include_dirs=['./alephzero/include/'],
                           extra_compile_args=['-std=c++17', '-O3'])

setup(name='alephzero',
      version='0.2.4',
      description='TODO: description',
      author='Leonid Shamis',
      author_email='leonid.shamis@gmail.com',
      url='https://github.com/alephzero/py',
      long_description='''TODO: long description''',
      ext_modules=[module],
      py_modules=['a0'],
      headers=headers)
