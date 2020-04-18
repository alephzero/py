from distutils.core import setup, Extension
import pybind11

module = Extension('alephzero_bindings',
                   include_dirs = [
                       '/usr/include',
                        pybind11.get_include(True),
                        pybind11.get_include(False),
                   ],
                   library_dirs = ['/usr/lib'],
                   libraries = ['alephzero'],
                   sources = ['module.cc'],
                   extra_compile_args = ['-std=c++17'],
                   extra_link_args=['-lrt'])

setup(name = 'alephzero',
      version = '0.1',
      description = 'TODO: description',
      author = 'Leonid Shamis',
      author_email = 'leonid.shamis@gmail.com',
      url = 'https://github.com/alephzero/py',
      long_description = '''TODO: long description''',
      ext_modules = [module],
      py_modules = ['a0'])
