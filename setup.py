from distutils.core import setup, Extension
import pybind11
import subprocess


def pkgconfig(*packages, **kwargs):
    config = kwargs.setdefault('config', {})
    optional_args = kwargs.setdefault('optional', '')
    
    flag_map = {
        'include_dirs': ['--cflags-only-I', 2],
        'library_dirs': ['--libs-only-L', 2],
        'libraries': ['--libs-only-l', 2],
        'extra_compile_args': ['--cflags-only-other', 0],
        'extra_link_args': ['--libs-only-other', 0],
    }
    for package in packages:
        for distutils_key, (pkg_option, n) in flag_map.items():
            items = subprocess.check_output(['pkg-config', optional_args, pkg_option, package]).decode('utf8').split()
            config.setdefault(distutils_key, []).extend([i[n:] for i in items])
    return config


def merge_flags(*flags_groups):
    all_flags = {}
    for flags_group in flags_groups:
        for key, vals in flags_group.items():
            all_flags.setdefault(key, []).extend(vals)
    return all_flags


module = Extension('alephzero_bindings',
                   sources = ['module.cc'],
                   **merge_flags(
                       pkgconfig('alephzero'),
                       {
                           'include_dirs': [
                               pybind11.get_include(True),
                               pybind11.get_include(False),
                           ],
                           'extra_compile_args': [
                               '-std=c++17',
                           ],
                       }
                   ))

setup(name = 'alephzero',
      version = '0.1',
      description = 'TODO: description',
      author = 'Leonid Shamis',
      author_email = 'leonid.shamis@gmail.com',
      url = 'https://github.com/alephzero/py',
      long_description = '''TODO: long description''',
      ext_modules = [module],
      py_modules = ['a0'])
