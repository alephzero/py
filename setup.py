from distutils.core import setup, Extension
import glob
# import subprocess

# subprocess.check_call(['git', 'submodule', 'init'], cwd='./alephzero')
# subprocess.check_call(['git', 'submodule', 'update'], cwd='./alephzero')
module = Extension('alephzero_bindings',
                   sources=['module.cc'] + glob.glob('./alephzero/src/*.c*'),
                   include_dirs = ['./alephzero/include/'],
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
