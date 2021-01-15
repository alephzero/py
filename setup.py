from setuptools import setup, Extension
import glob
# import subprocess


class get_pybind_include(object):

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


# subprocess.check_call(['git', 'submodule', 'init'], cwd='./alephzero')
# subprocess.check_call(['git', 'submodule', 'update'], cwd='./alephzero')
module = Extension('alephzero_bindings',
                   sources=['module.cc'] + glob.glob('./alephzero/src/*.c*'),
                   include_dirs = ['./alephzero/include/', get_pybind_include(), get_pybind_include(user=True)],
                   extra_compile_args = ['-std=c++17', '-O3'])


setup(name='alephzero',
      version='0.2.0',
      description='TODO: description',
      author='Leonid Shamis',
      author_email='leonid.shamis@gmail.com',
      url='https://github.com/alephzero/py',
      long_description='''TODO: long description''',
      ext_modules=[module],
      py_modules=['a0'],
      install_requires=["pybind11>=v2.5.0"])
